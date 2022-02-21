## **1. Verwendete Geräte:**

### 1.1. Pyrometer
In dem Experiment sind derzeitig zwei Arten von Pyrometer in Verwendung - Langwellige und Kurzwellige.

Das kurzwellige Pyrometer was in dem Experiment verwendet wird ist ein IGA 6/23 – Laser von der Firma LumaSense. 

Für die langwelligen Pyrometer wird das Impac® Series 600 von Advanced Energy. An dieses werden zwei Pyrometer angeschlossen. Eins hat ein Aspecktverhältnis von 20:1 und das andere von 10:1. 

Für die Pyrometer ist die von mir erstellte Bibliothek "pyrometer.py" zuständig. Die Befehle und ein groß Teil des Programms wurden mir vom IKZ bereit gestellt. 

<img src="Bilder/PyroKw.png" alt="Geräte" title="Pyrometer Kurzwellig" width=300/><img src="Bilder/PyroLw.png" alt="Geräte" title="Pyrometer Langwellig" width=300/>

**Wichtiges zu beachten:**
1. Langwellige Pyrometer:
    - Grenzwerte Pyrometer: 10 % - 120 %    
    In dem Programm wird der Emissionsgrad aber zwischen 100 % und minimal möglicher Wert gehalten.
2. Kurzwellige Pyrometer
    - Grenzwerte Pyrometer: 5 % - 100 % (bei Emissions- und Transmissionsgrad)    
    In dem Programm wird der Emissionsgrad aber zwischen 100 % und minimal möglicher Wert gehalten.
    - misst erst ab einer Temperatur von 74 °C (zeigt unter der Temperatur immer 74 °C an)

### 1.2. Adafruit - Pt100
Die Pt100 werden über Adafruit Module und dem Raspberry Pi 400 mit dem Programm verbunden. 

Diese Pt100 werden in 4-Leiter-Anschluss an den Modulen befestigt. 

Für diese Module ist die von mir geschriebene Bibliothek "adafruit.py" zuständig.

<img src="Bilder/Adafruit-Modul.jpg" alt="Geräte" title="Adafruit Modul" width=300/>

**Wichtiges zu beachten:**
- Durch die spezielle Bibliothek für die Adafruit Module läuft das Programm erst wenn alles richtig installiert wurde. Selbst die Test-Funktion läuft nicht. Das liegt daran das board.py nicht vorhanden ist bzw. das verwendete Board nicht findet. Unter https://github.com/nemocrys/exp-T-control kann man eine Beschreibung finden wie man das Problem löst.    

### 1.3. Heizer
Diese Geräte werden von der von mir geschriebenen Bibliothek "heizer.py" gesteuert. 

In dieser Bibliothek gibt es bisher zwei Heizer - die Heizplatte IKA® C-MAG HS 7 von IKA und der Regler von Eurotherm. Für den Eurotherm wurden bisher die Module 902P und 905S getestet. Nur der 905S hat aber bisher mit uns kommuniziert. 

<img src="Bilder/Heizplatte_IKA.png" alt="Geräte" title="Heizplatte von IKA mit Pt1000" width=300/><img src="Bilder/Eurotherm.jpg" alt="Geräte" title="Eurotherm 905S" width=232/>

**Wichtiges zu beachten:**
1. Eurotherm:
    - minimal Temperatur ist 20 °C
2. Heizplatte IKA
    - nach einer vom Geräte Pt1000 gemessenen Temperatur von ca. 360 °C stellt sich das Gerät ab und gibt einen Fehler aus