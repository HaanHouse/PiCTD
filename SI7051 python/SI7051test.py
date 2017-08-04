import smbus
import time

bus = smbus.SMBus(1)

bus.write_byte(0x40,0xFE)

while True:
	bus.write_byte(0x40,0xF3)
	time.sleep(2)
	data= bus.read_i2c_block_data(0x40,0xE0,2)
	rt= data[0] * 256 + data[1]
	temp=((175.72 * rt)/65536)-46.85
	tempf=1.8 * temp + 32
	print ('Temperature %.3f'%temp, "C %.3f" %tempf, 'F')
