import cv2
import numpy as np
import pickle
import os 
import time
cwd = os.getcwd()
# time taken by program to execute
start_time = time.time()

# check if file exists in directory
def file_exists(filename):
    try:
        with open(filename):
            pass
    except IOError:
        return False
    return True

def build_squares(img):
	x, y, w, h = 420, 140, 10, 10
	d = 10
	imgCrop = None
	crop = None
	for i in range(10):
		for j in range(5):
			if np.any(imgCrop == None):
				imgCrop = img[y:y+h, x:x+w]
			else:
				imgCrop = np.hstack((imgCrop, img[y:y+h, x:x+w]))
			cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 1)
			x+=w+d
		if np.any(crop == None):
			crop = imgCrop
		else:
			crop = np.vstack((crop, imgCrop)) 
		imgCrop = None
		x = 420
		y+=h+d
	return crop

def get_hand_hist():
	# cam = cv2.VideoCapture(1)
	# if cam.read()[0]==False:
	# 	cam = cv2.VideoCapture(0)
	x, y, w, h = 300, 100, 300, 300
	flagPressedC, flagPressedS = False, False
	imgCrop = None
	i=0
	j=0	
	flag_first = True
	while True:
		if file_exists(cwd + '/frame_img/frame' + str(i) + '.jpg') == True:
			with open(cwd + '/frame_img/frame' + str(i) + '.jpg', 'rb') as f:
				check_chars = f.read()[-2:]
			if check_chars != b'\xff\xd9':
				# print('Not complete image')
				continue
		else:
			continue    
		# print('complete image')

		# display the image
		img = cv2.imread(cwd + '/frame_img/frame' + str(i) + '.jpg')
		os.remove(cwd + '/frame_img/frame' + str(i) + '.jpg')
		# img = cam.read()[1]
		img = cv2.flip(img, 1)
		img = cv2.resize(img, (640, 480))
		hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		
		# keypress = cv2.waitKey(1)
		keypress = None
		curr_time = time.time() - start_time
		if curr_time > 10 and curr_time < 15:
			keypress = ord('c')
		elif curr_time > 15 and curr_time < 20:
			keypress = ord('s')
	
		if keypress == ord('c'):		
			hsvCrop = cv2.cvtColor(imgCrop, cv2.COLOR_BGR2HSV)
			flagPressedC = True
			hist = cv2.calcHist([hsvCrop], [0, 1], None, [180, 256], [0, 180, 0, 256])
			cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
		elif keypress == ord('s'):
			flagPressedS = True	
			break
		if flagPressedC:
			dst = cv2.calcBackProject([hsv], [0, 1], hist, [0, 180, 0, 256], 1)
			dst1 = dst.copy()
			disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10,10))
			cv2.filter2D(dst,-1,disc,dst)
			blur = cv2.GaussianBlur(dst, (11,11), 0)
			blur = cv2.medianBlur(blur, 15)
			ret,thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
			thresh = cv2.merge((thresh,thresh,thresh))
			#cv2.imshow("res", res)
			# press c to view thresh
			cv2.imwrite(cwd + '/SignLanguage/thresh_images/frame' + str(j) + '.jpg', thresh)
			# read image from folder
			# while file_exists(cwd + '/SignLanguage/thresh_images/frame' + str(j) + '.jpg') :
			# 	with open(cwd + '/SignLanguage/thresh_images/frame' + str(j) + '.jpg', 'rb') as f:
			# 		check_chars = f.read()[-2:]
			# 	if check_chars != b'\xff\xd9':
			# 		print('Not complete image')
			# 		continue
			# 	# thresh = cv2.imread(cwd + '/SignLanguage/thresh_images/frame' + str(j) + '.jpg')
			# 	# cv2.imshow("Thresh", thresh)
			# 	break
			j+=1
			
		if not flagPressedS:
			imgCrop = build_squares(img)
		# cv2.imshow("Set hand histogram", img)
		# if cv2.waitKey(1000) & 0xFF == ord('q'):
		# 	break
		# os.remove(cwd + '/../webapp2.0/Live-Streaming-using-OpenCV-Flask/frame_img/frame' + str(i) + '.jpg')
		i+=1
	#cam.release()
	cv2.destroyAllWindows()
	with open("hist", "wb") as f:
		pickle.dump(hist, f)

if __name__ == "__main__":
	get_hand_hist()
