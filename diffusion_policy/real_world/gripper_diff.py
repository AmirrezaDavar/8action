# import serial
# import time
# from datetime import datetime
# from pynput import keyboard
# import threading

# class GripperController:
#     def __init__(self, port='/dev/ttyACM0', baudrate=9600, log_file="gripper_status_log.txt"):
#         self.port = port
#         self.baudrate = baudrate
#         self.log_file = log_file
        
#         # Define initial jaw states
#         self.left_jaw_state = 1  # Assuming the left jaw is open at the start
#         self.right_jaw_state = 1  # Assuming the right jaw is open at the start

#         # Lock for thread-safe access to jaw states
#         self.state_lock = threading.Lock()
        
#         # Set up serial communication with Arduino
#         try:
#             self.ser = serial.Serial(self.port, self.baudrate)
#             time.sleep(2)  # Give some time for the connection to establish
#             print("Serial connection established.")
#         except serial.SerialException:
#             print("Error: Could not connect to Arduino.")
        
#         # Log the initial state
#         self.log_gripper_status("initial_state")

#     def update_state(self, left=None, right=None, action=None):
#         """Update jaw states safely with a lock."""
#         with self.state_lock:
#             if left is not None:
#                 self.left_jaw_state = left
#             if right is not None:
#                 self.right_jaw_state = right
#         if action:
#             self.log_gripper_status(action)

#     def log_gripper_status(self, action):
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         log_entry = f"Timestamp: {timestamp}, Left_Jaw_State: {self.left_jaw_state}, Right_Jaw_State: {self.right_jaw_state}, Action: {action}\n"
#         with open(self.log_file, "a") as file:
#             file.write(log_entry)
#         print(f"Gripper Log -> {log_entry.strip()}")  # Debug Print

#     # def on_press(self, key):
#     #     try:
#     #         if key.char == 'o':
#     #             self.ser.write(b'open_right_request\n')
#     #             self.ser.flush()
#     #             self.right_jaw_state = 1  # Update state to 'open'
#     #             self.log_gripper_status("open_right")
#     #         elif key.char == 'l':
#     #             self.ser.write(b'close_right_request\n')
#     #             self.ser.flush()
#     #             self.right_jaw_state = 0  # Update the state to 'closed'
#     #             self.log_gripper_status("close_right")
#     #         elif key.char == 'i':
#     #             self.ser.write(b'open_left_request\n')
#     #             self.ser.flush()
#     #             self.left_jaw_state = 1  # Update the state to 'open'
#     #             self.log_gripper_status("open_left")
#     #         elif key.char == 'k':
#     #             self.ser.write(b'close_left_request\n')
#     #             self.ser.flush()
#     #             self.left_jaw_state = 0  # Update the state to 'closed'
#     #             self.log_gripper_status("close_left")
#     #     except AttributeError:
#     #         pass  # Do nothing if AttributeError occurs

#     def on_press(self, key):
#         try:
#             if key.char == 'o':
#                 self.ser.write(b'open_right_request\n')
#                 self.ser.flush()
#                 self.update_state(right=1, action="open_right")
#             elif key.char == 'l':
#                 self.ser.write(b'close_right_request\n')
#                 self.ser.flush()
#                 self.update_state(right=0, action="close_right")
#             elif key.char == 'i':
#                 self.ser.write(b'open_left_request\n')
#                 self.ser.flush()
#                 self.update_state(left=1, action="open_left")
#             elif key.char == 'k':
#                 self.ser.write(b'close_left_request\n')
#                 self.ser.flush()
#                 self.update_state(left=0, action="close_left")
#         except AttributeError:
#             pass  # Do nothing if AttributeError occurs

#     def on_release(self, key):
#         # Exit program on 'q'
#         if key.char == 'q':
#             return False

#     def start_key_listener(self):
#         # Start listening for keypresses
#         with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
#             listener.join()

#     def get_states(self):
#         """Return the current jaw states safely."""
#         with self.state_lock:
#             print(f"Fetching Gripper States -> Left: {self.left_jaw_state}, Right: {self.right_jaw_state}")  # Debug Print
#             return self.left_jaw_state, self.right_jaw_state

#     def close(self):
#         # Close the serial connection when done
#         self.ser.close()

# # Usage
# if __name__ == "__main__":
#     gripper = GripperController()
#     gripper.start_key_listener()
#     gripper.close()

# gripper_diff.py

import serial
import time
from datetime import datetime
from pynput import keyboard
import threading
from multiprocessing import Value  # Import Value for shared variables

class GripperController:
    def __init__(self, port='/dev/ttyACM0', baudrate=9600, log_file="gripper_status_log.txt"):
        self.port = port
        self.baudrate = baudrate
        self.log_file = log_file

        # Use multiprocessing.Value for shared variables
        self.left_jaw_state = Value('i', 1)  # Assuming the left jaw is open at the start
        self.right_jaw_state = Value('i', 1)  # Assuming the right jaw is open at the start

        # Set up serial communication with Arduino
        try:
            self.ser = serial.Serial(self.port, self.baudrate)
            time.sleep(2)  # Give some time for the connection to establish
            print("Serial connection established.")
        except serial.SerialException:
            print("Error: Could not connect to Arduino.")
            self.ser = None  # Prevent errors if serial is not connected

        # Log the initial state
        self.log_gripper_status("initial_state")

    def update_state(self, left=None, right=None, action=None):
        """Update jaw states safely using locks."""
        if left is not None:
            with self.left_jaw_state.get_lock():
                self.left_jaw_state.value = left
        if right is not None:
            with self.right_jaw_state.get_lock():
                self.right_jaw_state.value = right
        if action:
            self.log_gripper_status(action)

    def log_gripper_status(self, action):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        left_state = self.left_jaw_state.value
        right_state = self.right_jaw_state.value
        log_entry = f"Timestamp: {timestamp}, Left_Jaw_State: {left_state}, Right_Jaw_State: {right_state}, Action: {action}\n"
        with open(self.log_file, "a") as file:
            file.write(log_entry)
        print(f"Gripper Log -> {log_entry.strip()}")  # Debug Print

    def on_press(self, key):
        try:
            if key.char == 'o':
                if self.ser:
                    self.ser.write(b'open_right_request\n')
                    self.ser.flush()
                self.update_state(right=1, action="open_right")
            elif key.char == 'l':
                if self.ser:
                    self.ser.write(b'close_right_request\n')
                    self.ser.flush()
                self.update_state(right=0, action="close_right")
            elif key.char == 'i':
                if self.ser:
                    self.ser.write(b'open_left_request\n')
                    self.ser.flush()
                self.update_state(left=1, action="open_left")
            elif key.char == 'k':
                if self.ser:
                    self.ser.write(b'close_left_request\n')
                    self.ser.flush()
                self.update_state(left=0, action="close_left")
        except AttributeError:
            pass  # Do nothing if AttributeError occurs

    def on_release(self, key):
        # Exit program on 'q'
        if key.char == 'q':
            return False

    def start_key_listener(self):
        # Start listening for keypresses in a separate thread
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()  # Start in a non-blocking way

    def get_states(self):
        """Return the current jaw states safely."""
        with self.left_jaw_state.get_lock(), self.right_jaw_state.get_lock():
            left = self.left_jaw_state.value
            right = self.right_jaw_state.value
            print(f"Fetching Gripper States -> Left: {left}, Right: {right}")  # Debug Print
            return left, right

    def close(self):
        # Close the serial connection when done
        if self.ser:
            self.ser.close()
        self.listener.stop()

# No need for the 'if __name__ == "__main__"' block since we instantiate GripperController in the main script
