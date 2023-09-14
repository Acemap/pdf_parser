__all__ = ["Parser", "ParserBackend"]

import logging
import os

from .backends import *

logger = logging.getLogger(__name__)


class ParserBackend:
    GROBID = "grobid"
    SCIENCE = "scienceparse"
    PDFFIGURES = "pdffigures"
    PDFFIGURES2 = "pdffigures2"
    CERMINE = "cermine"


parser_backend = {
    ParserBackend.GROBID: Grobid,
    ParserBackend.SCIENCE: ScienceParse,
    ParserBackend.PDFFIGURES: PDFFigures,
    ParserBackend.PDFFIGURES2: PDFFigures2,
    ParserBackend.CERMINE: Cermine
}


class Parser:
    def __init__(self, backend, **kwargs):
        self.backend = backend
        self.handler = self._init_handler(**kwargs)

    def _init_handler(self, **kwargs):
        parser = parser_backend.get(self.backend)
        if not parser:
            raise ValueError(f"parser backend is not valid: {self.backend}")
        return parser(**kwargs)

    def _check_input_dir(self, input_path):
        if not os.path.exists(input_path):
            logger.error(f"Input path not found: {input_path}!")
            return False
        return True

    def _check_output_dir(self, output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except PermissionError:
            logger.error("Cannot make output dir. Check permission please.")
            return False
        except FileExistsError:
            logger.error(f"File exists with the same name of output dir: {output_dir}")
            return False

        if not os.access(output_dir, os.W_OK):
            logger.error("The output dir has no write permission.")
            return False
        return True

    def parse(self, typ, input_path, output_dir, num_threads=0, **kwargs):
        if not self._check_input_dir(input_path):
            raise ValueError(f"input path is not valid: {input_path}")
        if not self._check_output_dir(output_dir):
            raise ValueError(f"output dir is not valid: {output_dir}")

        logger.info(f"Start parsing {typ} of pdf files using {self.backend}.")
        num_parsed = self.handler.parse(typ, input_path, output_dir, num_threads, **kwargs)
        logger.info("Finish.")
        return num_parsed
