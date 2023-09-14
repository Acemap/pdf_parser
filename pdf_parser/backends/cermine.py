import os
import math
import shutil
import random
import logging
import tempfile
import subprocess as sp
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from .base import Backend

logger = logging.getLogger(__name__)


class Cermine(Backend):
    def __init__(self):
        super(Cermine, self).__init__()
        file_dir = os.path.dirname(__file__)
        self.jar = os.path.join(file_dir, '..', 'jar', 'cermine-1.13.jar')

        self.typ2service = {
            'text': 'jats',
            'figure': 'images',
        }

        self.health = None
        self._check_java()

    def _check_java(self):
        cmd = ['java', '-version']
        try:
            sp.run(cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL, check=True)
            self.health = True
        except Exception:
            self.health = False
            logger.error('No java in your environment.')

    @staticmethod
    def _move_result_from_tmp_to_output(tmp_dir, output_dir):
        for name in os.listdir(tmp_dir):
            prefix, ext = os.path.splitext(name)
            if ext == '.cermxml':
                new_name = prefix + '.cermine.xml'
                shutil.move(os.path.join(tmp_dir, name), os.path.join(output_dir, new_name))
            elif ext == '.images':
                if len(os.listdir(os.path.join(tmp_dir, name))) == 0:
                    continue
                new_name = prefix + '.cermine.figure'
                shutil.move(os.path.join(tmp_dir, name), os.path.join(output_dir, new_name))

    def _process_pdf(self, input_file, output_dir, service, **kwargs):
        if not self.health:
            return 0

        class_name = 'pl.edu.icm.cermine.ContentExtractor'
        with tempfile.TemporaryDirectory() as dirname:
            shutil.copy(input_file, dirname)
            cmd = ['java', '-cp', self.jar, class_name, '-path', dirname, '-outputs', service]
            try:
                sp.run(cmd, stdout=sp.DEVNULL, stderr=None, check=True)
            except Exception as e:
                logger.warning('Cermine exit exceptly with error: %s', str(e))
            self._move_result_from_tmp_to_output(dirname, output_dir)
        return 1

    def _process_batch(self, batch_input_files, output_dir, service, **kwargs):
        if not self.health:
            return 0
        logger.debug('One Batch of %s pdfs: %s...', len(batch_input_files), ', '.join(list(batch_input_files)[:3]))

        class_name = 'pl.edu.icm.cermine.ContentExtractor'
        with tempfile.TemporaryDirectory() as dirname:
            for input_file in batch_input_files:
                shutil.copy(input_file, dirname)
            cmd = ['java', '-cp', self.jar, class_name, '-path', dirname, '-outputs', service]
            try:
                sp.run(cmd, stdout=sp.DEVNULL, stderr=None, check=True)
            except Exception as e:
                logger.warning('Cermine exit exceptly with error: %s', str(e))
            self._move_result_from_tmp_to_output(dirname, output_dir)
        return len(batch_input_files)

    def _process_dir(self, input_dir, output_dir, service, n_threads=0, **kwargs):
        if not self.health:
            return 0

        if n_threads == 0:
            n_threads = min(os.cpu_count() // 2, 30)  # one cermine process use 200% cpus average, and not exceed 30 to reduce memory

        pdf_files = []
        for file in os.listdir(input_dir):
            if file.endswith('.pdf'):
                pdf_files.append(os.path.join(input_dir, file))
        random.shuffle(pdf_files)
        batch_size = min(100, math.ceil(len(pdf_files) / n_threads / 2))

        logger.info(f'{len(pdf_files)} PDF files to process.')
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures = []
            count = 0
            for batch_start in range(len(pdf_files)):
                batch_input_files = pdf_files[batch_start:batch_start + batch_size]
                futures.append(executor.submit(self._process_batch, batch_input_files, output_dir, service, **kwargs))
            for future in as_completed(futures):
                count += future.result()
                if count // 1000 != (count - future.result()) // 1000:
                    logger.debug(f'{count} PDF files are processed')
                if count // 10000 != (count - future.result()) // 10000:
                    logger.info(f'{count} PDF files are processed')
        return len(pdf_files)

    # def parse(self, typ, input_path, output_dir, n_threads=0, **kwargs):
    #     typ2service = {
    #         'text': 'jats',
    #         'figure': 'images',
    #     }
    #
    #     if typ not in typ2service:
    #         logger.error(f'Backend {self.__name__} could not parse for type "{typ}".')
    #         return 0
    #     service = typ2service[typ]
    #
    #     if os.path.isfile(input_path):
    #         return self._process_pdf(input_path, output_dir, service, **kwargs)
    #     else:
    #         return self._process_dir(input_path, output_dir, service, n_threads, **kwargs)
