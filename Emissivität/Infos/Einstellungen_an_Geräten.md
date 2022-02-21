## 1. Einstellungen

### 1.1. Eurotherm 905S
Mit der "PAGE" Taste (links außen) steuert man durch die Bildschirme des Gerätes und kann aus einem Untermenü ins überlegende Menü wechseln. Mit der "VIEW" Taste (zweite von links) springt man in die Untermenüs. Mit den Pfeiltasten (zweite und dritte von rechts) kann man die Werte ändern. Mit der ganz rechten Taste kann man in den Menüs scrollen, ein Angewähltes Menü leuchtet Grün. Diese Taste wird Parametertaste.  

Die Ortsangaben beziehen sich auf die folgenden Bilder.

*Einstellung für die Sollwertgrenzen wie folgt:*   
1. mit der "PAGE" Taste auf Seite "ZUGRIFF AUF"  
<img src="../Bilder/Ein-Soll-Grenz_Zugriff_Auf.jpg" alt="Sollwertgrenzen einstellen auf 905S" title="Schritt 1 zur Sollwertgrenzen Einstellung" width=200/>   

2. "EBEBNE 3" auswählen und "VIEW" drücken                
3. "SOLLWERT" mit "VIEW" auswählen        
<img src="../Bilder/Ein-Soll-Grenz_Ebene3.jpg" alt="Sollwertgrenzen einstellen auf 905S" title="Schritt 3 zur Sollwertgrenzen Einstellung" width=200/>

4. "SP GRENZEN" mit "VIEW" auswählen  
<img src="../Bilder/Ein-Soll-Grenz_Sollwert.jpg" alt="Sollwertgrenzen einstellen auf 905S" title="Schritt 2 zur Sollwertgrenzen Einstellung" width=200/>

5. "SPH" und "SPL" auswählen und mit den Pfeiltasten ändern       
<img src="../Bilder/Ein-Soll-Grenz_SPGrenzen.jpg" alt="Sollwertgrenzen einstellen auf 905S" title="Schritt 3 zur Sollwertgrenzen Einstellung" width=200/>       

*Einstellung der Baudrate und Adresse für die Kommunikation:*
1. Gerät starten
2. Page "Zugriff AUF" auswählen    
<img src="../Bilder/Ein-Soll-Grenz_Zugriff_Auf.jpg" alt="Baudrate und Adresse auf 905S" title="Schritt 1 zur Baudrate und Adresse Einstellung" width=200/> 

3. "EBENE 3" auswählen  

4. "Kommunikation" auswählen  
<img src="../Bilder/B_A_einstellen_1.jpg" alt="Baudrate und Adresse auf 905S" title="Schritt 2 zur Baudrate und Adresse Einstellung" width=200/>   

5. Baudrate und Adresse einstellbar mit Pfeiltasten   
<img src="../Bilder/B_A_einstellen_2.jpg" alt="Baudrate und Adresse auf 905S" title="Schritt 3 zur Baudrate und Adresse Einstellung" width=200/> 

*Auch das Kommunikationsprotokoll muss eingestellt werden:*   
1. Konfiguration (Einschalten + PAGE und VIEW Taste drücken)   
2. "Anwendung" auswählen   
<img src="../Bilder/KommPro_einstellen_1.jpg" alt="Kommunikationsprotokoll auf 905S" title="Schritt 1 zur Kommunikationsprotokoll Einstellung" width=200/>   

3. "Schnittstelle" auswählen   
<img src="../Bilder/KommPro_einstellen_2.jpg" alt="Kommunikationsprotokoll auf 905S" title="Schritt 2 zur Kommunikationsprotokoll Einstellung" width=200/> 

4. "Komm Typ" auswählen (über Master Config)    
<img src="../Bilder/KommPro_einstellen_3.jpg" alt="Kommunikationsprotokoll auf 905S" title="Schritt 3 zur Kommunikationsprotokoll Einstellung" width=200/>

5. Wir nutzen das Protokoll: **EI BISYNC**    
<img src="../Bilder/KommPro_einstellen_4.jpg" alt="Kommunikationsprotokoll auf 905S" title="Schritt 4 zur Kommunikationsprotokoll Einstellung" width=200/>    

Der Istwert kann über verschiedene Sensoren bestimmt werden. In diesen Experiment sind Thermoelemente und Widerstandsthermometer die Sensoren der Wahl. Um diese aber nutzen zu können muss man sie richtig anschließen und richtig konfigurieren. Wie die Sensoren anzuschließen sind kann man in dem Manual "Eurotherm 900EPC-BA-HA150789GER.pdf" auf S. 17 (siehe dazu auch Quellen - Kapitel 3) nach lesen. Wie diese Konfiguriert werden kann man folgend sehen:    

*Sensor auswählen:*
1. Konfiguration (Einschalten + PAGE und VIEW Taste drücken)   
2. "Instrument" auswählen   
<img src="../Bilder/KommPro_einstellen_1.jpg" alt="Sensor auf 905S" title="Schritt 1 zur Sensor Einstellung" width=200/>

3. "Prozess Eing" auswählen   
<img src="../Bilder/Sensor_Ein_1.jpg" alt="Sensor auf 905S" title="Schritt 2 zur Sensor Einstellung" width=200/>

4. "Linearisierung" auswählen   
<img src="../Bilder/Sensor_Ein_2.jpg" alt="Sensor auf 905S" title="Schritt 3 zur Sensor Einstellung" width=200/>

5. den Sensor der angestöpselt ist auswählen (RT100 = Pt100 - Widerstandsthermometer und wir nutzen K T/C - Thermoelement von Typ K)    
<img src="../Bilder/Sensor_Ein_3.jpg" alt="Sensor auf 905S" title="Schritt 4 zur Sensor Einstellung" width=200/>

Als die Sensoren getauscht wurden, wurde plötzlich der Fehler Fühlerbruch angezeigt. Bei näheren durch suchen der Konfiguration und Einstellung in "Ebene 3" wurde klar das die Sollwertgrenzen alle auf 400 °C gestellt wurde und der Wertebereich des Sensors stannt auf 750 °C bei Maximal und Minimal. Nach der Ändrung des Minimal Wertes konnte man die Sollwertgrenzen ändern und es wurde auch ein plausibler Wert ausgegeben.

*Wertebereich einstellen:*
1. führe die Schritte 1 - 3 von *Sensor auswählen* durch
2. "Wertebereich" auswählen     
<img src="../Bilder/Sensor_Ein_2.jpg" alt="Wertebereich auf 905S" title="Schritt 3 zur Wertebereich Einstellung" width=200/>

3. Max und Min Wert ändern   
<img src="../Bilder/Wertebereich_Ein.jpg" alt="Wertebereich auf 905S" title="Schritt 4 zur Wertebereich Einstellung" width=200/>

Bei den Thermoelementen ist es noch wichtig das die richtige Vergleichsstelle eingestellt ist, dies geht wie folgt:
1. Konfiguration (Einschalten + PAGE und VIEW Taste drücken)   
2. "Anwendung" auswählen   
<img src="../Bilder/KommPro_einstellen_1.jpg" alt="Vergleichsstelle auf 905S" title="Schritt 1 zur Vergleichsstelle Einstellung" width=200/>  

3. "Eingaenge" auswählen   
<img src="../Bilder/KommPro_einstellen_2.jpg" alt="Vergleichsstelle auf 905S" title="Schritt 2 zur Vergleichsstelle Einstellung" width=200/> 

3. "Vergl Stelle" auswählen   
<img src="../Bilder/Vergleichsstelle_1.jpg" alt="Vergleichsstelle auf 905S" title="Schritt 3 zur Vergleichsstelle Einstellung" width=200/> 

4. "Intern" auswählen     
<img src="../Bilder/Vergleichsstelle_2.jpg" alt="Vergleichsstelle auf 905S" title="Schritt 4 zur Vergleichsstelle Einstellung" width=200/> 

Auf den folgenden Bildern wird erläutert was man für das AutoTune/Selbstoptimierung machen muss. Zudem wird gezeigt, wie man die Parameter findet.

**Konfigurationen**    
1. Konfiguration (Einschalten + PAGE und VIEW Taste drücken)   
2. "Anwendung" auswählen   
<img src="../Bilder/KommPro_einstellen_1.jpg" alt="AutoTune Konfig" title="Schritt 1 für AutoTune Konfig" width=200/>  

3. "SELBSTOPTIM" auswählen    
<img src="../Bilder/KommPro_einstellen_2.jpg" alt="AutoTune Konfig" title="Schritt 2 für AutoTune Konfig" width=200/> 

4. "SELBSTOPT" auf "J" (JA) stellen ("ADAPTION" am besten auch)       
<img src="../Bilder/AutoTune_1.jpg" alt="AutoTune Konfig" title="Schritt 3 für AutoTune Konfig" width=200/>     

5. Zurück in die Konfiguration     
6. "Instrument" auswählen       
<img src="../Bilder/KommPro_einstellen_1.jpg" alt="AutoTune Konfig" title="Schritt 4 für AutoTune Konfig" width=200/>     

7. "DIG EIN FUNKT" auswählen    
<img src="../Bilder/AutoTune_2.jpg" alt="AutoTune Konfig" title="Schritt 5 für AutoTune Konfig" width=200/>   

8. Unter 1 (Regelkreis 1) auf "SELBSTOPT- 1" stellen     
<img src="../Bilder/AutoTune_3.jpg" alt="AutoTune Konfig" title="Schritt 6 für AutoTune Konfig" width=200/>   

**Parameter finden und AutoTune starten**     
1. mit der "PAGE" Taste auf Seite "ZUGRIFF AUF"  
<img src="../Bilder/Ein-Soll-Grenz_Zugriff_Auf.jpg" alt="AutoTune Starten" title="Schritt 1 zum AutoTune Start" width=200/>   

2. "KREIS 1 ADAPT" auswählen    
<img src="../Bilder/AutoTune_5.jpg" alt="AutoTune Starten" title="Schritt 2 zum AutoTune Start" width=200/>  

3. "SELBSTOPT" auswwählen und View drücken (Taste)     
<img src="../Bilder/AutoTune_4.jpg" alt="AutoTune Starten" title="Schritt 3 zum AutoTune Start" width=200/>  
    - AT erscheint auf dem Bildschirm (vor SP)     
    <img src="../Bilder/AutoTune_6.jpg" alt="AutoTune Starten" title="Schritt 3.1 zum AutoTune Start" width=200/>    
    - Max OP, Min OP sowie der Sollwert können hier eingestellt werden
    - bei "PID-PAR AUSW" Auswahl kann man ATS auf dem Bildschrim erzeugen, dies bedeutet das die Selbstoptimierung mit GAIN SCHEDULING durchgeführt wird (mehr dazu im "Eurotherm 900EPC-BA-HA150789GER.pdf" S. 56-58)
    - AutoTune verläuft nun selbstständig, sobald das AT verschwunden ist, ist auch das AutoTune fertig
    - Nach "https://manualzz.com/doc/53693352/eurotherm-900epc-user-manual" (Engliche Version des Manuals - S. 68) wird gesagt das die Parameter nicht auf Null stehen sollen (P, I, D, Cutback, etc.)

4. zurück in "EBENE 3"
5. "PID PARAMETER" oder "ZUSATZ-PARAM" auswählen    
<img src="../Bilder/AutoTune_9.jpg" alt="PID Werte" title="Schritt 1 zum PID Werte" width=200/> 

6. "PID PARAMETER" ausgewählt (XP, TI, TD Werte sehen und einstellbar)    
<img src="../Bilder/AutoTune_7.jpg" alt="PID Werte" title="Schritt 2 zum PID Werte" width=200/> 

6. "ZUSATZ-PARAM" ausgewählt (CBH, CBL (Cutback) Werte sehen und einstellbar)    
<img src="../Bilder/AutoTune_8.jpg" alt="PID Werte" title="Schritt 3 zum PID Werte" width=200/> 

### 1.2. Schnittstelle am Eurotherm 905S und 902P:   
Im inneren des Gerätes gibt es einen Schalter (bzw. Brückenschaltden) den man erst auf RS232 oder RS485 stellen muss. Auf den nachfolgenden Bildern kann man es für den 905S sehen.

<img src="../Bilder/Board_Platine_905.jpg" alt="Platine mit Schalfür 905S" title="Auf der draußen liegenden Platine ist der Schalter" width=500/>    

<img src="../Bilder/Schalter_905.jpg" alt="Platine mit Schalter 905S" title="Brückenschalter" width=500/>

Auf dem folgenden Bild ist der Schalter von dem Eurotherm 902P zusehen.    

<img src="../Bilder/Schalter_902.jpg" alt="Platine mit Schalter 902P" title="Schalter" width=500/> 

Um bei beiden Geräten an die besagten Schalter ran zukommen, muss man das Gerät öffnen und die Platine entfernen. Auf dem Bildern kann man dies sehen. 


### 1.3. Heizplatte IKA
Bei der Heizplatte gibt es zwei wichtige Dinge die man nicht über ein Programm ändern kann.    
(Quelle: Readme (deutsch) von https://github.com/nemocrys/exp-T-control)

Die erste sache ist wie man die **Sicherheitstemperatur einstellt**.   
Dies geht wie folgt:         
1. links vom Ein-Aus-Schalter gibt es ein kleines Loch
2. mit einem Schraubenzieher geht man in das Loch und dreht die darin liegende Schraube
3.  einstellbarer Bereich:  100 °C ... 650 °C   
    - die Solltemperatur richtet sich nach dieser Sicherheitstemperatur und kann bei bestimmten Sicherheitstemperaturen nur bedingt groß sein      
            
Die zweite Sache ist die Auswahl des **Reglers**. Zur Auswahl steht der PID und der 2P (Zweipunktregler).     
Die Einstellung geht wie folgt:              
1. die Einstellung geht nur wenn kein Programm vom Pc läuft (Schnittstelle nicht in Nutzung)
2. Betätige die Taste mit dem Schraubenschlüssel
3. mit dem rechten Drehknopf solange drehen bis PID oder 2P auf dem Bildschirm blinkt 
4. zu Bestätigung einmal den Drehknopf drücken         
5. nun den Drehknopf solange drehen bis der gewünschte Regler erscheint        
6. nach der Auswahl, Drehknopf einmal drücken und zum Verlassen des Menüs die taste mit dem Schraubenschlüssel betätigen     

### 1.3. Kurzwellige Pyrometer
Hinten an dem Pyrometer kann man mit einem Inbusschlüssel den Laser des Gerätes einstellen.