import serial
import time
import tkinter as tk
import matplotlib.pyplot as plt
from collections import deque
from datetime import datetime

SerialObj = serial.Serial('COM3') # opening the serial communication port in this example COM3
                                   
SerialObj.baudrate = 9600  # set Baud rate to 9600
SerialObj.bytesize = 8     # Number of data bits = 8
SerialObj.parity   ='N'    # No parity
SerialObj.stopbits = 1     # Number of Stop bits = 1

SerialObj.timeout  = None  # Setting timeouts here No timeouts, waits forever

time.sleep(3)
 
def map(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def adjustRGB(temperatura):
    tempMax = 27
    tempMin = 17
    G = 0 
    R = 0
    B = 0

    if temperatura == 21:
        R = 0
        G = 225
        B = 120
    elif temperatura >= tempMin and temperatura <= tempMax:
        R = map(temperatura, tempMin, tempMax, 20, 225)
        G = map(temperatura, tempMin, tempMax, 15, 0)
        B = map(temperatura, tempMin, tempMax, 160, 5)
    else:
        R = 255
        G = 255
        B = 255
        
    # print("R:", R, " G:", G, " B:", B)
    return int(R),int(G),int(B)

def extract_data_from_DHT11(data_string):
    # Split the string into parts by the "|" character
    parts = data_string.split("|")
    # The first part contains humidity and its unit
    humidity_part = parts[0].split(":")[1].strip()
    # Extract humidity by removing "%" and spaces
    humidity = int(humidity_part[:-3])
    # The second part contains temperature and its unit
    temperature_part = parts[1].strip()
    # Extract temperature value by removing "*C" and spaces
    temperature = int(temperature_part[:-2])

    return humidity, temperature

def extract_int_value_from_sensor(data_string):
    parts = data_string.split(":")
    analogRead = parts[1].strip()
    return int(analogRead)

# Initialize data and plot queue
data_queue = deque(maxlen=100)  # Queue to store the last 100 data points
time_queue = deque(maxlen=100)  # Queue to store time stamps for the data
# plt.ion()  # Turn on Matplotlib interactive mode
fig, ax = plt.subplots()
line, = ax.plot(time_queue, data_queue, color='blue')  # Create a line on the plot
ax.set_ylim(0, 1000)  # Set the y-axis limits for the plot

def update_plot(new_data):
    # Add new data and time to the queues
    data_queue.append(new_data)
    time_queue.append(datetime.now())

    # Update the plot data
    line.set_xdata(time_queue)
    line.set_ydata(data_queue)

    # Adjust the X and Y axes to the new data
    ax.relim()
    ax.autoscale_view()

    # Redraw the plot
    plt.draw()
    plt.pause(0.01)

try:
    oldTemp = -999
    while True:
        
        print("________________________________________________________")
        ReceivedString = SerialObj.readline()
        data = ReceivedString.decode('utf-8')
        print(f"Recieved data from arduino: \n \t{data}")
        
        if data.startswith("DHT11"):
            humidity, temperature = extract_data_from_DHT11(data)
            R,G,B = adjustRGB(temperature)
            
            #Convert String to Byte format
            if oldTemp!=temperature:
                print('\t\t*NOWA TEMPERATURA*')
                SendString = 'RGB LED:R'+ str(R) + 'G' + str(G) + 'B' + str(B)
                SendString = bytearray(SendString,'utf8')
                
            oldTemp=temperature
            print(f"Data sended to arduino: \n \t{SendString}")
            SerialObj.write(SendString)
            
        if data.startswith("SoundSensorLM393"):
            new_dataFun = extract_int_value_from_sensor(data)
            update_plot(new_dataFun)
        
        if data.startswith("WaterLVL"):
            # new_dataFun = extract_int_value_from_sensor(data)
            # update_plot(new_dataFun)
            pass
            
except KeyboardInterrupt:
    pass

plt.ioff()  
plt.show() 
SerialObj.close()