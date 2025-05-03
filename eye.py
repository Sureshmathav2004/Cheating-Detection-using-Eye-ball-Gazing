import geometry
from constants import constants
import cv2 as cv
import numpy as np
from scipy.spatial import distance as dist

class EyeTracker:
    def __init__(self):
        self.left_count = 0
        self.right_count = 0
        self.up_count = 0
        self.down_count = 0
        self.blink_count = 0
        self.last_warning_time = 0
        self.movement_history = []
        self.current_gaze = "center"
        self.consecutive_left = 0
        self.consecutive_right = 0
        
    def get_blinking_ratio(self, points, landmarks, frame):
        left_point = (landmarks.part(points[0]).x, landmarks.part(points[0]).y)
        right_point = (landmarks.part(points[3]).x, landmarks.part(points[3]).y)
        center_top = geometry.midpoint(landmarks.part(points[1]), landmarks.part(points[2]))
        center_bottom = geometry.midpoint(landmarks.part(points[4]), landmarks.part(points[5]))

        horizontal_dis = geometry.distance_btw_points(left_point, right_point)
        vertical_dis = geometry.distance_btw_points(center_top, center_bottom)

        return horizontal_dis / vertical_dis

    def get_gaze_ratio(self, points, landmarks, frame, gray):
        eye_region = self.get_eye_region(points, landmarks)
        height, width, _ = frame.shape
        mask = np.zeros((height, width), np.uint8)

        cv.polylines(mask, [eye_region], True, constants.WHITE, 2)
        cv.fillPoly(mask, [eye_region], constants.WHITE)
        eye_mask = cv.bitwise_and(gray, gray, mask=mask)

        gray_eye = self.min_max_frame(eye_region, eye_mask)
        _, threshold_eye = cv.threshold(gray_eye, 63, 255, cv.THRESH_BINARY)

        height, width = threshold_eye.shape
        left_half = threshold_eye[0:height, 0:int(width/2)]
        right_half = threshold_eye[0:height, int(width/2):]
        left_white = cv.countNonZero(left_half)
        right_white = cv.countNonZero(right_half)
        
        top_half = threshold_eye[0:int(height/2), 0:width]
        bottom_half = threshold_eye[int(height/2):, 0:width]
        top_white = cv.countNonZero(top_half)
        bottom_white = cv.countNonZero(bottom_half)

        try:
            h_ratio = left_white / right_white
            v_ratio = top_white / bottom_white
            
            # Determine current gaze direction
            if h_ratio < constants.GAZE_THRESHOLD_LEFT:
                self.current_gaze = "left"
            elif h_ratio > constants.GAZE_THRESHOLD_RIGHT:
                self.current_gaze = "right"
            elif v_ratio < constants.GAZE_THRESHOLD_UP:
                self.current_gaze = "up"
            else:
                self.current_gaze = "center"
                
            return h_ratio, v_ratio
        except ZeroDivisionError:
            self.current_gaze = "center"
            return None, None

    def check_malpractice(self, current_time):
        # Reset counts if looking center
        if self.current_gaze == "center":
            self.consecutive_left = 0
            self.consecutive_right = 0
        else:
            # Track consecutive left/right gazes
            if self.current_gaze == "left":
                self.consecutive_left += 1
                self.consecutive_right = 0
            elif self.current_gaze == "right":
                self.consecutive_right += 1
                self.consecutive_left = 0

        # Check for continuous left/right movements
        if self.consecutive_left >= 15:  # Alert after 10 consecutive left movements
            self.last_warning_time = current_time
            return "excessive_left"
        if self.consecutive_right >= 15:  # Alert after 10 consecutive right movements
            self.last_warning_time = current_time
            return "excessive_right"
        
        return None

    def get_eye_region(self, points, landmarks):
        return np.array([(landmarks.part(points[0]).x, landmarks.part(points[0]).y),
                         (landmarks.part(points[1]).x, landmarks.part(points[1]).y),
                         (landmarks.part(points[2]).x, landmarks.part(points[2]).y),
                         (landmarks.part(points[3]).x, landmarks.part(points[3]).y),
                         (landmarks.part(points[4]).x, landmarks.part(points[4]).y),
                         (landmarks.part(points[5]).x, landmarks.part(points[5]).y)], np.int32)

    def min_max_frame(self, region, frame):
        min_x = np.min(region[:, 0])
        max_x = np.max(region[:, 0])
        min_y = np.min(region[:, 1])
        max_y = np.max(region[:, 1])
        return frame[min_y: max_y, min_x: max_x]