import cv2 as cv
import dlib
import time
from constants import constants
from eye import EyeTracker
import sms

def main():
    # Initialize tracker
    tracker = EyeTracker()

    cap = cv.VideoCapture(0)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    start_time = time.time()

    def show_stats(frame, tracker):
        stats = f"L: {tracker.left_count} | R: {tracker.right_count} | U: {tracker.up_count} | D: {tracker.down_count} | B: {tracker.blink_count}"
        cv.putText(frame, stats, (20, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, constants.BLUE, 2)

    while True:
        _, frame = cap.read()
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = detector(gray)
        current_time = time.time() - start_time

        for face in faces:
            landmarks = predictor(gray, face)

            # Blinking detection
            left_blink = tracker.get_blinking_ratio(constants.LEFT_EYE, landmarks, frame)
            right_blink = tracker.get_blinking_ratio(constants.RIGHT_EYE, landmarks, frame)
            blink_ratio = (left_blink + right_blink) / 2
            
            if blink_ratio > constants.BLINKING_RATIO:
                tracker.blink_count += 1
                cv.putText(frame, "BLINKING", (50, 100), cv.FONT_HERSHEY_SIMPLEX, 1, constants.RED, 2)

            # Gaze detection
            left_h_ratio, left_v_ratio = tracker.get_gaze_ratio(constants.LEFT_EYE, landmarks, frame, gray)
            right_h_ratio, right_v_ratio = tracker.get_gaze_ratio(constants.RIGHT_EYE, landmarks, frame, gray)
            
            if left_h_ratio and right_h_ratio and left_v_ratio and right_v_ratio:
                h_ratio = (left_h_ratio + right_h_ratio) / 2
                v_ratio = (left_v_ratio + right_v_ratio) / 2
                
                # Horizontal gaze
                if h_ratio < constants.GAZE_THRESHOLD_LEFT:
                    tracker.left_count += 1
                    cv.putText(frame, "LOOKING LEFT", (50, 150), cv.FONT_HERSHEY_SIMPLEX, 1, constants.RED, 2)
                elif h_ratio > constants.GAZE_THRESHOLD_RIGHT:
                    tracker.right_count += 1
                    cv.putText(frame, "LOOKING RIGHT", (50, 150), cv.FONT_HERSHEY_SIMPLEX, 1, constants.RED, 2)
                
                # Vertical gaze
                if v_ratio < constants.GAZE_THRESHOLD_UP:
                    tracker.up_count += 1
                    cv.putText(frame, "LOOKING UP", (50, 200), cv.FONT_HERSHEY_SIMPLEX, 1, constants.RED, 2)
                elif v_ratio > constants.GAZE_THRESHOLD_DOWN:
                    tracker.down_count += 1
                    cv.putText(frame, "LOOKING DOWN", (50, 200), cv.FONT_HERSHEY_SIMPLEX, 1, constants.RED, 2)

            # Check for malpractice
            if tracker.check_malpractice(current_time):
                sms.SMSSender(constants.ADMIN_NUMBER, constants.WARNING_MESSAGE)
                cv.putText(frame, "WARNING SENT TO ADMIN", (50, 250), cv.FONT_HERSHEY_SIMPLEX, 1, constants.RED, 2)

            show_stats(frame, tracker)

        cv.imshow("Eye Tracker", frame)
        
        # Reset counts every minute
        if current_time > 60:
            start_time = time.time()
            tracker.left_count = 0
            tracker.right_count = 0
            tracker.up_count = 0
            tracker.down_count = 0
            tracker.blink_count = 0

        if cv.waitKey(1) == 27:
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()