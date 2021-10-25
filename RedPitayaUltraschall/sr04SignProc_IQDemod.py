#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#An dem analogen Echosignal des Ultraschallsensors HC-SR04 wird eine
#Quadraturdemodulation durchgeführt.
#Der Signalverlauf wird über eine Textdatei eingelesen.
#Durch Multiplikation mit einem Kosinus bwzw. Sinus und anschließender
#Tiefpassfilterung wird die I und die Q-Komponente des Signals berechnet.
#Im Plot wird die Amplitude des Echoverlaufs dargestellt.
# !! Vorher den SCPI-Server des REd Pitaya starten !!
#
#S. Mack, 24.10.21


import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from matplotlib.ticker import EngFormatter

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

DECIMATION = 64 # Einstellung Decimation am Red Pitaya

order = 3 # Ordung des Filters 3
fs = 125e6 / DECIMATION   # Abtastrate der Signalwerte bzw. des Filters
cutoff = 4e3  # cut off frequency in Hz 4 kHz

FILE_NAME = 'us_echo_wall.txt' # mit Red Pitaya aufgenommenes Echosignal
FREQ = 40.0e3 # Sendefrequenz des HC-SR04 (gemessen)

times,voltages = np.loadtxt(FILE_NAME)
cos = 0.1*np.cos(2*np.pi*FREQ*times)
sine = 0.1*np.sin(2*np.pi*FREQ*times)

sig_i = voltages * cos
sig_q = voltages * -sine

sig_i_filt = butter_lowpass_filter(sig_i, cutoff, fs, order)+ 0.0001
# Offset damit Rauschen um 0 kein Phasensprung verursacht
sig_q_filt = butter_lowpass_filter(sig_q, cutoff, fs, order)

sig_amp = np.sqrt(np.square(sig_i_filt)+np.square(sig_q_filt))
sig_phase = np.arctan2(sig_q_filt,sig_i_filt)

fig, (ax0, ax1, ax2) = plt.subplots(nrows=3)
formatter1 = EngFormatter(unit='s')
ax0.xaxis.set_major_formatter(formatter1)
ax0.plot(times, sig_amp)
ax0.set_ylabel('Amlitude (a.u.)')
ax0.set_xlabel('Time (s)')
ax1.xaxis.set_major_formatter(formatter1)
ax1.plot(times, sig_phase)
ax1.set_ylabel('Phase (a.u.)')
ax1.set_xlabel('Time (s)')
ax2.xaxis.set_major_formatter(formatter1)
ax2.plot(times, voltages)
ax2.set_ylabel('Signal (a.u.)')
ax2.set_xlabel('Time (s)')
plt.tight_layout()

plt.show()