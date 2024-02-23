from time import sleep
from multiprocessing import Event

from CaptureLightIntensity import CaptureLightIntensity

shutdown_event = Event()
shutdown_event.clear()

capture_process = CaptureLightIntensity(shutdown_event, 27, 5)
capture_process.start()

i = 0
while i < 30:
    print("Waiting around...")
    sleep(1)
    i += 1

shutdown_event.set()
capture_process.join()

print("Capturing complete, Process closed.")