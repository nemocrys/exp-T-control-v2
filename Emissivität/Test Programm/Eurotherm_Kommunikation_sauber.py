import serial
import time

portName = "/dev/ttyUSB1"

ser_py = serial.Serial(
    port = portName,
    baudrate = int(9600),
    parity = 'E',
    stopbits = int(1),
    bytesize = int(7),
    timeout = 2.0)

sEOT = '\x04'
sETX = '\x03'
sSTX = '\x02'
sENQ = '\x05'
sACK = '\x06'
sNAK = '\x15'

gid = 0
uid = 3

write_befehl = 'SL190.0'
read_befehl = 'II'

def bcc(string):
    bcc_list = []
    for c in string:
        dec = ord(c)                                # https://stackoverflow.com/questions/3673428/convert-int-to-ascii-and-back-in-python
        bcc_list.append(dec)
    bcc_list.append(3)
    bcc = 0
    for item in bcc_list:
        bcc = (bcc^item)
    return chr(bcc)                                  # https://stackoverflow.com/questions/3673428/convert-int-to-ascii-and-back-in-python

#################################################################################
# Schreiben:
bcc_write = bcc(write_befehl)
send = sEOT + str(gid) + str(gid) + str(uid) + str(uid) + sSTX + write_befehl + sETX + bcc_write
ser_py.write(send.encode())
answer = ser_py.readline().decode() 
if answer == sACK:
    print('Befehl erfolgreich gesendet!')

ser_py.write((sEOT+ str(gid) + str(gid) + str(uid) + str(uid) +'EE'+ sENQ).encode())
answer = ser_py.readline().decode()
print(f'EE = {answer[4:-2]}')
#################################################################################
print('')
#################################################################################
# Lesen:
send = sEOT + str(gid) + str(gid) + str(uid) + str(uid) + read_befehl + sENQ
ser_py.write(send.encode())
answer = ser_py.readline().decode() 

bcc_read = answer[-1]
answer = answer[3:-2]
print(answer)

bcc_control = bcc(read_befehl + answer)
if bcc_control == bcc_read:
    print ('BCC Stimmt!')

ser_py.write((sEOT+ str(gid) + str(gid) + str(uid) + str(uid) +'EE'+ sENQ).encode())
answer = ser_py.readline().decode()
print(f'EE = {answer[4:-2]}')

'''
Befehle:
Schreiben/Lesen:
SL - Sollwert ändern
XP - Proportional Band
TI - Integral Zeit
TD - Derivative Zeit (D-Glied)
HB - Cutback High
LB - Cutback Low
II - Geräte Identität
VO - Software Version
IM - Instrument Mode

Read-Only:
EE - Fehler Meldung des vorrigen Befehls (0 = alles in Ordnung, 2 = BCC Error, 8 = Grenzen üerschritten,
     1F = UID fehlt oder ist falsch, 22 = Parameter nicht konfiguriert)
PV - Istwert lesen
SP - Arbeitssollwert lesen
HS - Obere Sollwertgrenze
LS - Untere Sollwertgrenze
'''

