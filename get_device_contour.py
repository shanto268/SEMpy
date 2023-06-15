# -*- coding: utf-8 -*-
"""
=======================================================
Program : sem_image_analysis/get_device_contour.py
=======================================================
Summary:
"""
__author__ =  "Sadman Ahmed Shanto"
__date__ = "04/18/2023"
__email__ = "shanto@usc.edu"

#libraries used
import os
import cv2
import argparse
import numpy as np
import imutils
from imutils.paths import list_images
from skimage.exposure import is_low_contrast

def pixel_to_nanometer_conversion(ref_pixels, ref_nanometers):
    return ref_nanometers / ref_pixels

def process_directory(input_dir, results_dir):
    imagePaths = sorted(list(list_images(input_dir)))
    for (i, imagePath) in enumerate(imagePaths):
        print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
        image = cv2.imread(imagePath)
        image = imutils.resize(image, width=900) # Increase width for higher resolution
        
        # Crop the bottom 80 pixels of the image
        height, _, _ = image.shape
        cropped_img = image[:height - 80, :, :]
        
        gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 30, 150)
        
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        contour_img = np.zeros_like(cropped_img)
        
        # Calculate the conversion factor
        conversion_factor = pixel_to_nanometer_conversion(370, 400)
        
        for c in cnts:
            cv2.drawContours(contour_img, [c], -1, (255, 255, 255), 2)
            
            # Label the contour size
            contour_length = cv2.arcLength(c, True)
            contour_length_nm = contour_length * conversion_factor
            x, y, w, h = cv2.boundingRect(c)
            
            # Draw red measurement lines
            cv2.line(contour_img, (x, y), (x + w, y), (0, 0, 255), 1)
            cv2.line(contour_img, (x, y), (x, y + h), (0, 0, 255), 1)
            
            # Adjust label position to minimize overlap
            label_x = x - 10 if x - 10 > 0 else x + 10
            label_y = y - 10 if y - 10 > 0 else y + h + 20
            cv2.putText(contour_img, f"{contour_length_nm:.1f} nm", (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        output_filename = os.path.join(results_dir, os.path.splitext(os.path.basename(imagePath))[0] + '.png')
        cv2.imwrite(output_filename, contour_img, [cv2.IMWRITE_PNG_COMPRESSION, 0])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True, help="path to input directory of images")
    ap.add_argument("-t", "--thresh", type=float, default=0.05, help="threshold for low contrast")
    args = vars(ap.parse_args())
    
    input_dir = args["input"]
    results_dir = "results"

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    process_directory(input_dir, results_dir)
