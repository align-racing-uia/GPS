# CURRENTLY SET UP FOR OUTPUT TYPE ISL
import serial
import can
import sys
import math
import time

port = sys.argv[1] #Com port
can_channel = sys.argv[2] #can channel
last_gps_send = round(time.time()*1000)

try:
    ser = serial.Serial(port, 115200, timeout=2)
except:
    print("No serial on this port!")
    exit()


data_types = [None,"Yaw", "Pitch", "Roll", "PosLat", "PosLon", None, "VelN", "VelE", None, "AccelX", "AccelY", "AccelZ", None, None, None]
#data_types = [None, "Yaw", "Pitch", "Roll", None, None, None, "VelX", "VelY", "VelZ", "AccelX", "AccelY", "AccelZ", None, None, None]
try:
    bus = can.Bus(interface="socketcan", channel=can_channel)
except:
    print("Not on linux")
while True:

    data = ser.readline()
    new_data = str.split(str(data), ",")
    dct = dict(zip(data_types, new_data))
    current_time = round(time.time()*1000)

    dct.pop(None)
    try:
        dct["Yaw"] = int(float(dct["Yaw"]) * 10)
        dct["Pitch"] = int(float(dct["Pitch"]) * 10)
        dct["Roll"] = int(float(dct["Roll"]) * 10)

        dct["AccelX"] = int(float(dct["AccelX"]) * 100)
        dct["AccelY"] = int(float(dct["AccelY"]) * 100)
        dct["AccelZ"] = int(float(dct["AccelZ"]) * 100)

        dct["Speed"] = round(math.sqrt(float(dct["VelN"])**2+float(dct["VelE"])**2) * 3.6)

        dct["PosLat"] = int(float(dct["PosLat"])*1000000)
        dct["PosLon"] = int(float(dct["PosLon"])*1000000)

        print(str(dct))

    except:
        #Handeling unknown message formats
        print("Unknown serial format: ")
        print(dct)

    try:
        byte_data = dct["Yaw"].to_bytes(2,"little",signed=True)+dct["Pitch"].to_bytes(2,"little",signed=True)+dct["Roll"].to_bytes(2,"little",signed=True)
        msg = can.Message(arbitration_id=0x0C8,data=byte_data, is_extended_id=False)
        byte_data2 = dct["AccelX"].to_bytes(2,"little",signed=True)+dct["AccelY"].to_bytes(2,"little",signed=True)+dct["AccelZ"].to_bytes(2,"little",signed=True)+dct["Speed"].to_bytes(2,"little",signed=False)
        msg2 = can.Message(arbitration_id=0x0C9,data=byte_data2, is_extended_id=False)
        bus.send(msg)
        bus.send(msg2)
        if(current_time>=last_gps_send+50):
            byte_data3 = dct["PosLat"].to_bytes(2,"little", signed=True)+dct["PosLon"].to_bytes(2,"little", signed=True)
            msg3 = can.Message(arbitration_id=0x0CA,data=byte_data3, is_extended_id=False)
            bus.send(msg3)
        
    except:
        # Handling canbus errors
        print("Could not send to canbus")
        pass
