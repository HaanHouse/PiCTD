import smbus
import time
import os
import glob
import datetime
import fcntl
import string
import io 

bus=1
file_read = io.open("/dev/i2c-1", "rb", buffering=0)
file_write = io.open("/dev/i2c-1", "wb", buffering=0)

I2C_SLAVE = 0x703
fcntl.ioctl(file_read, I2C_SLAVE, 100)  #atlas scientific conductivity prob address 100
fcntl.ioctl(file_write, I2C_SLAVE, 100)

TXT = str(datetime.datetime.now())
TXT=TXT[2:16]
TXT=TXT.replace('-','')
TXT=TXT.replace(' ','')
TXT=TXT.replace(':','')
TXT="/home/pi/Documents/CTD/CTD"+TXT+".txt"

fo = open(TXT, "a")
fo.write("Date       Time,Pres,Depth,temp-.01,temp0,temp5,Conduct,TDS,salinity,spec_grav\n")
fo.close()

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'


def read_con():
	# reads a specified number of bytes from I2C, then parses and displays the result
	res = file_read.read(31)         # read from the board
	res=res.replace('\x00','')
	res=res[1:]
	return res

def read_temp():
        
        device_folder = glob.glob(base_dir + '28*')[dev]
        device_file = device_folder + '/w1_slave'
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        equals_pos = lines[1].find('t=')
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def pres():
	bus = smbus.SMBus(1)

	bus.write_byte(0x76, 0x1E)

	time.sleep(0.5)

	data = bus.read_i2c_block_data(0x76, 0xA2, 2)
	C1 = data[0] * 256 + data[1]

	data = bus.read_i2c_block_data(0x76, 0xA4, 2)
	C2 = data[0] * 256 + data[1]

	data = bus.read_i2c_block_data(0x76, 0xA6, 2)
	C3 = data[0] * 256 + data[1]

	data = bus.read_i2c_block_data(0x76, 0xA8, 2)
	C4 = data[0] * 256 + data[1]

	data = bus.read_i2c_block_data(0x76, 0xAA, 2)
	C5 = data[0] * 256 + data[1]

	data = bus.read_i2c_block_data(0x76, 0xAC, 2)
	C6 = data[0] * 256 + data[1]

	bus.write_byte(0x76, 0x40)

	time.sleep(0.5)

	value = bus.read_i2c_block_data(0x76, 0x00, 3)
	D1 = value[0] * 65536 + value[1] * 256 + value[2]

	bus.write_byte(0x76, 0x50)

	time.sleep(0.5)

	value = bus.read_i2c_block_data(0x76, 0x00, 3)
	D2 = value[0] * 65536 + value[1] * 256 + value[2]

	dT = D2 - C5 * 256
	TEMP = 2000 + dT * C6 / 8388608
	OFF = C2 * 65536 + (C4 * dT) / 128
	SENS = C1 * 32768 + (C3 * dT ) / 256
	T2 = 0
	OFF2 = 0
	SENS2 = 0

	if TEMP > 2000 :
	    T2 = 7 * (dT * dT)/ 137438953472
	    OFF2 = ((TEMP - 2000) * (TEMP - 2000)) / 16
	    SENS2= 0
	elif TEMP < 2000 :
		T2 = 3 * (dT * dT) / 8589934592
		OFF2 = 3 * ((TEMP - 2000) * (TEMP - 2000)) / 8
		SENS2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 8
		if TEMP < -1500:
			OFF2 = OFF2 + 7 * ((TEMP + 1500) * (TEMP + 1500))
			SENS2 = SENS2 + 4 * ((TEMP + 1500) * (TEMP + 1500))

	TEMP = TEMP - T2
	OFF = OFF - OFF2
	SENS = SENS - SENS2
	pressure = ((((D1 * SENS) / 2097152) - OFF) / 32768.0) / 10.0
	return pressure

SL=(pres()+pres()+pres()+pres())/4
print "ok",SL

while True:
    dev=0
    Tc0=read_temp()
    Ts="T,"+str(Tc0)+"\00"
    file_write.write(Ts)
    time.sleep(.5)
    file_write.write("R\00")
    time.sleep(1.5)
    con=read_con()
    p=pres()
    dp=(p-SL)/98.1
    dev=2
    Tc2 = read_temp()
    Tc2 = Tc2 + .13
    dev=1
    Tc1= read_temp()
    tpt=str(datetime.datetime.now())
    fo = open(TXT, "a")
    fo.write(tpt[0:19])
    fo.write(",%.2f" %p)
    fo.write(",%.3f" %dp)
    fo.write(",%.2f," %Tc1)
    fo.write("%.2f," %Tc0)
    fo.write("%.2f," %Tc2)
    fo.write(con)
    fo.write("\n")
    fo.close()
    
