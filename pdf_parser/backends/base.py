import os
import logging
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class Backend(object, metaclass=ABCMeta):
    def __init__(self):
        self.typ2service = None

    @abstractmethod
    def _process_pdf(self, input_file, output_file, service, **kwargs):
        """Parse one pdf file, please implement in subclass"""

    @abstractmethod
    def _process_dir(self, input_dir, output_dir, service, n_threads=0, **kwargs):
        """Parse multiple pdf files in a same directory, please implement in subclass"""

    # @abstractmethod
    # def parse(self, typ, input_dir, output_dir, n_threads=0, **kwargs):
    #     """Parse pdf(s), please implement in subclass"""

    def parse(self, typ, input_path, output_dir, n_threads=0, **kwargs):
        if typ not in self.typ2service:
            raise ValueError(f'Backend {self.__class__.__name__} could not parse for type "{typ}".')
        services = self.typ2service[typ]

        if os.path.isfile(input_path):
            return self._process_pdf(input_path, output_dir, services, **kwargs)
        else:
            return self._process_dir(input_path, output_dir, services, n_threads, **kwargs)
