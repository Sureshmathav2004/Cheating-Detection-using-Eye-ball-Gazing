from flask import Flask, render_template, Response, request, redirect, url_for, session
import cv2
import dlib
from eye import EyeTracker
from constants import constants
import threading
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

tracker = None
camera_thread = None
is_tracking = False
cap = None

def generate_frames():
    global cap
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'admin123':
            session['username'] = username
            return redirect(url_for('index'))
        elif username == 'student' and password == 'student123':
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/malpractice_detected')
def malpractice_detected():
    return render_template('malpractice.html')

@app.route('/start_tracking')
def start_tracking():
    global tracker, camera_thread, is_tracking
    
    if not is_tracking:
        tracker = EyeTracker()
        is_tracking = True
        camera_thread = threading.Thread(target=run_eye_tracking)
        camera_thread.daemon = True
        camera_thread.start()
    
    return redirect(url_for('index'))

@app.route('/stop_tracking')
def stop_tracking():
    global is_tracking, cap
    is_tracking = False
    if cap:
        cap.release()
        cap = None
    return redirect(url_for('index'))

@app.route('/stats')
def get_stats():
    if tracker:
        warning = tracker.check_malpractice(time.time())
        if warning in ["excessive_left", "excessive_right"]:
            return {
                'left': tracker.consecutive_left,
                'right': tracker.consecutive_right,
                'up': tracker.up_count,
                'down': tracker.down_count,
                'blinks': tracker.blink_count,
                'warning': warning,
                'redirect': True
            }
        return {
            'left': tracker.consecutive_left,
            'right': tracker.consecutive_right,
            'up': tracker.up_count,
            'down': tracker.down_count,
            'blinks': tracker.blink_count,
            'warning': warning,
            'redirect': False
        }
    return {}

def run_eye_tracking():
    global tracker, is_tracking, cap
    
    cap = cv2.VideoCapture(0)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    start_time = time.time()
    
    while is_tracking and cap.isOpened():
        _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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

            # Gaze detection
            left_h_ratio, left_v_ratio = tracker.get_gaze_ratio(constants.LEFT_EYE, landmarks, frame, gray)
            right_h_ratio, right_v_ratio = tracker.get_gaze_ratio(constants.RIGHT_EYE, landmarks, frame, gray)
            
            if left_h_ratio and right_h_ratio and left_v_ratio and right_v_ratio:
                h_ratio = (left_h_ratio + right_h_ratio) / 2
                v_ratio = (left_v_ratio + right_v_ratio) / 2
                
                # Horizontal gaze
                if h_ratio < constants.GAZE_THRESHOLD_LEFT:
                    tracker.left_count += 1
                    tracker.movement_history.append(current_time)
                elif h_ratio > constants.GAZE_THRESHOLD_RIGHT:
                    tracker.right_count += 1
                    tracker.movement_history.append(current_time)
                
                # Vertical gaze
                if v_ratio < constants.GAZE_THRESHOLD_UP:
                    tracker.up_count += 1
                elif v_ratio > constants.GAZE_THRESHOLD_DOWN:
                    tracker.down_count += 1

            # Check for malpractice
            warning = tracker.check_malpractice(current_time)
            if warning in ["excessive_left", "excessive_right"]:
                is_tracking = False
                cap.release()
                return

        # Reset counts every minute
        if current_time > 60:
            start_time = time.time()
            tracker.left_count = 0
            tracker.right_count = 0
            tracker.up_count = 0
            tracker.down_count = 0
            tracker.blink_count = 0
            tracker.movement_history = []

    cap.release()

if __name__ == '__main__':
    app.run(debug=True)