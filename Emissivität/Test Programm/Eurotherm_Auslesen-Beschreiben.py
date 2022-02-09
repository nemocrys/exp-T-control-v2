import serial
import time

test_on = False
dbg_on = False
delay = 0.5         # in s

portName = '/dev/ttyACM1' 
try:
    serial.Serial(port=portName)
except serial.SerialException:
    print ('Port ' + portName + ' not present')
    if not test_on:
        quit()                              # Sollte kein Test laufen und keine COM Stelle angesprochen werden, so wird das Programm beendet
        
if test_on == False:                          
    ser_py = serial.Serial(
        port = portName,
        baudrate = int(19200),
        parity = 'N',
        stopbits = int(1),
        bytesize = int(8),
        timeout = 2.0)          
else:
    print('Ein Test läuft gerade!')

def bcc(string):
    bcc_list = []
    for c in string:
        dec = ord(c)                  # https://stackoverflow.com/questions/3673428/convert-int-to-ascii-and-back-in-python
        bcc_list.append(dec)
    bcc_list.append(3)
    bcc = 0
    for item in bcc_list:
        bcc = (bcc^item)
    return chr(bcc)                    # https://stackoverflow.com/questions/3673428/convert-int-to-ascii-and-back-in-python

def send(write_befehl):   # Funktion um einen Befehl zu senden
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

        bcc_write = bcc(write_befehl)
        send = sEOT + str(0) + str(0) + str(3) + str(3) + sSTX + write_befehl + sETX + bcc_write
        ser_py.write(send.encode())
        time.sleep(delay)
        
        # Als Antwort beim schreiben soll das ACK = \x06 zurückkommen
        answer = ser_py.readline().decode() 
        if answer == sACK:
            print('Befehl erfolgreich gesendet!')
        if answer != "":    
            # Kontrolle ob alles OK:
            n = 0    # Die Schleife soll 10 mal durchgeführt werden 
            while answer == sNAK and n <= 10:                                         
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
                answer = ser_py.readline().decode()
                n += 1

            # im folgenden wird geschaut was das EE zurückgibt, eine Null bedeutet das kein Fehler vorliegt
            ser_py.write((sEOT+ str(0) + str(0) + str(3) + str(3) +'EE'+ sENQ).encode())
            time.sleep(delay)
            answer = ser_py.readline().decode()
            if answer[4:-2] != '0000':
                print(f'EE = {answer[4:-2]}')
        else:    
            print("Beim Schreiben kam ein Leerer String")

def read(read_befehl):            # Funktion zum Lesen eines Wertes + BCC Prüfung
    if test_on == True:
        print ('Testmodus aktiv!')
        quit()
    else:
        sEOT = '\x04'
        sENQ = '\x05'
            
        send = sEOT + str(0) + str(0) + str(3) + str(3) + read_befehl + sENQ
        ser_py.write(send.encode())
        time.sleep(delay)
        answer = ser_py.readline().decode()
        # print(answer)
        
        if answer != "":                # Leere Strings ignorieren und Null zurückgeben
            bcc_read = answer[-1]       # das letzte Zeichen in der Antwort ist das BCC
            #print(bcc_read)
            value = answer[3:-2]        # Antwort wird beschnitten (Steuerzeichen und BCC raus, nur der Wert bleibt)
            if len(read_befehl) == 3:   # Es kann sein das ein Befehl 3 Zeichen hat, wenn ein Regklkreis oder kanal gewählt werden muss!
                value = answer[4:-2]
            
            # Kontrolle BCC
            bcc_control = bcc(read_befehl + value)
            if bcc_control == bcc_read and dbg_on == True:
                print ('BCC Stimmt!')

            # Kontrolle ob alles OK:
            n = 0    # Die Schleife soll 10 mal durchgeführt werden 
            while bcc_control != bcc_read and n <= 10:                    # sollte der BCC nicht gleich sein, wird der Befehl nochmal gesendet
                print('BCC der Antwort ist falsch. Wiederhole Abfrage!')
                ser_py.write  (send.encode())
                time.sleep(delay)
                answer = ser_py.readline().decode()
                if answer != "":
                    bcc_read = answer[-1]       
                    value = answer[3:-2]
                    bcc_control = bcc(read_befehl + value) # Erneute Kontrolle
                else:
                    print('Beim wiederholten senden - Leerer Sring')
                n += 1

            # Kontrolle durch EE:
            ser_py.write((sEOT+ str(0) + str(0) + str(3) + str(3) +'EE'+ sENQ).encode())
            time.sleep(delay)
            answer = ser_py.readline().decode()
            #print(answer)
            if answer[4:-2] != '0000':
                print(f'EE = {answer[4:-2]}')
            return value
        return "Leerer String"

#send('OP50')
#send('11L20')

#befehl = '11H'                       # 1 wegen des Regelkreises
#nameHI = read(befehl)
#befehl = '11L'
#nameLI = read(befehl)
#print(f'Istwertgrenzen = max. {nameHI} °C bis min. {nameLI} °C')

#befehl = 'OP'
#name = read(befehl)
#print(name)

time.sleep(1)
'''
#ser_py.write('\x040033\x02SL30\x03"'.encode())
send = "\x040033EE\x05"
ser_py.write(send.encode())
time.sleep(delay)
try:
    answer = ser_py.readline().decode()
except:
    print("Decode Fehler!")
    answer = 0
if answer == "":
    answer = 0
print(f'Antwort Arduino: {answer}')


for n in range(0,10,1):
    send = '\x040033SL\x05'
    ser_py.write(send.encode())
    time.sleep(delay)
    answer = ser_py.readline().decode()
    if answer == "":
        answer = 0
    print(answer)
'''
#time.sleep(delay)
#ser_py.write('\x040033PV\x05'.encode())
#time.sleep(delay)
#answer = ser_py.readline()#.decode()
#print(answer)

one = read('SL')
send('SL100')
tree = read('SL')

print(f'Solltemperatur war vorher {one} °C und wurde auf {tree} °C gesetzt!')

iden = read('II')
print(f'Identität: {iden}')
iden = read('V0')
print(f'Version: {iden}')
iden = read('O1')
print(f'Identität: {iden}')
#for n in range(0,10,1):
#   one = read('PV')
#   print(one)