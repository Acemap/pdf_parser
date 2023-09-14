import os
import shutil
import logging
import tempfile
import subprocess as sp
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from .base import Backend

logger = logging.getLogger(__name__)


class PDFFigures(Backend):
    def __init__(self):
        super(PDFFigures, self).__init__()

        file_dir = os.path.dirname(__file__)
        self.bin = os.path.join(file_dir, '..', 'bin', 'pdffigures')

        self.typ2service = {
            'figure': ['-c', '-j'],
        }

        self.health = None
        self._check_bin()

    def _check_bin(self):
        cmd = [self.bin, '--help']
        try:
            sp.run(cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL, check=True)
            self.health = True
        except Exception:
            self.health = False
            logger.error('pdffigures cannot run with your environment. '
                              'Please check whether the dependencies "leptonica" and "poppler" have been installed.')

    @staticmethod
    def _move_result_from_tmp_to_output(tmp_dir, output_dir, input_file):
        if len(os.listdir(tmp_dir)) <= 1:
            return
        pdf_name = os.path.splitext(os.path.basename(input_file))[0]
        pdf_output_sub_dir = os.path.join(output_dir, pdf_name + '.pdffigures.figure')
        if not os.path.exists(pdf_output_sub_dir):
            os.makedirs(pdf_output_sub_dir)
        for name in os.listdir(tmp_dir):
            ext = os.path.splitext(name)[1]
            if ext == '.json':
                shutil.move(os.path.join(tmp_dir, name), os.path.join(pdf_output_sub_dir, 'figure-data.json'))
            elif ext == '.png':
                figure_name = name.split('-', maxsplit=1)[1]
                shutil.move(os.path.join(tmp_dir, name), os.path.join(pdf_output_sub_dir, figure_name))

    def _process_pdf(self, input_file, output_dir, services, **kwargs):
        if not self.health:
            return 0

        with tempfile.TemporaryDirectory() as dirname:
            prefix = os.path.join(dirname, 'prefix')
            cmd = [self.bin]
            for service in services:
                cmd.extend([service, prefix])
            cmd.append(input_file)
            sp.run(cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            self._move_result_from_tmp_to_output(dirname, output_dir, input_file)
        return 1

    def _process_dir(self, input_dir, output_dir, services, n_threads=0, **kwargs):
        if not self.health:
            return 0

        if n_threads == 0:
            n_threads = os.cpu_count()  # one cermine process use 200% cpus average

        pdf_files = []
        for file in os.listdir(input_dir):
            if file.endswith('.pdf'):
                pdf_files.append(os.path.join(input_dir, file))

        logger.info(f'{len(pdf_files)} PDF files to process.')
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures = []
            for file in pdf_files:
                futures.append(executor.submit(self._process_pdf, file, output_dir, services))
            for idx, _ in enumerate(as_completed(futures)):
                if idx % 1000 == 0:
                    logger.debug(f'{idx} PDF files are processed')
                if idx % 10000 == 0:
                    logger.info(f'{idx} PDF files are processed')
        return len(pdf_files)

    # def parse(self, typ, input_path, output_dir, n_threads=0, **kwargs):
    #     typ2services = {
    #         'figure': ['-c', '-j'],
    #     }
    #
    #     if typ not in typ2services:
    #         logger.error(f'Backend {self.__name__} could not parse for type "{typ}".')
    #         return 0
    #     services = typ2services[typ]
    #
    #     if os.path.isfile(input_path):
    #         return self._process_pdf(input_path, output_dir, services, **kwargs)
    #     else:
    #         return self._process_dir(input_path, output_dir, services, n_threads, **kwargs)
