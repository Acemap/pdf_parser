import os
import stat
from setuptools import setup, find_packages
from setuptools.command.install import install


class OverrideInstall(install):

    def run(self):
        install.run(self)  # calling install.run(self) insures that everything that happened previously still happens, so the installation does not break!
        # here we start with doing our overriding and private magic ..
        bin_path = os.path.join('pdf_parser', 'bin')
        add_mode = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        for filepath in self.get_outputs():
            if bin_path in filepath:
                # print('filepath', filepath)
                st = os.stat(filepath)
                os.chmod(filepath, st.st_mode | add_mode)


setup(
    name='pdf-parser',
    version='1.1.12',
    description='This is a multi-backend PDF parser for IIoT.',
    author='Shuhao Li & Yuting Jia',
    packages=find_packages(),
    package_data={
        'pdf_parser': [
            "bin/pdffigures",
            "jar/cermine-1.13.jar",
            "jar/pdffigures2-0.1.0.jar",
        ],
    },
    install_requires=[
        'requests>=2.23.0',
        'science-parse-api>=1.0.1'
    ],
    cmdclass={'install': OverrideInstall}
)
