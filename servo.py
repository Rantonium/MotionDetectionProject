import RPi.GPIO as GPIO
import time
import sys

SERVO_PIN = 32

if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)

    # Set the GPIO servo motor pin and start
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    GPIO.setwarnings(False)
    servo = GPIO.PWM(SERVO_PIN, 50)
    servo.start(0)

    # Rotate servo according to given input
    servo.ChangeDutyCycle(float(sys.argv[1]))
    time.sleep(0.3)
    servo.ChangeDutyCycle(0)
    time.sleep(0.7)
    servo.stop()
    GPIO.cleanup()
