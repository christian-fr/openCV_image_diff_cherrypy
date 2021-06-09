#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import cherrypy
from cherrypy.lib import static
from openCV_diff_classes import OpenCVDiff
from pathlib import Path
import logging

localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)

config = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
        'server.thread_pool': 8,
        'server.max_request_body_size': 0,
        'server.socket_timeout': 60
    }
}


def remove_all_png_files_from_subfolders(path_object: Path):
    set_of_files_to_remove = set()
    for root, dirs, files in os.walk(path_object, topdown=False):
        for file in files:
            if os.path.splitext(file)[1] == '.png':
                set_of_files_to_remove.add(Path(root, file))

    for file in set_of_files_to_remove:
        os.remove(file)


class App:
    def __init__(self):
        self.logger = logging.getLogger('debug')
        self.startup_logger(log_level=logging.DEBUG)
        self.logger.info('starting up webservice')

    def startup_logger(self, log_level=logging.DEBUG):
        """
        CRITICAL: 50, ERROR: 40, WARNING: 30, INFO: 20, DEBUG: 10, NOTSET: 0
        """
        logging.basicConfig(level=log_level)
        fh = logging.FileHandler("{0}.log".format('log_' + __name__))
        fh.setLevel(log_level)
        fh_format = logging.Formatter('%(name)s\t%(module)s\t%(funcName)s\t%(asctime)s\t%(lineno)d\t'
                                      '%(levelname)-8s\t%(message)s')
        fh.setFormatter(fh_format)
        self.logger.addHandler(fh)

    @cherrypy.expose
    def upload(self, uploaded_file_1, uploaded_file_2):
        self.logger.info('upload started')
        self.logger.info('removing old files')
        remove_all_png_files_from_subfolders(Path(absDir))
        self.logger.info('old files removed')

        allowed_extensions_list = ['.png']

        # Upload-Path

        # create strings with filename and extesion of uploaded file

        input_filename_1, input_extension_1 = os.path.splitext(uploaded_file_1.filename)
        self.logger.info(
            f'input filenames set; input_filename_1: "{input_filename_1}", input_extension_1: "{input_extension_1}"')

        if input_extension_1.lower() not in allowed_extensions_list:
            return f'Extension "{input_extension_1}" not allowed! Filename: "{uploaded_file_1.filename}"'

        # create strings with filename and extesion of uploaded file
        input_filename_2, input_extension_2 = os.path.splitext(uploaded_file_2.filename)
        self.logger.info(
            f'input filenames set; input_filename_2: "{input_filename_2}", input_extension_2: "{input_extension_2}"')

        if input_extension_2.lower() not in allowed_extensions_list:
            return f'Extension "{input_extension_2}" not allowed! Filename: "{uploaded_file_2.filename}"'

        # create string with full path of uploaded file
        input_file_1 = os.path.join(absDir, 'input_1' + input_extension_1)
        self.logger.info(
            f'input_file_1: "{input_file_1}"')

        input_file_2 = os.path.join(absDir, 'input_2' + input_extension_2)
        self.logger.info(
            f'input_file_2: "{input_file_2}"')

        print(f'input_file1: "{input_file_1}"')
        print(f'input_file2: "{input_file_2}"')

        # DEV DEBUG obsolete, but maybe useful for debugging
        size_1, size_2 = 0, 0

        with open(input_file_1, 'wb') as file1:
            self.logger.info(f'writing "uploaded_file_1" to: "{input_file_1}"')

            while True:
                data = uploaded_file_1.file.read(8192)
                if not data:
                    break
                file1.write(data)

                # DEV DEBUG obsolete, but may be useful for debugging
                size_1 += len(data)

        with open(input_file_2, 'wb') as file2:
            self.logger.info(f'writing "uploaded_file_2" to: "{input_file_2}"')

            while True:
                data = uploaded_file_2.file.read(8192)
                if not data:
                    break
                file2.write(data)

                # DEV DEBUG obsolete, but may be useful for debugging
                size_2 += len(data)

        self.logger.info(f'starting up OpenCVDiff')

        OpenCVDiff(file1=input_file_1, file2=input_file_2)
        self.logger.info(f'OpenCVDiff is done')
        self.logger.info(
            f'''path of file that is being sent back: "{os.path.splitext(input_file_1)[0] + '_modified' + os.path.splitext(input_file_1)[1]}"''')
        return static.serve_file(os.path.splitext(input_file_1)[0] + '_modified' + os.path.splitext(input_file_1)[1],
                                 'application/x-download',
                                 'attachment', input_filename_1 + '_modified' + input_extension_1)


if __name__ == '__main__':
    cherrypy.quickstart(App(), '/', config)
