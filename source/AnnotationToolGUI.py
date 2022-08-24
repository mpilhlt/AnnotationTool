from __future__ import annotations
from distutils.filelist import FileList
from textwrap import wrap
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import Grid
from tkinter import filedialog
from tkinter import messagebox
import shutil
from tkinter import scrolledtext
import paramiko
from paramiko import SSHClient 
from datetime import datetime
import re
from pdf2image import convert_from_path
import os
class MySFTPClient(paramiko.SFTPClient):
    def put_dir(self, source, target):
        ''' Uploads the contents of the source directory to the target path. The
            target directory needs to exists. All subdirectories in source are 
            created under target.
        '''
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), '%s/%s' % (target, item))
            else:
                self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        ''' Augments mkdir by adding an option to not fail if the folder exists  '''
        try:
            super(MySFTPClient, self).mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise


def close_window():
    mainWindow.destroy()

def openFile():
    name = filedialog.askopenfilename() 
    #print(name)
    return name

#TODO: Allgemeine Variante zum Pfad auswählen schreiben/implementieren
#Pfad wählen
def setPath():
#    global tmpPath
    tmpPath = os.path.abspath(openFile())
    return tmpPath

#Pfad zur Dateiliste setzen
def setDateilistePfad():
    global FileListPath
    FileListPath = os.path.abspath(openFile())
    with open(FileListPath, 'r', encoding = "utf8") as f:
        DateiListe.insert(INSERT, f.read())
        DateiListe.config(state = DISABLED)
    labDateiListenPfad.config(text = FileListPath)

#Pfad zur Tagliste setzen
def setWordListPath():
    global WordListPath
    WordListPath = os.path.abspath(openFile())
    with open(WordListPath, 'r', encoding = "utf8") as f:
        TagListe.insert(INSERT, f.read())
        TagListe.config(state = DISABLED)
    labWordListPath.config(text = WordListPath)

#Pfad zum Quellordner der xml Dateien setzen
def setSourceFolder():
    global sourceFolderPath
    sourceFolderPath = filedialog.askdirectory()
    #print("Source Folder: " + sourceFolderPath)
    labSourceFolder.config(text = sourceFolderPath)

#Pfad zum Zielordner der annotierten xml Dateien setzen
def setDestinationFolder():
    global destinationFolderPath
    destinationFolderPath = filedialog.askdirectory()
    #print("Destination Folder: " + destinationFolderPath)
    labDestinationFolder.config(text = destinationFolderPath)

###########################################################
#Einlesen von Tags und Wörtern, die getaggt werden sollen
def readAnnotationData(WordListPath):
    listOfWords = open(WordListPath, 'r', encoding = "utf8").read().splitlines()
###########################################################

#Ersetzung der Wörter
def f_ersetzung(filedata, currTag, currWord):
    #resp = "auto" --> sind automatisch erstellte Tags; reicht das aber so?
    #Richtiges Format für die Tags: <term key="Alkohol">alkoholischer Getränke</term>
    #Annotiert wird:
    #Diese Bedingungen sorgen gleichzeitig dafür, dass bereits annotierte Worte nicht doppelt annotiert werden!
    #Wenn das Wort von Leerzeichen angeführt und gefolgt wird
    #a) von einem Leerzeichen
    filedata = filedata.replace(" " + currWord + " ", (" <term key=\"" + currTag + "\" resp=\"auto\">" + currWord + "</term> "))
    # #b) von einem Komma
    filedata = filedata.replace(" " + currWord + ",", (" <term key=\"" + currTag + "\" resp=\"auto\">"+ currWord + "</term>,"))
    #c) von einem Punkt (= Satzende)
    filedata = filedata.replace(" " + currWord + ".", (" <term key=\"" + currTag + "\" resp=\"auto\">"+ currWord + "</term>."))
    #d) von einem Ausrufezeichen
    filedata = filedata.replace(" " + currWord + "!", (" <term key=\"" + currTag + "\" resp=\"auto\">"+ currWord + "</term>!"))
    #e) von einem Fragezeichen
    filedata = filedata.replace(" " + currWord + "?", (" <term key=\"" + currTag + "\" resp=\"auto\">"+ currWord + "</term>?"))

def f_regex_ersetzung(filedata, currTag, currWord):
    #ersetzung mit regex
    #AUs der Mail von Polina
    # Fall A: Linebreak im Wort "Maschine"
    # Ma<lb break="no"
    #           facs="#facs_3_l118" n="N000"/>schine
    #Regex dafür: <lb break="no"\n*\s* facs=(.*)"/>

    # Fall B: Seiten- und Pagebreak
    # 3. des<pb break="no" facs="#facs_6" n="48" xml:id="img_0006"/><lb break="no" facs="#facs_6_l31" n="N000"/>fallsige

    #resp = "auto" --> sind automatisch erstellte Tags; reicht das aber so?
    #Richtiges Format für die Tags: <term key="Alkohol">alkoholischer Getränke</term>
    #Annotiert wird:
    #Diese Bedingungen sorgen gleichzeitig dafür, dass bereits annotierte Worte nicht doppelt annotiert werden!
    #Wenn das Wort von Leerzeichen angeführt und gefolgt wird
    #a) von einem Leerzeichen
    filedata = filedata.replace(" " + currWord + " ", (" <term key=\"" + currTag + "\" resp=\"auto\">" + currWord + "</term> "))
    # #b) von einem Komma
    filedata = filedata.replace(" " + currWord + ",", (" <term key=\"" + currTag + "\" resp=\"auto\">"+ currWord + "</term>,"))
    #c) von einem Punkt (= Satzende)
    filedata = filedata.replace(" " + currWord + ".", (" <term key=\"" + currTag + "\" resp=\"auto\">"+ currWord + "</term>."))
    #d) von einem Ausrufezeichen
    filedata = filedata.replace(" " + currWord + "!", (" <term key=\"" + currTag + "\" resp=\"auto\">"+ currWord + "</term>!"))
    #e) von einem Fragezeichen
    filedata = filedata.replace(" " + currWord + "?", (" <term key=\"" + currTag + "\" resp=\"auto\">"+ currWord + "</term>?"))

    ######Ersetzungen mit Linebreaks
    #Pattern erzeugen, das ersetzt werden soll: space + currWord + space --> und irgendwo da drin kann ein Ausdruck der Form <lb break="no"\n*\s* facs=(.*)"/> liegen

    # Fall A: Linebreak im Wort "Maschine"
    # Ma<lb break="no"
    #           facs="#facs_3_l118" n="N000"/>schine
    #Regex dafür: <lb break="no"\n*\s* facs=(.*)"/>



    #baue tmpString space+currWord+space
    #gehe tmpString durch: wenn zwischen space+1. Buchstaben, 1./2. Buchstaben, etc. ein lb kommt --> ersetzen

    tmpString = " " + currWord + " "
    for i in range(0,len(tmpString)):
        print(i)

#def copyToServer(ip, port, user, pwd, localpath, remotepath):
def copyToServer(HOST, PORT, USERNAME, PASSWORD, source_path, target_path):
    transport = paramiko.Transport((HOST, PORT))
    transport.connect(username=USERNAME, password=PASSWORD)
    sftp = MySFTPClient.from_transport(transport)
    sftp.mkdir(target_path, ignore_existing=True)
    sftp.put_dir(source_path, target_path)
    sftp.close()


#Hauptfunktion: Annotation starten
def mainFkt(FileListPath, WordListPath, destinationFolderPath, sourceFolderPath):

    ###########################################################
    #Backups anlegen
    # def BackupXML(ListFilename):
    #     import shutil #Bibliothek zum Dateien kopieren
    #     fileList = open(ListFilename, 'r', encoding = "utf8").read().splitlines()
    #     for line in fileList:
    #         shutil.copyfile((line+".xml"),(line+".xml.backup"))
    ###########################################################

    ###########################################################
    #Backups einspielen (nur fürs Testen)
    # def restoreXMLBackups(ListFilename):
    #     import shutil #Bibliothek zum Dateien kopieren
    #     fileList = open(ListFilename, 'r', encoding = "utf8").read().splitlines()
    #     for line in fileList:
    #         shutil.copyfile((line+".xml.backup"),(line+".xml"))
    ###########################################################

    #Pfade für Dateien

    #Nur im Testen: Backups wiederherstellen (später Backups anlegen!)
    #restoreXMLBackups(FileListPath)
    #BackupXML(FileListPath)

    #Gehe alle Dateien aus der fileList durch
    fileList = open(FileListPath, 'r', encoding = "utf8").read().splitlines()
    #print(fileList)

    for currFile in fileList:
        # Aktuelle Datei einlesen
        if os.name == "nt":
            with open((sourceFolderPath + "\\" + currFile+".xml"), 'r', encoding = "utf8") as file :
                filedata = file.read()
        elif os.name == "posix":
            #print("Curr File: " + sourceFolderPath  + "/" + currFile + ".xml")
            with open((sourceFolderPath  + "/" + currFile + ".xml"), 'r', encoding = "utf8") as file :
                filedata = file.read()

        # Zeichenkette ersetzen
        ### Einlesen von Tags und Wörtern
        wordList = open(WordListPath, 'r', encoding = "utf8").read().splitlines()
        #Gehe alle Wörter durch
        for currWord in wordList:
            #Wenn aktuelles Wort mit # beginnt, setze aktuelles Tag darauf
            if currWord.startswith("#"):
                currTag = currWord[1:] #Entferne das # (=den 1. char des strings)
            #Wenn nicht, ersetze aktuelles Wort mit dem Tag
            else:
                f_ersetzung(filedata, currTag, currWord)
                #Annotiert wird:
                #Diese Bedingungen sorgen gleichzeitig dafür, dass bereits annotierte Worte nicht doppelt annotiert werden!
                #Wenn das Wort von Leerzeichen angeführt und gefolgt wird
                #a) von einem Leerzeichen
                # filedata = filedata.replace(" " + currWord + " ", (" <term key=\"" + currTag + "\">" + currWord + "</term> "))
                # #Richtiges Format für die Tags:                <term key="Alkohol">alkoholischer Getränke</term>
                # #b) von einem Komma
                # filedata = filedata.replace(" " + currWord + ",", (" <term key=\"" + currTag + "\">"+ currWord + "</term>,"))
                # #c) von einem Punkt (= Satzende)
                # filedata = filedata.replace(" " + currWord + ".", (" <term key=\"" + currTag + "\">"+ currWord + "</term>."))
                # #d) von einem Ausrufezeichen
                # filedata = filedata.replace(" " + currWord + "!", (" <term key=\"" + currTag + "\">"+ currWord + "</term>!"))
                # #e) von einem Fragezeichen
                # filedata = filedata.replace(" " + currWord + "?", (" <term key=\"" + currTag + "\">"+ currWord + "</term>?"))
        
        #Checken, ob Zielordner existiert, sonst anlegen
        if os.path.exists(destinationFolderPath) == False:
            os.makedirs(destinationFolderPath)
        
        #Annotierte Dateien schreiben
        if os.name == "nt":
            with open(destinationFolderPath  + "\\" +  currFile + ".xml", "w", encoding = "utf8") as file:
                file.write(filedata)
                #print("Wrote File: " + destinationFolderPath + "\\" + currFile+ ".xml")
        elif os.name == "posix":
            with open(destinationFolderPath  + "/" +  currFile + ".xml", "w", encoding = "utf8") as file:
                file.write(filedata)
                #print("Wrote File: " + destinationFolderPath + "/" + currFile + ".xml")



 
# def setPath():
# #    global tmpPath
#     tmpPath = os.path.abspath(openFile())
#     return tmpPath

################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
#Kreiert Fenster

mainWindow = Tk()
mainWindow.title("Annotations-Tool NsRdMi") #Fenstertitel
mainWindow.geometry("1000x600") #Fenstergröße: Breite x Höhe
mainWindow.minsize(width = 800, height = 800) #Mindestgrößen
#root.maxsize(width = 1000, height = 750) #Maximalgrößen
#mainWindow.resizable(width = False, height = False) #Sperre Veränderbarkeit der Größe

tabControl = ttk.Notebook(mainWindow)
tabSRCconvert = ttk.Frame(tabControl)
tabAnnotation = ttk.Frame(tabControl)
tabXMLmanual = ttk.Frame(tabControl)
tabOCRSRVcopy = ttk.Frame(tabControl)


tabControl.add(tabSRCconvert, text="Quellen konvertieren")
#TODO: Import von CSV statt aus txt
tabControl.add(tabAnnotation, text = "Quellen annotieren")
tabControl.add(tabXMLmanual, text = "Manuelle Transkription in XML")


tabControl.pack(expand=1, fill="both")

#ttk.Label(tabAnnotation, text="Welcome to GeeksForGeeks").grid(column=0, row=0, padx=30, pady=30)
#ttk.Label(tabSRCconvert, text="Hier kann man Quellen konvertieren - von PDF in Einzelbilder.").grid(column=0, row=0, columnspan = 2, padx=30, pady=30)
#ttk.Label(tabXMLmanual, text="Hier kann man Quellen manuell in TEI XML transkribieren.").grid(column=0, row=0, padx=30, pady=30)

FileListPath = "Keine Dateiliste ausgewählt"
WordListPath = "Keine Tagliste ausgewählt"
sourceFolderPath = "Kein Quellordner ausgewählt"
destinationFolderPath = "Kein Zielordner ausgewählt"

#Anzeige der ausgewählten Dateien
global labDateiListenPfad
DateiListe = Text(tabAnnotation)
labDateiListenPfad = tk.Label(tabAnnotation, text = FileListPath)

global labWordListPath
TagListe = Text(tabAnnotation)
labWordListPath = tk.Label(tabAnnotation, text = WordListPath)

BeschreibungAllgemein = tk.Label(tabAnnotation, text = "Die beiden Spalten zeigen die zu bearbeitenden Dateien links und die zu setzenden Tags und ihre dazugehörigen Signalworte rechts. \n Über die darunterstehenden Buttons können die jeweiligen Dateien sowie der Quell- und Zielordner angegeben werden.", wraplength=800, justify=LEFT)

BeschreibungDateiliste = tk.Label(tabAnnotation, text = "In diese Liste müssen die zu annotierenden Dateien in einzelnen Zeilen, ohne Dateiendung (d.h. nur die ID) eingetragen werden.", wraplength=400,justify=LEFT)

BeschreibungTagliste = tk.Label(tabAnnotation, text = "In die Tagliste müssen die Tags und dazugehörigen zu markierenden Worte in einzelnen Zeilen wie folgt eingetragen werden:\n Das # markiert ein Schlagwort, alle bis zum nächsten # folgenden Worte werden mit diesem annotiert. Es werden *nur* die angegebenen Schreibweisen annotiert, keine Abwandlungen davon (d.h. Pause != Pausen). Sobald das nächste # folgt, wird ein neues Tag annotiert.", wraplength=400,justify=LEFT)

#Button: Dateiliste auswählen
btnDateiliste = tk.Button(tabAnnotation, text = "Dateiliste auswählen", command = lambda: [setDateilistePfad()])

#Button: Tagliste auswählen
btnWordList = tk.Button(tabAnnotation, text = "Tagliste auswählen", command = lambda: [setWordListPath()])

#Button: Quellordner
btnChooseSourceFolder = tk.Button(tabAnnotation, text = "Quellordner auswählen", command = lambda: [setSourceFolder()])
global labSourceFolder
labSourceFolder = tk.Label(tabAnnotation, text = sourceFolderPath)


#Button: Zielordner
btnChooseDestinationFolder = tk.Button(tabAnnotation, text = "Zielordner wählen", command = lambda: [setDestinationFolder()])
global labDestinationFolder
labDestinationFolder = tk.Label(tabAnnotation, text = destinationFolderPath)

#Button, um die Annotation zu starten
btnAnnotieren = tk.Button(tabAnnotation, text="Annotation starten", command = lambda: mainFkt(FileListPath, WordListPath, destinationFolderPath, sourceFolderPath))

#Abbrechen-Button
btnAbbrechen = tk.Button(tabAnnotation, text="Schließen", command = close_window)

################################################################################
### Manuelle Transkription
#TODO: Keep indentation of original TEI XML file
labXMLmanualDescr = tk.Label(tabXMLmanual, text = "Hier können Quellen manuell annotiert werden. Diese Funktion ist insbesondere für die Quellen der DMZ gedacht.", wraplength=800,justify=LEFT)
labXMLmanualDescr.grid(row = 0, column = 0, padx = 5, pady = 5, columnspan= 2)

def setXMLDestinationFolder():
    global XMLdestinationFolderPath
    XMLdestinationFolderPath = filedialog.askdirectory()
    #print("Destination Folder: " + destinationFolderPath)
    labXMLDestinationFolder.config(text = XMLdestinationFolderPath)

btnChooseXMLDestFolder = tk.Button(tabXMLmanual, text = "Exportordner auswählen", command = lambda: [setXMLDestinationFolder()])
btnChooseXMLDestFolder.grid(row = 1, column = 1, padx = 5, pady = 5)

global XMLlabDestinationFolder
labXMLDestinationFolder = tk.Label(tabXMLmanual, text = "")
labXMLDestinationFolder.grid(row = 1, column = 0, padx = 5, pady = 5)

# 2. Daten der Quelle eingeben
labSRCID = tk.Label(tabXMLmanual, text = "Quellen-ID:", justify = LEFT)
labSRCID.grid(row = 2, column = 0, padx = 5, pady = 5)
SRCIDbox = Entry(tabXMLmanual)
SRCIDbox.insert(END, "99999") #default value
SRCIDbox.grid(row = 2, column = 1, padx = 5, pady = 5)

labWHEN = tk.Label(tabXMLmanual, text = "Datum:", justify = LEFT)
labWHEN.grid(row = 3, column = 0, padx = 5, pady = 5)
WHENlabel = tk.Label(tabXMLmanual, text = datetime.now().strftime("%Y-%m-%d+%H:%M"), justify = LEFT)
WHENlabel.grid(row = 3, column = 1, padx = 5, pady = 5)

labSRCYEAR = tk.Label(tabXMLmanual, text = "Jahr der Quelle:", justify = LEFT)
labSRCYEAR.grid(row = 4, column = 0, padx = 5, pady = 5)
SRCYEARbox = Entry(tabXMLmanual)
SRCYEARbox.insert(END, "9999") #default value
SRCYEARbox.grid(row = 4, column = 1, padx = 5, pady = 5)

labSRCBIBL = tk.Label(tabXMLmanual, text = "Quellennachweis (inkl. Seite):", justify = LEFT)
labSRCBIBL.grid(row = 5, column = 0, padx = 5, pady = 5)
SRCBIBLbox = Entry(tabXMLmanual)
SRCBIBLbox.insert(END, "Beispielzeitschrift, Ausgabe 9999, 01.01.9999, S. 99") #default value
SRCBIBLbox.grid(row = 5, column = 1, padx = 5, pady = 5)

labSHORTTITLE = tk.Label(tabXMLmanual, text = "Kurztitel (AO_FIRMA_ORT_JAHR):", justify = LEFT)
labSHORTTITLE.grid(row = 6, column = 0, padx = 5, pady = 5)
SHORTTITLEbox = Entry(tabXMLmanual)
SHORTTITLEbox.insert(END, "AO_Beispielfirma_Beispielort_9999") #default value
SHORTTITLEbox.grid(row = 6, column = 1, padx = 5, pady = 5)

labTITLE = tk.Label(tabXMLmanual, text = "Offizieller Titel:", justify = LEFT)
labTITLE.grid(row = 7, column = 0, padx = 5, pady = 5)
TITLEbox = Entry(tabXMLmanual)
TITLEbox.insert(END, "Arbeitsordnung der Beispielfirma am Beispielort vom 1.1.9999") #default value
TITLEbox.grid(row = 7, column = 1, padx = 5, pady = 5)

labSRCTEXT = tk.Label(tabXMLmanual, text = "Text der Quelle:", justify = LEFT)
labSRCTEXT.grid(row = 8, column = 0, padx = 5, pady = 5, columnspan=2)
SRCTEXTbox = scrolledtext.ScrolledText(tabXMLmanual, wrap=tk.WORD, width=100, height=20)
SRCTEXTbox.grid(row = 9, column = 0, padx = 5, pady = 5, columnspan=2)

#Button um XML Vorlagedatei auszuwählen
labXMLVorlage = tk.Label(tabXMLmanual, text = "", justify = LEFT)
labXMLVorlage.grid(row = 10, column = 0, padx = 5, pady = 5)

def setXMLVorlage():
    global XMLVorlagePath
    global XMLVorlageText
    XMLVorlagePath = filedialog.askopenfilename()
    labXMLVorlage.config(text = XMLVorlagePath)

btnChooseXMLVorlage = tk.Button(tabXMLmanual, text = "XML-Vorlage wählen", command = lambda: [setXMLVorlage()])
btnChooseXMLVorlage.grid(row = 10, column = 1, padx = 5, pady = 5)


# 4. Speichern-Button!
btnSaveXMLManual = tk.Button(tabXMLmanual, text = "Speichern", command = lambda: [saveXMLManual()])
btnSaveXMLManual.grid(row = 11, column = 0, padx = 5, pady = 5, columnspan=2)

def saveXMLManual():
    #1. Get all the data from entry fields
    SRCID = SRCIDbox.get()
    WHEN = WHENlabel.cget("text")
    SRCYEAR = SRCYEARbox.get()
    SRCBIBL = SRCBIBLbox.get()
    SHORTTITLE = SHORTTITLEbox.get()
    TITLE = TITLEbox.get()

    #replace linebreaks, and symbol etc in SRCTEXT with XML linebreaks (depending on OS!)
    SRCTEXT = SRCTEXTbox.get('1.0', tk.END)
    if os.name == "posix":
        SRCTEXT = SRCTEXT.replace("\n", "<lb/>\n")
        SRCTEXT = SRCTEXT.replace("&", "&amp;")
    elif os.name == "nt":
        SRCTEXT = SRCTEXT.replace("\r\n","<lb/>\r\n")
        SRCTEXT = SRCTEXT.replace("&", "&amp;")

    
    #Open XML Vorlage file
    with open(XMLVorlagePath, "r", encoding = "utf8") as file:
        XMLVorlageText = file.read()
    #4. replace variables in XML data
    XMLVorlageText = XMLVorlageText.replace("$SRCID", SRCID)
    XMLVorlageText = XMLVorlageText.replace("$WHEN", WHEN)
    XMLVorlageText = XMLVorlageText.replace("$SRCYEAR", SRCYEAR)
    XMLVorlageText = XMLVorlageText.replace("$SRCBIBL", SRCBIBL)
    XMLVorlageText = XMLVorlageText.replace("$SHORTTITLE", SHORTTITLE)
    XMLVorlageText = XMLVorlageText.replace("$TITLE", TITLE)
    XMLVorlageText = XMLVorlageText.replace("$SRCTEXT", SRCTEXT)

    #5. Write new XML File for current source
    #open text file
    if os.name == "posix":
        newXMLSource = open((XMLdestinationFolderPath + "/" + SRCID + ".xml"), "w")
    elif os.name == "nt":
        newXMLSource = open((XMLdestinationFolderPath + "\\" + SRCID + ".xml"), "w")
    #write string to file
    newXMLSource.write(XMLVorlageText)
    #close file
    newXMLSource.close()

# $SRCID: 00123
# $WHEN: YYYY-MM-DD+HH:MM
# $SRCYEAR: YYYY
# $SRCBIBL: Quellennachweis
# $SHORTTITLE: AO_…. —> Kurztitel
# $TITLE: Musterarbeitsordnung…
# $SRCTEXT

################################################################################
### PDFs zu Einzelbildern machen
def fktCONVpdf2img():
    currPDF = convert_from_path(pdfSRCpath)
    #dateinamen bekommen
    pdfFILEname = os.path.basename(pdfSRCpath).split(".")[0]
    #Ordnerstruktur anlegen
    pdfFOLDERname = os.path.dirname(pdfSRCpath)

    #Unterscheidung Windows/POSIX
    if os.name == "posix":
        if os.path.exists(os.path.dirname(pdfSRCpath) + "/" + pdfFILEname) == False:
            os.makedirs(os.path.dirname(pdfSRCpath) + "/" + pdfFILEname) #lege Ordner im Verzeichnis der PDF Datei an, der benannt ist wie die PDF datei
            os.makedirs(os.path.dirname(pdfSRCpath) + "/" + pdfFILEname + "/input")
            os.makedirs(os.path.dirname(pdfSRCpath) + "/" + pdfFILEname + "/processing") #lege die beiden anderen Ordner an, die zur Verarbeitung durch ocr4all nötig sind
        elif os.path.exists(os.path.dirname(pdfSRCpath) + "/" + pdfFILEname) == True: #Wenn ORdner vorhanden, wird der gelöscht und neu geschrieben
            #lösche Verzeichnis
            shutil.rmtree(os.path.dirname(pdfSRCpath) + "/" + pdfFILEname)
            #Funktion erneut aufrufen
            fktCONVpdf2img()
    elif os.name == "nt":
        if os.path.exists(os.path.dirname(pdfSRCpath) + "\\" + pdfFILEname) == False:
            os.makedirs(os.path.dirname(pdfSRCpath) + "\\" + pdfFILEname) #lege Ordner im Verzeichnis der PDF Datei an, der benannt ist wie die PDF datei
            os.makedirs(os.path.dirname(pdfSRCpath) + "\\" + pdfFILEname + "\\input")
            os.makedirs(os.path.dirname(pdfSRCpath) + "\\" + pdfFILEname + "\\processing") #lege die beiden anderen Ordner an, die zur Verarbeitung durch ocr4all nötig sind
        elif os.path.exists(os.path.dirname(pdfSRCpath) + "\\" + pdfFILEname) == True: #Wenn ORdner vorhanden, wird der gelöscht und neu geschrieben
            #lösche Verzeichnis
            shutil.rmtree(os.path.dirname(pdfSRCpath) + "\\" + pdfFILEname)
            #Funktion erneut aufrufen
            fktCONVpdf2img()

    for i in range(len(currPDF)):
        if os.name == "posix":
        #BEnnennt die Seiten: ID (5 Stellen) _ 0001, 0002, etc.
            currPDF[i].save(os.path.dirname(pdfSRCpath) + "/" + pdfFILEname + "/input/" + pdfFILEname[:5] + "_" + str(i+1).zfill(4) +".jpg", "JPEG")
        elif os.name == "nt":
            currPDF[i].save(os.path.dirname(pdfSRCpath) + "\\" + pdfFILEname + "\\input\\" + pdfFILEname[:5] + "_" + str(i+1).zfill(4) +".jpg", "JPEG")

#Pfad zum Quellordner der xml Dateien setzen
def setPDFsrcPath():
    #Pfad bekommen
    global pdfSRCpath
    pdfSRCpath = filedialog.askopenfilename()
    labPDFSRCpath.config(text = pdfSRCpath) #Label ändern

#TAB SRC convert
labConvertSRC = tk.Label(tabSRCconvert, text = "Bitte die PDF-Datei auswählen")

btnChosePDFSRC = tk.Button(tabSRCconvert, text = "PDF-Datei auswählen", command = lambda: [setPDFsrcPath()])
btnChosePDFSRC.grid(row = 2, column = 2, padx = 5, pady = 5)

labPDFSRCpath = tk.Label(tabSRCconvert)
labPDFSRCpath.grid(row = 2, column = 1, padx = 5, pady = 5)

btnConvertPDF = tk.Button(tabSRCconvert, text = "PDF konvertieren", command = lambda: [fktCONVpdf2img()])
btnConvertPDF.grid(row = 3, column = 1, columnspan = 2, padx = 5, pady = 5)

#global labSourceFolder
#labSourceFolder = tk.Label(tabAnnotation, text = sourceFolderPath)


################################################################################
#TAB Auf/vom OCR Server kopieren
tabControl.add(tabOCRSRVcopy, text = "Daten auf den OCR Server kopieren")
labUPLOADintro = tk.Label(tabOCRSRVcopy, text = "Der Inhalt des ausgewählten Ordners wird auf den OCR-Server hochgeladen. In diesem Ordner müssen die Dateien also in der Dafür notwendigen Struktur (00123_BLA/input/HierhinDieBilder; 00123_BLA/processing/) vorhanden sein. Falls die Bilder über dieses Tool bearbeitet wurden, ist diese Ordnerstruktur bereits vorhanden.", wraplength=800,justify=LEFT)
labUPLOADintro.grid(row = 1, column = 1, columnspan = 2, padx = 5, pady = 5)
# ttk.Label(tabOCRSRVcopy, text="Hier können Quellen auf den OCR-Server kopiert werden.").grid(column=0, row=0, padx=30, pady=30)

labUPLOADpath = tk.Label(tabOCRSRVcopy, text = "Bitte den Pfad auswählen auswählen")
labUPLOADpath.grid(row = 2, column = 1, padx = 5, pady = 5)

btnChoseUPLOADpath = tk.Button(tabOCRSRVcopy, text = "Pfad auswählen", command = lambda: [setUPLOADpath()])
btnChoseUPLOADpath.grid(row = 2, column = 2, padx = 5, pady = 5)

#Ablauf
# 1. Ordner auswählen --> multi folder
#TODO: Mehrere Ordner auswählbar machen!
#Pfad zum Quellordner der xml Dateien setzen
def setUPLOADpath():
    #Pfad bekommen
#    global uploadPATH
    global source_path
#    uploadPATH = filedialog.askdirectory()
    source_path = filedialog.askdirectory()
    labUPLOADpath.config(text = source_path) #Label ändern

# 2. SSH verbindung

#set ssh credentials
labIP = tk.Label(tabOCRSRVcopy, text = "IP-Adresse:", justify = LEFT)
labIP.grid(row = 4, column = 1, padx = 5, pady = 5)
sshIPbox = Entry(tabOCRSRVcopy)
sshIPbox.grid(row = 4, column = 2, padx = 5, pady = 5)

labPORT = tk.Label(tabOCRSRVcopy, text = "Port:", justify = LEFT)
labPORT.grid(row = 5, column = 1, padx = 5, pady = 5)
sshPORTbox = Entry(tabOCRSRVcopy)
sshPORTbox.grid(row = 5, column = 2, padx = 5, pady = 5)

labUSER = tk.Label(tabOCRSRVcopy, text = "Benutzer:", justify = LEFT)
labUSER.grid(row = 6, column = 1, padx = 5, pady = 5)
sshUSERbox = Entry(tabOCRSRVcopy)
sshUSERbox.grid(row = 6, column = 2, padx = 5, pady = 5)

labPWD = tk.Label(tabOCRSRVcopy, text = "Passwort:", justify = LEFT)
labPWD.grid(row = 7, column = 1, padx = 5, pady = 5)
sshPWDbox = Entry(tabOCRSRVcopy, show = "*")
sshPWDbox.grid(row = 7, column = 2, padx = 5, pady = 5)


btnUPLOAD = tk.Button(tabOCRSRVcopy, text = "Hochladen", command = lambda: [copyToServer(sshIPbox.get(), int(sshPORTbox.get()), sshUSERbox.get(), sshPWDbox.get(), source_path, "/var/data/ocr4all/data")])

btnUPLOAD.grid(row = 8, column = 1, columnspan = 2, padx = 5, pady = 5)

################################################################################
#TAB Annotation
# Grid bauen: jede Spalte bekommt ein Gewicht; so werden sie auf die Breite verteilt
tabAnnotation.columnconfigure(0, weight = 1)
tabAnnotation.columnconfigure(1, weight = 1)

#Widgets anordnen
BeschreibungAllgemein.grid(column = 0, row = 0, padx=5, pady=5, columnspan=2)

BeschreibungDateiliste.grid(column = 0, row = 1, padx=5, pady=5)
BeschreibungTagliste.grid(column = 1, row = 1, padx=5, pady=5)

DateiListe.grid(column=0, row=2, padx=5, pady=5)
TagListe.grid(column=1, row=2, padx=5, pady=5)

btnDateiliste.grid(column = 0, row = 3)
btnWordList.grid(column = 1, row = 3)

labWordListPath.grid(column=1, row=4, padx=5, pady=5)
labDateiListenPfad.grid(column=0, row=4, padx=5, pady=5)

btnChooseSourceFolder.grid(column = 0, row = 5)
btnChooseDestinationFolder.grid(column = 1, row = 5)

labSourceFolder.grid(column=0, row=6, padx=5, pady=5)
labDestinationFolder.grid(column=1, row=6, padx=5, pady=5)

btnAnnotieren.grid(column=0, row=7)
btnAbbrechen.grid(column=1, row=7)

#Mainloop-Methode --> "Eventloop" --> muss aufgerufen werden --> Endlosschleife, die Interaktionen mit GUI abfängt
mainWindow.mainloop()
#Was hier drunter steht, wird erstmal nicht ausgeführt!!!!