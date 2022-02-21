## 1. Quellen
### 1.1. Quellen für die Geräte (Manuals und Info Beschaffung)
#### 1.1.1. Eurotherm
Für den Eurotherm Regler wurden verschiedene Manuals genutzt. In diesen Kapitel sollen diese einmal erwähnt werden.    

- Eurotherm 900EPC-BA-HA150789GER.pdf    
    - zu finden im Internet:    
        - https://www.eurotherm.com/download/900-epc-benutzer-handbuch-ha150789ger/
        - https://www.eurotherm.com/download/900-epc-benutzer-handbuch-ha150789ger/?ind=0&filename=900EPC-BA-HA150789GER.pdf&wpdmdl=27254&refresh=61e97823233e71642690595  
    - Sprache: Deutsch    
    - **wichtiger Inhalt**:
        - das Manual bezieht sich auf den hier genannten 905S Eurotherm   
        - S. 17 - Anschluss von Thermoelement und Widerstandsthermometer
        - S. 23 - Anschluss Digitale Kommunikation
        - S. 53 - 54 - AutoTune/Selbstoptiemierung
        - S. 96 - Einstellung der Kommunikationsparameter (Baudrate und Adresse)
        - S. 98 - Einstellung der Sollwertgrenzen
        - S. 116 - Konfiguration und wie man dort hineinkommt
        - S. 166 - Kapitel 7 Kommunikation 
        - S. 172 - 177 - Mnemonik Befehle

- EIBYSINC Beispiel.pdf
    - Dieses Dokument wurde als Antwort an uns von Eurotherm gesendet.
    - Zeigt wie der Code den man an die Schnittstelle senden muss fürs Lesen und Schreiben eines Befehls aussehen muss.
    - zeigt wie der BCC berechnet wird. 

- eurothermCOM.pdf
    - zu finden im Internet: https://www.esrf.fr/computing/bliss/guides/detection/eurotherm/1pdfs/eurothermCOM.pdf 
    - das Dokument bezieht sich auf die 2000 Serie von Eurotherm
    - Hier ist aber auf S. 32 - 33 ein Beispiel zum Lesen und auf S. 34 - 35 ein Beispiel fürs schreiben.

    *Notiz*:    
    Später wird noch erklärt wie die Befehle hier im Programm aussehen!

- 900comms_023776_2_1.pdf   
    - zu finden im Internet: http://www.jjmiller.info/files/BVT3000/900comms_023776_2_1.pdf 
    - S. 26 - EE Bedeutung (Fehlererklärung)
    - S. 29 - 32 - Mnemonik Befehle (die mehr verwendet) (für 902,903 und 904)
    - S. 39 - 44 - Mnemonik Befehle für 900 EPC (905S gehört dazu)

#### 1.1.2. IKA Heizplatte
Die Befehle und Informationen für die Heizplatte kann man auf der nachfolgenden Internetseite finden. Das Dokument zeigt die Betriebsanleitung des Gerätes.   
https://www.ika.com/de/Produkte-Lab-Eq/Magnetruehrer-Heizruehrer-Laborruehrer-Ruehrer-csp-188/C-MAG-HS-7-control-Downloads-cpdl-20002694/

*Dokument:*     
20000031429_DE_C-MAG HS 7 control_112020_web.pdf

#### 1.1.3. Pyrometer
Die Unterlagen für die Pyrometer wurden mir vom IKZ bereitgestellt.     
   
*Dokument Kw:*   
- de-op-iga6-23-manual.pdf
    - S. 33 - 35 Befehle
    - S. 20 - 21 Messfleck und Messfleck-Formel
- https://www.disai.net/wp-content/uploads/catalogos_pdf/MI_en-op-iga6-23-advanced-manual.pdf
    - Englisches Manual   

*Dokument Lw:*    
- Series 600_manual_English.pdf
    - S. 39 - 41 Messfleck
    - S. 26 - 36 Befehle
- https://www.advancedenergy.com/globalassets/resources-root/german/data-sheets/de-op-series600-data-sheet.pdf 
    - S. 2 - einstellbarer Bereich Emissionsgrad

#### 1.1.4. Adafruit
Vom IKZ bekommen:
- adafruit_max31865_rtd_pt100_amplifier-1396508.pdf

Das Dokument bassiert auf folgenden Internetseiten:
- https://learn.adafruit.com/adafruit-max31865-rtd-pt100-amplifier/overview
- https://learn.adafruit.com/adafruit-max31865-rtd-pt100-amplifier/pinouts 
- https://learn.adafruit.com/adafruit-max31865-rtd-pt100-amplifier/assembly 
- https://learn.adafruit.com/adafruit-max31865-rtd-pt100-amplifier/rtd-wiring-config
- https://learn.adafruit.com/adafruit-max31865-rtd-pt100-amplifier/arduino-code 
- https://learn.adafruit.com/adafruit-max31865-rtd-pt100-amplifier/python-circuitpython <*>
- https://learn.adafruit.com/adafruit-max31865-rtd-pt100-amplifier/f-a-q 
- https://learn.adafruit.com/adafruit-max31865-rtd-pt100-amplifier/downloads

<*> Dort steht alles zur Installation und Arbeit mit Python

Die Python Bibliothek ist unter dem Link https://github.com/adafruit/Adafruit_CircuitPython_MAX31865 zu finden. Bei der Installation gab es Probleme, da der Raspberry nicht in der Bibliothek zu finden war. Da das Teil meines Praktikums war, kan man auf der Seite https://github.com/nemocrys/exp-T-control_archive (von mir geschrieben) in Kapitel 5 nachlesen wie das problem behoben wurde. 

### 1.2. Programmquellen
1. Wie man mit tkinter arbeitet:
    - https://pythonbuch.com/gui.html 
2. Erzeugung eines Live-Plotes:
    - https://www.delftstack.com/de/howto/matplotlib/how-to-automate-plot-updates-in-matplotlib/
3. Wie das mit dem logging funktioniert:
    - https://docs.python.org/3/howto/logging.html 
4. Wie man Ordner mit Python erstellt:
    - https://www.delftstack.com/de/howto/python/python-create-directory/ 
5. Autoscalling:
    - https://stackoverflow.com/questions/10984085/automatically-rescale-ylim-and-xlim-in-matplotlib 
    - https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.axis.html
    - http://2d.9lo.lublin.pl/DOC/python-matplotlib-doc/html/api/_as_gen/matplotlib.axes.Axes.relim.html 
6. Praktikum:
    - https://github.com/nemocrys/exp-T-control 
    - Bericht_Fachpraktikum_Elektrotechnik_Vincent-Funke_570994.pdf
7. BCC Berechnung:
    - https://www.rapidtables.com/code/text/ascii-table.html 
    - https://stackoverflow.com/questions/3673428/convert-int-to-ascii-and-back-in-python
    - https://learntutorials.net/de/python/topic/730/bitweise-operatoren
    - https://www.delftstack.com/de/howto/python/xor-in-python/
8. Echotest:
    - https://www.arduino.cc/reference/en/language/functions/communication/serial/begin/