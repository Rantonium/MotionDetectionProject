import numpy as np
import imutils
import cv2


class MotionDetector:
    def __init__(self, weight=0.5):
        # Initializing of background and background weight for the image
        self.general_background_weight = weight
        self.general_background = None

    def update(self, image):
        # Check if background exists, if not, update it
        if self.general_background is None:
            self.general_background = image.copy().astype("float")
            return
        cv2.accumulateWeighted(image, self.general_background, self.general_background_weight)

    def detect(self, image, tVal=25):
        # Compute difference between background model and image passed in
        differnce_delta = cv2.absdiff(self.general_background.astype("uint8"), image)
        threshhold_computed = cv2.threshold(differnce_delta, tVal, 255, cv2.THRESH_BINARY)[1]
        # Erode and Dilate the image 2 times each to remove useless small portions of image(blobs)
        threshhold_computed = cv2.erode(threshhold_computed, None, iterations=2)
        threshhold_computed = cv2.dilate(threshhold_computed, None, iterations=2)
        # Compute image countours and initialize the coordinates for the bounding box
        found_countours = cv2.findContours(threshhold_computed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        found_countours = imutils.grab_contours(found_countours)
        (minX, minY) = (np.inf, np.inf)
        (maxX, maxY) = (-np.inf, -np.inf)
        if len(found_countours) == 0:
            # If there were no countours found, return None
            return None
        for contours in found_countours:
            # Calculate bounding box for each contour
            (x, y, w, h) = cv2.boundingRect(contours)
            (minX, minY) = (min(minX, x), min(minY, y))
            (maxX, maxY) = (max(maxX, x + w), max(maxY, y + h))
        # Return image of threshhold with a bounding box
        return threshhold_computed, (minX, minY, maxX, maxY)
