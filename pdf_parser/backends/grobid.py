import os
import time
import logging
import requests
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from .base import Backend

logger = logging.getLogger(__name__)


class Grobid(Backend):
    def __init__(self, host, port, sleep_time=5, coordinates=None):
        super(Grobid, self).__init__()
        self.host = host
        self.port = port
        self.url = f'http://{self.host}:{self.port}'

        self.sleep_time = sleep_time
        self.coordinates = coordinates or ["persName", "figure", "ref", "biblStruct", "formula"]

        self.typ2service = {
            'text': 'processFulltextDocument',
        }

        self.health = None
        self._check_server()

    def _check_server(self):
        check_url = f'{self.url}/api/isalive'
        try:
            r = requests.get(check_url, timeout=2)
        except Exception:
            self.health = False
            logger.error(f'Cannot connect to {self.url}.')
            return

        status = r.status_code
        if status == 200:
            self.health = True
            logger.info('GROBID server is up and running.')
        else:
            self.health = False
            logger.error('GROBID server does not appear.')

    def _process_pdf(self, input_file, output_dir, service, **kwargs):
        if not self.health:
            return 0

        input_filename = os.path.basename(input_file)
        output_file = os.path.join(output_dir, os.path.splitext(input_filename)[0] + '.grobid.xml')

        if not kwargs.get('force', False) and os.path.exists(output_file):
            return 1

        files = {
            'input': (
                input_file,
                open(input_file, 'rb'),
                'application/pdf',
                {'Expires': '0'}
            )
        }

        url = f'{self.url}/api/{service}'
        data = {}
        if kwargs.get('generateIDs', False):
            data['generateIDs'] = '1'
        if kwargs.get('consolidate_header', False):
            data['consolidateHeader'] = '1'
        if kwargs.get('consolidate_citations', False):
            data['consolidateCitations'] = '1'
        if kwargs.get('teiCoordinates', False):
            data['teiCoordinates'] = self.coordinates

        while True:
            r = requests.post(url=url, data=data, files=files, headers={'Accept': 'application/xml'})
            if r.status_code == 200:  # success
                break
            elif r.status_code != 503:  # not 503 means fatal error, do not re-try, return directly
                logger.warning(f"PDF parse failed: {input_file} with http code {r.status_code}")
                return 0
            time.sleep(self.sleep_time)

        try:
            with open(output_file, 'wb') as out:
                out.write(r.content)
        except Exception:
            logger.error(f"Could not write out result file: {output_file}")
            return 0

        return 1

    def _process_dir(self, input_dir, output_dir, service, n_threads=0, **kwargs):
        if not self.health:
            return 0

        if n_threads == 0:
            n_threads = 112  # the number of cpus of server10, because the grobid server always run on server10

        pdf_files = []
        for file in os.listdir(input_dir):
            if file.endswith('.pdf'):
                pdf_files.append(os.path.join(input_dir, file))

        logger.info(f'{len(pdf_files)} PDF files to process.')
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures = []
            for file in pdf_files:
                futures.append(executor.submit(self._process_pdf, file, output_dir, service, **kwargs))
            for idx, _ in enumerate(as_completed(futures)):
                if idx % 1000 == 0:
                    logger.debug(f'{idx} PDF files are processed')
                if idx % 10000 == 0:
                    logger.info(f'{idx} PDF files are processed')
        return len(pdf_files)

    # def parse(self, typ, input_path, output_dir, n_threads=0, **kwargs):
    #     typ2service = {
    #         'text': 'processFulltextDocument',
    #     }
    #
    #     if typ not in typ2service:
    #         logger.error(f'Backend {self.__name__} could not parse for type "{typ}".')
    #         return 0
    #     service = typ2service[typ]
    #
    #     if os.path.isfile(input_path):
    #         return self._process_pdf(input_path, output_dir, service, force=True, **kwargs)
    #     else:
    #         return self._process_dir(input_path, output_dir, service, n_threads, force=True, **kwargs)
