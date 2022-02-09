# Test-Programme
Hier findet man verschiedene Programme um z.B. die Eurotherm Funktion oder Kommunikation über die Schnittstelle zu testen.

---

## 1. Eurotherm_Auslesen-Beschreiben.py
Mit dem Programm kann man die heizer.py Funktionen für den Eurotherm und der Emulation austesten. Das Programm beinhaltet nur die **read()** und **send()** Funktion der heizer.py Bibliothek. 

Im folgenden kann man nun entweder mit send() und read() die Funktionen auslösen, sowie im Hauptprogramm oder direkt die Befehle mit **.write()** und **.readline()** senden. Unter den Funktionen kann man dies sehen. Die Auskommentierten Zeilen sind verschiedene Test Zeilen. 

Die Com-Stelle muss hier per Hand eingetragen werden. 

---

## 2. Test_1_Klassen-und-YML.py
Dieses Testprogramm benötigt alle Bibliotheken (Adafruit, Pyrometer und Heizer) sowie die Parameterliste (YAML). 

Im Unterschied zum Hauptprogramm ist dies hier sehr abgespeckt. Nach der Initialisierung gibt es in dem Beispiel eine kleine For-Schleife. In dieser werden die Messdaten ausgelesen und zufällig Emissionsgrade in die Pyrometer geschrieben. Die Graphik ist die selbe wie im Hauptprogramm. 

---

## 3. Eurotherm_Kommunikation_sauber.py
Dieses Programm dient auch dem einfachen Test. Mit write_befehl und read_befehl kann man leicht die Mnemonic Zeichen und den Wert angeben. Diese werden im folgenden bearbeitet und kontrolliert. Diese Kontrolle geht über die BCC Berechnung, die Kontrolle auf ACK und die Kontrolle von EE (Fehlermeldung). 