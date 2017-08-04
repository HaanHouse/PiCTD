# PiCTD
Using a Raspberry Pi Zero W to record conductivity, tempurature and depth (CTD)
with python 2.7 

Idea inspired by Dr. Andrew Thaler
[OpenCTD](https://github.com/OceanographyforEveryone/OpenCTD)and 
[Oceanography for Everyone](http://us11.campaign-archive1.com/home/?u=bbe1875ee67aa199087ef6805&id=9127339d31)
lots of good info there. 

I'll get this setup better soon. 

The pressure sensor [MS5803-14BA](https://github.com/ControlEverythingCommunity/MS5803-14BA)

set-up and calibration of [Atlas-Scientific Conductivity](https://github.com/AtlasScientific/Raspberry-Pi-sample-code)

[Adafruit's](http://adafruit.com) temperature probe [DS18B20 setup](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/ds18b20)


once you have those setup my
python 2.7 file should work 

and my .txt .csv files from tests. file naming is 'CTD'+YY+MM+DD+HH+MM+'.txt'

just added python file for SI7051 i2c temp prob will be added into new PiCTD
learned some writing this so hopefully have CTD.py running in python 3
