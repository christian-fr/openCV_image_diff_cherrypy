#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import cherrypy
from cherrypy.lib import static, sessions
from openCV_diff_classes import OpenCVDiff
from pathlib import Path
import logging
from delete_old_files import delete_old_files
import hashlib
from typing import Union

local_dir = os.path.dirname(__file__)
abs_dir = os.path.join(os.getcwd(), local_dir)
tmp_subdir = Path('tmp')
abs_tmp_subdir = Path(abs_dir, tmp_subdir)

config = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 9191,
        'server.thread_pool': 8,
        'server.max_request_body_size': 0,
        'server.socket_timeout': 60,
        'log.access_file': f'{Path(abs_dir, "cherrypy_access.log")}',
        'log.error_file': f'{Path(abs_dir, "cherrypy_error.log")}'
    }
}


# def return_all_active_sessions():
#     sessions = os.listdir('./sessions')
#     sessions = filter(lambda session: '.lock' not in session, sessions)
#     return [entry for entry in sessions]
#

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
        if not abs_tmp_subdir.exists():
            os.mkdir(abs_tmp_subdir)
        else:
            delete_old_files(abs_tmp_subdir)

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
    def session_cleanup(self, session_id):
        cherrypy.session.acquire_lock()
        self.logger.info('session cleanup started - removing old files')
        tmp_session_output_file_path = Path(
            f'{abs_dir}/tmp/{session_id}_input_1_modified.png')
        self.logger.info(f'file to be deleted: "{tmp_session_output_file_path}"')
        if Path(tmp_session_output_file_path).exists():
            os.remove(tmp_session_output_file_path)
            self.logger.info(f'file "{tmp_session_output_file_path}" has been deleted.')
        else:
            self.logger.info(f'file "{tmp_session_output_file_path}" does not exist.')

    # # DEV could be implemented, but I am not sure if this is really useful - can those PNG files really be identical?
    # @staticmethod
    # def check_if_identical(self, input_file1: Union[str, Path], input_file2: Union[str, Path]):
    #     with open(input_file1, 'r') as input_file1:
    #         with open(input_file2, 'r') as input_file2:
    #             difference = set(input_file1).difference(input_file2)
    #     return True

    @cherrypy.expose
    def upload(self, uploaded_file_1, uploaded_file_2):
        cherrypy.session.acquire_lock()
        self.logger.info('upload started')

        allowed_extensions_list = ['.png']

        cherrypy.session['Something'] = 'asdf'
        self.logger.info(f'cherrypy session id: {cherrypy.session.id}')

        # Upload-Path
        # create strings with filename and extension of uploaded file 1:
        input_filename_1, input_extension_1 = os.path.splitext(uploaded_file_1.filename)
        self.logger.info(
            f'input filenames set; input_filename_1: "{input_filename_1}", input_extension_1: "{input_extension_1}"')

        # check if file extension is in allowed_extensions_list
        if input_extension_1.lower() not in allowed_extensions_list:
            return f'Extension "{input_extension_1}" not allowed! Filename: "{uploaded_file_1.filename}"'

        # create strings with filename and extesion of uploaded file 2:
        input_filename_2, input_extension_2 = os.path.splitext(uploaded_file_2.filename)
        self.logger.info(
            f'input filenames set; input_filename_2: "{input_filename_2}", input_extension_2: "{input_extension_2}"')

        # check if file extension is in allowed_extensions_list
        if input_extension_2.lower() not in allowed_extensions_list:
            return f'Extension "{input_extension_2}" not allowed! Filename: "{uploaded_file_2.filename}"'

        # create strings with full path of uploaded file
        # for uploaded file 1
        input_file_1 = os.path.join(abs_tmp_subdir, cherrypy.session.id + '_input_1' + input_extension_1)
        self.logger.info(
            f'input_file_1: "{input_file_1}"')

        # for uploaded file 2
        input_file_2 = os.path.join(abs_tmp_subdir, cherrypy.session.id + '_input_2' + input_extension_2)
        self.logger.info(
            f'input_file_2: "{input_file_2}"')

        # DEV DEBUG obsolete, but maybe useful for debugging - variables for upload size
        size_1, size_2 = 0, 0

        # read uploaded file 1, write to local input_file_1
        with open(input_file_1, 'wb') as file1:
            self.logger.info(f'writing "uploaded_file_1" to: "{input_file_1}"')

            while True:
                data = uploaded_file_1.file.read(8192)

                if not data:
                    break
                file1.write(data)

                # DEV DEBUG obsolete, but may be useful for debugging
                size_1 += len(data)

        # read uploaded file 2, write to local input_file_2
        with open(input_file_2, 'wb') as file2:
            self.logger.info(f'writing "uploaded_file_2" to: "{input_file_2}"')

            while True:
                data = uploaded_file_2.file.read(8192)
                if not data:
                    break
                file2.write(data)

                # DEV DEBUG obsolete, but may be useful for debugging
                size_2 += len(data)
        cherrypy.session.release_lock()

        # ToDo 2021-06-11: try out md5hash of files to compare them, fire up openCV only if images differ from each other!

        # if hashlib.md5(input_file_1).hexdigest() != hashlib.md5(input_file_2).hexdigest():
        # self.logger.info(hashlib.md5(input_file_1).hexdigest())
        # self.logger.info(hashlib.md5(input_file_2).hexdigest())

        self.logger.info(f'size of file1: {size_1}')
        self.logger.info(f'size of file2: {size_2}')

        self.logger.info(f'starting up OpenCVDiff')

        output_path1 = os.path.splitext(input_file_1)[0] + '_modified' + os.path.splitext(input_file_1)[1]

        while True:
            try:
                open_cv_object = OpenCVDiff(file1=input_file_1,
                                            file2=input_file_2,
                                            output_path1=output_path1,
                                            output_path2=None)
                open_cv_object.write_images_to_output_paths()
                break
            except:
                continue
        self.logger.info(f'output_path1: {output_path1}')

        del open_cv_object
        self.logger.info(f'openCV object deleted')

        # bytes_string_image1, bytes_string_image2 = open_cv_object.return_base64_string_tuple()
        self.logger.info(f'OpenCVDiff is done')

        # # prepare temporary file to send back
        # tmpfile1 = tempfile.NamedTemporaryFile()
        # output_file2 = Path(tmpfile1.name)
        #
        # tmpfile1.write(bytes_string_image2)

        self.logger.info(f'cleaning up uploaded files')
        # clean up uploaded files
        os.remove(input_file_1)
        os.remove(input_file_2)
        self.logger.info(f'uploaded files successfully cleaned up {[input_file_1, input_file_2]}')

        # self.logger.info(
        #     f'''path of file that is being sent back: "{os.path.splitext(input_file_1)[0] + '_modified' + os.path.splitext(input_file_1)[1]}"''')

        # terminate session (?)
        cherrypy.lib.sessions.expire()

        return static.serve_file(output_path1,
                                 'application/x-download',
                                 'attachment', input_filename_1 + '_modified' + input_extension_1 + 'hui')
        # return static.serve_file(os.path.splitext(input_file_1)[0] + '_modified' + os.path.splitext(input_file_1)[1],
        #                          'application/x-download',
        #                          'attachment', input_filename_1 + '_modified' + input_extension_1)


cherrypy.config.update({'tools.sessions.on': True,
                        'tools.sessions.storage_class': cherrypy.lib.sessions.FileSession,
                        'tools.sessions.storage_type': "ram",
                        # 'tools.sessions.storage_path': 'sessions',
                        'tools.sessions.timeout': 10
                        })

if __name__ == '__main__':
    cherrypy.quickstart(App(), '/', config)
