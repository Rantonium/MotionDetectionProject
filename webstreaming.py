from pyimagesearch.motion_detection.motiondetector import MotionDetector
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
from flask import request
import subprocess
import threading
import argparse
import datetime
import imutils
import time
import cv2
import RPi.GPIO as GPIO

# Initialize the output frame and the threading_lock used in thread safety
output_frame = None
threading_lock = threading.Lock()

# Initializing the Flask Application
app = Flask(__name__)

# Initialize the GPIO Pin for the Servo Motor
SERVO_PIN = 32
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setwarnings(False)
servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

# Initialize video stream and Power on Camera
video_stream = VideoStream(src=0).start()
time.sleep(2.0)


@app.route("/home")
def index():
    return render_template("index.html")


def detect_motion(frameCount):
    global video_stream, output_frame, threading_lock

    # Initialize the motion detector and the frame count
    motion_detector = MotionDetector(weight=0.1)
    current_frame_count = 0

    # Iterate over Frame Video Stream
    while True:
        # Read the current frame, resize it, convert it to gray then blur it
        frame = video_stream.read()
        frame = imutils.resize(frame, width=400)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        # Take current timestamp to add it to the frame
        current_time = datetime.datetime.now()
        cv2.putText(frame, current_time.strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        # If the number of frames is enough for processing enter If
        if current_frame_count > frameCount:
            # Detect motion
            motion = motion_detector.detect(gray)

            # Check if motion was found
            if motion is not None:
                # If motion was found then send an email alerting the user and draw the bounding box on the frame
                subprocess.Popen("python3 send_email.py", shell=True)
                (thresh, (minX, minY, maxX, maxY)) = motion
                cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 0, 255), 2)

        # Update the background model for accuracy and increment the number of current frames
        motion_detector.update(gray)
        current_frame_count += 1
        # Acquire the lock, set the output frame and release the lock
        with threading_lock:
            output_frame = frame.copy()


def generate():
    global output_frame, threading_lock

    # Iterate over Frames from Video Stream
    while True:
        # Acquire threading lock
        with threading_lock:
            if output_frame is None:
                continue
            # If we have an output frame then we convert it to image and send it to the webpage
            (flag, encodedImage) = cv2.imencode(".jpg", output_frame)
            if not flag:
                continue
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'


@app.route("/move_slider", methods=['POST'])
def move_right():
    # Initialize camera location and control slider with the Submit button in the HTML Page
    location = 2
    if request.method == 'POST':
        location = request.form.getlist('myRange')
    subprocess.Popen("python3 servo.py " + str(location[0]), shell=True)
    return render_template('index.html')


@app.route("/video_feed")
def video_feed():
    # Return the response image for the Video Feed
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == '__main__':
    # Create argument Parser for Server Details
    argument_parser = argparse.ArgumentParser()

    # Set Server Details
    argument_parser.add_argument("-i", "--ip", type=str, required=True, help="the ip address(use ifconfig)")
    argument_parser.add_argument("-o", "--port", type=int, default=5000, required=True, help="port of the application - preferred 5000")
    argument_parser.add_argument("-f", "--frame-count", type=int, default=32, help="the number of framer, default 32")
    arguments = vars(argument_parser.parse_args())

    # Intialize thread for Motion Detection
    thread_for_motion_detection = threading.Thread(target=detect_motion, args=(arguments["frame_count"],))
    thread_for_motion_detection.daemon = True
    thread_for_motion_detection.start()

    # Start Flask App with details parsed from the command line
    app.run(host=arguments["ip"], port=arguments["port"], debug=True, threaded=True, use_reloader=False)
video_stream.stop()
