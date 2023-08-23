from bot import PressKey, ReleaseKey, moveMouse, clickMouse
import numpy as np
import cv2
import math
import time
from win32gui import GetWindowText, GetForegroundWindow

from capture import CircleCapture

from rgbprint import gradient_print, Color, rgbprint


def waitsec(sec):
	'''
	wait 'sec' seconds
	'''
	for i in range(sec, 0, -1):
		rgbprint(' -  Starting in: ' + str(i),color=Color.medium_violet_red)
		time.sleep(1)

def calcdistance(x, y, x2=252, y2=318):
	'''
	euclidean distance
	'''
	distance = math.sqrt((x-x2)**2 + (y-y2)**2)
	return round(distance, 2)

def calcAngle(x, y, x2, y2):
	'''
	Get the relative angle of two points

	x2 and y2 are the center, think of this as the origin (0,0)
	x and y are the other point, forming a line to the origin
	the angle returned goes from -180 to 180
	positive to the right, negative to the left
	'''
	if (y-y2) == 0:
		return 0
	angle = -(np.arctan((x-x2)/(y-y2)) * 180/3.14159)
	if y2 < y:
		angle = -angle
		if angle >= 0:
			angle = 180 - angle
		else:
			angle = -180 - angle
	return angle

def print_title():
	logo_text = """
  __  __     ______     __         ______        ______     ______     ______  
 /\ \_\ \   /\  __ \   /\ \       /\  __ \      /\  == \   /\  __ \   /\__  _\ 
 \ \  __ \  \ \  __ \  \ \ \____  \ \ \/\ \     \ \  __<   \ \ \/\ \  \/_/\ \/ 
  \ \_\ \_\  \ \_\ \_\  \ \_____\  \ \_____\     \ \_____\  \ \_____\    \ \_\ 
   \/_/\/_/   \/_/\/_/   \/_____/   \/_____/      \/_____/   \/_____/     \/_/ 
	
	"""

	author = """	An autonomous farming bot that plays griffball in Halo Reach
	______________________________
	|                            |
	| Created by: @Alex Sturgeon | 
	|____________________________|

	Calibration: A window will pop up with a screen shot of your monitor. Just follow the prompts.

	Controls:
		- Press 'ctrl + c' to quit
		- To Restart Calibration, delete the capture_config.json file and restart the bot

	Note: This bot is a visual bot, it does not read memory or anything like that. It just looks at the screen and clicks.
	      If you move you window around or change the resolution, you will need to recalibrate the bot.

-----------------------------------------------------------------------------
	"""

	gradient_print(logo_text, 
		start_color=0x4BBEE3, 
		end_color=Color.medium_violet_red
	)

	rgbprint(author, color=Color.medium_violet_red)

def main():
	# Print the main startup splash screen in the terminal
	print_title()

	# keyboard scan codes
	W = 0x11
	A = 0x1E
	S = 0x1F
	D = 0x20

	# load config
	attack_distance, show, xlevel = 40, False, 10

	#Initialize the capture system
	capture = CircleCapture()
	
	# Make sure the circle is set up
	#print("Center Value", capture.center)
	if capture.center is None:
		rgbprint('[!] Calibration Needed.',color=Color.medium_violet_red)
		rgbprint(' -  Click into the game when a minimap is visible and calibration will start automatically.',color=Color.medium_violet_red)
		time.sleep(3)
		while True:
			if GetWindowText(GetForegroundWindow()) == "Halo: The Master Chief Collection  ":
				rgbprint('[!] Calibration Starting...',color=Color.medium_violet_red)
				capture.setup_circle()
				rgbprint('- Calibration Complete.',color=Color.medium_violet_red)
				break
			time.sleep(0.7)

		
	
	rgbprint('[!] Starting Bot. Ensure you have the MCC Window Clicked',color=Color.medium_violet_red)
	waitsec(5)

	

	# main loop
	#while GetWindowText(GetForegroundWindow()) == "Halo: The Master Chief Collection  " or show == 'True':
	while True:
		if GetWindowText(GetForegroundWindow()) != "Halo: The Master Chief Collection  ":
			rgbprint('[!] MCC Window not in focus. Pausing...',color=Color.medium_violet_red)
			time.sleep(3)
				
		frame, grey = capture.get_frame()
		center = (int(frame.shape[0]/2), int(frame.shape[1]/2))

		if any(frame[center[0]][center[1]]) == 0:
			rgbprint('Waiting for game',color=Color.medium_violet_red)
			#print('Waiting for game')
			time.sleep(5)

		else:
			contours, _ = cv2.findContours(
				grey, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

			# Choose the contour closest to the center
			w, h = 0, 0  # width and height of a blob
			shortx, shorty, shortw, shorth = 0, 0, 0, 0  # values of the closest blob
			shortest_distance = 5000
			for c in contours:
				x, y, w, h = cv2.boundingRect(c)

				distance = calcdistance(x, y, center[0], center[1])
				if distance < shortest_distance:
					shortest_distance = distance
					shortx, shorty, shortw, shorth = (x, y, w, h)
				else:
					cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
				cv2.putText(frame, '. Distance: ' + str(distance), (x, y),
							cv2.FONT_HERSHEY_COMPLEX_SMALL, .5, (255, 255, 255))

			# Little extra drawng in our cv2 window
			cv2.rectangle(frame, (shortx, shorty),
						  (shortx+shortw, shorty+shorth), (0, 255, 255), 2)
			cv2.line(frame, (center[0], center[1]+500),
					 (center[0], center[1]-500), (255, 0, 0))
			cv2.line(frame, (center[0]+500, center[1]),
					 (center[0]-500, center[1]), (255, 0, 0))
			cv2.line(frame, (center[0]+500, center[1]+xlevel),
					 (center[0]-500, center[1]+xlevel), (0, 0, 255))

			# angle of the closest dot
			angle = calcAngle(shortx, shorty, center[0], center[1])

			# movement and look around commands
			if len(contours) < 1:
				PressKey(W)
				ReleaseKey(A)
				ReleaseKey(D)
				ReleaseKey(S)
			else:
				if shortx+w/2 > center[0]:
					ReleaseKey(A)
					PressKey(D)
				elif shortx+w/2 < center[0]:
					ReleaseKey(D)
					PressKey(A)
				if shorty+h/2 > center[1] + xlevel:
					ReleaseKey(W)
					PressKey(S)
				elif shorty+h/2 < center[1] + xlevel:
					ReleaseKey(S)
					PressKey(W)
				moveMouse(x=2*angle, y=0)

			# strike command
			if shortest_distance < attack_distance and np.absolute(angle) < 10:
				clickMouse()

			# display the cv2 frame
			if show == "True":
				cv2.imshow("Halo_Reach_Griff_Bot", frame)
			# exit situations
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break


if __name__ == "__main__":
	main()
