from time import sleep
from multiprocessing import Event, Queue

from CaptureLightIntensity import CaptureLightIntensity

shutdown_event = Event()
shutdown_event.clear()

data_queue = Queue()

capture_process = CaptureLightIntensity(shutdown_event, data_queue, 27, 5)
capture_process.start()

i = 0
while i < 30:
    data = data_queue.get(block=True)
    print(f"S0: {data[0]}, S1: {data[1]}, S2: {data[2]}, S3: {data[3]}")
    i += 1

shutdown_event.set()
capture_process.join()

print("Capturing complete, Process closed.")