from skimage.metrics import structural_similarity as ssim
import imutils
from pathlib import Path
from typing import Union
import logging

# to install opencv2:
# $ pip install opencv-python
import cv2


class OpenCVDiff:
    def __init__(self, file1: Union[Path, str],
                 file2: Union[Path, str],
                 output_path1: Union[Path, str, None] = None,
                 output_path2: Union[Path, str, None] = None):

        self.logger = logging.getLogger('debug')
        self.startup_logger(log_level=logging.DEBUG)
        self.logger.info('starting up webservice')

        self.file1_path = file1
        self.file2_path = file2

        self.output_path1 = output_path1
        self.output_path2 = output_path2

        # read the images
        self.input_image_1 = cv2.imread(file1)
        self.input_image_2 = cv2.imread(file2)

        # convert the images to grayscale
        self.input_image_1_grayscale = cv2.cvtColor(self.input_image_1, cv2.COLOR_BGR2GRAY)
        self.input_image_2_grayscale = cv2.cvtColor(self.input_image_2, cv2.COLOR_BGR2GRAY)

        # calculate structural similarity index
        score, difference = ssim(self.input_image_1_grayscale, self.input_image_2_grayscale, full=True)
        difference = (255 * difference).astype("uint8")
        self.logger.info(f'SSIM: {score}')

        # threshold the difference image
        thresh = cv2.threshold(difference, 0, 255,
                               cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        # searching for contours of differing regions
        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)

        contours = imutils.grab_contours(contours)

        # loop over the contours
        for c in contours:
            # create a bounding rectangle around the contour
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(self.input_image_1, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(self.input_image_2, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # # DEV save png images as base64 encoded strings
        # retval_a, buffer_a = cv2.imencode('.png', self.input_image_1)
        # retval_b, buffer_b = cv2.imencode('.png', self.input_image_2)
        # self.buffer_a_as_text = base64.b64encode(buffer_a)
        # self.buffer_b_as_text = base64.b64encode(buffer_b)

    def write_images_to_output_paths(self):
        # write the output images
        if self.output_path1 is not None:
            cv2.imwrite(self.output_path1, self.input_image_1)
        if self.output_path2 is not None:
            cv2.imwrite(self.output_path2, self.input_image_2)

    # # DEV tried out to return the images as base64 strings
    # def return_base64_string_tuple(self):
    #     return self.buffer_a_as_text, self.buffer_b_as_text

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
