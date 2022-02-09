### Bibliotheken:
import yaml
import numpy as np                              # Bibliothek für das Arbeiten mit Vektoren usw.
import matplotlib.pyplot as plt                 # Bibliothek für die Ausgabe von Graphen                                  

import random

import heizer                         
import pyrometer   
import adafruit                      

# Parameterliste einlesen
config_file = 'config_Parameter.yml'  
with open(config_file) as fi:   
    config = yaml.safe_load(fi)

# Variablen voreinstellen:
test = False
dbg = False
pyrometer.truth_pyro(test, dbg)
heizer.truth_heiz(test, dbg)
adafruit.truth_pt100(test, dbg)

# Pyrometer KW Initialisieren:
pyroKW = {}
for name, data in config['Pyrometer_KW'].items():
         pyKW = pyrometer.PyrometerKW(name, **data)
         pyroKW.update({name: pyKW})

# Pyrometer LW Initialisieren:
pyroLW = {}
array_data = config['Pyrometer_LW']['Schnittstelle']
schnittstelle_LW = pyrometer.Array(**array_data)
for name, data in config['Pyrometer_LW']['Geraete'].items():
        pyLW = pyrometer.PyrometerLW(name, schnittstelle=schnittstelle_LW.ser_py, **data)
        pyroLW.update({name: pyLW})

# Heizer auswählen:
heizer_wahl = config['Heizer']['Auswahl']['String']
heizer_config = config['Heizer']['Schnittstelle']
if heizer_wahl == 'Eurotherm':
    heizer_config.update(config["Eurotherm"])
    heizer = heizer.HeizerEurotherm(**heizer_config)
elif heizer_wahl == 'IKA':
    heizer = heizer.HeizerPlatte(**heizer_config)
else:
    print(f'Der Heizer "{heizer_wahl}" exestiert nicht in diesem Programm')
    quit()

# Adafruit Initialisieren:
pt_sam = {}
for name, data in config['Pt100'].items():
    pt100 = adafruit.Adafruit(name, **data)
    pt_sam.update({name: pt100})

# Hauptprogramm:
n_list = []
temp_heiz = []

# Grafik erzeugen:
plt.ion()
figure = plt.figure(figsize=(12,9))                                                 
figure.suptitle("Temperatur + Emissionsgrad Messungen",fontsize=25)                 

# Temperatur:
ax1 = plt.subplot(211)
line, = ax1.plot(n_list, temp_heiz, 'r', label=heizer.type)
for name, Pyro in pyroLW.items():
    Pyro.grafik_T(ax1, n_list)
for name, Pyro in pyroKW.items():
    Pyro.grafik_T(ax1, n_list)
for name, pt in pt_sam.items():
    pt.grafik(ax1, n_list) 
plt.ylabel("Temperatur in °C",fontsize=12)
plt.legend(loc='best') 
plt.grid()

# Emissionsgrad:
ax2 = plt.subplot(212)
for name, Pyro in pyroLW.items():
    Pyro.grafik_E(ax2, n_list)
for name, Pyro in pyroKW.items():
    Pyro.grafik_E(ax2, n_list)
plt.ylabel("Emissionsgrad in %",fontsize=12)
plt.legend(loc='best') 
plt.grid()

e = [100, 90, 80, 70, 60, 50, 40, 30, 20]   # Emissionsgrad setzen Test (Listen Elemente werden später zufällig aufgerufen)

for n in range(0, 100):
    # Listen werden geupdatet:
    for name, Pyro in pyroLW.items():
        Pyro.update_list_T()
    for name, Pyro in pyroKW.items():
        Pyro.update_list_T()
    for name, pt in pt_sam.items():
        pt.update_list()

    for name, Pyro in pyroLW.items():
        Pyro.update_list_E()
    for name, Pyro in pyroKW.items():
        Pyro.update_list_E()

    temp_heiz.append(heizer.get_istwert())
    n_list.append(n)                            # x-Liste

    # Autoscroll:
    ax1.axis('auto')                                
    ax1.relim()                                     
    ymin, ymax = ax1.get_ylim()                     
    ax1.set_ylim(ymin - 5, ymax + 5)                
    ax1.set_xlim(0,n_list[-1] + 10)

    ax2.axis('auto')                                
    ax2.relim()                                    
    ymin, ymax = ax2.get_ylim()                     
    ax2.set_ylim(ymin - 5, ymax + 5)                
    ax2.set_xlim(0,n_list[-1] + 10)

    # Kurven aktualisieren:
    line.set_xdata(n_list)               
    line.set_ydata(temp_heiz)

    for name, Pyro in pyroLW.items():
        Pyro.update_T(n_list)
    for name, Pyro in pyroKW.items():
        Pyro.update_T(n_list)
    for name, pt in pt_sam.items():
        pt.update(n_list)

    for name, Pyro in pyroLW.items():
        Pyro.update_E(n_list)
    for name, Pyro in pyroKW.items():
        Pyro.update_E(n_list)

    # Grafik aktualisieren:    
    figure.canvas.draw()            
    figure.canvas.flush_events()        

    # Zufallsgenerator für die Emissionswerte:
    for name, Pyro in pyroLW.items():
        Pyro.write_pyro_para('e', random.choice(e))
    for name, Pyro in pyroKW.items():
        Pyro.write_pyro_para('e', random.choice(e))

