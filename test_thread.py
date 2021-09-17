# Python program to illustrate the concept
# of threading
# importing the threading module
import threading
import time 
from SignLanguage.set_hand_hist import get_hand_hist
def print_cube():
	"""
	function to print cube of given num
	"""
	print("Cube")

def print_square():
	"""
	function to print square of given num
	"""
	while True:
		time.sleep(0.5)
		print("in thread")
	# print("Square: {}".format(num * num))

# if __name__ == "__main__":
	# creating thread
# t1 = threading.Thread(target=get_hand_hist)
# t2 = threading.Thread(target=print_cube)

# # starting thread 1
# # starting thread 2
# t1.start()
# t2.start()
get_hand_hist()
	# # wait until thread 1 is completely executed
	# t1.join()
	# # wait until thread 2 is completely executed
	# t2.join()

	# both threads completely executed
	# print("\nDone!")
