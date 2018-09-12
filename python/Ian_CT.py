import time
import io
import fcntl
import math

file_read = io.open("/dev/i2c-1", "rb", buffering=0)
file_write = io.open("/dev/i2c-1", "wb", buffering=0)

I2C_SLAVE = 0x703

def read_con():
	fcntl.ioctl(file_read, I2C_SLAVE, 100)  #atlas scientific conductivity prob address 100
	fcntl.ioctl(file_write, I2C_SLAVE, 100)
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
	fcntl.ioctl(file_read, I2C_SLAVE, 100)  #atlas scientific conductivity prob address 100
	fcntl.ioctl(file_write, I2C_SLAVE, 100)
        # reads a specified number of bytes from I2C, then parses and displays the result
        Ts="T,25\00"
        file_write.write(Ts)
        time.sleep(.3)
        file_write.write("R\00")
        time.sleep(.7)
        res = file_read.read(31)         # read from the board
        res=res.replace('\x00','')
	conly=res.find(',')              #if only doing conductivity comment out whole line and
        res=res[1:conly]                 #remove 'conly' from this line
        return res

def RTD():
	fcntl.ioctl(file_read, I2C_SLAVE, 102)  #atlas scientific temp prob address 102
	fcntl.ioctl(file_write, I2C_SLAVE, 102)
        # reads a specified number of bytes from I2C, then parses and displays the result
        file_write.write("R\00")
        time.sleep(.7)
        res = file_read.read(31)         # read from the board
        res=res.replace('\x00','')
        res=res[1:]
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

while True:
	temp=RTD()
	print "temp =",temp
	c=read_con()                     #comment out whole line if not doing salinity on EC EZO
	print "temp corrected con =",c   #comment out whole line if not doing salinity on EC EZO
	uc=raw_con()
	print "No temp correction =",uc
	s=salinity(uc,temp,0)
	print "calculated salinity =",s
	time.sleep(4)


