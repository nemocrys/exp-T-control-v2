# Bibliotheken:
import serial
import random
import numpy as np                              
import matplotlib.pyplot as plt                 

# Test und Debug Funktion (bzw. Werte) vorbereiten
global test_on, dbg_on

test_on = False
dbg_on = False

def truth_pyro(test, dbg):
    global test_on, dbg_on

    test_on = test
    dbg_on = dbg


class Pyrometer:
    # Temperatur Grafik:
    def update_list_T(self):
        self.listT.append(self.read_pyro())

    def grafik_T(self, graph, x_list):
        self.lineT, = graph.plot(x_list, self.listT, label=self.name)

    def update_T(self, x_list):
        self.lineT.set_xdata(x_list)               
        self.lineT.set_ydata(self.listT)

    # Emissionsgrad Grafik:
    def update_list_E(self):
        self.listE.append(self.get_pyro_para('e'))

    def grafik_E(self, graph, x_list):
        self.lineE, = graph.plot(x_list, self.listE, label=self.name)

    def update_E(self, x_list):
        self.lineE.set_xdata(x_list)               
        self.lineE.set_ydata(self.listE)

    # Initialisierung:
    def init_pyro(self):
        portName = self.com                                                        
        try:
            serial.Serial(port=portName)
        except serial.SerialException:
            print ('Port ' + portName + ' not present')
            if not test_on:
                quit()
        
        if not test_on:
            ser_py_ = serial.Serial(
                port = portName,
                baudrate = int(self.bd),
                parity = self.parity,
                stopbits = int(self.stopbits),
                bytesize = int(self.bytesize),            
                timeout = 0.1)
            self.ser_py = ser_py_
        else:                       # Das nochmal ansehen, test läuft derzeitig nicht ohne!!
            self.ser_py = None

    # Bestimmung der Werte für die Emissionsgrad Anpassung:
    def anpassung(self, e_Aktuell, e_Drauf):
        self.e_py = e_Aktuell
        self.e_Drauf = e_Drauf


# Die Langwelligen Pyrometer hängen an dem selben Array mit der selben Schnittstelle
class Array(Pyrometer):
    def __init__(self, com, bd, parity, stopbits, bytesize):
        self.com = com
        self.bd = bd
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.init_pyro()


class PyrometerKW(Pyrometer):
    def __init__(self, name, com, bd, parity, stopbits, bytesize, emis, trans, t90):
        self.name = name
        self.com = com
        self.bd = bd                                # Baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.e = emis
        self.t = trans
        self.t90 = t90
        self.listT = []
        self.listE = []
        
        self.init_pyro()
        self.config_pyro()
        
        
    def config_pyro(self):                                          # Gerät Konfigurieren 
        if not test_on:
            print ('Pyrometer ', self.name, ' : ', self.get_ID())
            self.write_pilot(False)                                   # Laser vorerst ausschalten
            self.write_pyro_para('e', str(self.e))                    # Emissionsgrad
            self.write_pyro_para('t', str(self.t))                    # Transmissonsgrad   
            self.write_pyro_para('t90', self.t90)
            fokus = self.get_focus().replace('\r','')[4:]
            print(f'Derzeitig eingestellter Pyrometer Fokus = {fokus} mm')

    def get_ID(self):                                               # Geräte ID erfragen
        p = '00na\r'
        self.ser_py.write(p.encode())
        pyro_id = self.ser_py.readline().decode()
        return (pyro_id)

    def get_focus(self):                                            # Fokus des Messfleckes (Messfleckabstand) erfragen
        p = '00df\r'
        self.ser_py.write(p.encode())                                           
        pyro_focus = self.ser_py.readline().decode()
        return (pyro_focus)

    def get_OK(self):
        answer = self.ser_py.readline().decode()
        print ('Pyrometer ', self.name, ' = ', answer)
        return answer

    def write_pyro_para(self, para, str_val):                       # Pyrometer Parameter einstellen
        if para == 'e':                                                             # Emission (e)
            val = '%05.1f' % float(str_val)
            str_val = str(val).replace('.', '')    
            p = '00em' + str_val + '\r'
        if para == 't':                                                             # Transmission (t)                      
            val = '%05.1f' % float(str_val)
            str_val = str(val).replace('.', '')    
            p = '00et' + str_val + '\r'
        if para == 't90':                                                           # Erfassungszeit (t90)
            p = '00ez' + str_val + '\r'
        if not test_on:
            if dbg_on:
                print ('Sending to ' + self.ser_py.port +': ', p.encode())
            self.ser_py.write(p.encode())                                             # Übergibt den jeweiligen Befehl an das Pyrometer
            check = self.get_OK()                                                     # Erfragt ob der Befehl eingegangen ist
            
            # Kontrolle ob alles OK:
            n = 0    # Die Schleife soll 10 mal durchgeführt werden 
            while 'no' in check and n <= 10:                                                    
                print(f'KW - Schreiben des Wertes für {para} fehlgeschlagen. Wiederhole senden! Befehl = {p}')
                self.ser_py.write(p.encode())                                         
                check = self.get_OK()
                n += 1
            
            # Liest den gerade geänderten Wert aus und printed das Ergebnis:
            answer = self.get_pyro_para(para)                                         
            if para == 'e':
                print ('Pyrometer ', self.name, ' emission = ', answer)
            if para == 't':
                print ('Pyrometer ', self.name, ' transmission = ', answer)     
            if para == 't90':
                print ('Pyrometer ', self.name, ' t90 = ', answer)     
        else:
            print ('Pyro ' + self.name + ' parameter: ', p)

    def get_pyro_para(self, para):                                  # Pyrometer Parameter erfragen
        ### e = emission, t = transmission, t90 = Erfassungszeit
        if para == 'e':
            p = '00em\r'
        if para == 't':
            p = '00et\r'
        if para == 't90':
            p = '00ez\r'
        if not test_on:
            if dbg_on:
                print ('Sending to ' + self.com +': ', p.encode())
            self.ser_py.write(p.encode())
            answer = self.ser_py.readline().decode()
            
            # Kontrolle ob alles OK:
            n = 0    # Die Schleife soll 10 mal durchgeführt werden 
            while 'no' in answer and n <= 10:                                             
                print(f'KW - Gerät sendet bei Abfrage des Wertes für {para} ein "no". Wiederhole senden! Befehl = {p}')
                self.ser_py.write(p.encode())
                answer = self.ser_py.readline().decode()
                n += 1

            if para == 'e' or para == 't':                                    # Bei Emissionsgrad und Transmissionsgrad werden so sofort die Werte in einen float umgewandelt
                answer = answer[:-1]
                l = len(answer)
                answer = answer[:l-1] + '.' + answer[l-1:]
                answer = float(answer)  
        else:                                                                 
            print ('Pyro ' + self.name + ' parameter: ', p)
            answer = random.uniform(30,40)
        return (answer)

    def read_pyro(self):                                                    # Istwert der Temperatur erfragen
        p = '00ms\r'                                                          
        if not test_on:
            if dbg_on:
                print ('Sending to ' + self.com + ': ', p.encode())
            self.ser_py.write(p.encode())
            temp = self.ser_py.readline().decode()
            
            # Kontrolle ob alles OK:
            n = 0    # Die Schleife soll 10 mal durchgeführt werden 
            while 'no' in temp and n <= 10:                                             
                print(f'KW - Bei Frage für Istwert - Antwort vom Gerät ist "no". Wiederhole senden! Befehl = {p}')
                self.ser_py.write(p.encode())
                temp = self.ser_py.readline().decode()
                n += 1
            
            temp = temp[:-1]                                                  # Abschlusszeichen entfernen
            l = len(temp)
            temp = temp[:l-1] + '.' + temp[l-1:]                              # Zusammensetzung zur Zahl, Punkt (Komma) einfügen (Rückgabe z.B. 00740 = 74,0 bzw 74.0)
            if dbg_on:
                print ('Reading from ' + self.com + ': ', float(temp))
        else:
            temp = random.uniform(20,22)                                      
        return (float(temp)) 

    def write_pilot(self, state):                                       # Laser einstellen
        print ('Pilot-'+ self.name + ' : ' + str(state))
        if not test_on:
            if state:
                p = '00la1\r'                                               # Laser Ein
            else:
                p = '00la0\r'                                               # Laser Aus
            if dbg_on:
                print ('Sending to ' + self.com +': ', p.encode()) 
            self.ser_py.write(p.encode())
            check = self.get_OK()        


class PyrometerLW(Pyrometer):
    def __init__(self, name, emis, array_num, schnittstelle):
        self.name = name
        self.e = emis
        self.i = array_num
        self.listT = []
        self.listE = []
        
        self.ser_py = schnittstelle   
        self.config_pyro()
        
    def config_pyro(self):                                              # Gerät Konfigurieren 
        if not test_on:
            print ('Pyrometer Array', self.name, ' : ', self.get_ID())
            self.write_pyro_para('e', str(self.e))                          # Emissionsgrad

    def get_ID(self):                                                   # Geräte ID erfragen
        p = '00A' + str(self.i) + 'sn\r'
        self.ser_py.write(p.encode())
        pyro_head_id = self.ser_py.readline().decode()
        return (pyro_head_id)

    def Get_nb_of_head(self):                                           # Anzahl der Sensoren an der Box    
        if not test_on:
            p = '00oc\r'
            self.ser_py.write(p.encode())
            pyro_head_nb = self.ser_py.readline().decode().replace('\r','')
            return (pyro_head_nb)
        else:
            return 0

    def get_OK(self):
        answer = self.ser_py.readline().decode()
        print ('Pyrometer Array', str(self.i), ' = ', answer)
        return answer

    def write_pyro_para(self, para, str_val):                           # Pyrometer Parameter einstellen
        if para == 'e':
            val = '%05.1f' % float(str_val)
            str_val = str(val).replace('.', '')    
            p = '00A' + str(self.i) + 'em' + str_val + '\r'
        if para == 't90':
            p = '00A' + str(self.i) + 'ez' + str_val + '\r'
        if not test_on:
            if dbg_on:
                print ('Sending to head ' + str(self.i) +': ', p.encode())
            self.ser_py.write(p.encode())
            check = self.get_OK()
            
            # Kontrolle ob alles OK:
            n = 0    # Die Schleife soll 10 mal durchgeführt werden 
            while 'no' in check and n <= 10:                                                    
                print(f'Lw {self.i} - Bekommt "no" beim senden von {para}-Wert zurück. Wiederhole senden! Befehl = {p}')
                self.ser_py.write(p.encode())
                check = self.get_OK()
                n += 1
            
            answer = self.get_pyro_para(para)
            if para == 'e':
                print ('Pyrometer array head ', str(self.i), ' emission = ', answer)
            if para == 't90':
                print ('Pyrometer array head ', str(self.i), ' t90 = ', answer)     
        else:
            print ('Pyrometer array head ' +str(self.i) + ' parameter: ', p)

    def get_pyro_para(self, para):                                      # Pyrometer Parameter auslesen
        ### e = emission, t = transmission
        if para == 'e':
            p = '00A' + str(self.i) + 'em\r'
        if para == 't90':
            p = '00A' + str(self.i) + 'ez\r'
        if not test_on:
            if dbg_on:
                print ('Sending to pyrometer head ' + str(self.i) + ': ', p.encode())
            self.ser_py.write(p.encode())
            answer = self.ser_py.readline().decode()
            
            # Kontrolle ob alles OK:
            n = 0    # Die Schleife soll 10 mal durchgeführt werden 
            while 'no' in answer and n <= 10:                                                   
                print(f'Lw {self.i} - Bekommt "no" beim abfragen des {para}-Wertes zurück. Wiederhole senden! Befehl = {p}')
                self.ser_py.write(p.encode())
                answer = self.ser_py.readline().decode()
                n += 1
            
            if para == 'e':                                                         # Bei Emissionsgrad werden so sofort die Werte in einen float umgewandelt
                answer = answer[:-1]
                l = len(answer)
                answer = answer[:l-1] + '.' + answer[l-1:]
                answer = float(answer)  
        else:                                                                      
            print ('Pyrometer array head ' + str(self.i) + ' parameter: ', p)    
            answer = random.uniform(30,40)
        return (answer)   

    def read_pyro(self):                                                # Istwert der Temperatur auslesen
        p = '00A' + str(self.i) + 'ms\r'
        if not test_on:
            if dbg_on:
                print ('Sending to head ' + str(self.i) + ': ' , p.encode())
            self.ser_py.write(p.encode())
            temp = self.ser_py.readline().decode()
            
            # Kontrolle ob alles OK:
            n = 0    # Die Schleife soll 10 mal durchgeführt werden 
            while 'no' in temp and n <= 10:                                             
                print(f'Lw {self.i} - Bekommt "no" beim abfragen des Istwertes zurück. Wiederhole senden! Befehl = {p}')
                self.ser_py.write(p.encode())
                temp = self.ser_py.readline().decode()
                n += 1
            
            temp = temp[:-1]
            l = len(temp)
            temp = temp[:l-1] + '.' + temp[l-1:]
            if dbg_on:
                print ('Reading from head ' + str(self.i) + ': ', float(temp))
        else:
            temp = random.uniform(20,22)
        return (float(temp))