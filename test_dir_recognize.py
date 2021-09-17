# from SignLanguage.recognize_gesture import run_script_gesture
from SignLanguage.fun_util import run_script_fun
import threading
if __name__ == '__main__':
    t2 = threading.Thread(target=run_script_fun)
    t2.start()
    # run_script_gesture()