import serial
import time
import tkinter as tk
import matplotlib.pyplot as plt
from collections import deque
from datetime import datetime

SerialObj = serial.Serial('COM3') # COMxx   format on Windows
                                   # ttyUSBx format on Linux
                                   
SerialObj.baudrate = 9600  # set Baud rate to 9600
SerialObj.bytesize = 8     # Number of data bits = 8
SerialObj.parity   ='N'    # No parity
SerialObj.stopbits = 1     # Number of Stop bits = 1

SerialObj.timeout  = None  # Setting timeouts here No timeouts,waits forever

time.sleep(3)

# Funkcja map w C++ mapuje wartość z jednego zakresu na inny. 
def map(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def adjustRGB(temperatura):
    tempMax = 27
    tempMin = 17
    G = 0  # Stała wartość dla koloru zielonego
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
    # Podziel ciąg znaków na części, rozdzielając go na podstawie znaku "|"
    parts = data_string.split("|")
    # Pierwsza część zawiera wilgotność i jej jednostkę
    humidity_part = parts[0].split(":")[1].strip()
    # Wyodrębnij samą liczbę wilgotności, usuwając "%" i spacje
    humidity = int(humidity_part[:-3])
    # Druga część zawiera temperaturę i jej jednostkę
    temperature_part = parts[1].strip()
    # Wyodrębnij samą liczbę temperatury, usuwając "*C" i spacje
    temperature = int(temperature_part[:-2])

    return humidity, temperature

def extract_int_value_from_sensor(data_string):
    parts = data_string.split(":")
    analogRead = parts[1].strip()
    return int(analogRead)

# Inicjalizacja kolejki na dane i wykresu
data_queue = deque(maxlen=100)  # kolejka przechowująca ostatnie 100 punktów danych
time_queue = deque(maxlen=100)  # kolejka przechowująca czasowe znaczniki dla danych
# plt.ion()  # Włącz tryb interaktywny Matplotlib
fig, ax = plt.subplots()
line, = ax.plot(time_queue, data_queue, color='blue')  # utwórz linię na wykresie
ax.set_ylim(0, 1000)

def update_plot(new_data):
    # Dodaj nowe dane i czas do kolejek
    data_queue.append(new_data)
    time_queue.append(datetime.now())

    # Zaktualizuj dane na wykresie
    line.set_xdata(time_queue)
    line.set_ydata(data_queue)

    # Dostosuj osie X i Y do nowych danych
    ax.relim()
    ax.autoscale_view()

    # Ponownie narysuj wykres
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
            # new_dataFun = extract_int_value_from_sensor(data)
            # update_plot(new_dataFun)
            pass
        
        if data.startswith("WaterLVL"):
            new_dataFun = extract_int_value_from_sensor(data)
            update_plot(new_dataFun)
            
except KeyboardInterrupt:
    pass

plt.ioff()  
plt.show() 
SerialObj.close()