import os
import json
import shutil
import tempfile
import logging

from pathlib import Path
from science_parse_api.api import parse_pdf

from .base import Backend

logger = logging.getLogger(__name__)


class ScienceParse(Backend):
    def __init__(self, host, port, retry=3):
        super(ScienceParse, self).__init__()
        self.host = host
        self.port = port
        self.retry = retry
        self.typ2service = {
            'text': 'text',
        }

    @staticmethod
    def _move_result_from_tmp_to_output(tmp_dir, output_dir):
        count = 0
        for name in os.listdir(tmp_dir):
            prefix, ext = os.path.splitext(name)
            prefix = os.path.splitext(prefix)[0]
            new_name = prefix + '.scienceparse.json'
            shutil.move(os.path.join(tmp_dir, name), os.path.join(output_dir, new_name))
            count += 1
        return count

    def _process_pdf(self, input_file, output_dir, service, **kwargs):
        output_file = os.path.join(output_dir, os.path.basename(input_file) + '.scienceparse.json')
        output_dict = parse_pdf(f'http://{self.host}', Path(input_file), port=str(self.port))
        for _ in range(self.retry):
            try:
                with open(output_file, 'w') as f:
                    json.dump(output_dict, f)
            except Exception:
                logger.error(f"Could not write out result file: {output_file}")
                if _ == self.retry - 1:
                    raise

    def _process_dir(self, input_dir, output_dir, service, n_threads=0, **kwargs):
        with tempfile.TemporaryDirectory() as dirname:
            self._move_result_from_tmp_to_output(dirname, output_dir)
