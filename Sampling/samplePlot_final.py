#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#+++Testprogramm zum Erklären Aliasing-Effekt im Messtechnikpraktikum+++
#Red Pitaya wird z.B. mit 10 kHz Sinussignal 4 Vpp von Funktionsgenerator versorgt.
#Studis sollen schrittweise den Dezimierungsfaktor der Abtastrate erhöhen und
#beobachten, wie sich das abgetastete Signal verändert.
#Solange das Samplingtheorem noch erfüllt ist, kann in einem zweiten Schritt
#z.B. das abgetastete Signal sin(x)/interpoliert werden, um Amplitude und Phase
#des Eingangssignals trotz geringer Abtastrate zu rekonstruieren.
#
#++Bemerkung 1:
#Sobald 'ACQ:START' gesendet wurde, beginnt das Abtasten und Füllen des Ringspeichers.
#'ACQ:TRIG:DLY 8192' verschiebt den Triggerzeitpunkt an den Beginn der Abtastreihe.
#Mit 'ACQ:TRIG NOW' wird das Triggerereignis (unabhängig vom Signalverlauf) gesetzt.
#Nachfolgend muss wegen des Delays noch der ganze Ringspeicher mit seinen 16384
#Datenwerten gefüllt werden. Dafür ist bei geringen effektiven Abtastraten eine
#lange Zeit nötig.
#
#++Bemerkung 2:
#Ein zuverlässiges Triggern auf das Signal z.B. bei 0 V und positiver Flanke
#'ACQ:TRIG CH1_PE' funktioniert nur bei höheren Abtastraten. Dann muss mit einer
#While-Schleife zuerst gewartet werden, bis die Triggerbedingung erfüllt wurde.    
#
#!!Beim Red Pitaya muss über dessen Webinterface der SCPI-Server aktiviert werden!!
#
#S. Mack, 16.1.22

import redpitaya_scpi as scpi
import matplotlib.pyplot as plt
import numpy as np
import time


DEC_EXP = 8 # Exponent 0,1,...,16 für Decimation Faktor
TIME_SPAN = 0.002  # Zeitdauer Sampling in Sekunden
BUFF_SIZE = 16384 # Größe / Anzahl Samples im Ringspeicher
SAMP_RATE = 125e6 # Abtastrate (ohne Dezimierung)

dec_fac = int(2**DEC_EXP) # Dezinierungsfaktor
samp_period = dec_fac / SAMP_RATE  
num_dat_pts = min(int(TIME_SPAN / samp_period + 1),BUFF_SIZE) # Maximal 16384 Samples
buff_fill_time = BUFF_SIZE * samp_period # Zeit um den Puffer mit 16384 Samples zu fuellen

print('Dezimierungsfaktor: {}, Abtastperiode: {} s, Abtastrate: {}, Datenpunkte: {}, Abtastzeit komplett: {} s'
      .format(dec_fac, samp_period, int(SAMP_RATE/dec_fac), num_dat_pts, num_dat_pts * samp_period))
print('Dauer Abtastung Red Pitaya für 16384 Samples: {} s'.format(buff_fill_time))
if (buff_fill_time > 1.0):
    print('ACHTUNG: Wegen langsamer effektiver Abtastrate >1 s Wartezeit um Ringspeicher mit Samples zu füllen!')

rp_s = scpi.scpi.rst
rp_s = scpi.scpi('192.168.178.33')

rp_s.tx_txt('ACQ:RST') # Mögliches Abtasten stoppen und Defaultwerte dafür aufrufen 
rp_s.tx_txt(('ACQ:DEC ' + str(dec_fac))) # Dezimierungsfaktor einstellen
rp_s.tx_txt('ACQ:SOUR1:GAIN HV') # Eingangsspannungsbereich LV = +-1 V, HV = +-20 V
rp_s.tx_txt('ACQ:DATA:FORMAT ASCII')
rp_s.tx_txt('ACQ:DATA:UNITS VOLTS')
#rp_s.tx_txt('ACQ:TRIG:LEV 0') # Triggerlevel setzen (nur relevant ohne 'ACQ:TRIG NOW')
# Triggerzeitpunkt im Puffer schieben (positiv = nach links, min -8191 ... max 8192)
rp_s.tx_txt('ACQ:TRIG:DLY 8192') 
rp_s.tx_txt('ACQ:START') # Abtastvorgang starten

## ----Option 2: Software Trigger auf steigende Flanke CH1 > funktioniert bei geringen Abtastraten nicht.
#rp_s.tx_txt('ACQ:TRIG CH1_PE') 
#while 1:
#    rp_s.tx_txt('ACQ:TRIG:STAT?')
#    if rp_s.rx_txt() == 'TD':
#        break

# ----Option 1: Triggerereignis setzen
time.sleep(0.1) # Puffer vor Triggerereignis füllen (bei Delay 0 z.B.: samp_period*BUFF_SIZE/2)
rp_s.tx_txt('ACQ:TRIG NOW')   
time.sleep(buff_fill_time + 0.1) # Posttriggersamples alle lesen (bei Delay 0: samp_period*BUFF_SIZE/2)

rp_s.tx_txt('ACQ:SOUR1:DATA?') # kompletten Puffer (16384 Samples im Ringspeicher) auslesen 
buff = rp_s.rx_txt()
        
# Formatierungszeichen entfernen und nur die ersten num_dat_pts Elemente ausschneiden
buff_string = (buff.strip('{}\n\r').replace("  ", "").split(','))[0:num_dat_pts] # 

voltages = (np.asarray(buff_string)).astype(float) # y-Werte
times = np.arange(len(voltages)) * samp_period # x-Werte

fig, ax = plt.subplots(figsize=(20, 6))
ax.plot(times*1000, voltages, ':o', linewidth=1, markersize=2) # x-Werte in Millisekunden
ax.grid(linestyle=':')
ax.set_ylabel('Voltage (V)')
ax.set_xlabel('Time (ms)')

rp_s.tx_txt('ACQ:STOP')
rp_s.close()
