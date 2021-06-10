# source: https://www.pyimagesearch.com/2017/06/19/image-difference-with-opencv-and-python/

# import the necessary packages
from skimage.metrics import structural_similarity as ssim
# import argparse
import imutils
# import os
# to install opencv2:
# $ pip install opencv-python
import cv2

from pathlib import Path
from typing import Union
# from io import BytesIO
import logging

import base64


# # construct the argument parse and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-f", "--first", required=True,
# 	help="first input image")
# ap.add_argument("-s", "--second", required=True,
# 	help="second")
# args = vars(ap.parse_args())

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

        # load the two input images
        self.imageA = cv2.imread(file1)
        self.imageB = cv2.imread(file2)
        # convert the images to grayscale
        self.grayA = cv2.cvtColor(self.imageA, cv2.COLOR_BGR2GRAY)
        self.grayB = cv2.cvtColor(self.imageB, cv2.COLOR_BGR2GRAY)

        # compute the Structural Similarity Index (SSIM) between the two
        # images, ensuring that the difference image is returned
        (score, diff) = ssim(self.grayA, self.grayB, full=True)
        diff = (diff * 255).astype("uint8")
        print("SSIM: {}".format(score))

        # threshold the difference image, followed by finding contours to
        # obtain the regions of the two input images that differ
        thresh = cv2.threshold(diff, 0, 255,
                               cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        # loop over the contours
        for c in contours:
            # compute the bounding box of the contour and then draw the
            # bounding box on both input images to represent where the two
            # images differ
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(self.imageA, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(self.imageB, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # save png images as base64 encoded strings
        retval_a, buffer_a = cv2.imencode('.png', self.imageA)
        retval_b, buffer_b = cv2.imencode('.png', self.imageB)
        self.buffer_a_as_text = base64.b64encode(buffer_a)
        self.buffer_b_as_text = base64.b64encode(buffer_b)

    def write_images_to_output_paths(self):

        # write the output images
        if self.output_path1 is not None:
            cv2.imwrite(self.output_path1, self.imageA)
        if self.output_path2 is not None:
            cv2.imwrite(self.output_path2, self.imageB)

        # cv2.imshow("Original", imageA)
        # cv2.imshow("Modified", imageB)
        # cv2.imshow("Diff", diff)
        # cv2.imshow("Thresh", thresh)
        # cv2.waitKey(0)



    def return_base64_string_tuple(self):
        return self.buffer_a_as_text, self.buffer_b_as_text

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

# usage:
# $ python image_diff.py --first images/original_02.png
# 	--second images/modified_02.png
