import serial
import time
from datetime import datetime
from pynput import keyboard
import threading

class GripperController:
    def __init__(self, port='/dev/ttyACM0', baudrate=9600, log_file="gripper_status_log.txt"):
        self.port = port
        self.baudrate = baudrate
        self.log_file = log_file
        
        # Define initial jaw states
        self.left_jaw_state = 1  # Assuming the left jaw is open at the start
        self.right_jaw_state = 1  # Assuming the right jaw is open at the start
        
        # Set up serial communication with Arduino
        try:
            self.ser = serial.Serial(self.port, self.baudrate)
            time.sleep(2)  # Give some time for the connection to establish
            print("Serial connection established.")
        except serial.SerialException:
            print("Error: Could not connect to Arduino.")
        
        # Log the initial state
        self.log_gripper_status("initial_state")

    def log_gripper_status(self, action):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"Timestamp: {timestamp}, Left_Jaw_State: {self.left_jaw_state}, Right_Jaw_State: {self.right_jaw_state}, Action: {action}\n"
        with open(self.log_file, "a") as file:
            file.write(log_entry)

    def on_press(self, key):
        try:
            if key.char == 'o':
                self.ser.write(b'open_right_request\n')
                self.ser.flush()
                self.right_jaw_state = 1  # Update state to 'open'
                self.log_gripper_status("open_right")
            elif key.char == 'l':
                self.ser.write(b'close_right_request\n')
                self.ser.flush()
                self.right_jaw_state = 0  # Update the state to 'closed'
                self.log_gripper_status("close_right")
            elif key.char == 'i':
                self.ser.write(b'open_left_request\n')
                self.ser.flush()
                self.left_jaw_state = 1  # Update the state to 'open'
                self.log_gripper_status("open_left")
            elif key.char == 'k':
                self.ser.write(b'close_left_request\n')
                self.ser.flush()
                self.left_jaw_state = 0  # Update the state to 'closed'
                self.log_gripper_status("close_left")
        except AttributeError:
            pass  # Do nothing if AttributeError occurs

    def on_release(self, key):
        # Exit program on 'q'
        if key.char == 'q':
            return False

    def start_key_listener(self):
        # Start listening for keypresses
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def close(self):
        # Close the serial connection when done
        self.ser.close()

# Usage
if __name__ == "__main__":
    gripper = GripperController()
    gripper.start_key_listener()
    gripper.close()
