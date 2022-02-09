# Bibliotheken:
import serial
import random
import time

# Globale Variablen:
global test_on, dbg_on, delay

# Test und Debug Funktion (bzw. Werte) vorbereiten:
test_on = False
dbg_on = False

def truth_heiz(test, dbg):
    global test_on, dbg_on

    test_on = test
    dbg_on = dbg

# Für Emulation Eurotherm eingefügt, zwischen dem Senden und Abfragen eines Wertes kurz warten!
def serial_delay(time_delay):
    global delay
    
    delay = time_delay


class Heizer:  
    def print_type(self):   # Gibt an welcher Heizer genutzt wird
        print(self.type)

    def init_heizer(self):   # initialisiert die Schnittelle des Heizers               
        portName = self.com
        try:
            serial.Serial(port=portName)
        except serial.SerialException:
            print ('Port ' + portName + ' not present')
            if not test_on:
                quit()                              # Sollte kein Test laufen und keine COM Stelle angesprochen werden, so wird das Programm beendet
        
        if test_on == False:                          
            ser_py = serial.Serial(
                port = portName,
                baudrate = int(self.bd),
                parity = self.parity,
                stopbits = int(self.stopbits),
                bytesize = int(self.bytesize),
                timeout = 2.0)
            self.ser_py = ser_py
            self.print_type()
            time.sleep(1)   # Kurzes Delay, damit die Emulation richtig sich vorbereiten kann
            print(f'Heizer: {self.get_name()} bereit!')       
            if dbg_on == True:
                print(repr(self.ser_py) )            
        else:
            print('Ein Test läuft gerade!')

    
class HeizerPlatte(Heizer):                                     # IKA Heizplatte
    def __init__(self, com, bd, parity, stopbits, bytesize):
        self.type = "Heizplatte"
        self.com = com
        self.bd = bd                                # Baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.init_heizer()

    def get_name(self):                 # Auslesen des Geräte Namens
        if test_on == False:
            if dbg_on:
                print ('Sending to ' + self.com + ' den Befehl IN_NAME\\r\\n')
            self.ser_py.write(('IN_NAME' +'\r\n').encode())                    # Sendet Befehl an Heizplatte, \r\n == CR LF
            name = self.read()
        return name

    def get_istwert(self):             # Befehl zur Temperatur Ausgabe des Temperaturfühlers übergeben (Erfragt die Temperatur des externen Messfühlers)
        if test_on == False:
            if dbg_on:
                print ('Sending to ' + self.com + ' den Befehl IN_PV_1\\r\\n')
            self.ser_py.write(('IN_PV_1' +'\r\n').encode())
            tempF = self.read().split(' ')[0]
            
            # Kontrolle ob alles OK:
            n = 0    # Die Schleife soll 10 mal durchgeführt werden 
            while (tempF == '' or tempF == '0') and n <= 10:                                        
                print('Gerät sendet bei Istwert Leeren String oder Null. Wiederhole senden!')
                self.ser_py.write(('IN_PV_1' +'\r\n').encode())
                tempF = self.read().split(' ')[0] 
                n += 1    
        else:
            tempF = random.uniform(0,100)                            
        return float(tempF)                                          

    def get_TempHeizplat(self):        # Befehl zur Temperatur Ausgabe der Heizplatte übergeben (Erfragt Temperatur der Heizplatte)
        if test_on == False:
            if dbg_on:
                print ('Sending to ' + self.com + ' den Befehl IN_PV_2\\r\\n')
            self.ser_py.write(('IN_PV_2' +'\r\n').encode())
            tempP = self.read().split(' ')[0]
            
            # Kontrolle ob alles OK:
            n = 0    # Die Schleife soll 10 mal durchgeführt werden 
            while (tempP == '' or tempP == '0') and n <= 10:                                       
                print('Gerät sendet bei Heizplattentemperatur Leeren String oder Null. Wiederhole senden!')
                self.ser_py.write(('IN_PV_2' +'\r\n').encode())
                tempP = self.read().split(' ')[0]  
                n += 1  
        else:
            tempP = random.uniform(0,100)                                     
        return float(tempP)

    def read(self):                     # Mit der Funktion kann man sich die Antwort anzeigen lassen!!
        if test_on == True:
            print ('Testmodus aktiv!')
            quit()
        else:
            st = ''
            back = self.ser_py.readline().decode()                                 # Die Antwort wird komplett ausgelesen
            if dbg_on == True:    
                print('Reading From ' + self.com + ': ' + repr(back))                                           
            st = back.replace('\r\n', '')               
            return st                                                               

    def change_SollTemp(self, Solltemp):    # Befehl zum ändern der Solltemperatur wird der Heizplatte übergeben (auf Display der Hp kann man das sehen)
        if test_on == False:
            self.ser_py.write(('OUT_SP_1 ' + Solltemp +'\r\n').encode())
            if dbg_on:
                print ('Sending to ' + self.com + f' den Befehl OUT_SP_1 {Solltemp}\\r\\n')
                self.get_SollTemp()
                self.get_SaveTemp()

    def get_SollTemp(self):                 # Befehl - Erfragen der Solltemperatur
        if test_on == False:
            if dbg_on:
                print ('Sending to ' + self.com + ' den Befehl IN_SP_1\\r\\n')
            self.ser_py.write(('IN_SP_1' + '\r\n').encode())
        tempSoll = self.read().split(' ')[0] 
        print (f'Die Solltemperatur ist gerade {tempSoll} °C groß.')
        return tempSoll

    def get_SaveTemp(self):                # Befehl - Erfragen der Sicherheitstemperatur
        if test_on == False:
                if dbg_on:
                    print ('Sending to ' + self.com + ' den Befehl IN_SP_3\\r\\n')
                self.ser_py.write(('IN_SP_3 ' + '\r\n').encode())
        SaveTemp = self.read().split(' ')[0] 
        print(f'Die Sicherheitstemperatur ist gerade {SaveTemp} °C groß.')

    def start_heizung(self):              # Befehl zum Starten der Heizplatte wird übergeben 
        if test_on == False:
                if dbg_on:
                    print ('Sending to ' + self.com + ' den Befehl START_1\\r\\n')
                self.ser_py.write(('START_1' + '\r\n').encode())
                print('Heizvorgang Startet, Heizung An!')

    def stop_heizung(self):              # Befehl zum Stoppen der Heizplatte wird übergeben
        if test_on == False:
            if dbg_on:
                print ('Sending to ' + self.com + ' den Befehl STOP_1\\r\\n')
            self.ser_py.write(('STOP_1' + '\r\n').encode())
            print('Heizvorgang Zuende, Heizung Aus!')


class HeizerEurotherm(Heizer):
    def __init__(self, gid, uid, kp, ti, td, com, bd, parity, stopbits, bytesize):
        self.type = "Eurotherm"
        self.com = com
        self.bd = bd                                
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.gid = gid
        self.uid = uid
        self.kp = kp
        self.ti = ti
        self.td = td
        
        self.init_heizer()
        self.change_PID()
        self.get_setting()
         
    def get_name(self):                     # Ausgabe des Instrumenten Namen (bzw. Identität)
        befehl = 'II'
        name = self.read(befehl)
        return name

    def get_setting(self):                  # Auslesen und ausgeben von bestimmten Werten zur anfänglichen Kontrolle der Einstellungen!
        befehl = 'V0'
        name = self.read(befehl)
        print(f'Softwareversion = {name}')
        # Sollwertgrenze:
        befehl = 'HS'
        nameHS = self.read(befehl)
        befehl = 'LS'
        nameLS = self.read(befehl)
        print(f'Sollwertgrenzen = max. {nameHS} °C bis min. {nameLS} °C')
        # Istwertgrenze (Prozessgröße):
        befehl = '11H'                       # 1 wegen des Regelkreises
        nameHI = self.read(befehl)
        befehl = '11L'
        nameLI = self.read(befehl)
        print(f'Istwertgrenzen = max. {nameHI} °C bis min. {nameLI} °C')
        # PID:
        befehl = 'XP'
        namePG = self.read(befehl)
        befehl = 'TI'
        nameIG = self.read(befehl)
        befehl = 'TD'
        nameDG = self.read(befehl)
        print(f'PID-Parameter = xp = {namePG} (P-Glied), Ti = {nameIG} (I-Glied) und Td = {nameDG} (D-Glied)')
        print()

    def get_istwert(self):                  # Holt den Istwert 
        if test_on == False:
            befehl = 'PV'
            tempIst = self.read(befehl)
        else:
            tempIst = random.uniform(0,100)                            
        return float(tempIst) 

    def get_SollTemp(self):                 # Holt die Solltemperatur
        befehl = 'SL'
        tempSoll = self.read(befehl)
        return tempSoll

    def change_SollTemp(self, Solltemp):    # Überschreibt den alten Sollwert mit dem neuen
        if test_on == False:
            befehl = 'SL' + Solltemp
            self.send(befehl)

    def change_PID(self):                   # PID Parameter
        if test_on == False:
            befehl = 'XP' + str(self.kp)
            self.send(befehl)
            befehl = 'TI' + str(self.ti)
            self.send(befehl)
            befehl = 'TD' + str(self.td)
            self.send(befehl)
    
    def get_power_OUT(self):                # Leistung abfragen
        if test_on == False:
            befehl = 'O1'
            euroPow = self.read(befehl)
        else:
            euroPow = random.uniform(0,100)                            
        return float(euroPow)

    def bcc(self, string):
        bcc_list = []
        for c in string:
            dec = ord(c)                  # https://stackoverflow.com/questions/3673428/convert-int-to-ascii-and-back-in-python
            bcc_list.append(dec)
        bcc_list.append(3)
        bcc = 0
        for item in bcc_list:
            bcc = (bcc^item)
        return chr(bcc)                    # https://stackoverflow.com/questions/3673428/convert-int-to-ascii-and-back-in-python

        '''
        In der Funktion "bcc" wird der BCC Wert (Prüfsumme) bestimmt. Diese Funktion bestimmt 
        sowohl den BCC zum senden und den BCC von der Geräteantwort beim lesen. 
        Der Befehl (zum Schreiben oder Antwort) wird Charakter für Charakter von ASCII in 
        eine Dezimal Zahl zerlegt und dann an die Liste "bcc_list" angehangen. Das Abschluss 
        Zeichen für beide Möglichkeiten ist das ETX welches in DEC 3 entspricht und auch an die 
        Liste angehangen wird. Darauf hin wird die Prüfsumme über XOR berechnet und wieder als ASCII zurückgegeben.  
        '''

    def read(self, read_befehl):            # Funktion zum Lesen eines Wertes + BCC Prüfung
        if test_on == True:
            print ('Testmodus aktiv!')
            quit()
        else:
            sEOT = '\x04'
            sENQ = '\x05'
            
            send = sEOT + str(self.gid) + str(self.gid) + str(self.uid) + str(self.uid) + read_befehl + sENQ
            self.ser_py.write(send.encode())
            if dbg_on == True:
                print ('Sending to ' + self.com + f' den Befehl [EOT]{self.gid}{self.gid}{self.uid}{self.uid}{read_befehl}[ETX]')
            time.sleep(delay)
            answer = self.ser_py.readline().decode()
            
            if answer != "":                # Leere Strings ignorieren und Null zurückgeben
                bcc_read = answer[-1]       # das letzte Zeichen in der Antwort ist das BCC
                value = answer[3:-2]        # Antwort wird beschnitten (Steuerzeichen und BCC raus, nur der Wert bleibt)
                if len(read_befehl) == 3:   # Es kann sein das ein Befehl 3 Zeichen hat, wenn ein Regklkreis oder kanal gewählt werden muss!
                    value = answer[4:-2]
                
                # Kontrolle BCC
                bcc_control = self.bcc(read_befehl + value)
                if bcc_control == bcc_read and dbg_on == True:
                    print ('BCC Stimmt!')
                
                # Kontrolle ob alles OK:
                n = 0    # Die Schleife soll 10 mal durchgeführt werden 
                while bcc_control != bcc_read and n <= 10:                    # sollte der BCC nicht gleich sein, wird der Befehl nochmal gesendet
                    print('BCC der Antwort ist falsch. Wiederhole Abfrage!')
                    self.ser_py.write(send.encode())
                    time.sleep(delay)
                    answer = self.ser_py.readline().decode()
                    if answer != "":
                        bcc_read = answer[-1]       
                        value = answer[3:-2]
                        bcc_control = bcc(read_befehl + value) # Erneute Kontrolle
                    n += 1

                # Kontrolle durch EE:
                self.ser_py.write((sEOT+ str(self.gid) + str(self.gid) + str(self.uid) + str(self.uid) +'EE'+ sENQ).encode())
                if dbg_on == True:
                    print ('Sending to ' + self.com + f' den Befehl [EOT]{self.gid}{self.gid}{self.uid}{self.uid}EE[ETX]')
                time.sleep(delay)
                answer = self.ser_py.readline().decode()
                if answer[4:-2] != '0000':
                    print(f'EE = {answer[4:-2]}')
                return value
            return 0    # Sollte Kein Wert zurückgegeben werden, so wird eine Null ausgegeben!

    def send(self, write_befehl):   # Funktion um einen Befehl zu senden
        if test_on == True:
            print ('Testmodus aktiv!')
            quit()
        else:
            sEOT = '\x04'
            sETX = '\x03'
            sSTX = '\x02'
            sENQ = '\x05'
            sACK = '\x06'
            sNAK = '\x15'   

            bcc_write = self.bcc(write_befehl)
            send = sEOT + str(self.gid) + str(self.gid) + str(self.uid) + str(self.uid) + sSTX + write_befehl + sETX + bcc_write
            self.ser_py.write(send.encode())
            if dbg_on == True:
                bcc_hex = hex(ord(bcc_write)).replace('0','\\')
                print ('Sending to ' + self.com + f' den Befehl [EOT]{self.gid}{self.gid}{self.uid}{self.uid}[STX]{write_befehl}[ETX]<{bcc_hex}>')
            time.sleep(delay)
            
            # Als Antwort beim schreiben soll das ACK = \x06 zurückkommen
            answer = self.ser_py.readline().decode() 
            if answer == sACK:
                print('Befehl erfolgreich gesendet!')
            
            # Kontrolle ob alles OK (NAK und ein Leerer String sorgen für Wiederholung):
            n = 0    # Die Schleife soll 10 mal durchgeführt werden 
            while (answer == sNAK or answer == "") and n <= 10:                                         
                # Fehler Grund ermitteln:
                print('Gerät antwortet mit NAK! Wiederhole senden.')
                # Nach einem NAK soll auch die Ursache des Fehlers geprintet werden
                self.ser_py.write((sEOT+ str(self.gid) + str(self.gid) + str(self.uid) + str(self.uid) +'EE'+ sENQ).encode())  
                time.sleep(delay)
                answer = self.ser_py.readline().decode()
                print(f'EE = {answer[4:-2]}')
                # Erneute Sendung:
                self.ser_py.write(send.encode())
                time.sleep(delay)
                answer = self.ser_py.readline().decode()
                n += 1

            # im folgenden wird geschaut was das EE zurückgibt, eine Null bedeutet das kein Fehler vorliegt
            self.ser_py.write((sEOT+ str(self.gid) + str(self.gid) + str(self.uid) + str(self.uid) +'EE'+ sENQ).encode())
            if dbg_on == True:
                print ('Sending to ' + self.com + f' den Befehl [EOT]{self.gid}{self.gid}{self.uid}{self.uid}EE[ETX]')
            time.sleep(delay)
            answer = self.ser_py.readline().decode()
            if answer[4:-2] != '0000':
                print(f'EE = {answer[4:-2]}')