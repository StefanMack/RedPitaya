#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Auslesen anloges Echosignal eines HC-SR04 Ultraschallsensors.
#Der Sensor wird am Eingang Trig über ein 100 µs langen Puls (3,3 V)
#über GPIO DIO0_N getriggert.
#Der Pin DIO0_p (EXT.FRIG.) wird als externer Trigger verwendet und nach
#einem 1:1 Spannungsteiler (Sensor hat 5 V Logik!) mit dem Pin GPIO DIO0_N
#verbunden.
#Getriggert wird auf die fallende Flanke und einer Schwelle von 1 V.
#Damit die Samples erst nach dem Störecho beginnen, wird ein Delay
#von 16000 Samples eingestellt.
#Der Dezimierungsfaktor beträgt 64, d.h. die Samplingrate beträgt 125 MS/s / 64
#= 1,953125 MS/s
# !! Vorher den SCPI-Server des REd Pitaya starten !!
#
#S. Mack, 21.10.21

import time
import redpitaya_scpi as scpi
import numpy as np
import matplotlib.pyplot as plot

FILE_NAME = 'us_echo.txt'
DECIMATION = 64
SampPeriod = DECIMATION / 125e6  

#rp_s = scpi.scpi('169.254.110.216')
rp_s = scpi.scpi('169.254.61.8')

period = 0.1 # seconds
buff_string = ''

rp_s.tx_txt('DIG:PIN:DIR OUT,DIO0_N')
rp_s.tx_txt('DIG:PIN  DIO0_N,'+ str(0))
rp_s.tx_txt('ACQ:RST')
rp_s.tx_txt('ACQ:DATA:FORMAT ASCII')
rp_s.tx_txt('ACQ:DATA:UNITS VOLTS')
rp_s.tx_txt('ACQ:DEC ' + str(DECIMATION))
rp_s.tx_txt('ACQ:TRIG:LEVEL 1')
rp_s.tx_txt('ACQ:TRIG:DLY 16000')
rp_s.tx_txt('ACQ:START')
rp_s.tx_txt('ACQ:TRIG EXT_NE')

time.sleep(period)
rp_s.tx_txt('DIG:PIN  DIO0_N,' + str(1))
time.sleep(0.0001)
rp_s.tx_txt('DIG:PIN  DIO0_N,' + str(0))

while 1:
    rp_s.tx_txt('ACQ:TRIG:STAT?')
    if rp_s.rx_txt() == 'TD':
        break

rp_s.tx_txt('ACQ:SOUR1:DATA?')
buff_string = rp_s.rx_txt()
buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')

voltages = (np.asarray(buff_string)).astype(float)
times = np.arange(len(voltages)) * SampPeriod

meas_file = open(FILE_NAME,'w')
np.savetxt(FILE_NAME, (times,voltages))
meas_file.close()

plot.plot(times*1000, voltages)
plot.ylabel('Voltage (V)')
plot.xlabel('Time (ms)')
plot.show()