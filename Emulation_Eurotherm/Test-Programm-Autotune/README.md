# Programm für AutoTune/Selbstoptimierung
Das Program wurde aus dem Programm hauptprogram.py und heizer.py erstellt. Anders als das Programm besitzt dieses hier nur eine sehr kleine GUI mit Beenden und Start. Hier werden keine Graphen automatisch gespeichert noch Textdatein erstellt. Mit der Grafik soll nur eine Überwachung der gerade nebenbei laufenden Messung stattfinden. 

Um genau zu sein wurde das Programm für die Überwachung des AutoTunes genutzt. Das Programm liest die Leistungswerte von Arduino und Eurotherm aus und sendet den Leistungswert von Eurotherm an den Arduino. Das Programm kann zu dem den Temperaturwert aus Eurotherm auslesen. 

Übernommen aus:
1. hauptprogramm.py
    - fenster_GUI()
    - get_Measurment()
    - Update_Graph(Kurve, Update_Y)
    - AutoScroll(Graph, minusY, plusY)
    - Start()
    - Stop()
2. heizer,py
    - bcc(string)
    - send(write_befehl)
    - read(read_befehl, schnitt, delay)

Die verschiedenen Funktionen wurden aus den besagten Programmen kopiert und dann an die neuen Anforderungen angepasst. Z.B. unter fenster_GUI() sind alle anderen Funktionen die nicht mit Start und Beenden zutun haben entfernt. Die Funktionen wurden stark vereinfacht.

Das Programm dient der Variante 3 (Eurotherm und Arduino) und soll somit die Selbstoptimierung möglich machen. Die Schnittstellen müssen per Hand im Programm eingegeben werden.

Das Programm kann aber auch für andere Überwachungen oder Test genutzt werden.  

Am Ende des Programmes werden 5 Werte vom Eurotherm erfragt:
- XP (P-Glied)
- TI (I-Glied)
- TD (D-Glied)
- Cutback (Max und Min)

Über die Variable "Ardu_on" kann man zwischen der Variante 1 und 3 wechseln. Wenn die Variable auf True steht, so arbeitet das Programm mit dem Arduino, wenn es auf False steht wird nur der Eurotherm beachtet!

## GUI:



## Graph:
<img src="Bilder/Beispiel.png" alt="AutoTune Programm" title="Grafik Aussehen"/>

Auf dem Bild ist auch ein AutoTune des Eurotherms zu sehen.