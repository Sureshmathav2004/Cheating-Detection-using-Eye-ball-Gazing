# Eye Movement Tracking for Exam Proctoring

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.0%2B-lightgrey)
![OpenCV](https://img.shields.io/badge/opencv-4.5%2B-orange)
![dlib](https://img.shields.io/badge/dlib-19.22%2B-green)

A real-time eye movement tracking system designed to detect suspicious behavior during online exams. The system monitors eye movements and detects patterns that may indicate malpractice.

## Features

- Real-time eye tracking using webcam
- Detection of:
  - Excessive left/right eye movements
  - Frequent up/down movements
  - Abnormal blinking patterns
  - Sustained suspicious gaze patterns
- Visual warning interface when malpractice is detected
- Admin dashboard for monitoring
- Secure login system

## Technology Stack

- **Backend**: Python, Flask
- **Computer Vision**: OpenCV, dlib
- **Frontend**: HTML, CSS, Bootstrap
- **Facial Landmarks**: shape_predictor_68_face_landmarks.dat

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/eye-tracking-proctoring.git
   cd eye-tracking-proctoring
