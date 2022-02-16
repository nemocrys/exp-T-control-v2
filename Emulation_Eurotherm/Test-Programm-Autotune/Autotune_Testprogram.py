# Selbstoptimierung:

import serial
import time
import datetime  
from tkinter import *                           
from tkinter import ttk
import numpy as np                              
import matplotlib.pyplot as plt                 

portName = '/dev/ttyUSB1' 
try:
    serial.Serial(port=portName)
except serial.SerialException:
    print ('Port ' + portName + ' not present')                          
                                
ser_py = serial.Serial(
    port = portName,
    baudrate = int(9600), # Emulation 19200 (8N1)
    parity = 'E',
    stopbits = int(1),
    bytesize = int(7),
    timeout = 2.0)          

def bcc(string):
    bcc_list = []
    for c in string:
        dec = ord(c)                 
        bcc_list.append(dec)
    bcc_list.append(3)
    bcc = 0
    for item in bcc_list:
        bcc = (bcc^item)
    return chr(bcc)

def send(write_befehl):   # Funktion um einen Befehl zu senden
    sEOT = '\x04'
    sETX = '\x03'
    sSTX = '\x02'
    sENQ = '\x05'
    sACK = '\x06'
    sNAK = '\x15'   

    delay = 0.1
    
    bcc_write = bcc(write_befehl)
    send = sEOT + str(0) + str(0) + str(3) + str(3) + sSTX + write_befehl + sETX + bcc_write
    ser_py.write(send.encode())
    time.sleep(delay)
            
    # Als Antwort beim schreiben soll das ACK = \x06 zurückkommen
    try:
        answer = ser_py.readline().decode()
    except:
        answer = ""
        print("Decode Fehler beim lesen! - send")
    if answer == sACK:
        print('Befehl erfolgreich gesendet!')
            
    # Kontrolle ob alles OK (NAK und ein Leerer String sorgen für Wiederholung):
    n = 0    # Die Schleife soll 10 mal durchgeführt werden 
    while (answer == sNAK or answer == "") and n <= 10:                                         
        # Fehler Grund ermitteln:
        print('Gerät antwortet mit NAK! Wiederhole senden.')
        # Nach einem NAK soll auch die Ursache des Fehlers geprintet werden
        ser_py.write((sEOT+ str(0) + str(0) + str(3) + str(3) +'EE'+ sENQ).encode())  
        time.sleep(delay)
        answer = ser_py.readline().decode()
        print(f'EE = {answer[4:-2]}')
        # Erneute Sendung:
        ser_py.write(send.encode())
        time.sleep(delay)
        try:
            answer = ser_py.readline().decode()
        except:
            answer = ""
            print("Erneuter Decode Fehler beim lesen! - send")
        n += 1

        # im folgenden wird geschaut was das EE zurückgibt, eine Null bedeutet das kein Fehler vorliegt
        ser_py.write((sEOT+ str(0) + str(0) + str(3) + str(3) +'EE'+ sENQ).encode())
        time.sleep(delay)
        answer = ser_py.readline().decode()
        if answer[4:-2] != '0000':
            print(f'EE = {answer[4:-2]}')
            
def read(read_befehl, schnitt, delay):            # Funktion zum Lesen eines Wertes + BCC Prüfung
    sEOT = '\x04'
    sENQ = '\x05'
            
    send = sEOT + str(0) + str(0) + str(3) + str(3) + read_befehl + sENQ
    schnitt.write(send.encode())
    time.sleep(delay)
    answer = schnitt.readline().decode()
        
    if answer != "":                # Leere Strings ignorieren und Null zurückgeben
        bcc_read = answer[-1]       # das letzte Zeichen in der Antwort ist das BCC
        value = answer[3:-2]        # Antwort wird beschnitten (Steuerzeichen und BCC raus, nur der Wert bleibt)
        if len(read_befehl) == 3:   # Es kann sein das ein Befehl 3 Zeichen hat, wenn ein Regklkreis oder kanal gewählt werden muss!
            value = answer[4:-2]
            
        # Kontrolle BCC
        bcc_control = bcc(read_befehl + value)
        if bcc_control == bcc_read:
            print ('BCC Stimmt!')

        # Kontrolle ob alles OK:
        n = 0    # Die Schleife soll 10 mal durchgeführt werden 
        while bcc_control != bcc_read and n <= 10:                    # sollte der BCC nicht gleich sein, wird der Befehl nochmal gesendet
            print('BCC der Antwort ist falsch. Wiederhole Abfrage!')
            schnitt.write  (send.encode())
            time.sleep(delay)
            answer = schnitt.readline().decode()
            if answer != "":
                bcc_read = answer[-1]       
                value = answer[3:-2]
                bcc_control = bcc(read_befehl + value) # Erneute Kontrolle
            else:
                print('Beim wiederholten senden - Leerer Sring')
            n += 1

        # Kontrolle durch EE:
        schnitt.write((sEOT+ str(0) + str(0) + str(3) + str(3) +'EE'+ sENQ).encode())
        time.sleep(delay)
        answer = schnitt.readline().decode()
        if answer[4:-2] != '0000':
            print(f'EE = {answer[4:-2]}')
        return value
    return "Leerer String"

def fenster_GUI():
    # Definitionen der Aktionen der Knöpfe:
    def button_action_1():                  # Start Knopf
        anweisungs_label_1.config(Start())  

    def button_action_3():                  # Beenden Knopf
        info_label.config(Stop())
        quit()
    
    def task():
        if nStart == True:                         
            get_Measurment()
            fenster.after(1000, task) 
        else:
            fenster.after(10, task)
    
    # X -Button wird verriegelt
    def disable_event():
        pass
    
    # Ein Fenster erstellen:
    fenster = Tk()
    # Den Fenstertitle erstellen:
    fenster.title("Selbstoptiemierung")

    # Buttons:
    Start_button_1 = Button(fenster, text="Start", command=button_action_1)                                
    exit_button = ttk.Button(fenster, text="Beenden", command=button_action_3) 

    # Label:
    anweisungs_label_1 = Label(fenster, text="Start \nHeizung/Messung!")
    info_label = Label(fenster, text="Schließen und Stoppen")

    # Fenstergröße definieren:
    fenster.geometry("200x200")
    
    #### Start und Beenden
    anweisungs_label_1.place(x = 30, y = 30, width=120, height=35)    # Start
    Start_button_1.place(x = 60, y = 70, width=70, height=30)
    info_label.place(x = 10, y = 110, width=200, height=30)           # Beenden
    exit_button.place(x = 60, y = 140, width=70, height=40)
    
    fenster.protocol("WM_DELETE_WINDOW", disable_event)               
    fenster.after(10, task) 
    fenster.mainloop()  

def get_Measurment():
    sEOT = '\x04'
    sETX = '\x03'
    sSTX = '\x02'
    sENQ = '\x05'
    
    time_actual = datetime.datetime.now()
    dt = (time_actual - time_start).total_seconds()
    
    eurotemp = read('PV', ser_py, 0.1)
    euroPow = read('OP', ser_py, 0.1)
    
    listTiRe.append(dt)
    listTempPt.append(float(eurotemp))
    listPowEu.append(float(euroPow))
    
    # Arduino:
    bcc_write = bcc('OP' + euroPow)
    send = sEOT + str(0) + str(0) + str(3) + str(3) + sSTX + 'OP' + euroPow + sETX + bcc_write
    schnitt_emu.write(send.encode())
    
    arduPow = read('OP', schnitt_emu, 0.1)
    listPowAr.append(float(arduPow))
    
    # Autoscaling:
    AutoScroll(ax1, 2, 2)            # Temperatur
    AutoScroll(ax2, 2, 2)            # Leistung in %
                        
    # Grafiken - Heizer
    Update_Graph(line1, listTempPt)                
    Update_Graph(line2, listPowEu)                 
    Update_Graph(line3, listPowAr)
        
    figure.canvas.draw()            
    figure.canvas.flush_events()

def Update_Graph(Kurve, Update_Y):                                                                                   # Funktion für das Updaten der Kurven
    updated = Update_Y
    Kurve.set_xdata(listTiRe)               
    Kurve.set_ydata(updated)

def AutoScroll(Graph, minusY, plusY):                                      
    Graph.axis('auto')                                  
    Graph.relim()                                       
    ymin, ymax = Graph.get_ylim()                       
    Graph.set_ylim(ymin - minusY, ymax + plusY)         
    Graph.set_xlim(0,listTiRe[-1] + 10)                            

def Start():
    global figure, ax1, ax2, line1, line2, line3, nStart
    global listTiRe, listTempPt, listPowEu, listPowAr, time_start
    
    if nStart == False:
        time_start = datetime.datetime.now()
        listTiRe = []
        listTempPt = []
        listPowEu = []
        listPowAr = []
        
        nStart = True
        # Grafik Erzeugung:
        plt.ion()
        figure = plt.figure(figsize=(10,5))                                                 
        figure.suptitle("Selbstoptiemierung Überwachung",fontsize=25)                 
            
        # Regelsensor:
        ax1 = plt.subplot(121)                                                              
        line1, = ax1.plot(listTiRe, listTempPt, 'r', label='Pt100 Eurotherm')                                                            
        plt.ylabel("Temperatur Kontrollsensor in °C",fontsize=12)
        plt.xlabel("Zeit in s",fontsize=12)
        plt.legend(loc='best') 
        plt.grid()
        
        ax2 = plt.subplot(122)                                                              
        line2, = ax2.plot(listTiRe, listTempPt, 'b', label='Output Eurotherm')
        line3, = ax2.plot(listTiRe, listTempPt, 'g', label='Output Arduino') 
        plt.ylabel("Ausgangsleistung in %",fontsize=12)
        plt.xlabel("Zeit in s",fontsize=12)
        plt.legend(loc='best') 
        plt.grid()
            
def Stop():
    if nStart == True:
        P = read('XP', ser_py, 0.1)
        I = read('TI', ser_py, 0.1)
        D = read('TD', ser_py, 0.1)
        Cut_Max = read('HB', ser_py, 0.1)
        Cut_Min = read('LB', ser_py, 0.1)
        print(f'XP = {P} & TI = {I} & TD = {D}')
        print(f'Cutback: Max = {Cut_Max} & Min = {Cut_Min}')
        quit()

# Vorab:
#send('SL50')
nStart = False

portNameS = '/dev/ttyACM0'
try:
    serial.Serial(port=portNameS)
except serial.SerialException:
    print ('Port ' + portNameS + ' not present')
schnitt_emu = serial.Serial(
    port = portNameS,
    baudrate = int(19200),
    parity = 'N',
    stopbits = int(1),
    bytesize = int(8),
    timeout = 2.0)
print("Emulation/Arduino initialisiert!\n")

fenster_GUI()
