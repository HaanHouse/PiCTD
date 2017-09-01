import smbus
import time
import datetime

TXT = str(datetime.datetime.now())
TXT=TXT[2:16]
TXT=TXT.replace('-','')
TXT=TXT.replace(' ','')
TXT=TXT.replace(':','')
TXT="TD"+TXT+".txt"
fo=open(TXT,'a')
fo.write('date    time,pressure,depth M,Depth F,temp C,Temp F\n')
fo.close()

bus = smbus.SMBus(1)
bus.write_byte(0x40,0xFE)
time.sleep(1)
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

def pres():
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
print ("ok",SL)

while True:
	bus.write_byte(0x40,0xF3)
	time.sleep(2)
	data= bus.read_i2c_block_data(0x40,0xE0,2)
	rt= data[0] * 256 + data[1]
	temp=((175.72 * rt)/65536)-46.85
	tempf=1.8 * temp + 32
	p=pres()
	dpM=(SL-p)/98.1
	dpFT=3.28084*dpM
	tpt=str(datetime.datetime.now())
	print ('Temperature %.3f'%temp, "C %.3f" %tempf, 'F')
	fo=open(TXT,'a')
	fo.write(tpt[0:19])
	fo.write(',%.2f' %p)
	fo.write(',%.3f' %dpM)
	fo.write(',%.3f' %dpFT)
	fo.write(',%.2f' %temp)
	fo.write(',%.2f\n' %tempf)
	fo.close()
	
