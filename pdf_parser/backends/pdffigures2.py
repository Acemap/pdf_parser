import os
import json
import shutil
import logging
import tempfile
import subprocess as sp

from .base import Backend

logger = logging.getLogger(__name__)


class PDFFigures2(Backend):
    def __init__(self):
        super(PDFFigures2, self).__init__()

        file_dir = os.path.dirname(__file__)
        self.jar = os.path.join(file_dir, '..', 'jar', 'pdffigures2-0.1.0.jar')

        self.typ2service = {
            'text': ['-g'],
            'figure': ['-d', '-m'],
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
    def _move_result_from_tmp_to_output(tmp_dir, output_dir, tmp_id2pdf_name, services):
        if '-g' in services:  # text mode
            for name in os.listdir(tmp_dir):
                tmp_id, ext = os.path.splitext(name)
                if ext == '.json':
                    new_name = tmp_id2pdf_name[tmp_id] + '.pdffigures2.json'
                    shutil.move(os.path.join(tmp_dir, name), os.path.join(output_dir, new_name))
        else:  # figure mode
            new_dirs = []
            for name in os.listdir(tmp_dir):
                ext = os.path.splitext(name)[1]
                if ext == '.json':
                    tmp_id = os.path.splitext(name)[0]
                    pdf_output_sub_dir = os.path.join(output_dir, tmp_id2pdf_name[tmp_id] + '.pdffigures2.figure')
                    if not os.path.exists(pdf_output_sub_dir):
                        new_dirs.append(pdf_output_sub_dir)
                        os.makedirs(pdf_output_sub_dir)

                    # update renderURL in figure data json, and then write to output_dir
                    with open(os.path.join(tmp_dir, name), encoding='utf-8', errors='ignore') as fp_in:
                        figure_data = json.load(fp_in)
                        for item in figure_data:
                            new_render_url = os.path.basename(item['renderURL']).split('-', maxsplit=1)[1]
                            item['renderURL'] = new_render_url
                        with open(os.path.join(pdf_output_sub_dir, 'figure-data.json'), 'w',
                                  encoding='utf-8') as fp_out:
                            json.dump(figure_data, fp_out)
                elif ext == '.png':
                    tmp_id, figure_name = name.split('-', maxsplit=1)
                    pdf_output_sub_dir = os.path.join(output_dir, tmp_id2pdf_name[tmp_id] + '.pdffigures2.figure')
                    if not os.path.exists(pdf_output_sub_dir):
                        os.makedirs(pdf_output_sub_dir)
                    shutil.move(os.path.join(tmp_dir, name), os.path.join(pdf_output_sub_dir, figure_name))
            for dirname in new_dirs:
                if len(os.listdir(dirname)) <= 1:
                    shutil.rmtree(dirname)

    def _process_pdf(self, input_file, output_dir, services, **kwargs):
        if not self.health:
            return 0

        tmp_id2pdf_name = {'0': os.path.splitext(os.path.basename(input_file))[0]}
        with tempfile.TemporaryDirectory() as dirname:
            shutil.copy(input_file, os.path.join(dirname, '0.pdf'))
            if not dirname.endswith(os.sep):
                dirname += os.sep
            cmd = ['java', '-jar', self.jar, '-e']
            for service in services:
                cmd.extend([service, dirname])
            cmd.append(dirname)
            sp.run(cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            self._move_result_from_tmp_to_output(dirname, output_dir, tmp_id2pdf_name, services)
        return 1

    def _process_batch(self, batch_input_files, output_dir, services, n_threads=0, **kwargs):
        if not self.health:
            return 0
        logger.debug('One Batch of %s pdfs: %s...', len(batch_input_files), ', '.join(list(batch_input_files)[:3]))

        with tempfile.TemporaryDirectory() as dirname:
            if not dirname.endswith(os.sep):
                dirname += os.sep

            tmp_id2pdf_name = {}
            for input_file in batch_input_files:
                tmp_id = str(len(tmp_id2pdf_name))
                pdf_name = os.path.splitext(os.path.basename(input_file))[0]
                tmp_id2pdf_name[tmp_id] = pdf_name
                shutil.copy(input_file, os.path.join(dirname, '%s.pdf' % tmp_id))

            cmd = ['java', '-jar', self.jar, '-e', '-t', str(n_threads)]
            for service in services:
                cmd.extend([service, dirname])
            cmd.append(dirname)

            sp.run(cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            self._move_result_from_tmp_to_output(dirname, output_dir, tmp_id2pdf_name, services)
        return len(batch_input_files)

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
        count = 0
        step = 1000
        for start in range(0, len(pdf_files), step):
            self._process_batch(pdf_files[start: start + step], output_dir, services, n_threads, **kwargs)
            count += step
            if count // 1000 != (count - step) // 1000:
                logger.debug(f'{count} PDF files are processed')
            if count // 10000 != (count - step) // 10000:
                logger.info(f'{count} PDF files are processed')
        return len(pdf_files)

    # def parse(self, typ, input_path, output_dir, n_threads=0, **kwargs):
    #     typ2services = {
    #         'text': ['-g'],
    #         'figure': ['-d', '-m'],
    #     }
    #
    #     if typ not in typ2services:
    #         logger.error(f'Backend {self.__name__} could not parse for type "{typ}".')
    #         return 0
    #     services = typ2services[typ]
    #
    #     if os.path.isfile(input_path):
    #         return self._process_pdf(input_path, output_dir, services)
    #     else:
    #         return self._process_dir(input_path, output_dir, services, n_threads)
