#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Ultraschallbursts mit einer Trägerfrequenz von 40 kHz und einer Bandbreite
#von 200 Hz werden simuliert und zeitlich verschoben in das 10 ms lange
#Echosignal kopiert.
#Auf dieses Mehrfachechosignal wird eine Quadraturdemodulation angewendet.
#Der I und Q Output davon wird ausgegeben.
#
#S. Mack, 24.10.21


import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, gausspulse
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


order = 3 # Ordung des Filters 3
fs = 1e6   # Abtastrate der Signalwerte bzw. des Filters 1e6 Hz
cutoff = 4e3  # cut off frequency in Hz 4 kHz

FREQ = 40.0e3 # Trägerfrequenz 40 kHz
delay_sig_2 = 0.000502 # Delay zweiter Burst
atten_sig_2 = 0.7 # Dämpfung zweiter Burst
delay_sig_3 = 0.001507 # Delay zweiter Burst
atten_sig_3 = 0.5 # Dämpfung zweiter Burst

times = np.linspace(-0.005, 0.005, 2 * 5000, endpoint=False) # Zeitraum von +/- 5 ms
# Trägerfrequenz 40 kHz, Bandbreite 0.05*40 kHz = 200 Hz
burst_sig_1 = gausspulse(times, fc=40000, bw=0.05) 
burst_sig_2 = atten_sig_2 * gausspulse(times - delay_sig_2, fc=40000, bw=0.05) 
burst_sig_3 = atten_sig_3 * gausspulse(times - delay_sig_3, fc=40000, bw=0.05) 
cos = np.cos(2*np.pi*FREQ*times)
sine = np.sin(2*np.pi*FREQ*times)

burst = burst_sig_1 + burst_sig_2 + burst_sig_3

sig_i = burst * cos
sig_q = burst * -sine

sig_i_filt = butter_lowpass_filter(sig_i, cutoff, fs, order) + 0.0001
# Offset damit Rauschen um 0 kein Phasensprung verursacht
sig_q_filt = butter_lowpass_filter(sig_q, cutoff, fs, order)

sig_amp = np.sqrt(np.square(sig_i_filt)+np.square(sig_q_filt))
#sig_phase = np.arctan(sig_q_filt/sig_i_filt)
sig_phase = np.arctan2(sig_q_filt,sig_i_filt)

fig, (ax0, ax1, ax2) = plt.subplots(nrows=3)

formatter1 = EngFormatter(unit='s')
ax0.xaxis.set_major_formatter(formatter1)
ax0.plot(times, sig_amp)
ax0.set_ylabel('Amlitude (a.u.)')
ax0.set_xlabel('Time (s)')
ax1.xaxis.set_major_formatter(formatter1)
ax1.plot(times, sig_phase)
ax1.set_ylabel('Phase (rad)')
ax1.set_xlabel('Time (s)')
ax2.xaxis.set_major_formatter(formatter1)
ax2.plot(times, burst)
#ax2.plot(times, sig_q_filt)
ax2.set_ylabel('Signal (a.u.)')
ax2.set_xlabel('Time (s)')
plt.tight_layout()

plt.show()