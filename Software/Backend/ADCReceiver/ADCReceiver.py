import spidev
import time
import numpy as np
import matplotlib.pyplot as plt
import threading
import RPi.GPIO as GPIO

class halleffectandadc:
   def __init__(self, desired_clock_cycles, pin, clock_speed, buff_size):
	   
       self.start_event = threading.Event()
       self.started_event = threading.Event()
       self.stop_event = threading.Event()
       self.stopped_event = threading.Event()
       self.start_plotting_event = threading.Event()
       self.plotting_completed_event = threading.Event()


       self.spi = spidev.SpiDev()
       self.spi.open(0, 0)
       self.spi.max_speed_hz = clock_speed
       self.buff_size = buff_size
       self.buff = np.ndarray((self.buff_size,), dtype="uint16")
       self.desired_clock_cycles = desired_clock_cycles
       self.pin = pin
       GPIO.setmode(GPIO.BCM)
       GPIO.setup(pin, GPIO.IN)

   def get_adc_val(self):
       response = self.spi.xfer([0x00, 0x00])
       return (response[0] << 8) + response[1]


   def adcreceiver(self):
       while True:
		   
		   #Wait for the start_event to be set by halleffect_monitor
           self.start_event.wait()
           #Once the event has been started clear the start event flag
           self.start_event.clear() 
           #Set the started_event flag to True, ADC receiving process has started  
           self.started_event.set() 


           print("The thread is starting to collect data")
           self.time_start = time.perf_counter()


           i = 0
           while i < self.buff_size and not self.stop_event.is_set():
               self.buff[i] = self.get_adc_val()
               i += 1
               print(i)


           self.time_end = time.perf_counter()
           
           #Set the started event flag to False , the ADC has stopped processing data 
           self.stopped_event.set() 
           print("The thread has been stopped to plot the data")

   def halleffect_monitor(self):
       while True:
		   #Clear the stop event flag 
           self.stop_event.clear()
           
           #Clear the stopped event flag
           self.stopped_event.clear()
           
           #Set the start event flag, this will start the adcreceiver 
           self.start_event.set()
           
           #Wait until the ADC receiver begins receiving, then start checking for a magnetic field
           self.started_event.wait()


           hall_effect_clock_count = 0
           while hall_effect_clock_count < self.desired_clock_cycles:
               print("Waiting....")
               if GPIO.wait_for_edge(self.pin, GPIO.RISING):
                   hall_effect_clock_count += 1
                   print(f"Magnetic Field Detected, Number of Magnetic Fields Detected: {hall_effect_clock_count}")
                   
		   #Once we have detected the correct number of magnetic fields stop the hall effect sensor
           self.stop_event.set()
           #Wait until the ADC receiver has set the stopped flag to True 
           self.stopped_event.wait()
			
           #Clear the completed event flag
           self.plotting_completed_event.clear()
           
           self.start_plotting_event.set()
           self.plotting_completed_event.wait()


   def plot_data(self):
       elapsed_time = self.time_end - self.time_start


       time_points = np.linspace(0, elapsed_time, self.buff_size, endpoint=True)
       self.buff[0] = self.buff[1]
       self.buff[1] = self.buff[2]
       plt.plot(time_points, self.buff / 65535 * 5)


       plt.xlabel("Elapsed Time (s)", fontsize=12)
       plt.title("Change in Potentiometer Wiper Voltage", fontsize=12)
       plt.ylabel("Voltage (V)", fontsize=12)
       print(
           f"dT: {elapsed_time}s, STD: {np.std(self.buff):.2f}, MIN: {min(self.buff)}, MAX: {max(self.buff)}, AVG: {np.mean(self.buff):.2f}"
       )
       plt.show()
       
try:
   adc1 = halleffectandadc(1, 17, 2200000, 75000)
   #Setting both threads to daemon, will kill both threads automatically when the program exits. 
   threading.Thread(target=adc1.halleffect_monitor, daemon=True).start()
   threading.Thread(target=adc1.adcreceiver, daemon=True).start()
   while True:
       adc1.start_plotting_event.wait()
       adc1.start_plotting_event.clear()
       adc1.plot_data()
       adc1.plotting_completed_event.set()
except KeyboardInterrupt:
   adc1.spi.close()




  





