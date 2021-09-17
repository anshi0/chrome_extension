from SignLanguage.fun_util import run_script_fun
from flask import Flask, render_template, Response, request
import cv2
# from time import sleep
# from flask import jsonify 
# import io
# from base64 import encodebytes
# from PIL import Image
import threading
import time

from SignLanguage.set_hand_hist import get_hand_hist
# from SignLanguage.recognize_gesture import run_script_gesture
from SignLanguage.fun_util import run_script_fun

import os
cwd = os.getcwd()
app = Flask(__name__)

# check if file exists in directory
def file_exists(filename):
    try:
        with open(filename):
            pass
    except IOError:
        return False
    return True


#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)
  # use 0 for web camera


def gen_frames(folder):  # generate frame by frame from camera
    camera = cv2.VideoCapture(0)
    i=0
    # delete files from directory
    # old_frames = os.listdir(cwd + f'/{folder}')
    # # print(old_frames)
    # for file in old_frames:
    #     os.remove(cwd + f'/{folder}/{file}')
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            cv2.imwrite(cwd + f'/{folder}/frame' + str(i) + '.jpg', frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            i+=1
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def thresh_frames():
    i=0
    flag_first = True
    while True:

        if file_exists(cwd + '/SignLanguage/thresh_images/frame' + str(i) + '.jpg') :
            with open(cwd + '/SignLanguage/thresh_images/frame' + str(i) + '.jpg', 'rb') as f:
                check_chars = f.read()[-2:]
            if check_chars != b'\xff\xd9':
                # print('Not complete image')
                continue
        else:
            continue    
        # print('complete image')
        img = cv2.imread(cwd + '/SignLanguage/thresh_images/frame' + str(i) + '.jpg')
        os.remove(cwd + '/SignLanguage/thresh_images/frame' + str(i) + '.jpg')
        ret,buffer = cv2.imencode('.jpg',img)
        frame = buffer.tobytes()
        i+=1
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
def result_frames():
    i=0
    flag_first = True
    while True:

        if file_exists(cwd + '/recognize_img/result' + str(i) + '.jpg') :
            with open(cwd + '/recognize_img/result' + str(i) + '.jpg', 'rb') as f:
                check_chars = f.read()[-2:]
            if check_chars != b'\xff\xd9':
                # print('Not complete image')
                continue
        else:
            continue    
        # print('complete image')
        img = cv2.imread(cwd + '/recognize_img/result' + str(i) + '.jpg')
        os.remove(cwd + '/recognize_img/result' + str(i) + '.jpg')
        ret,buffer = cv2.imencode('.jpg',img)
        frame = buffer.tobytes()
        i+=1
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
def result_frames_thresh():
    i=0
    flag_first = True
    while True:

        if file_exists(cwd + '/recognize_img/thresh' + str(i) + '.jpg') :
            with open(cwd + '/recognize_img/thresh' + str(i) + '.jpg', 'rb') as f:
                check_chars = f.read()[-2:]
            if check_chars != b'\xff\xd9':
                # print('Not complete image')
                continue
        else:
            continue    
        # print('complete image')
        img = cv2.imread(cwd + '/recognize_img/thresh' + str(i) + '.jpg')
        os.remove(cwd + '/recognize_img/thresh' + str(i) + '.jpg')
        ret,buffer = cv2.imencode('.jpg',img)
        frame = buffer.tobytes()
        i+=1
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def delete_files(folder):
    # delete files from directory
    old_frames = os.listdir(cwd + f'/{folder}')
    # print(old_frames)
    for file in old_frames:
        os.remove(cwd + f'/{folder}/{file}')
    
@app.route('/video_feed')
def video_feed():           
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames("frame_img"), mimetype='multipart/x-mixed-replace; boundary=frame')
    
@app.route('/video_feed_r')
def video_feed_r():           
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames("recognize_img"), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/result')
def result():           
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(result_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/result_thresh')
def result_thresh():           
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(result_frames_thresh(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/thresh_feed')
def thresh_feed():
    return Response(thresh_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/index')
def index():
    # list files from directory
    t0 = threading.Thread(target=delete_files, args=("frame_img",))
    t0.start()
    t0.join()

    t1 = threading.Thread(target=get_hand_hist)
    t1.start()
    time.sleep(1)
    return render_template('index.html')

@app.route('/convert')
def convert():
    t0 = threading.Thread(target=delete_files, args=("recognize_img",))
    t0.start()
    t0.join()
    
    t2 = threading.Thread(target=run_script_fun)
    t2.start()
    time.sleep(1)
    
    return render_template('tmp.html')

@app.route('/')
def proj():
    return render_template('pre_index.html')

if __name__ == '__main__':
    app.run(debug=True, port = int(os.getenv('PORT')))
    #app.run(debug=False)