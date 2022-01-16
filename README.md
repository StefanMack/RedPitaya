# RedPitaya
Mess- und Sensortechnik mit dem Red Pitaya

## Ultraschallmessungen und -signalverarbeitung
Im Verzeichnis `RedPitayaUltraschall` wird die Verwendung des Red Pitaya vorgestellt, um das anloge Echosignal eines HC-SR04 Ultraschallsensors auszulesen und auszuwerten.
Die Arbeiten hierzu sind in einem Jupyter Notebook zusammengefasst.  

Verwenden Sie zum Anschauen dieses Notebooks den Viewer "nbviewer" [über diesen Link](https://nbviewer.org/github/StefanMack/RedPitaya/blob/main/RedPitayaUltraschall/RedPitayaUltraschall.ipynb).  

## Analog-Digital-Wandlung mit Hilfe des SCPI-Servers
Im Verzeichnis Sampling finden sich Quellcodes, um im Praktikum Messtechnik mit dem Red Pitaya über dessen SCPI-Server Signale abzutasten. Hierbei sollen die Studis das Eingangssignal oder die Abtastrate ändern und dabei das Abtastergebnis beobachten.  
In einem nächsten Schritt sollen die Studis erkennen, wann das Abtasttheorem erfüllt ist, und dann mit einer sin(x)/x Interpolation das Eingangssignal rekonstruieren.
