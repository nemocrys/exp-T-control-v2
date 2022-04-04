# Vincent Funke

### Python Bibliotheken:
import yaml                                     # Arbeiten mit yml Datein
import time
import datetime                                 # Holt die Tageszeit + Datum
import os                                       # Bibliothek für Dateipfade
from tkinter import *                           # Damit kann man Schaltoberflächen erstellen
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt                 # Erzeugung von Graphen
import argparse                                 # Werte bei Konsolenstart setzen
import configparser                             # Auslesen einer Datei Mithilfe von Überschriften
import logging                                  # Ereignisse in Datei speichern
import subprocess                               # Bibliothek zum Ausführen von Unterprozessen

### Eigene Bibliotheken:
import heizer
import pyrometer
import adafruit

# Globale Variablen:
global nEMess, time_start, end
global nStart, Stop_Graph                          # Start und Stop Variablen
global pyroLW, pyroKW, pt_sam                      # Init Listen für Objekte
global figure, ax1, ax2, ax3, ax4, line1, line2    # Grafik Variablen
global listTiRe, listTempPt, listZusatz            # Listen
global obj_heizer                                  # Objekt

# Funktionen:
###########################################################################
def Init_File():                                                          # Erstelle die Köpfe der File-Datei
###########################################################################
    global FileOutName, FileOutNameE, FileOutNameEEnd, AutoStop_Pt, AutoStop_Hp, AutoStop_Py, Folder

    # Variablen und Listen Initialisierung:
    actual_date = datetime.datetime.now().strftime('%Y_%m_%d')            # Variablen für den Datei Namen
    FileOutPrefix = actual_date
    FileOutIndex = str(1).zfill(2)
    FileOutName = ''

    # Boolche Variablen um bestimmte Aktionen zu Verriegeln oder freizuschalten
    AutoStop_Pt = False
    AutoStop_Hp = False
    AutoStop_Py = False

    # Versionsnummer von GitHub Lesen:
    version = (
        subprocess.check_output(["git", "describe", "--tags", "--dirty", "--always"])
        .strip()
        .decode("utf-8")
    )

    # Eindeutige Ordnernamen + Ordner erstellen (Ordner nach Tagen erstellen):
    Folder = 'Bilder_und_Daten/Daten_vom_' + FileOutPrefix                      # Erstelle Ordner Pfad
    if not os.path.exists(Folder):                                              # schaue ob es den Ordner schon gibt
        os.makedirs(Folder)                                                     # wenn nicht dann erstelle ihn
    if args.log == True:   logging.info(f'Ordner - {Folder} erstellt/geprüft')

    # Automatische Erzeugung von eindeutigen Filenamen, ohne das eine alte Datei überschrieben wird:
    FileOutName = FileOutPrefix + '_#' + FileOutIndex + '_temp.txt'             # Andere Dateiendungen (z.B. dat) auch möglich
    j = 1
    while os.path.exists(Folder + '/' + FileOutName) :                          # Schaut ob es den Namen schon in dem Verzeichnis gibt ...
        j = j + 1                                                               # ... wenn ja wird der FleOutIndex (j) solange erhöht bis es eine neue Datei erstellen kann
        FileOutIndex = str(j).zfill(2)
        FileOutName = FileOutPrefix + '_#' + FileOutIndex + '_temp.txt'
    print ('Output data: ', FileOutName)
    if args.log == True:   logging.info('File Name erzeugt')

    # Öffnen und Erstellen der Datei *temp.txt:
    with open(Folder + '/' + FileOutName,"w", encoding="utf-8") as fo:
        fo.write("Temperaturdaten der Geräte\n")
        fo.write(f"Datum: {actual_date}\n\n")
        fo.write(f"Version: {version}\n\n")
        fo.write("\nabs. Zeit".ljust(15) + "rel. Zeit [s]".ljust(20))
        heizer_wahl = config['Heizer']['Auswahl']['String']
        if heizer_wahl == 'IKA':
            fo.write("Temp. Platte [°C]".ljust(22))
        if heizer_wahl == 'Eurotherm':
            fo.write("Out.Leistung [%]".ljust(22))
        fo.write("Regler Temp. [°C]".ljust(22))
        for name, Pyro in pyroKW.items():
            fo.write(f"Temp. {name} [°C]".ljust(35))
        for name, Pyro in pyroLW.items():
            fo.write(f"Temp. {name} [°C]".ljust(35))
        for name, pt in pt_sam.items():
            fo.write(f"Temp. {name} [°C]".ljust(35))
        fo.write('\n')
        if args.log == True:   logging.info('File Kopf erstellt')

    # Datei für die Emissionswerte erstellen:
    # Alle Emissionswerte:
    FileOutNameE = FileOutPrefix + '_#' + FileOutIndex + '_Emis.txt'
    print ('Output data: ', FileOutNameE)
    with open(Folder + '/' + FileOutNameE,"w", encoding="utf-8") as foE:
        foE.write('Auflistung der Emissionsgrade:\n')
        foE.write(f"Datum: {actual_date}\n\n")
        foE.write(f"Version: {version}\n\n")
        foE.write('Rezept:\n')
        foE.write('-------\n')
        foE.write(f'Solltemperaturen:     {TempTrep}\n')
        foE.write(f'Regelbereich:         {TempArea}\n')
        foE.write(f'Zeit im Regelbereich: {TempTime}\n\n')
        foE.write('Emissionsrad ist 100 % - wenn keine Anpassung vorgenommen wird!\n\n')
        foE.write("abs. Zeit".ljust(15) + "Zeit [s]".ljust(15))
        for name, Pyro in pyroKW.items():
            foE.write(f"Emiss. {name} [%]".ljust(35))
        for name, Pyro in pyroLW.items():
            foE.write(f"Emiss. {name} [%]".ljust(35))
        foE.write('\n')
        if args.log == True:   logging.info('File für Emissionsgrade erstellt')

    # Nur die Letzten:
    FileOutNameEEnd = FileOutPrefix + '_#' + FileOutIndex + '_Emis_Ende.txt'
    print ('Output data: ', FileOutNameEEnd)
    with open(Folder + '/' + FileOutNameEEnd,"w", encoding="utf-8") as foEE:
        foEE.write('Auflistung der Emissionsgrade:\n')
        foEE.write(f"Datum: {actual_date}\n\n")
        foEE.write(f"Version: {version}\n\n")
        name_rs = config['Strings']['Regelsensor']
        vergleich_ort = f'Regelsensor {name_rs}'                # Wenn kein Vergleichssensor unter den Adafruit Pt100 ausgewählt, dann wird der Regelsensor ausgewählt!
        for name, pt in pt_sam.items():
            if pt.vergleich == True:
                vergleich_ort = name
        foEE.write(f'Vergleichsgeräte für die Pyrometeranpassung: {vergleich_ort}\n\n')
        print(f'\nVergleichssensor: {vergleich_ort}\n')
        if args.log == True:   logging.info(f'Vergleichsgerät = {vergleich_ort}')
        foEE.write('Rezept:\n')
        foEE.write('-------\n')
        foEE.write(f'Solltemperaturen:     {TempTrep}\n')
        foEE.write(f'Regelbereich:         {TempArea}\n')
        foEE.write(f'Zeit im Regelbereich: {TempTime}\n\n')
        foEE.write('Emissionsrad ist 100 % - wenn keine Anpassung vorgenommen wird!\n\n')
        foEE.write("Soll. Temperatur".ljust(25))
        foEE.write("Vergleichs-Temperatur".ljust(35))
        for name, Pyro in pyroKW.items():
            foEE.write(f"Emiss. {name} [%]".ljust(35))
        for name, Pyro in pyroLW.items():
            foEE.write(f"Emiss. {name} [%]".ljust(35))
        foEE.write('\n')
        if args.log == True:   logging.info('File für Emissionsgrade Endwerte erstellt')

###########################################################################
def fenster_GUI():                                                        # Enthält die Eingabefelder und Knöpfe für die Schaltoberfläche!
###########################################################################
    '''
    Die Abkürzungen stammen noch aus dem alten Programmcode von https://github.com/nemocrys/exp-T-control. Zum Beispiel ändert sich in dem neuen Code die bedeutung von Hp.
    Pt steht nun für Regelsensor, da dieser nun auch Ausgetauscht werden kann (Pt100, Pt1000 oder Thermoelement).
    Hp steht für das Extra Diagramm was je nach Heizer Wahl andere Parameter beinhaltet.
    Py steht für das Diagramm mit den Pyrometer und Adafruit Modulen.
    '''

    # Definitionen der Aktionen der Knöpfe:
    def button_action_1():                  # Start Knopf
        anweisungs_label_1.config(Start())

    def button_action_3():                  # Beenden Knopf
        info_label.config(Stop())
        quit()

    def button_action_5_Pt():                  # Autoscaling beenden Knopf - Regelsensor
        global AutoStop_Pt, xBestPt, yBestPt, xVonPt, yVonPt
        AutoStop_Pt = True

        xBestPt = Eingabe_Koordinaten(eingabefeld_xAchsePt, change_label_xPt, 'xEnde')
        yBestPt = Eingabe_Koordinaten(eingabefeld_yAchsePt, change_label_yPt, 'yEnde')
        xVonPt = Eingabe_Koordinaten(eingabefeld_xVonPt, change_label_xvPt, 'xBeginn')
        yVonPt = Eingabe_Koordinaten(eingabefeld_yVonPt, change_label_yvPt, 'yBeginn')

    def button_action_5_Hp():                  # Autoscaling beenden Knopf - Heizer Zusatz
        global AutoStop_Hp, xBestHp, yBestHp, xVonHp, yVonHp
        AutoStop_Hp = True

        xBestHp = Eingabe_Koordinaten(eingabefeld_xAchseHp, change_label_xHp, 'xEnde')
        yBestHp = Eingabe_Koordinaten(eingabefeld_yAchseHp, change_label_yHp, 'yEnde')
        xVonHp = Eingabe_Koordinaten(eingabefeld_xVonHp, change_label_xvHp, 'xBeginn')
        yVonHp = Eingabe_Koordinaten(eingabefeld_yVonHp, change_label_yvHp, 'yBeginn')

    def button_action_5_Py():                  # Autoscaling beenden Knopf - Pyrometer + Adafruit
        global AutoStop_Py, xBestPy, yBestPy, xVonPy, yVonPy
        AutoStop_Py = True

        xBestPy = Eingabe_Koordinaten(eingabefeld_xAchsePy, change_label_xPy, 'xEnde')
        yBestPy = Eingabe_Koordinaten(eingabefeld_yAchsePy, change_label_yPy, 'yEnde')
        xVonPy = Eingabe_Koordinaten(eingabefeld_xVonPy, change_label_xvPy, 'xBeginn')
        yVonPy = Eingabe_Koordinaten(eingabefeld_yVonPy, change_label_yvPy, 'yBeginn')

    def button_action_6_Pt():                   # Autoscaling einschalten Knopf - Regelsensor
        global AutoStop_Pt
        AutoStop_Pt = False

    def button_action_6_Hp():                   # Autoscaling einschalten Knopf - Heizer Zusatz
        global AutoStop_Hp
        AutoStop_Hp = False

    def button_action_6_Py():                   # Autoscaling einschalten Knopf - Pyrometer + Adafruit
        global AutoStop_Py
        AutoStop_Py = False

    def button_action_7():                      # Bild/Graph/Diagramm speichern Knopf
        save_label.config(save())

    def button_action_17():                     # Graph aktualisieren anhalten, Toggelend
        global Stop_Graph

        if Stop_Graph == False:
            Stop_Graph = True
            change_label_nogra.config(text="Graph Stopp")
        else:
            Stop_Graph = False
            change_label_nogra.config(text="Graph Weiter")

    # Aufruf der sich wiederholenden Aufgabe/Funktion:
    def task():
        if nStart == True:                         # Startet nur wenn auch der Start-Knopf betätigt wird!
            get_Measurment()
            fenster.after(sampling_Time, task)
        else:
            fenster.after(10, task)                # Solange Start nicht gedrückt wird, soll der task so schnell wie möglich widerholt werden! So kommen bei größeren Messabständen keine Riesigen Lücken zum Koordinatenursprung zustande!

    # Funktion um das Autocalling Aus zu vereinfachen (anstatt bei allen drei Graphen das wieder und wieder schreiben, alles in eine Funktion tun)
    def Eingabe_Koordinaten(Einagbefeld, ChangeLabel, Modi):                    # Funktion für die Einstellung der Koordinaten der Graphen
        wert = 0
        entry_text = Einagbefeld.get()                                          # Eingabe für die Koordinate
        if (entry_text == ""):                                                  # Bei Leerem Eingabefeld wird ein Default übergeben
            if Modi == 'xEnde':                                                 # Je nach Modi wird etwas anderes verändert
                ChangeLabel.config(text="x = 100 min")
                wert = 100
            elif Modi == 'yEnde':
                ChangeLabel.config(text="y = 100 °C")
                wert = 100
            elif Modi == 'xBeginn':
                ChangeLabel.config(text="x startet bei 0 min")
                wert = 0
            elif Modi == 'yBeginn':
                ChangeLabel.config(text="y startet bei 0 °C")
                wert = 0
        else:
            new = entry_text.replace(',','.')                                   # Wenn ein Text vorhanden ist, so wird bei Komma Eingabe, das zu einem Punkt - Somit ist als Eingabe sowohl ein Komma als auch der Punkt möglich
            if new.replace('.','').isnumeric() == True:                         # Wenn die Eingabe eine Zahl ist - so wird die Koordinate geändert
                wert = float(new)
                if Modi == 'xEnde':
                    ChangeLabel.config(text="x = "+ new + " min")
                elif Modi == 'yEnde':
                    ChangeLabel.config(text="y = " + new + " °C")
                elif Modi == 'xBeginn':
                    ChangeLabel.config(text="x beginnt bei "+ new + " min")
                elif Modi == 'yBeginn':
                    ChangeLabel.config(text="y beginnt bei " + new + " °C")
            else:                                                                # Sollte die Eingabe falsch sein, so wird es auch als Falsch ausgegeben, der Defaultwert wird ausgegeben!
                ChangeLabel.config(text="Die Eingabe ist Falsch!")
                if Modi == 'xEnde' or Modi == 'yEnde':
                    wert = 100
                elif Modi == 'xBeginn' or Modi == 'yBeginn' :
                    wert = 0
        return wert

    # X -Button wird verriegelt
    def disable_event():
        pass

    ################################################################################################################

    # Ein Fenster erstellen:
    fenster = Tk()
    # Den Fenstertitle erstellen:
    fenster.title("Temperaturmessung und Emissionsgradmessung")

    ################################################################################################################

    # Buttons:
    Start_button_1 = Button(fenster, text="Start", command=button_action_1)                                # Start der Heizung und Messung
    exit_button = ttk.Button(fenster, text="Beenden", command=button_action_3)                             # Fenster Schließen und Heizung Stoppen
    ## AutoScale Ein/Aus Knöpfe:
    AutoStop_button_1_Pt = Button(fenster, text="AutoScale Aus + Ändern", command=button_action_5_Pt)      # Beenden Auto Skalieren - Regelsensor
    AutoStop_button_1_Hp = Button(fenster, text="AutoScale Aus + Ändern", command=button_action_5_Hp)      # Beenden Auto Skalieren - Heizer Zusatz
    AutoStop_button_1_Py = Button(fenster, text="AutoScale Aus + Ändern", command=button_action_5_Py)      # Beenden Auto Skalieren - Pyrometer + Adafruit
    AutoStop_button_2_Pt = Button(fenster, text="AutoScale Ein", command=button_action_6_Pt)               # Einschalten Auto Skalieren - Regelsensor
    AutoStop_button_2_Hp = Button(fenster, text="AutoScale Ein", command=button_action_6_Hp)               # Einschalten Auto Skalieren - Heizer Zusatz
    AutoStop_button_2_Py = Button(fenster, text="AutoScale Ein", command=button_action_6_Py)               # Einschalten Auto Skalieren - Pyrometer + Adafruit
    ## Save Bild:
    save_button = Button(fenster, text="Bild speichern!", command=button_action_7)                         # Bild soll gespeichert werden
    ## Graph anhalten/weitermachen:
    nogra_button = Button(fenster, text="Graph I/O", command=button_action_17)                             # Hält das Aktualisieren des Plottes an!

    ################################################################################################################

    # Labels (Texte auf der Schaltoberfläche):
    ### Start und Beenden:
    anweisungs_label_1 = Label(fenster, text="Start \nHeizung/Messung!")
    info_label = Label(fenster, text="Schließen und Stoppen")
    ### Auto Scaling:
    #### Regelsensor
    change_label_xPt = Label(fenster)                               # Ende der Skala
    change_label_yPt = Label(fenster)
    change_label_xvPt = Label(fenster)                              # Beginn der Skala
    change_label_yvPt = Label(fenster)
    #### Heizer Zusatz (Hp noch aus dem allten Progrmm geblieben)
    change_label_xHp = Label(fenster)                               # Ende der Skala
    change_label_yHp = Label(fenster)
    change_label_xvHp = Label(fenster)                              # Beginn der Skala
    change_label_yvHp = Label(fenster)
    #### Pyrometer und Adafruit
    change_label_xPy = Label(fenster)                               # Ende der Skala
    change_label_yPy = Label(fenster)
    change_label_xvPy = Label(fenster)                              # Beginn der Skala
    change_label_yvPy = Label(fenster)
    # Zeilen Label
    label_x = Label(fenster, text="x-Achse Ende: ")                 # Ende der Skala
    label_y = Label(fenster, text="y-Achse Ende: ")
    label_xv = Label(fenster, text="x-Achse Beginn: ")              # Beginn der Skala
    label_yv = Label(fenster, text="y-Achse Beginn: ")
    # Spalten Label
    label_pt = Label(fenster, text="Regelsensor Koordinaten")            # Welche Eingabefelder welchem Graph gehören
    label_heiz = Label(fenster, text="Heizer Zusatz Koordinaten")
    label_py = Label(fenster, text="Pyro. & Pt100 Koordinaten")

    ### Save:
    save_label = Label(fenster, text="Zwischen Speichern")

    ### Graph anhalten/weitermachen:
    change_label_nogra = Label(fenster)

    ################################################################################################################

    # Eingabefelder:
    # Achsen-Koordinaten Graph Regelsensor
    eingabefeld_xAchsePt = Entry(fenster, bd=2, width=10)       # Ende Skala
    eingabefeld_yAchsePt = Entry(fenster, bd=2, width=10)
    eingabefeld_xVonPt = Entry(fenster, bd=2, width=10)         # Beginn Skala
    eingabefeld_yVonPt = Entry(fenster, bd=2, width=10)
    # Achsen-Koordinaten Graph Heizer Zusatz
    eingabefeld_xAchseHp = Entry(fenster, bd=2, width=10)       # Ende Skala
    eingabefeld_yAchseHp = Entry(fenster, bd=2, width=10)
    eingabefeld_xVonHp = Entry(fenster, bd=2, width=10)         # Beginn Skala
    eingabefeld_yVonHp = Entry(fenster, bd=2, width=10)
    # Achsen-Koordinaten Graph Pyrometer + Adafruit
    eingabefeld_xAchsePy = Entry(fenster, bd=2, width=10)       # Ende Skala
    eingabefeld_yAchsePy = Entry(fenster, bd=2, width=10)
    eingabefeld_xVonPy = Entry(fenster, bd=2, width=10)         # Beginn Skala
    eingabefeld_yVonPy = Entry(fenster, bd=2, width=10)

    ################################################################################################################

    # Fenstergröße definieren:
    fenster.geometry("1200x400")

    # Bestimmung der Orte für die einzelnen Knöpfe, Eingabefeldern und Labels auf der Schaltoberfläche:

    #### Start und Beenden
    anweisungs_label_1.place(x = 1030, y = 50, width=120, height=35)    # Start
    Start_button_1.place(x = 1060, y = 90, width=70, height=30)
    info_label.place(x = 1000, y = 130, width=200, height=30)           # Beenden
    exit_button.place(x = 1060, y = 160, width=70, height=40)

    #### Auto Scaling - Knöpfe
    AutoStop_button_1_Pt.place(x=150, y=80, width=180, height=20)       # Aus - Regelsensor (kurz Pt)
    AutoStop_button_1_Hp.place(x=450, y=80, width=180, height=20)       # Aus - Heizer Zusatz (kurz Hp)
    AutoStop_button_1_Py.place(x=750, y=80, width=180, height=20)       # Aus - Pyrometer & Adafruit (kurz Py)
    AutoStop_button_2_Pt.place(x=150, y=50, width=150, height=20)       # Ein - Pt1000
    AutoStop_button_2_Hp.place(x=450, y=50, width=150, height=20)       # Ein - Heizer Zusatz
    AutoStop_button_2_Py.place(x=750, y=50, width=150, height=20)       # Ein - Pyrometer & Adafruit
    #
    #### Auto Scaling - Ende
    eingabefeld_xAchsePt.place(x=160, y=130)                            # Eingabefelder
    eingabefeld_yAchsePt.place(x=160, y=180)
    eingabefeld_xAchseHp.place(x=460, y=130)
    eingabefeld_yAchseHp.place(x=460, y=180)
    eingabefeld_xAchsePy.place(x=760, y=130)
    eingabefeld_yAchsePy.place(x=760, y=180)
    #
    change_label_xPt.place(x=210, y=130, width=200, height=20)          # änderbare Labels mit Eingabewerten
    change_label_yPt.place(x=210, y=180, width=200, height=20)
    change_label_xHp.place(x=510, y=130, width=200, height=20)
    change_label_yHp.place(x=510, y=180, width=200, height=20)
    change_label_xPy.place(x=810, y=130, width=200, height=20)
    change_label_yPy.place(x=810, y=180, width=200, height=20)
    #
    label_x.place(x=50, y=130, width=100, height=20)                    # Zeilenlabels
    label_y.place(x=50, y=180, width=100, height=20)
    #
    #### Auto Scaling - Beginn
    eingabefeld_xVonPt.place(x=160, y=230)                              # Eingabefelder
    eingabefeld_yVonPt.place(x=160, y=280)
    eingabefeld_xVonHp.place(x=460, y=230)
    eingabefeld_yVonHp.place(x=460, y=280)
    eingabefeld_xVonPy.place(x=760, y=230)
    eingabefeld_yVonPy.place(x=760, y=280)
    #
    change_label_xvPt.place(x=240, y=230, width=200, height=20)         # änderbare Labels mit Eingabewerten
    change_label_yvPt.place(x=240, y=280, width=200, height=20)
    change_label_xvHp.place(x=540, y=230, width=200, height=20)
    change_label_yvHp.place(x=540, y=280, width=200, height=20)
    change_label_xvPy.place(x=840, y=230, width=200, height=20)
    change_label_yvPy.place(x=840, y=280, width=200, height=20)
    #
    label_xv.place(x=40, y=230, width=120, height=20)                   # Zeilenlabels
    label_yv.place(x=40, y=280, width=120, height=20)
    #
    #### Auto Scaling - Welche Eingabefelder zu welchen Gerät gehören
    label_pt.place(x=150, y=310, width=170, height=30)
    label_heiz.place(x=450, y=310, width=180, height=30)
    label_py.place(x=750, y=310, width=200, height=30)

    #### Save
    save_label.place(x=1020, y=220, width=150, height=30)
    save_button.place(x=1040, y=250, width=110, height=30)

    ### Graph anhalten/weitermachen:
    change_label_nogra.place(x = 1050, y = 340, width=90, height=40)
    nogra_button.place(x = 1060, y = 300, width=70, height=40)

    ################################################################################################################

    fenster.protocol("WM_DELETE_WINDOW", disable_event)               # X-Button Aus
    fenster.after(10, task)                                           # nach 1s soll die Funktion task aufgerufen werden!

    # In der Ereignisschleife auf Eingabe des Benutzers warten.
    if args.log == True:   logging.info('GUI erzeugt')
    fenster.mainloop()

###########################################################################
def get_Measurment():                                                     # Aufnahme und Verarbeitung der Messwerte, Werte werden in File eingetragen und ins Diagramm übergeben! Emissionsgradanpassung in der Funktion.
###########################################################################
    global loop, StartConfig, nextTempIn, nEMess, end

    # Zeiten für das weitere Arbeiten und für das Dokument:
    time_abs = datetime.datetime.now().strftime('%H:%M:%S')
    time_actual = datetime.datetime.now()

    # Messwerte holen und Listen aktualisieren:
    dt = (time_actual - time_start).total_seconds()
    if args.log == True:   logging.info(f'Zeit = {dt}')
    tempPt = obj_heizer.get_istwert()
    if args.log == True:   logging.info(f'Messwerte Heizersensor = {tempPt}')
    listTempPt.append(tempPt)
    if args.log == True:   logging.info(f'Temp.Listen Länge von listTempPt = {len(listTempPt)}')
    heizer_wahl = config['Heizer']['Auswahl']['String'] # Extra Diagramm - IKA (Heizplattentemperatur) - Eurotherm (Ausgangsleistung)
    if heizer_wahl == 'IKA':
        zusatz = obj_heizer.get_TempHeizplat()
    if heizer_wahl == 'Eurotherm':
        zusatz = obj_heizer.get_power_OUT()
    if args.log == True:   logging.info(f'Extra Messwert von {heizer_wahl} = {zusatz}')
    listZusatz.append(zusatz)
    if args.log == True:   logging.info(f'Zusatz Listen Länge von listZusatz = {len(listZusatz)}')
    for name, Pyro in pyroLW.items():
        Pyro.update_list_T()
        if args.log == True:   logging.info(f'Messwerte Pyrometer {name} = {Pyro.listT[-1]}')
        if args.log == True:   logging.info(f'Temp.Listen Länge von {name} = {len(Pyro.listT)}')
    for name, Pyro in pyroKW.items():
        Pyro.update_list_T()
        if args.log == True:   logging.info(f'Messwerte Pyrometer {name} = {Pyro.listT[-1]}')
        if args.log == True:   logging.info(f'Temp.Listen Länge von {name} = {len(Pyro.listT)}')
    for name, pt in pt_sam.items():
        pt.update_list()
        if args.log == True:   logging.info(f'Messwerte Adafruit {name} = {pt.list[-1]}')
        if args.log == True:   logging.info(f'Temp.Listen Länge von Adafruit {name} = {len(pt.list)}')
    listTiRe.append(dt/60) # Die x-Achse soll in Minuten angegeben werden!
    if args.log == True:   logging.info(f'Listen Länge von listTiRe = {len(listTiRe)}')

    # Sollwert in Liste:
    listSollwert.append(float(TempTrep[loop]))
    if args.log == True:   logging.info(f'Listen Länge von listSollwert = {len(listSollwert)}')
    if args.log == True:   logging.info('Messwerte geholt und Listen aktualisiert')

    # Vergleichstemperatur für Anpassung bestimmen:
    tempVergleich = listTempPt[-1]                  # Wenn kein Vergleichssensor unter den Adafruit Pt100 ausgewählt, dann wird der Regelsensor ausgewählt!
    if tempVergleich == 0:                          # Fehlerbehandlung (bei Null wird der alte Wert wieder genommen!)
        tempVergleich = listTempPt[-2]
        if args.log == True:   logging.info('Vergleichstemperatur war Null!')
    for name, pt in pt_sam.items():
        if pt.vergleich == True:
            tempVergleich = pt.list[-1]             # Der Letzte Wert in der ausgewählten Liste ist der aktuelle Wert!
            if tempVergleich == 0:                  # Fehlerbehandlung
                tempVergleich = pt.list[-2]
                if args.log == True:   logging.info('Vergleichstemperatur war Null!')
    if args.log == True:   logging.info('Vergleichstemperatur wird bestimmt!')
    if args.log == True:   logging.info(f'Vergleichstemperatur = {tempVergleich}')

    # Temperatur File wird erneut geöffnet und dann mit den Daten belegt:
    with open(Folder + '/' + FileOutName,"a", encoding="utf-8") as fo:
        time_abs = datetime.datetime.now().strftime('%H:%M:%S')
        fo.write(f"{time_abs:<15}{dt:<20.1f}")
        fo.write(f'{zusatz:<22.1f}') # Ausgangsleistung oder Heizplattentemperatur - Wahl Heizer beachten
        fo.write(f'{tempPt:<22.1f}')
        for name, Pyro in pyroKW.items():
            fo.write(f"{Pyro.listT[-1]:<35.1f}")
        for name, Pyro in pyroLW.items():
            fo.write(f"{Pyro.listT[-1]:<35.1f}")
        for name, pt in pt_sam.items():
            fo.write(f"{pt.list[-1]:<35.1f}")
        fo.write('\n')
        if args.log == True:   logging.info('File wird mit Messwerten erweitert')

    # Rezept wird abgearbeitet + Emissionsgradanpassung + Emis. File Bearbeitung:
    Area = float(TempArea[loop])
    Time = int(TempTime[loop])
    Soll = float(TempTrep[loop])
    lenght = len(TempTrep)                                                              # Um das Ende des Ablaufes zu erkennen
    jetzt =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')                      # aktuelle Zeit

    if (Soll + Area) < tempPt or (Soll - Area) > tempPt:                                # Solange der Istwert außerhalb des Bereiches ist wird StartConfig auf False gesetzt
        if StartConfig == True:                                                         # Sollte StartConfig gerade True sein, so wird folgendes passieren:
            with open(Folder + '/' + FileOutNameE,"a", encoding="utf-8") as foE:            # 1. Wenn der Bereich verlassen wird, soll dies gemerkt werden.
                foE.write(f'- - - Außerhalb des Bereiches - {jetzt} - - -\n\n')             # 2. Alle Emissionsgrade wieder auf 100 % setzen
                if args.log == True:   logging.info('Außerhalb des gegeben Temperaturbereiches - Emissionsgrade auf 100 %')
                for name, Pyro in pyroLW.items():
                    Pyro.write_pyro_para('e', 100)
                    Pyro.anpassung(100, 100)
                for name, Pyro in pyroKW.items():
                    Pyro.write_pyro_para('e', 100)
                    Pyro.anpassung(100, 100)
        Emis_Update()                                                                   # Der Emissionsgrad wird aus dem Gerät gelesen und in eine Liste getan
        StartConfig = False
    else:                                                                               # Wenn im Bereich dann wird das folgende abgearbeitet:
        if StartConfig == False:                                                        # Die if-Abfrage wird nur zu Beginn einer Anpassung ausgeführt. In ihr werden die nötigen endzeiten bestimmt.
            starttimeConfig = datetime.datetime.now()                                   # Startzeit - Bereich erreicht
            min = datetime.timedelta(minutes=Time)                                      # Wie lange muss die Kurve in dem Bereich bleiben
            nextTempIn = str(starttimeConfig + min).split('.')[0]                       # Berechne Endzeit und erzeuge String, lässt das Datum dran! (die Nachkommerstellen der Sekunden werden abgetrennt)
            print(f'Nächster Loop voraussichtlich um {nextTempIn.split(" ")[1]} Uhr am {nextTempIn.split(" ")[0]}!')
            if args.log == True:   logging.info('Beginn der Zeitmessung + Emissionsgrad ')
            with open(Folder + '/' + FileOutNameE,"a", encoding="utf-8") as foE:
                foE.write(f'- - - Nächster Loop voraussichtlich um {nextTempIn.split(" ")[1]} Uhr am {nextTempIn.split(" ")[0]}! - - -\n')
                foE.write(f'- - - Zyklus {loop + 1} - {Soll} °C - - -\n')
            nEMess = 0                                                                  # durch die Null werden 16 Werte aufgenommen
            StartConfig = True                                                          # verriegelt das if bis nächsten Zyklus oder bei vorzeitigen Sollwertbereich austritt

        # Emissionsgrad Anpassung - Ziel Temp.Oberfläche = Temp.Pyro - Files werden beschrieben:
        if nEMess <= 15:                                                                # das soll nur 16 mal durchgeführt werden, da die Rundung nah 10 - 13 Durschgängen keine Änderung mehr bringt
            with open(Folder + '/' + FileOutNameE,"a", encoding="utf-8") as foE:        # Anpassung durchführen
                foE.write(f'{time_abs:<15}{dt:<15.1f}')
                for name, Pyro in pyroKW.items():
                    Pyro.e_py, Pyro.e_Drauf = Emissions_Anpassung(Pyro.listT[-1], tempVergleich, Pyro.e_py, Pyro.e_Drauf, 100, 5)
                    Pyro.write_pyro_para('e', Pyro.e_py)
                    foE.write(f'{Pyro.e_py:<35}')
                for name, Pyro in pyroLW.items():
                    Pyro.e_py, Pyro.e_Drauf = Emissions_Anpassung(Pyro.listT[-1], tempVergleich, Pyro.e_py, Pyro.e_Drauf, 100, 10)
                    Pyro.write_pyro_para('e', Pyro.e_py)
                    foE.write(f'{Pyro.e_py:<35}')
                foE.write('\n')
                nEMess += 1
            if nEMess == 15:                                                                       # Speichere die endgültigen Emissionsgrade
                with open(Folder + '/' + FileOutNameEEnd,"a", encoding="utf-8") as foEE:
                    foEE.write(f'{Soll:<25}')
                    foEE.write(f'{tempVergleich:<35.1f}')
                    for name, Pyro in pyroKW.items():
                        foEE.write(f'{Pyro.e_py:<35}')
                    for name, Pyro in pyroLW.items():
                        foEE.write(f'{Pyro.e_py:<35}')
                    foEE.write('\n')
        Emis_Update()                                                                              # Der Emissionsgrad wird aus dem Gerät gelesen und in eine Liste getan

        # Prüfen ob der nächste Rezept-Zyklus Starten soll:
        if jetzt >= nextTempIn:                                                         # Vergleicht die beiden Zeiten
            with open(Folder + '/' + FileOutNameE,"a", encoding="utf-8") as foE:
                foE.write(f'- - - Zyklus {loop +1} abgeschlossen - - -\n')
            if loop == (lenght-1):                                                      # bei erreichen des Endes wird das Programm beendet!
                endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print()
                with open(Folder + '/' + FileOutNameE,"a", encoding="utf-8") as foE:
                    foE.write(f'- - - Rezept ist abgeschlossen! - {endtime} - - -\n')
                    if args.log == True:   logging.info('Rezept abgeschlossen')
                end = True  # Verhindert das eine Nachricht in foE geschrieben wird
                Stop()
                if Stop_Graph == True:                                                                      # Wenn die aktuelle Grafik gesperrt ist, so wird die Grafik vor beenden neu erstellt
                    figureEnd = plt.figure(figsize=(12,9))
                    figureEnd.suptitle("Temperatur + Emissionsgrad Messungen",fontsize=25)
                    # Linie PT1000
                    ax1End = plt.subplot(221)
                    sensor = config['Strings']['Regelsensor']# Erzeugt ersten Teilgraph
                    line1End, = ax1End.plot(listTiRe, listTempPt, 'r', label=sensor)
                    line11End, = ax1End.plot(listTiRe, listSollwert, 'b', label='Sollwert')
                    plt.ylabel("Temperatur in °C",fontsize=12)
                    plt.legend(loc='best')
                    plt.grid()
                    # Zusatz Linie - Abhängig von Heizer Wahl
                    ax2End = plt.subplot(223)                                                          # erzeugt zweiten Teilgraph
                    plt.xlabel("Zeit in min",fontsize=12)                                                # Haben gemeinsame x-Achse
                    if heizer_wahl == 'IKA':
                        label_zusatz = 'Heizplatten Temperatur'
                        plt.ylabel("Temperatur Heizplatte in °C",fontsize=12)
                    if heizer_wahl == 'Eurotherm':
                        label_zusatz = 'Ausgangsleistung'
                        plt.ylabel("Ausgangsleistung Eurotherm in %",fontsize=12)
                    line2End, = ax2End.plot(listTiRe, listZusatz, 'b', label=label_zusatz)
                    plt.legend(loc='best')
                    plt.grid()
                    # Linie Pyrometer
                    ax3End = plt.subplot(222)
                    for name, Pyro in pyroLW.items():
                        Pyro.grafik_T(ax3End, listTiRe)
                    for name, Pyro in pyroKW.items():
                        Pyro.grafik_T(ax3End, listTiRe)
                    for name, pt in pt_sam.items():
                        pt.grafik(ax3End, listTiRe)
                    plt.ylabel("Temperatur in °C",fontsize=12)
                    plt.legend(loc='best')                                                                  # erzeugt eine Legende am möglichst passendenden Ortes (passt sich automatisch an!)
                    plt.grid()
                    # Linie Emissionsgrad:
                    ax4End = plt.subplot(224)
                    for name, Pyro in pyroLW.items():
                        Pyro.grafik_E(ax4End, listTiRe)
                    for name, Pyro in pyroKW.items():
                        Pyro.grafik_E(ax4End, listTiRe)
                    plt.ylabel("Emissionsgrad in %",fontsize=12)
                    plt.xlabel("Zeit in min",fontsize=12)
                    plt.legend(loc='best')                                                                  # erzeugt eine Legende am möglichst passendenden Ortes (passt sich automatisch an!)
                    plt.grid()
                    plt.show()
                    NameDia = FileOutName.split('.')[0] + '_Bild_Rezept_End.png'        # das .txt wird vom Datennamen abgeschnitten und dann mit einem Bild-Datei-Ende versehen
                    figureEnd.savefig(Folder + '/' + NameDia)                           # speichert den Graf im Verzeichnis!
                    print ('Output data: ', NameDia)
                quit()                                                                  # ... beendet Programm!
            loop += 1                                                                   # Nächster Zyklus kann starten
            obj_heizer.change_SollTemp(TempTrep[loop])                                  # Änderung der Solltemperatur
            if args.log == True:   logging.info('Nächster Zyklus')

    if not Stop_Graph:    # Wenn True soll keine Grafik erzeugt werden oder wenn der Knopf "Graph I/O" auf True steht, soll es nicht ausgeführt werden
        # Update des Diagrammes:
        if nStart == True:
            # Autoscaling:
            AutoScroll(ax1, AutoStop_Pt, xVonPt, xBestPt, yVonPt, yBestPt, 2, 2)            # Regelsensor
            AutoScroll(ax2, AutoStop_Hp, xVonHp, xBestHp, yVonHp, yBestHp, 10, 20)          # Zusatz Graph - Heizerwahl Extra Wert (Leisttung oder Temperatur)
            AutoScroll(ax3, AutoStop_Py, xVonPy, xBestPy, yVonPy, yBestPy, 1, 5)            # Pyrometer + Adafruit
            AutoScroll(ax4, False, 0, 101, 0, 1000, 1, 1)                                   # Emissionsgrad (AutoScroll aus nicht vorhanden - die 6 Werte nach False sind dadurch egal)

            # Grafiken - Heizer
            Update_Graph(line1, listTempPt)                 # Regelsensor (IStwert)
            Update_Graph(line2, listZusatz)                 # Extra (Temperatur oder Leistung)
            Update_Graph(line3, listSollwert)               # Sollwert

            # Grafik Temperatur Pyrometer, Adafruit (Pt100)
            for name, Pyro in pyroKW.items():
                Pyro.update_T(listTiRe)
            for name, Pyro in pyroLW.items():
                Pyro.update_T(listTiRe)
            for name, pt in pt_sam.items():
                pt.update(listTiRe)

            # Grafik Emissionsgrad:
            for name, Pyro in pyroKW.items():
                Pyro.update_E(listTiRe)
            for name, Pyro in pyroLW.items():
                Pyro.update_E(listTiRe)

            if args.log == True:   logging.info('Draw figure!')       # Aktualisiere die Grafik
            figure.canvas.draw()
            figure.canvas.flush_events()
            if args.log == True:   logging.info('Diagramme werden geupdatet')

######################################################################################################################
def Update_Graph(Kurve, Update_Y):                                                                                   # Funktion für das Updaten der Kurven
######################################################################################################################
    updated = Update_Y
    Kurve.set_xdata(listTiRe)
    Kurve.set_ydata(updated)

######################################################################################################################
def AutoScroll(Graph, AutoStop, xVon, xEnde, yVon, yEnde, minusY, plusY):                                            # Funktion für das Autosrollen
######################################################################################################################
    if args.log == True:   logging.info('Autoscroll')
    if AutoStop == False:                                     # Autoscrollen ist aktiv
            Graph.axis('auto')                                  # Schaltet Autoscaling wieder ein!
            Graph.relim()                                       # Neu Berechnung der Datengrenzen
            ymin, ymax = Graph.get_ylim()                       # holt den max. und min. Wert aus dem jeweiligen Diagramm und ...
            Graph.set_ylim(ymin - minusY, ymax + plusY)         # ... setzt die neuen Grenzen für die Y-Achse und ...
            Graph.set_xlim(0,listTiRe[-1] + 10)                 # ... X-Achse (mit dem Plus und Minus, kann man Abstände zu den Achsen erstellen) ein
    elif AutoStop == True:                                    # Autoscrollen wurde deaktiviert
            Graph.axis([xVon,xEnde,yVon,yEnde])               # Übernimmt die Werte des Manuellen Anpassen der Achsen aus den Eingabefeldern!

######################################################################################################################
def Emissions_Anpassung(Temp_Pyro, Temp_Oberf, e_Alt, e_Drauf, o_Grenze, u_Grenze):                                  # Funktion für das Emissionsgrad bestimmen
######################################################################################################################
    if Temp_Pyro != Temp_Oberf:                               # Wenn die Werte gleich sind, soll der Emissionsgrad bleiben wir er ist
        e_Drauf = e_Drauf/2                                     # Bei Ungleichheit wird e_Drauf halbiert
    if Temp_Oberf > Temp_Pyro:                                # Wenn die Oberflächentempratur größer als die des Pyrometrs ist, so ...
        e_Alt = round(e_Alt - e_Drauf,1)                        # ... wird der Emissionsgrad kleiner
        if e_Alt < u_Grenze:                                    # Bei Grenzunterschreitung wird der Emissionsgrad auf der Untergrenze gehalten
            e_Alt = u_Grenze
            e_Drauf = e_Drauf * 2
    if Temp_Oberf < Temp_Pyro:                                # Wenn Pyrometer Temperatur größer ist als die der Oberfläche, dann ...
        e_Alt = round(e_Alt + e_Drauf,1)                        # ... wird der Emissionsgrad größer
        if e_Alt > o_Grenze:                                    # Bei Grenzüberschreitung wird der Emissionsgrad auf der Obergrenze gehalten
            e_Alt = o_Grenze
            e_Drauf = e_Drauf * 2
    e_Neu = e_Alt                                             # wenn die Temperaturen gleich sind, so wird der Alte_Wert zurückgegeben, sonst der neu berechnete!
    return e_Neu, e_Drauf

#################################################################################################################
def Emis_Update():
#################################################################################################################
        # Emissionsgrad in Listen eintragen:
        # Ist in einer Funktion da es an zwei Stellen (einmal im if und dann noch im else) aufgerufen werden muss
        # Während eines Rezeptes soll in jeder Sekunde der Emissionsgrad ausgelesen werden
        # auch im Letzten Durchgang bevor das Programm beendet wird!
        for name, Pyro in pyroKW.items():
            Pyro.update_list_E()
            if args.log == True:   logging.info(f'Messwert Emissionsgrad Pyrometer {name} = {Pyro.listE[-1]}')
            if args.log == True:   logging.info(f'Listen Länge von Emis.Liste für {name} = {len(Pyro.listE)}')
        for name, Pyro in pyroLW.items():
            Pyro.update_list_E()
            if args.log == True:   logging.info(f'Messwert Emissionsgrad Pyrometer {name} = {Pyro.listE[-1]}')
            if args.log == True:   logging.info(f'Listen Länge von Emis.Liste für {name} = {len(Pyro.listE)}')
        if args.log == True:   logging.info('Messwerte in Listen für Emissionsgrad geschrieben')

###########################################################################
def save():                                                               # Funktion zum Zwischen Speichern der Bilder
###########################################################################
    if args.log == True:   logging.info('Save-Button betätigt')
    if nStart == True:                                                      # Soll nur nach dem Start funkionieren
        # Bildnamen erzeugen (wie Filenamen) aus dem Filenamen
        SaveOutIndex = str(1).zfill(2)
        SNameHP = ''
        SNameHP = FileOutName.split('.')[0] + '_Bild_#' + SaveOutIndex + '.png'

        j = 1
        while os.path.exists(Folder + '/' + SNameHP) :
            j = j + 1
            SaveOutIndex = str(j).zfill(2)
            SNameHP = FileOutName.split('.')[0] + '_Bild_#' + SaveOutIndex + '.png'
        print ('Output data: ', SNameHP)
        figure.savefig(Folder + '/' + SNameHP)                              # speichert den Graf im Arbeitsverzeichnis!
        if args.log == True:   logging.info('Diagramm gespeichert')

###########################################################################
def Start():                                                              # Befehl zum Starten der Hardware + Der Plot wird erzeugt und nach erstmaligen Start auch der File neu erstellt
###########################################################################
    global time_start, nStart
    global figure, ax1, ax2, ax3, ax4, line1, line2, line3
    global listTiRe, listTempPt, listZusatz, listSollwert

    if nStart == False:                                         # Soll verhindern das eine neue Grafik bei mehreren Drücken von Start aufgeht! - Verriegellung bis das Programm beendet wird
        # File erzeugen:
        Init_File()

        # Variablen:
        time_start = datetime.datetime.now()
        nStart = True

        # Listen:
        listTiRe = []       # x-Wert der Grafik (Zeit)
        listTempPt = []     # PT1000 oder Pt100 der am Heizer/Heizerregler angeschlossen ist
        listZusatz = []     # Heizer Zusatz Daten (Ausgangsleistung oder Heizplattentemperatur)
        listSollwert = []   # Sollwert

        # Hardware starten:
        heizer_wahl = config['Heizer']['Auswahl']['String']
        if heizer_wahl == 'IKA':
            obj_heizer.start_heizung()                                                             # Start für die Heizplatte
            if args.log == True:   logging.info('Heizung Ein')

        # Ersten Sollwert setzen:
        obj_heizer.change_SollTemp(TempTrep[0])
        if args.log == True:   logging.info('Sollwert Zyklus 1 übergeben!')

        # Grafik Erzeugung:
        plt.ion()
        figure = plt.figure(figsize=(12,9))                                                 # Fenster Größe des Diagrammes festlegen
        figure.suptitle("Temperatur + Emissionsgrad Messungen",fontsize=25)                 # Erzeugt eine Gesamt Überschrifft des Graphen

        # Regelsensor und Sollwert:
        sensor = config['Strings']['Regelsensor']
        ax1 = plt.subplot(221)                                                              # Erzeugt ersten Teilgraph
        line1, = ax1.plot(listTiRe, listTempPt, 'r', label=sensor)
        line3, = ax1.plot(listTiRe, listSollwert, 'b', label='Sollwert')
        plt.ylabel("Temperatur in °C",fontsize=12)
        plt.legend(loc='best')
        plt.grid()
        if args.log == True:   logging.info('Diagramm Ist- und Sollwert erstellt')

        # Linie Zusatz (Temperatur oder Lesitung):
        ax2 = plt.subplot(223)                                                              # erzeugt zweiten Teilgraph
        if heizer_wahl == 'IKA':
            label_zusatz = 'Heizplatten Temperatur'
            plt.ylabel("Temperatur Heizplatte in °C",fontsize=12)
        if heizer_wahl == 'Eurotherm':
            label_zusatz = 'Ausgangsleistung'
            plt.ylabel("Ausgangsleistung Eurotherm in %",fontsize=12)
        line2, = ax2.plot(listTiRe, listZusatz, 'b', label=label_zusatz)
        plt.xlabel("Zeit in min",fontsize=12)                                               # Haben gemeinsame x-Achse
        plt.legend(loc='best')
        plt.grid()
        if args.log == True:   logging.info('Diagramm Zusatz Kurve Heizer erstellt')

        # Linien Temperatur Pyrometer und Pt100
        ax3 = plt.subplot(222)
        for name, Pyro in pyroLW.items():
            Pyro.grafik_T(ax3, listTiRe)
        for name, Pyro in pyroKW.items():
            Pyro.grafik_T(ax3, listTiRe)
        for name, pt in pt_sam.items():
            pt.grafik(ax3, listTiRe)
        plt.ylabel("Temperatur in °C",fontsize=12)
        plt.legend(loc='best')                                                          # erzeugt eine Legende am möglichst passendenden Ortes (passt sich automatisch an!)
        plt.grid()
        if args.log == True:   logging.info('Diagramm Pyrometer & Pt100-Adafruit erstellt')

        # Linien Emissionsgrad:
        ax4 = plt.subplot(224)
        for name, Pyro in pyroLW.items():
            Pyro.grafik_E(ax4, listTiRe)
        for name, Pyro in pyroKW.items():
            Pyro.grafik_E(ax4, listTiRe)
        plt.ylabel("Emissionsgrad in %",fontsize=12)
        plt.xlabel("Zeit in min",fontsize=12)
        plt.legend(loc='best')                                                          # erzeugt eine Legende am möglichst passendenden Ortes (passt sich automatisch an!)
        plt.grid()

###########################################################################
def Stop():                                                               # Befehl zum Stoppen der Heizplatte und zum Schließen und Speichern des Bildes/Graphes/Diagrammes
###########################################################################
    # Abschluss Nachricht für *Emis.txt bei Betätigung von Beenden
    if nStart == True and end == False:
        with open(Folder + '/' + FileOutNameE,"a", encoding="utf-8") as foE:
            time_of_End = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            foE.write(f'- - - Vorseitig Beenden gedrückt - {time_of_End} - - -\n')

    # Hardware stoppen:
    heizer_wahl = config['Heizer']['Auswahl']['String']
    if heizer_wahl == 'IKA':
        obj_heizer.stop_heizung()            # Stopp für die Heizplatte
        if args.log == True:   logging.info('Heizung Aus')

    # Leistungsausgang auf Null setzten bzw. Heizer abkühlen lassen:
    if heizer_wahl == 'Eurotherm':
        obj_heizer.change_SollTemp("20")
        end_OP = obj_heizer.get_power_OUT()
        if args.log == True:   logging.info(f'Heizer auf 20 °C gesetzt! OP = {end_OP}')

    # Grafik Speichern und schließen:
    if nStart == True:
        BNameHP = FileOutName.split('.')[0] + '_Bild.png'          # das .txt wird vom Datennamen abgeschnitten und dann mit einem Bild-Datei-Ende versehen
        figure.savefig(Folder + '/' + BNameHP)                     # speichert den Graf im Verzeichnis!
        print ('Output data: ', BNameHP)


#################################################################################
# Hauptprogramm:
# Variablen voreinstellen:
nStart = False          # Start noch nicht betätigt
Stop_Graph = False
end = False

# Initialisiere die Koordinatenvariablen:
xVonPt = xBestPt=  yVonPt = yBestPt = xVonHp = xBestHp = yVonHp = yBestHp = xVonPy = xBestPy = yVonPy = yBestPy = 0

# Parameterliste einlesen:
config_file = 'config_Parameter.yml'
with open(config_file) as fi:
    config = yaml.safe_load(fi)

# Extra Konsolen Parameter:
parser = argparse.ArgumentParser()
parser.add_argument('-test', help='test mode without connected instruments [optional, default=false]', action = 'store_true')                       # Test-Funktion Starten
parser.add_argument('-debug', help='debug mode - Anzeige der Befehle und Daten [optional, default=false]', action = 'store_true')                   # Debug-Funktion Starten
parser.add_argument('-dt', help='sampling steps in miliseconds [optional, default=1000]', type=int, default=1000)                                   # Abtastzeit Default einstellen
parser.add_argument('-log', help='logging the events [optional, default=false]', action = 'store_true')                                             # Soll die Events loggen

args = parser.parse_args()
parser.print_help()
print()

# Testfunktion und Debug-Funktion:
pyrometer.truth_pyro(args.test, args.debug)
heizer.truth_heiz(args.test, args.debug)
adafruit.truth_pt100(args.test, args.debug)

# Delay zwischen Senden und Abfragen:
delay_heiz = config['Delay']['Heizer']
heizer.serial_delay(delay_heiz)

# Log-datei erstellen:
if args.log:
    logging.basicConfig(filename='Logging.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S')
pyrometer.logging_on(args.log) # Muss außerhalb von If stehen, damit auch False übergeben wird!
heizer.logging_on(args.log)
adafruit.logging_on(args.log)

# Kontrolle ob es eine Emulation gibt:
emulation = config['Emulation']
heizer.emulation_on(**emulation)

# Abtastrate festlegen:
if args.dt:
    sampling_Time = args.dt

# Geräte Initialisieren:
# Heizer:
heizer_wahl = config['Heizer']['Auswahl']['String']
heizer_config = config['Heizer']['Schnittstelle']
if heizer_wahl == 'Eurotherm':
    heizer_config.update(config["Eurotherm"])
    obj_heizer = heizer.HeizerEurotherm(**heizer_config)
elif heizer_wahl == 'IKA':
    obj_heizer = heizer.HeizerPlatte(**heizer_config)
    obj_heizer.get_SaveTemp()
else:
    print(f'Der Heizer "{heizer_wahl}" existiert nicht in diesem Programm')
    quit()

# Pyrometer KW:
pyroKW = {}
if 'Pyrometer_KW' in config:
    for name, data in config['Pyrometer_KW'].items():
        pyKW = pyrometer.PyrometerKW(name, **data)
        pyroKW.update({name: pyKW})                 # Erzeugt einen Eintrag in das Dictionarie
        pyKW.anpassung(100,100)
    print() # zu Abhebung im Konsolenfesnter

# Pyrometer LW:
pyroLW = {}
nb_head = 0
if 'Pyrometer_LW' in config:
    array_data = config['Pyrometer_LW']['Schnittstelle']
    schnittstelle_LW = pyrometer.Array(**array_data)
    for name, data in config['Pyrometer_LW']['Geraete'].items():
        pyLW = pyrometer.PyrometerLW(name, schnittstelle=schnittstelle_LW.ser_py, **data)
        pyroLW.update({name: pyLW})
        pyLW.anpassung(100,100)
        nb_head = pyLW.Get_nb_of_head()
    print(f'Es gibt {nb_head} langwellige Pyrometer!\n')

# Adafruit - Pt100
pt_sam = {}
if 'Pt100' in config:
    for name, data in config['Pt100'].items():
        pt100 = adafruit.Adafruit(name, **data)
        pt_sam.update({name: pt100})
    print() # zu Abhebung im Konsolenfesnter

# Emissionsgrad Bestimmung - für Anpassung:
nEMess = 0

# Konsolen Eingabe - Rezept - welcher Ablauf soll durchgeführt werden:
StartConfig = False
loop = 0
nextTempIn = ''
TempTrep = []
TempArea = []
TempTime = []
Config_File = config['Strings']['Rezept']       # Rezept-Datei Name aus Parameterliste lesen
cp = configparser.ConfigParser()
cp.read(Config_File)
for section_name in cp.sections():                      # Die Überschriften in der datei durch gehen
    if section_name == 'Heating':                       # Unter "Heating" steht das Rezept
         for name, zeile in cp.items(section_name):
            TempTrep.append(zeile.split(',')[0])        # Erster Wert in der Zeile ist der Sollwert des Zykluses
            TempArea.append(zeile.split(',')[1])        # Zweiter Wert ist die Sollwertbereichs Grenze (Sollwert +/- Grenze)
            TempTime.append(zeile.split(',')[2])        # Dritter Wert ist die Zeit in dem der Istwert in dem Sollwertbereich sein soll
print('Start des Rezeptes')
print(f'Sollwerte         = {TempTrep}')
print(f'Sollwertbereich   = {TempArea}')
print(f'Zeiten im Bereich = {TempTime}')
print()
if args.log == True:   logging.info('Rezept Eingelesen')

# GUI öffnen:
fenster_GUI()