import cv2, pickle
import numpy as np
import tensorflow as tf
from SignLanguage.cnn_tf import cnn_model_fn
import os
import sqlite3
from keras.models import load_model
from threading import Thread
cwd = os.getcwd()
# time taken by program to execute
# start_time = time.time()

# check if file exists in directory
def file_exists(filename):
    try:
        with open(filename):
            pass
    except IOError:
        return False
    return True

# engine = pyttsx3.init()
# engine.setProperty('rate', 150)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# model = load_model('SignLanguage/cnn_model_keras2.h5')

def get_hand_hist():
	with open("hist", "rb") as f:
		hist = pickle.load(f)
	return hist

def get_image_size():
	img = cv2.imread('SignLanguage/gestures/0/100.jpg', 0)
	return img.shape

image_x, image_y = get_image_size()

def keras_process_image(img):
	img = cv2.resize(img, (image_x, image_y))
	img = np.array(img, dtype=np.float32)
	img = np.reshape(img, (1, image_x, image_y, 1))
	return img

def keras_predict(model, image):
	processed = keras_process_image(image)
	pred_probab = model.predict(processed)[0]
	pred_class = list(pred_probab).index(max(pred_probab))
	return max(pred_probab), pred_class

def get_pred_text_from_db(pred_class):
	conn = sqlite3.connect("SignLanguage/gesture_db.db")
	cmd = "SELECT g_name FROM gesture WHERE g_id="+str(pred_class)
	cursor = conn.execute(cmd)
	for row in cursor:
		return row[0]

def get_pred_from_contour(model,contour, thresh):
	
	x1, y1, w1, h1 = cv2.boundingRect(contour)
	save_img = thresh[y1:y1+h1, x1:x1+w1]
	text = ""
	if w1 > h1:
		save_img = cv2.copyMakeBorder(save_img, int((w1-h1)/2) , int((w1-h1)/2) , 0, 0, cv2.BORDER_CONSTANT, (0, 0, 0))
	elif h1 > w1:
		save_img = cv2.copyMakeBorder(save_img, 0, 0, int((h1-w1)/2) , int((h1-w1)/2) , cv2.BORDER_CONSTANT, (0, 0, 0))
	pred_probab, pred_class = keras_predict(model, save_img)
	if pred_probab*100 > 70:
		text = get_pred_text_from_db(pred_class)
	return text

hist = get_hand_hist()
x, y, w, h = 300, 100, 300, 300
is_voice_on = False

def get_img_contour_thresh(img):
	img = cv2.flip(img, 1)
	imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	dst = cv2.calcBackProject([imgHSV], [0, 1], hist, [0, 180, 0, 256], 1)
	disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10,10))
	cv2.filter2D(dst,-1,disc,dst)
	blur = cv2.GaussianBlur(dst, (11,11), 0)
	blur = cv2.medianBlur(blur, 15)
	thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
	thresh = cv2.merge((thresh,thresh,thresh))
	thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
	thresh = thresh[y:y+h, x:x+w]
	contours = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
	return img, contours, thresh

def say_text(text):
	if not is_voice_on:
		return
	# while engine._inLoop:
	# 	pass
	# engine.say(text)
	# engine.runAndWait()

def text_mode(model):
	global is_voice_on
	# model = load_model('SignLanguage/cnn_model_keras2.h5')
	text = ""
	word = ""
	count_same_frame = 0
	i=0
	while True:

		if file_exists(cwd + '/recognize_img/frame' + str(i) + '.jpg') == True:
			with open(cwd + '/recognize_img/frame' + str(i) + '.jpg', 'rb') as f:
				check_chars = f.read()[-2:]
			if check_chars != b'\xff\xd9':
				# print('Not complete image')
				continue
		else:
			continue    
		# print('complete image')
		img = cv2.imread(cwd + '/recognize_img/frame' + str(i) + '.jpg')
		os.remove(cwd + '/recognize_img/frame' + str(i) + '.jpg')

		img = cv2.resize(img, (640, 480))
		img, contours, thresh = get_img_contour_thresh(img)
		old_text = text
		if len(contours) > 0:
			contour = max(contours, key = cv2.contourArea)
			contour_area = cv2.contourArea(contour)
			# print(contour_area)
			if contour_area > 10000:
				text = get_pred_from_contour(model,contour, thresh)
				if old_text == text:
					count_same_frame += 1
				else:
					count_same_frame = 0

				# print("count_same_frame",count_same_frame)
				if count_same_frame > 5:
					if len(text) == 1:
						pass
					word = word + text
					if word.startswith('I/Me '):
						word = word.replace('I/Me ', 'I ')
					elif word.endswith('I/Me '):
						word = word.replace('I/Me ', 'me ')
					count_same_frame = 0

			elif contour_area < 1000:
				text = ""
				word = ""
		else:
			text = ""
			word = ""
		# print(word)
		blackboard = np.zeros((480, 640, 3), dtype=np.uint8)
		cv2.putText(blackboard, "Text Mode", (180, 50), cv2.FONT_HERSHEY_TRIPLEX, 1.5, (255, 0,0))
		cv2.putText(blackboard, "Predicted text- " + text, (30, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 0))
		cv2.putText(blackboard, word, (30, 240), cv2.FONT_HERSHEY_TRIPLEX, 2, (255, 255, 255))
		# if is_voice_on:
		# 	cv2.putText(blackboard, "Voice on", (450, 440), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 127, 0))
		# else:
		# 	cv2.putText(blackboard, "Voice off", (450, 440), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 127, 0))
		cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
		res = np.hstack((img, blackboard))
		# cv2.imshow("Recognizing gesture", res)
		# cv2.imshow("thresh", thresh)
		# keypress = cv2.waitKey(1)
		# if keypress == ord('q') or keypress == ord('c'):
		# 	break
		# if keypress == ord('v') and is_voice_on:
		# 	is_voice_on = False
		# elif keypress == ord('v') and not is_voice_on:
		# 	is_voice_on = True
		cv2.imwrite(cwd + '/recognize_img/result' + str(i) + '.jpg', res)
		cv2.imwrite(cwd + '/recognize_img/thresh' + str(i) + '.jpg', thresh)
		# if cv2.waitKey(1) == ord('q'):
		# 	break
		i+=1

	# if keypress == ord('c'):
	# 	return 2
	# else:
	return 0

def recognize(model):
	# cam = cv2.VideoCapture(1)
	# if cam.read()[0]==False:
	# 	cam = cv2.VideoCapture(0)
	text = ""
	word = ""
	count_same_frame = 0
	keypress = 1
	while True:
		if keypress == 1:
			keypress = text_mode(model)
		# elif keypress == 2:
		# 	keypress = calculator_mode(cam)
		else:
			break
def run_script_fun():
	model = load_model('SignLanguage/cnn_model_keras2.h5')
	keras_predict(model, np.zeros((50, 50), dtype = np.uint8))		
	recognize(model)

if __name__ == '__main__':
	run_script_fun()
