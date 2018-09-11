import smbus
import time
import datetime
import io
import fcntl
import math
#import glob
#import string

SG=1
file_read = io.open("/dev/i2c-1", "rb", buffering=0)
file_write = io.open("/dev/i2c-1", "wb", buffering=0)

I2C_SLAVE = 0x703
fcntl.ioctl(file_read, I2C_SLAVE, 100)  #atlas scientific conductivity prob address 100
fcntl.ioctl(file_write, I2C_SLAVE, 100)

lad=raw_input('lat degrees ')
lam=raw_input('lat min ')
las=raw_input('lat sec ')
lac=raw_input('N or S ')
lod=raw_input('long degrees ')
lom=raw_input('long min ')
los=raw_input('long sec ')
loc=raw_input('W or E ')
loca=lad+' '+lam+"' "+las+'" '+lac+' '+lod+' '+lom+"' "+los+'" '+loc
locad=str(float(lad) +round(((float(lam)+(float(las)/60))/60),6))+lac+str(float(lod)+round(((float(lom)+(float(los)/60))/60),6))+loc
lo=locad.replace('.','*')

TXT = str(datetime.datetime.now())
TXT=TXT[2:16]
TXT=TXT.replace('-','')
TXT=TXT.replace(' ','')
TXT=TXT.replace(':','')
TXT="/home/pi/Documents/CTD/CTD"+TXT+lo+".csv"
fo=open(TXT,'a')
fo.write('date    time,pressure,depth M,Depth F,temp C,Temp F,Conductivity,Salinity,SG,uncorrected Con,Calculated Sal,Calculated SG,'+loca+','+locad+'\n')
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

def read_con():
        # reads a specified number of bytes from I2C, then parses and displays the result
        Ts="T,"+str(temp)+"\00"
        file_write.write(Ts)
        time.sleep(.3)
        file_write.write("R\00")
        time.sleep(.7)
        res = file_read.read(31)         # read from the board
        res=res.replace('\x00','')
        res=res[1:]
        return res

def raw_con():
        # reads a specified number of bytes from I2C, then parses and displays the result
        Ts="T,25\00"
        file_write.write(Ts)
        time.sleep(.3)
        file_write.write("R\00")
        time.sleep(.7)
        res = file_read.read(31)         # read from the board
        res=res.replace('\x00','')
	conly=res.find(',')
        res=res[1:conly]
        return res

def salinity(c,t,p):
	#var R,rt,Rp,Rt,A,B,C,sal
	R = c / 4.29140
	rt = 0.6766097 + t * ( 0.0200564 + t * ( 1.104259e-04 + t * ( -6.9698e-07 + t * 1.0031e-09 ) ) )
	A = 0.4215 - 0.003107 * t
	B = 1 + t * ( 0.03426 + t * 0.0004464 )
	C = p * ( 2.07e-5 + p * ( -6.37e-10 + p * 3.989e-15 ) )
	Rp = 1 + C / ( B + A * R )
	Rt = R / rt / Rp
	Rt5 = math.sqrt( Rt )
	t15 = t - 15
	dels = t15 / ( 1 + 0.0162 * t15 )
	sal =  ( 14.0941 + dels * -0.0375 ) + Rt5 * ( ( -7.0261 + dels *  0.0636 ) + Rt5 * ( (  2.7081 + dels *  -0.0144 ) ) )
	sal = ( 0.008 + dels * 0.0005 ) + Rt5 * ( ( -0.1692 + dels * -0.0056 ) + Rt5 * ( ( 25.3851 + dels * -0.0066 ) + Rt5 * sal ) )
	return sal

def calSG(s,t,p):
	t2 = t * t
	t3 = t2 * t
	t4 = t3 * t	A =   1.001685e-04 + t * ( -1.120083e-06 + t * 6.536332e-09 )
	A = 999.842594 + t * (  6.793952e-02 + t * ( -9.095290e-03 + t * A ) )
	B =   7.6438e-05 + t * ( -8.2467e-07 + t * 5.3875e-09 )
	B =   0.824493 + t * ( -4.0899e-03 + t * B )
	C =  -5.72466e-03 + t * ( 1.0227e-04 - t * 1.6546e-06 )
	d0 = A + s * (  B + C * math.sqrt(s) + 4.8314e-04 * s )
	E = 19652.21 + 148.4206 * t - 2.327105 * t2 + 1.360477e-2 * t3 - 5.155288e-5 * t4
	F = 54.6746 - 0.603459 * t + 1.09987e-2 * t2 - 6.1670e-5 * t3
	G = 7.944e-2 + 1.6483e-2 * t - 5.3009e-4 * t2
	H = 3.239908 + 1.43713e-3 * t + 1.16092e-4 * t2 - 5.77905e-7 * t3
	I = 2.2838e-3 - 1.0981e-5 * t - 1.6078e-6 * t2
	J = 1.91075e-4
	M = 8.50935e-5 - 6.12293e-6 * t + 5.2787e-8 * t2
	N = -9.9348e-7 + 2.0816e-8 * t + 9.1697e-10 * t2
	s1p5 = s * math.sqrt(s)
	pb = p/10
	K = (E + F*s + G*s1p5) + (H + I*s + J*s1p5) * pb + (M + N*s) * pb * pb
	d = d0 / (1 - pb/K)
	d = d / 1000 #g/cm3
	return d

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
	pressure = ((((D1 * SENS) / 2097152) - OFF) / 8192) / 10.0
	return pressure
def tempC():
        bus.write_byte(0x40,0xF3)
        time.sleep(.5)
        data= bus.read_i2c_block_data(0x40,0xE0,2)
        rt= data[0] * 256 + data[1]
        temp=((175.72 * rt)/65536)-46.85
        return temp

SL=(pres()+pres()+pres()+pres())/4
print "ok",SL
tpt=str(datetime.datetime.now())
fo=open(TXT,'a')
fo.write(tpt[0:19])
fo.write(',%.2f\n' %SL)
fo.close()

while True:
	cnly=raw_con()
	print cnly
	cnly=float(cnly)
	cfsal=cnly/10000
	temp=tempC()
	tempf=1.8 * temp + 32
	p=pres()
	calSal=salinity(cfsal,temp,p)
	print calSal
	cSl=float(calSal)
	cSG=calSG(cSl,temp,p)
	cSG=float(cSG)
	print cSG
	dpM=(SL-p)/(98.1* SG)
	dpFT=3.28084*dpM
	con=read_con()
	print con
	sgp=con.rfind('.')
	sgp=sgp-1
	SG=con[sgp: ]
	SG=float(SG)
	tpt=str(datetime.datetime.now())
	print 'Temperature %.3f'%temp, "C %.3f" %tempf, 'F'
	fo=open(TXT,'a')
	fo.write(tpt[0:19])
	fo.write(',%.2f' %p)
	fo.write(',%.3f' %dpM)
	fo.write(',%.3f' %dpFT)
	fo.write(',%.2f' %temp)
	fo.write(',%.2f,' %tempf)
	fo.write(con)
	fo.write(',%.1f' %cnly)
	fo.write(',%.2f' %cSl)
	fo.write(',%.3f\n' %cSG)
	fo.close()
	
