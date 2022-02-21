## 1 . Befehle    

### 1.1. Eurotherm   
Die Kommunikation mit den Eurotherm Geräten erfolgt über die Serielle Schnittstelle. Die Baudrate und die Adresse des Gerätes kann über die Geräte herausgefunden werden. Bisher wurde es nur geschafft den 905P über die Schnittstelle an zusprechen. Dafür musste der in Kapitel 3 gezeigte Brückenschalter umgesteckt werden. Wie man die beiden Werte sowie das Kommunikationsprotokoll findet und einstellt siehe Kapitel 6.1.

Im Dokument "EIBYSINC Beispiel.pdf" kann man sehen wie die Befehle aufgebaut sind und im Dokument "eurothermCOM.pdf" kann man ein Beispiel finden. 

Anders als bei den anderen Geräten brauch man hier Steuerzeichen wie z.B. EOT, STX und ENQ.

Im folgenden wird es hier auch kurz gezeigt und erläutert (vergleiche mit den Quellen für Eurotherm - EIBYSINC Beispiel.pdf und eurothermCOM.pdf (S. 32 - 35))

**Lesebefehl**:   
EOT GID GID UID UID C1 C2 ENQ
- EOT und ENQ - Steuerzeichen 
- GID und UID - bilden die Adresse die man wie oben erklärt finden kann, sie kommen zweimal vor da sie für das Gerät validiert werden müssen     
GID = Gruppennummer   (group number)   
UID = Einheitennummer (unit number)
- C1 und C2 - Mnemonic Befehl (aus den Mnemonic Listen zu entnehmen)

Das EI BISINC arbeitet mit den Mnemonic Befehlen.

Antwort vom Gerät:    
STX C1 C2 D1 D2 D3 D4 D5 ETX BCC
- STX und ETX - Steuerzeichen
- BCC - Prüfsumme
- D1 - D5 - ausgelesener Wert

**Schreibbefehl**:    
EOT GID GID UID UID STX C1 C2 D1 D2 D3 D4 D5 ETX BCC

Antwort vom Gerät:   
NAK oder ACK
- bei ACK ist alles richtig eingegangen
- bei NAK ist ein Fehler aufgetreten

In welchem Format die Werte gesendet werden ist egal, es kann wie im Beispiel eurothermCOM.pdf (S. 32 - 35) komplett in Hex-Format sein oder wie in meinem Programm als Mischmasch aus ASCII und HEX.

**BCC Erklärt**:    
Sowohl beim schrieben und lesen ist der BCC Wert vorhanden. Beim Lesen eines Wertes bekommt man ihn als Antwort als Prüfwert zurück. Beim schreiben muss man diesen berechnen und an das Gerät senden.    
Der BCC Wert wird über das exklusiv Oder kurz XOR berechnet. Jedes Zeichen nach STX bis einschließlich ETX (Schreiben und Lesen) wird dort hinein berechnet.

Das Programm **heizer.py** berechnet in der Klasse Eurotherm den Wert selbst, sowohl beim Schreiben als auch beim Lesen. Im folgenden Beispiel wird kurz alles erklärt gezeigt.

**Beispiel Lesen:**   
Im Programm wird der zu sendende String wie folgt aussehen:   
\x040033PV\x05

Das \x04 steht für EOT und \x05 für ENQ. PV fragt den aktuellen Istwert ab. Durch die Funktion encode aus der serial Bibliothek ist das Übersendungsformat egal, hexadezimale Zahlen müssen nur das "\x" haben. 

Das Gerät könnte folgendes zurückgeben:   
\x02PV1.8\x03"    
(um es anzeigen zu können wurde die Funktion decode kurz auskommentiert, die Steuerzeichen bzw. bestimmte ASCII Symbole können nicht angezeigt werden)    
Am Ende des Strings kann man ein " sehen, dieses Zeichen ist der BCC übersetzt in ein ASCII Zeichen. 

**Berechnung**:   
P XOR V XOR 1 XOR . XOR 8 XOR \x03 = "   
Natürlich muss man alles in das selbe Format übergeben. Um es besser zu zeigen werden die Zeichen in Binär übersetzt! Bei XOR bekommt man immer dann eine 1 wenn die Vergleichspartner nicht gleich sind, heißt:    
0 XOR 0 und 1 XOR 1 = 0, 0 XOR 1 und 1 XOR 0 = 1   

P XOR V =  01010000 XOR 01010110 = 00000110   
00000110 XOR 1 = 00000110 XOR 00110001 = 00110111   
00110111 XOR . = 00110111 XOR 00101110 = 00011001   
00011001 XOR 8 = 00011001 XOR 00111000 = 00100001    
00100001 XOR \x03 = 00100001 XOR 00000011 = 00100010   
00100010 = "  

Wie man sehen kann bestimmt das Programm den Wert richtig.

Zur Berechnung wurde die Tabelle auf der folgenden Internetseite genutzt:  
https://www.rapidtables.com/code/text/ascii-table.html 

**Beispiel Schreiben:**    
Ein Beispiel sieht wie folgt aus:   
\x040033\x02SL120.0\x031
    
Die 1 ist in dem Fall der BCC:    
01010011 XOR    
01001100 =    
00011111 XOR    
00110001 =    
00101110 XOR   
00110010 =   
00011100 XOR    
00110000 =    
00101100 XOR   
00101110 =   
00000010 XOR    
00110000 =     
00110010 XOR    
00000011 =    
00110001 = 31h = 1 (ASCII)   

Die Antwort wird \x06 für ACK und \x15 für NAK sein! 

**Funktion Erklärt**:    
Die Funktion **bcc(self, string)** ist in der Klasse Eurotherm im Programm **heizer.py** für die Berechnung des BCC Wertes zuständig. Der String der der Berechnung übergeben wird besteht nur aus dem Mnemonic Zeichen und beim schreiben auch noch aus der Zahl.

1. Erzeugung einer leeren Liste für die Dezimal Zahlen
    - in der Funktion werden alle Zeichen in Dezimal Zahlen überführt
2. die einzelnen Zeichen des Strings werden umgewandelt
3. am Ende wird eine 3 (\x03 = ETX = 3 (Dec)) an die Liste gehangen die das Streuerzeichen ETX symbolisiert
4. die Variable bcc wird auf 0 gesetzt (etwas XOR 0 bleibt das selbe)
5. die einzelnen Listen Elemente (einzelnen Zeichen) werden über das XOR Schritt für Schritt verrechnet (wie im Beispiel Schreiben)
6. der berechnete BCC wird als ASCII an den Sende Befehl übermittelt

**Genutzte Befehle (Mnemonic):**
1. Werte Lesen:
<pre>
    * Identifikation        -->     II
    * Fehlermeldung         -->     EE 
    * Isttemperatur         -->     PV
    * Solltemperatur        -->     SL 
    * Software Version      -->     V0      
    * Sollwertgrenze Max    -->     HS      
    * Sollwertgrenze Min    -->     LS  
    * Istwertgrenze Max     -->     1H
    * Istwertgrenze Min     -->     1L    
    * Ausgangsleistung      -->     OP
    * Max. Ausgangsleistung -->     HO 
    PID-Parameter:     
    * Proportional Band     -->     XP     
    * Integral Zeit         -->     TI      
    * Ableitungszeit        -->     TD
</pre>
2. Werte Schreiben:
<pre>
    * Solltemperatur        -->     SL 
    * Max. Ausgangsleistung -->     HO 
    PID-Parameter:  
    * Proportional Band     -->     XP     
    * Integral Zeit         -->     TI      
    * Ableitungszeit        -->     TD                   
</pre>  

Bei 1H und 1L muss man den Befehl wie folgt senden: 11H und 11L. So werden diese Werte für den Regelkreis 1 ausgelesen (diese Befehle sind auch Read Only). 

### 1.2. Heizplatte IKA

Wie bei dem Eurotherm Gerät wird die Schnittstelle über die python Bibliothek serial eingestellt und somit die Kommunikation über RS232 bereitgemacht. 

Als Quelle dient hier das Readme (deutsch) aus dem Praktikumsprogramm von Seite https://github.com/nemocrys/exp-T-control.   

Zu dem kann dies im Manual, zu finden auf der Internetseite https://www.ika.com/de/Produkte-Lab-Eq/Magnetruehrer-Heizruehrer-Laborruehrer-Ruehrer-csp-188/C-MAG-HS-7-control-Downloads-cpdl-20002694/ nachgelesen werden. 

Um die Befehle richtig senden zu können benötigt man hier im Anschluss des Befehls ein \r\n, was auch bei den Funktionen schon dargestellt ist.  
        
1. Werte vom Gerät Erfragen:        
<pre>
    * Gerätenamen                       -->     IN_NAME\r\n
    * Isttemperatur (Externer Fühler)   -->     IN_PV_1\r\n 
    * Isttemperatur (Heizplatte)        -->     IN_PV_2\r\n
    * Solltemperatur                    -->     IN_SP_1\r\n 
    * Sicherheitstemperatur             -->     IN_SP_3\r\n
</pre>
2. Werte am Gerät ändern oder an das Gerät übergeben:
<pre>
    * Solltemperatur                    -->     OUT_SP_1 x\r\n                      
        Integer --> Bereich: x = 0 ... 500 °C       (Eingabe ohne Einheit)
    * Stoppe die Heizung                -->     STOP_1\r\n
    * Starte die Heizung                -->     START_1\r\n
</pre>     

### 1.3. Pyrometer
Auch die Pyrometer werden über eine RS232 Schnittstelle angesteuert. Der Unterschied zwischen den Langwelligen und Kurzwelligen Pyrometer ist, dass das langwellige Pyrometer nur eine Schnittstelle brauch und mehrere Pyrometer über eine Nummer steuert. 
#### 1.3.1. Kurzwellige Pyrometer
Die Befehle sind alle in dem Manual (siehe Quellen) zu finden. Alle Befehle brauchen am Ende ein \r um gesendet zu werden.  

Als Antwort bei einem Befehl sendet das Gerät ein ok zurück, sollte ein no zurück kommen, dann war das Senden oder bearbeiten des Befehls nicht erfolgreich. 
1. Auslese Befehle:
<pre>
    * ID                    -->     00na
    * Fokus                 -->     00df
    * Emissionsgrad         -->     00em
    * Transmissionsgrad     -->     00et
    * Erfassungszeit        -->     00ez
    * Istwert               -->     00ms
    * Laser An              -->     00la1
    * Laser Aus             -->     00la0
</pre>
2. Eingabe Befehle (Beispiel):
<pre>
    * Emissionsgrad         -->     00em1000
        - Der gesendete Wert besteht aus 4 Zahlen, wodurch die letzte Zahl 
        die erste Nachkommastelle ist (auch beim Lesen bekommt man die Zahl 
        so zurück, das Komma muss von Hand (Computer) eingetragen werden)
        - Der Zahlenstring muss aber nicht aus 4 Zeichen bestehen!
        - hier würde 100 % übergeben werden 
        - Möglich nur von 5 % - 100 %
    * Transmissionsgrad     -->     00et0105
        - hier würde 10,5 % übergeben werden 
        - Möglich nur von 5 % - 100 %
    * Erfassungszeit        -->     00ez7
        - die Möglichen Zahlen stehen im Manual (siehe 3.1.3.) S.34 (PDF) 
        und im Englischen auf S. 36 (Internet).
</pre>

#### 1.3.2. Langwellige Pyrometer
Auch hier sind die Befehle in den Manuals zu finden (siehe Quellen). Ein großer Unterschied zu dem Kurzwelligen ist, dass die Befehle eine Nummer (Adresse) brauchen. Auch diese befehle enden mit einem \r.

Die Nummer für die Pyrometer Erkennung beginnt mit 1. Diese Nummer wird im folgenden immer mit 1 gezeigt und wird im Manual (PDF) als "head address" (S. 26) bezeichnet.

Die "00" ist die Adresse der "converter box" (Manual (PDF) S. 26)

1. Auslese Befehle:
<pre>
    * ID                                        -->     00A1sn
    * Anzahl der angeschlossenen Pyrometer      -->     00oc
    * Emissionsgrad                             -->     00A1em
    * Erfassungszeit                            -->     00A1ez
    * Istwert                                   -->     00A1ms
</pre>
2. Eingabe Befehle (Beispiel):
<pre>
    * Emissionsgrad         -->     00A1em1000
        - Angabe des Wertes wie bei bei den Kurzwelligen 
        - Der Zahlenstring muss aber nicht aus 4 Zeichen bestehen!
        - hier würde 100 % übergeben werden 
        - Möglich nur von 10 % - 120 %
    * Erfassungszeit        -->     00A1ez6
        - die Möglichen Zahlen stehen im Manual (PDF) S. 29
</pre>

### 1.4. Adafruit Modul (Pt100)
Diese Module haben keine Befehle, das Modul wird nur ausgelesen mit Hilfe der heruntergeladenen python Bibliothek (siehe 3.1.4.). Die Funktion "temperatur" sorgt dafür, dass das Modul ausgelesen wird. 