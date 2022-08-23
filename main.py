from WindowCapture import WindowCapture
import cv2 as cv
import time
from PIL import Image
import h5py
import numpy as np
import random
from pynput.keyboard import Key, Listener
from pynput.mouse import Listener as mListener
import keyboard

def on_press(key):
	global ender
	if(key == Key.esc):
		ender = True
	elif (not(str(key) in key_arr)):
		key_arr.append(str(key))

def on_release(key):
    if (str(key) in key_arr):
    	key_arr.remove(str(key))

def on_click(x, y, button, pressed):
	if(pressed and not('click') in key_arr):
		key_arr.append('click')
	elif(not(pressed)):
		key_arr.remove('click')

def homogArray(in_arr):
	target = max(len(x) for x in in_arr)
	for element in in_arr:
		for i in range(len(element),target):
			element.append('')


def saveReplay(images,inputs,filename):
	""" 
	Stores an array of images to HDF5.
	Parameters:
	---------------
	images       images array, (N, 32, 32, 3) to be stored
	inputs       inputs array, (N, 1) to be stored
	"""

	homogArray(inputs)
	num_images = len(images)

	# Create a new HDF5 file
	file = h5py.File(f"{filename}_{num_images}.h5", "w")


	dataset = file.create_dataset(
	"images", np.shape(images), h5py.h5t.STD_U8BE, data=images
	)

	input_set = file.create_dataset(
	"inputs", np.shape(inputs), h5py.string_dtype(encoding='utf-8'), data=inputs
	)
	file.close()

def loadReplay(filename):
	file = h5py.File(filename,'r')
	images = np.array(file['images']).astype("uint8")
	inputs = np.array(file['inputs']).astype(str)
	return images, inputs

def viewReplay(images,inputs=[]):
	counter = 0
	while(True):
		if(counter < len(images)-1):
			counter+=1
		else:
			counter = 0
		cv.imshow('Environment Replay',images[counter]);
		if(len(inputs) > 0):
			print('Inputs:',inputs[counter])
		if(cv.waitKey(1)==ord('q')):
			cv.destroyAllWindows()
			break	


def test():
	images, inputs = loadReplay('captures/pong_gray_359.h5')
	viewReplay(images,inputs)
	

key_arr = []
ender = False
def main():

	kb_listener = Listener(on_press=on_press,on_release=on_release)
	m_listener = mListener(on_click=on_click)
	kb_listener.start()
	m_listener.start()

	
	window_name = 0xc10112
	imgReader = WindowCapture(window_name,version =2)
	imgReader.list_window_names()


	fps = 0
	start_time = time.perf_counter()
	last_ss_time = int(time.perf_counter()-start_time)
	color_arr = []
	gray_arr = []
	input_arr = []
	while not(ender):
		if(last_ss_time == int(time.perf_counter())):
			fps+=1
		else:
			print('Frames per second: ',fps)
			last_ss_time = int(time.perf_counter())
			fps = 0		

		if(fps%10 == 0):		
			frame = imgReader.get_screenshot()
			color_arr.append(frame[:])
			frame = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
			gray_arr.append(frame[:])
			input_arr.append(key_arr[:])	
			cv.imshow('Processed Output', frame)

		if(cv.waitKey(1)==ord('q')):
			cv.destroyAllWindows()
			break
	kb_listener.stop()
	m_listener.stop()

	saveReplay(color_arr,input_arr,'captures/bloxors_color')
	saveReplay(gray_arr,input_arr,'captures/bloxors_gray')
	print("Elapsed Time:",time.perf_counter()-start_time,"seconds.")



if __name__ == "__main__":
	#main()
	test()