import cv2
import numpy as np
from mss import mss
import json
import os
import pyautogui

from rgbprint import gradient_print, Color, rgbprint

def get_overlap_area(window, monitor):
    dx = min(window.right, monitor["left"] + monitor["width"]) - max(window.left, monitor["left"])
    dy = min(window.bottom, monitor["top"] + monitor["height"]) - max(window.top, monitor["top"])
    if (dx >= 0) and (dy >= 0):
        return dx * dy
    return 0

class CircleCapture:
    def __init__(self, window_title="halo: the master chief collection",config_file="capture_config.json"):
        self.config_file = config_file
        self.center = None
        self.edge = None
        self.radius = None
        self.width = None
        self.height = None
        self.window_title = window_title
        self.target_monitor = None
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.center = tuple(config['center'])
                self.edge = tuple(config['edge'])
                self.radius = config['radius']
                self.width = config['width']
                self.height = config['height']
                self.target_monitor = config['target_monitor']

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({
                'center': self.center,
                'edge': self.edge,
                'radius': self.radius,
                'width': self.width,
                'height': self.height,
                'target_monitor': self.target_monitor
            }, f)

    def select_center(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.center = (x, y)
            cv2.destroyAllWindows()

    def select_edge(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.edge = (x, y)
            # Calculate radius and set the box dimensions
            dx = self.center[0] - self.edge[0]
            dy = self.center[1] - self.edge[1]
            self.radius = int(np.sqrt(dx**2 + dy**2))
            self.width = self.height = 2 * self.radius
            cv2.destroyAllWindows()

    def capture_monitor_of_window(self):
        # Get a list of all windows
        windows = pyautogui.getAllWindows()
        target_window = None

        for x in windows:
            print(x.title.lower())
            if self.window_title.lower() in x.title.lower():
                print("Window Found", x.title.lower())
                target_window = x
                break

        if not target_window:
            raise Exception(f"Window not found: {self.window_title}")
        
        # Record the top-left corner of the window
        window_top, window_left = target_window.top, target_window.left

        # Determine which monitor the window has the most overlap with
        max_overlap = 0
        target_monitor = None



        with mss() as sct:
            for monitor in sct.monitors[1:]:
                overlap = get_overlap_area(target_window, monitor)
                print("Overlap", overlap)
                if overlap > max_overlap:
                    max_overlap = overlap
                    
                    target_monitor = monitor

        print("Target Monitor", target_monitor)

        if not target_monitor:
            raise Exception(f"No monitor found for window: {self.window_title}")
        
        self.target_monitor = target_monitor

        # Capture the screenshot of the entire monitor
        with mss() as sct:
            screenshot = sct.grab(target_monitor)

        return np.array(screenshot), window_top, window_left

    def setup_circle(self):
        # Record the top-left corner of the window
        frame, window_top, window_left = self.capture_monitor_of_window()
        rgbprint('====[!] Calibration [!]====',color=Color.medium_violet_red)
        rgbprint('====[!] Click on the center of the MiniMap [!]====',color=Color.medium_violet_red)
        cv2.imshow('Select Center of Circle', frame)
        cv2.setMouseCallback('Select Center of Circle', self.select_center)
        cv2.waitKey(0)
        
        rgbprint('====[!] Click on the right outside edge of the MiniMap [!]====',color=Color.medium_violet_red)
        cv2.imshow('Select Edge of Circle', frame)
        cv2.setMouseCallback('Select Edge of Circle', self.select_edge)
        cv2.waitKey(0)

        # Make the coordinates relative to the monitor
        self.center = (self.center[0] + window_left, self.center[1] + window_top)
        self.edge = (self.edge[0] + window_left, self.edge[1] + window_top)

        self.save_config()
        
        # Reload the config with the new values
        self.load_config()

    def capture_screenshot(self):
        with mss() as sct:
            # Create a bounding box around the circle
            top_left_y = self.center[1] - self.radius
            top_left_x = self.center[0] - self.radius
            bbox = {
                'top': top_left_y,
                'left': top_left_x,
                'width': self.width,
                'height': self.height
            }
            screenshot = sct.grab(bbox)
            return np.array(screenshot)

    def get_frame(self):
        frame = self.capture_screenshot()
        frame, grey = self.convert_frame(frame)
        return frame, grey

    def convert_frame(self, img):
        img2 = np.asarray(img, dtype='uint8')
        frame = cv2.cvtColor(img2, cv2.COLOR_BGRA2BGR)
        color_mask2 = cv2.inRange(frame, np.array([0, 0, 235]), np.array([75, 40, 255]))  # red
        redmask = cv2.bitwise_and(frame, frame, mask=color_mask2)
        grey = cv2.cvtColor(redmask, cv2.COLOR_RGB2GRAY)
        return frame, grey

if __name__ == "__main__":
    capture = CircleCapture()

    # Make sure the circle is set up
    if not capture.center:
        capture.setup_circle()

    

    roi, _ = capture.get_frame()
    cv2.imshow("ROI", roi)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
