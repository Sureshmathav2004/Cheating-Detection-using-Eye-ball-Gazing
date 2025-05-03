import cv2 as cv

class Constants:
    # Colors
    GREEN = (0, 255, 0)
    RED = (0, 0, 255)
    BLUE = (255, 0, 0)
    WHITE = (255, 255, 255)

    # Fonts
    FONT = cv.FONT_HERSHEY_PLAIN
    FONT2 = cv.QT_FONT_NORMAL

    # Eye landmarks
    LEFT_EYE = [36, 37, 38, 39, 40, 41]
    RIGHT_EYE = [42, 43, 44, 45, 46, 47]

    # Thresholds
    BLINKING_RATIO = 5
    GAZE_THRESHOLD_LEFT = 0.6
    GAZE_THRESHOLD_RIGHT = 2.0
    GAZE_THRESHOLD_UP = 0.5
    GAZE_THRESHOLD_DOWN = 1.5

    # Malpractice thresholds
    MAX_LEFT_MOVEMENTS = 15
    MAX_RIGHT_MOVEMENTS = 15
    MAX_UP_MOVEMENTS = 10
    MAX_DOWN_MOVEMENTS = 10
    MAX_BLINKS = 20

    # Frequency thresholds
    MAX_FREQUENT_MOVEMENTS = 10  # Max allowed frequent movements in 5 seconds
    MOVEMENT_TIME_WINDOW = 5  # Seconds to check for frequent movements

    # Warning messages
    WARNING_MESSAGE = "Warning: Suspicious eye movement pattern detected during exam"
    FREQUENT_LEFT_WARNING = "Excessive left eye movements detected!"
    FREQUENT_RIGHT_WARNING = "Excessive right eye movements detected!"
    GENERAL_WARNING = "Suspicious eye movement pattern detected!"

# Create an instance to import
constants = Constants()