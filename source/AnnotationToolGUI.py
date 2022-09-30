from __future__ import annotations

import os
import shutil
import tkinter as tk
from datetime import datetime
from distutils.filelist import FileList
from pathlib import Path
from stat import S_IMODE, S_ISDIR, S_ISREG
from textwrap import wrap
from tkinter import *
from tkinter import Grid, filedialog, scrolledtext, ttk

import fitz

import paramiko
import pysftp

from teivorlage import TEIVorlage


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

######

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
    #geöffnete FileList im entsprechenden Feld des Programmes anzeigen, damit man da manuell drin rumschreiben kann
    with open(FileListPath, 'r', encoding = "utf8") as f:
        #DateiListe.insert(INSERT, f.read())
        #DateiListe.config(state = DISABLED)
        boxDateiliste.insert(INSERT, f.read())
    labDateiListenPfad.config(text = FileListPath)


#Pfad zur Tagliste setzen
def setWordListPath():
    global WordListPath
    WordListPath = os.path.abspath(openFile())
    with open(WordListPath, 'r', encoding = "utf8") as f:
        #TagListe.insert(INSERT, f.read())
        #TagListe.config(state = DISABLED)
        boxWordlist.insert(INSERT, f.read())
    labDateiListenPfad.config(text = FileListPath)
    labWordListPath.config(text = WordListPath)

#Pfad zum Quellordner der xml Dateien setzen
def setSourceFolder():
    global sourceFolderPath
    global destinationFolderPath

    sourceFolderPath = filedialog.askdirectory()
    print("dest path: " + destinationFolderPath)
    labSourceFolder.config(text = sourceFolderPath)

    #if sourceFolderPath == False: #wenn kein Source Ordner ausgewählt, default destination path setzen, der abhängt vom source path
    if os.name == "nt":
        destinationFolderPath = sourceFolderPath + "\\annotierte_TEI_Dateien"
    elif os.name == "posix":
        destinationFolderPath = sourceFolderPath + "/annotierte_TEI_Dateien"
        print("dest folder:" + destinationFolderPath)
    print("dest path: " + destinationFolderPath)
    labDestinationFolder.config(text = destinationFolderPath)

#Pfad zum Zielordner der annotierten xml Dateien setzen
def setDestinationFolder():
    global destinationFolderPath
    destinationFolderPath = filedialog.askdirectory()
    labDestinationFolder.config(text = destinationFolderPath)
    print("dest folder set specifically")

###########################################################
#Einlesen von Tags und Wörtern, die getaggt werden sollen
def readAnnotationData(WordListPath):
    listOfWords = open(WordListPath, 'r', encoding = "utf8").read().splitlines()
###########################################################

###########################################################
def AutoAnnotation(FileListPath, WordListPath, destinationFolderPath, sourceFolderPath):
    #Gehe alle Dateien aus der fileList durch
    fileList = boxDateiliste.get('1.0', tk.END).splitlines() #hole den aktuellen boxDateiliste, um den zu verarbeiten (beginnt beim ersten Zeichen, endet am Ende der Textbox; dann in Zeilen splitten)

    for currFile in fileList:
        # Aktuelle Datei einlesen
        if os.name == "nt":
            with open((sourceFolderPath + "\\" + currFile + ".xml"), 'r', encoding = "utf8") as file :
                filedata = file.read()
        elif os.name == "posix":
            print("Curr File: " + sourceFolderPath  + "/" + currFile + ".xml")
            with open((sourceFolderPath  + "/" + currFile + ".xml"), 'r', encoding = "utf8") as file :
                filedata = file.read()

        # Zeichenkette ersetzen
        ### Einlesen von Tags und Wörtern
        wordList = boxWordlist.get('1.0', tk.END).splitlines()

        #Gehe alle Wörter durch
        for currWord in wordList:
            #Wenn aktuelles Wort mit # beginnt, setze aktuelles Tag darauf
            if currWord.startswith("#"):
                currTag = currWord[1:] #Entferne das # (=den 1. char des strings)
            #Wenn nicht, ersetze aktuelles Wort mit dem Tag
            else:
                #print("annotating " + currWord + " with the tag #" + currTag)
                #f_ersetzung(filedata, currTag, currWord)
                filedata = filedata.replace(" " + currWord + " ", (" <term key=\"" + currTag + "\" resp=\"auto\">" + currWord + "</term> "))
                #print(filedata)
                # #b) von einem Komma
                filedata = filedata.replace(" " + currWord + ",", (" <term key=\"" + currTag + "\" resp=\"auto\">"+ currWord + "</term>,"))
                #c) von einem Punkt (= Satzende)
                filedata = filedata.replace(" " + currWord + ".", (" <term key=\"" + currTag + "\" resp=\"auto\">"+ currWord + "</term>."))
                #d) von einem Ausrufezeichen
                filedata = filedata.replace(" " + currWord + "!", (" <term key=\"" + currTag + "\" resp=\"auto\">"+ currWord + "</term>!"))
                #e) von einem Fragezeichen
                filedata = filedata.replace(" " + currWord + "?", (" <term key=\"" + currTag + "\" resp=\"auto\">"+ currWord + "</term>?"))

        
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

#def copyToServer(ip, port, user, pwd, localpath, remotepath):
def copyToServer(HOST, PORT, USERNAME, PASSWORD, source_path, target_path):
    transport = paramiko.Transport((HOST, PORT))
    transport.connect(username=USERNAME, password=PASSWORD)
    sftp = MySFTPClient.from_transport(transport)
    sftp.mkdir(target_path, ignore_existing=True)
    sftp.put_dir(source_path, target_path)
    sftp.close()

################################################################################
#Kreiert Fenster

mainWindow = Tk()
mainWindow.title("AnnotationTool NsRdMi, v 0.9.1") #Fenstertitel
mainWindow.geometry("1200x800") #Fenstergröße: Breite x Höhe

#ttk.Notebook --> mehrere Reiter (Tabs) im Fenster
tabControl = ttk.Notebook(mainWindow, width=2000, height=200)

tabSRCconvert = ttk.Frame(tabControl)
tabAnnotation = ttk.Frame(tabControl)
tabOCRSRVdownload = ttk.Frame(tabControl)
tabXMLmanual = ttk.Frame(tabControl)
tabOCRSRVcopy = ttk.Frame(tabControl)


################################################################################
#Reihenfolge der Reiter im Programm
tabControl.add(tabSRCconvert, text="PDF in Einzelbilder aufteilen")
tabControl.add(tabOCRSRVcopy, text = "Einzelbilder auf OCR Server hochladen")
tabControl.add(tabOCRSRVdownload, text = "Einzelbilder vom OCR Server runterladen")
tabControl.add(tabAnnotation, text = "Quellen automatisch annotieren")
tabControl.add(tabXMLmanual, text = "Quellen manuell transkribieren")

#Einstellungen für die Reiter
tabControl.pack(expand=True, fill=tk.BOTH)


################################################################################
"""
PDFs zu Einzelbildern
"""

#Pfad zum Quellordner der PDF Dateien setzen
def setPDFsrcPath():
    #Pfad bekommen
    global pdfSRCpath
    pdfSRCpath = filedialog.askopenfilename()
    labPDFSRCpath.config(text = pdfSRCpath) #Label ändern

def fktCONVpdf2img():
    currPDF = os.path.abspath(pdfSRCpath)
    #dateinamen bekommen
    pdfFILEname = os.path.basename(pdfSRCpath).split(".")[0]
    #Ordnerstruktur anlegen
    pdfFOLDERname = os.path.dirname(pdfSRCpath)

    #Ordner anlegen
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

    #konvertieren
    #iterate through the pages of the document and create a RGB image of the page
    for page in fitz.open(pdfSRCpath):
        pix = page.get_pixmap()
        if os.name == "posix":
            index = "%i" % page.number
            pix.save(os.path.dirname(pdfSRCpath) + "/" + pdfFILEname + "/input/" + pdfFILEname[0:5] + "-" + str(index).zfill(4) + ".png")
        elif os.name == "nt":
            index = "%i" % page.number
            pix.save(os.path.dirname(pdfSRCpath) + "\\" + pdfFILEname + "\\input\\" + pdfFILEname[0:5] + "-" + str(index).zfill(4) + ".png" )

#################################################################################################################################################

#TAB SRC convert
labConvertDescr = tk.Label(tabSRCconvert, text = "In diesem Reiter können PDF-Dateien, wie sie z.B. vom Digitalisierungsdienst eines Archivs kommen, in einzelne Bilder zerlegt werden, um sie dann auf dem ocr4all-Server zu verarbeiten. Dies ist noch *nicht* der OCR- oder Annotations-Prozess, sondern lediglich die Konversion einer PDF-Datei in mehrere einzelne Bilddateien.", wraplength=800, justify=LEFT)
labConvertDescr.grid(row = 1, column = 1, columnspan = 2, padx = 5, pady = 5)

labPDFSRCpath = tk.Label(tabSRCconvert)
labPDFSRCpath.grid(row = 2, column = 1, padx = 5, pady = 5)

btnChosePDFSRC = tk.Button(tabSRCconvert, text = "PDF-Datei auswählen", command = lambda: [setPDFsrcPath()])
btnChosePDFSRC.grid(row = 2, column = 2, padx = 5, pady = 5, sticky = "E")

btnConvertPDF = tk.Button(tabSRCconvert, text = "PDF konvertieren", command = lambda: [fktCONVpdf2img()])
btnConvertPDF.grid(row = 3, column = 2, padx = 5, pady = 5, sticky = "E")

#global labSourceFolder
#labSourceFolder = tk.Label(tabAnnotation, text = sourceFolderPath)


################################################################################
#TAB Auf OCR Server kopieren
labUPLOADintro = tk.Label(tabOCRSRVcopy, text = "Mit dieser Funktion können die in Einzelbilder aufgeteilten, entzerrten und in die korrekte Ordnerstruktur gebrachten Quellen auf den ocr4all-Server hochgeladen werden, um dort OCR-bearbeitet zu werden. Der Inhalt des ausgewählten Ordners wird auf den Server hochgeladen. In diesem Ordner müssen die Dateien in der dafür notwendigen Struktur (00123_BLA/input/HierhinDieBilder; 00123_BLA/processing/) vorhanden sein. Falls die Bilder über dieses Tool bearbeitet wurden, ist diese Ordnerstruktur bereits vorhanden.\n Achtung: Der Inhalt des ausgewählten Ordners wird hochgeladen. Es darf also nicht der Quellenordner (00123_BLABLA) ausgewählt werden, sondern der darüberliegende Ordner. Es bietet sich an, alle hochzuladenden Quellen in einem Ordner wie Upload o.ä. zu sammeln, um diesen dann hochzuladen.", wraplength=800,justify=LEFT)
labUPLOADintro.grid(row = 1, column = 1, columnspan = 2, padx = 5, pady = 5)
# ttk.Label(tabOCRSRVcopy, text="Hier können Quellen auf den OCR-Server kopiert werden.").grid(column=0, row=0, padx=30, pady=30)

labUPLOADpath = tk.Label(tabOCRSRVcopy, text = "Bitte den Pfad auswählen auswählen")
labUPLOADpath.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = "W")

btnChoseUPLOADpath = tk.Button(tabOCRSRVcopy, text = "Pfad auswählen", command = lambda: [setUPLOADpath()])
btnChoseUPLOADpath.grid(row = 2, column = 2, padx = 5, pady = 5, sticky = "E")

#Ablauf
# 1. Ordner auswählen --> multi folder
#Pfad zum Quellordner der xml Dateien setzen
def setUPLOADpath():
    #Pfad bekommen
    global source_path
    source_path = filedialog.askdirectory()
    labUPLOADpath.config(text = source_path) #Label ändern

# 2. SSH verbindung

#set ssh credentials
labIP = tk.Label(tabOCRSRVcopy, text = "IP-Adresse:", justify = LEFT)
labIP.grid(row = 3, column = 1, padx = 5, pady = 5, sticky = "W")
sshIPbox = Entry(tabOCRSRVcopy)
sshIPbox.grid(row = 3, column = 2, padx = 5, pady = 5, sticky = "E")

labPORT = tk.Label(tabOCRSRVcopy, text = "Port:", justify = LEFT)
labPORT.grid(row = 4, column = 1, padx = 5, pady = 5, sticky = "W")
sshPORTbox = Entry(tabOCRSRVcopy)
sshPORTbox.grid(row = 4, column = 2, padx = 5, pady = 5, sticky = "E")

labUSER = tk.Label(tabOCRSRVcopy, text = "Benutzer:", justify = LEFT)
labUSER.grid(row = 5, column = 1, padx = 5, pady = 5, sticky = "W")
sshUSERbox = Entry(tabOCRSRVcopy)
sshUSERbox.grid(row = 5, column = 2, padx = 5, pady = 5, sticky = "E")

labPWD = tk.Label(tabOCRSRVcopy, text = "Passwort:", justify = LEFT)
labPWD.grid(row = 6, column = 1, padx = 5, pady = 5, sticky = "W")
sshPWDbox = Entry(tabOCRSRVcopy, show = "*")
sshPWDbox.grid(row = 6, column = 2, padx = 5, pady = 5, sticky = "E")

btnUPLOAD = tk.Button(tabOCRSRVcopy, text = "Hochladen", command = lambda: [copyToServer(sshIPbox.get(), int(sshPORTbox.get()), sshUSERbox.get(), sshPWDbox.get(), source_path, "/var/data/ocr4all/data")])

btnUPLOAD.grid(row = 7, column = 2, padx = 5, pady = 5, sticky = "E")



################################################################################
##
#Tab vom ocr Server runterladen
labDOWNLOADintro = tk.Label(tabOCRSRVdownload, text = "Mit dieser Funktion können die OCR-bearbeiteten Quellen vom Server heruntergeladen werden. Die Anmeldedaten sind die Selben wie die für den Upload. \n Es werden alle Dateien auf dem Server heruntergeladen und im angegebenen Ordner gespeichert. Von dort können sie zur Konversion nach TEI XML weitergegeben werden.\n Achtung: Das Herunterladen kann eine längere Zeit in Anspruch nehmen. Im Downloadordner wird eine Log-Datei angelegt, die den aktuellen Stand enthält.", wraplength=800,justify=LEFT)
labDOWNLOADintro.grid(row = 0, column = 0, columnspan = 2, padx = 5, pady = 5)

labDOWNLOADpath = tk.Label(tabOCRSRVdownload, text = "Bitte den Pfad auswählen auswählen")
labDOWNLOADpath.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = "W")

btnChoseUPLOADpath = tk.Button(tabOCRSRVdownload, text = "Speicherort auswählen", command = lambda: [setDOWNLOADpath()])
btnChoseUPLOADpath.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = "E")

#Ablauf
#Pfad zum Zielordner des Downloads
def setDOWNLOADpath():
    #Pfad bekommen
    global download_path
    download_path = filedialog.askdirectory()
    labDOWNLOADpath.config(text = download_path) #Label ändern

# 2. SSH verbindung

#set ssh credentials
labDOWNLOADIP = tk.Label(tabOCRSRVdownload, text = "IP-Adresse:", justify = LEFT)
labDOWNLOADIP.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = "W")
sshDOWNLOADIPbox = Entry(tabOCRSRVdownload)
sshDOWNLOADIPbox.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = "E")

labDOWNLOADPORT = tk.Label(tabOCRSRVdownload, text = "Port:", justify = LEFT)
labDOWNLOADPORT.grid(row = 3, column = 0, padx = 5, pady = 5, sticky = "W")
sshDOWNLOADPORTbox = Entry(tabOCRSRVdownload)
sshDOWNLOADPORTbox.grid(row = 3, column = 1, padx = 5, pady = 5, sticky = "E")

labDOWNLOADUSER = tk.Label(tabOCRSRVdownload, text = "Benutzer:", justify = LEFT)
labDOWNLOADUSER.grid(row = 4, column = 0, padx = 5, pady = 5, sticky = "W")
sshDOWNLOADUSERbox = Entry(tabOCRSRVdownload)
sshDOWNLOADUSERbox.grid(row = 4, column = 1, padx = 5, pady = 5, sticky = "E")

labDOWNLOADPWD = tk.Label(tabOCRSRVdownload, text = "Passwort:", justify = LEFT)
labDOWNLOADPWD.grid(row = 5, column = 0, padx = 5, pady = 5, sticky = "W")
sshDOWNLOADPWDbox = Entry(tabOCRSRVdownload, show = "*")
sshDOWNLOADPWDbox.grid(row = 5, column = 1, padx = 5, pady = 5, sticky = "E")

btnDOWNLOAD = tk.Button(tabOCRSRVdownload, text = "Herunterladen", command = lambda: [downloadFromServer(download_path)])

btnDOWNLOAD.grid(row = 8, column = 0, padx = 5, pady = 5, columnspan = 2)

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None    

def downloadFromServer(download_path):
    preserve_mtime=False
    server_ip = sshDOWNLOADIPbox.get()
    username = sshDOWNLOADUSERbox.get()
    password = sshDOWNLOADPWDbox.get()
    port = int(sshDOWNLOADPORTbox.get())

    remote_path = "/var/data/ocr4all/data/"

    #skript ausführen, das die Dateien auf dem Server lesbar macht
    script_exec = paramiko.SSHClient()
    script_exec.load_system_host_keys()
    script_exec.connect(server_ip, port, username, password)
    command = "/var/data/ocr4all/set_download_permissions.sh"
    (stdin, stdout, stderr) = script_exec.exec_command(command)
    for line in stdout.readlines():
        print(line)
    script_exec.close()

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None    
    sftp=pysftp.Connection(server_ip, username = username,password = password,cnopts=cnopts, port = port)

    #eventuell vorhandenes Logfile erstmal löschen
    if os.name == "posix":
        if os.path.exists(download_path + "/download_log.txt"):
            os.remove(download_path + "/download_log.txt")
    elif os.name == "nt":
        if os.path.exists(download_path + "\\download_log.txt"):
            os.remove(download_path + "\\download_log.txt")

    def download_files(sftp, remotedir, localdir, preserve_mtime=False):

    #(neues) Log anlegen
        if os.name == "posix":
            download_log = open(download_path + "/download_log.txt", "a") #öffne (neue) Log-Datei
            download_log.write("Downloading " + remotedir + "\n") #aktuelle Datei eintragen
            download_log.close() #Datei schließen = speichern
        elif os.name == "nt":
            download_log = open(download_path + "\\download_log.txt", "a")
            download_log.write("Downloading " + remotedir + "\n") #aktuelle Datei eintragen
            download_log.close() #Datei schließen = speichern

        for entry in sftp.listdir(remotedir):
            remotepath = remotedir + "/" + entry
            localpath = os.path.join(localdir, entry)
            mode = sftp.stat(remotepath).st_mode

            if S_ISDIR(mode):
                try:
                    Path(localpath).mkdir(parents=True, exist_ok=True)
                except OSError:     
                    pass
                download_files(sftp, remotepath, localpath, preserve_mtime)
            elif S_ISREG(mode):
                sftp.get(remotepath, localpath, preserve_mtime=preserve_mtime)

        if os.name == "posix":
            download_log = open(download_path + "download_log.txt", "a")
            download_log.write("Finished downloading " + remotedir + "\n")
            download_log.write("*********************************" + "\n")
            download_log.close()
        elif os.name == "nt":
            download_log = open(download_path + "download_log.txt", "a")
            download_log.write("Finished downloading " + remotedir + "\n")
            download_log.write("*********************************" + "\n")
            download_log.close()
    
    download_files(sftp, remote_path, download_path, preserve_mtime=False)

################################################################################
"""
Automatische Annotation
"""

FileListPath = "Keine Dateiliste ausgewählt"
WordListPath = "Keine Tagliste ausgewählt"
sourceFolderPath = "Kein Quellordner ausgewählt"
destinationFolderPath = "Kein Zielordner ausgewählt"

#Anzeige der Dateiliste
global labDateiListenPfad
labDateiListenPfad = tk.Label(tabAnnotation, text = FileListPath)
boxDateiliste = scrolledtext.ScrolledText(tabAnnotation, wrap=tk.WORD, width=100, height=20)

global labWordListPath
labWordListPath = tk.Label(tabAnnotation, text = WordListPath)
boxWordlist = scrolledtext.ScrolledText(tabAnnotation, wrap=tk.WORD, width=100, height=20)

BeschreibungAllgemein = tk.Label(tabAnnotation, text = "Mit dieser Funktion können die TEI XML-Dateien automatisch annotiert werden. Auf der linken Seite stehen die zu bearbeitenden Dateien, auf der rechten Seite die zu annotierenden Tags mit den dazugehörigen Signalwörtern. \n Außerdem müssen der Quell- und Zielordner der TEI XML-Dateien ausgewählt werden. Wird kein Zielordner angegeben, werden die annotierten Dateien am Standardort (Quellordner/annotierte_TEI_Dateien/) gespeichert.", wraplength=800, justify=LEFT)

BeschreibungDateiliste = tk.Label(tabAnnotation, text = "In die Dateiliste müssen die zu annotierenden Dateien in einzelnen Zeilen, ohne Dateiendung (d.h. nur die ID 00001, 00002, etc.) eingetragen oder aus einer Datei eingelesen werden.", wraplength=400,justify=LEFT)

BeschreibungTagliste = tk.Label(tabAnnotation, text = "In die Wortliste müssen die zu setzenden Tags und die dazugehörigen Signalworte in einzelnen Zeilen wie folgt eingetragen oder aus einer Datei eingelesen werden:\nDas # markiert ein Schlagwort, alle bis zum nächsten # folgenden Worte werden mit diesem annotiert. Es werden *nur* die angegebenen Schreibweisen annotiert, keine Abwandlungen davon (d.h. Pause != Pausen). Sobald das nächste # folgt, wird ein neues Tag annotiert. \n ACHTUNG: Die Tagliste darf keine Leerzeilen enthalten. Das wird in einer folgenden Softwareversion gefixt.", wraplength=400,justify=LEFT)

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
btnAnnotieren = tk.Button(tabAnnotation, text="Annotation starten", command = lambda: AutoAnnotation(FileListPath, WordListPath, destinationFolderPath, sourceFolderPath))


#Anordnung
BeschreibungAllgemein.grid(column = 0, row = 0, padx=5, pady=5, columnspan=2)

BeschreibungDateiliste.grid(column = 0, row = 1, padx=5, pady=5, sticky = "N")
BeschreibungTagliste.grid(column = 1, row = 1, padx=5, pady=5, sticky = "N")

#DateiListe.grid(column=0, row=2, padx=5, pady=5)
boxDateiliste.grid(column=0, row=2, padx=5, pady=5)


boxWordlist.grid(column=1, row=2, padx=5, pady=5)

btnDateiliste.grid(column = 0, row = 3)
btnWordList.grid(column = 1, row = 3)

labWordListPath.grid(column=1, row=4, padx=5, pady=5)
labDateiListenPfad.grid(column=0, row=4, padx=5, pady=5)

btnChooseSourceFolder.grid(column = 0, row = 5)
btnChooseDestinationFolder.grid(column = 1, row = 5)

labSourceFolder.grid(column=0, row=6, padx=5, pady=5)
labDestinationFolder.grid(column=1, row=6, padx=5, pady=5)

btnAnnotieren.grid(column=0, row=7, padx=5, pady=5, columnspan = 2)



################################################################################
"""
Manuelle Transkription
"""
labXMLmanualDescr = tk.Label(tabXMLmanual, text = "Hier können Quellen manuell transkribiert werden. Diese Funktion ist für die Quellen der DMZ sowie handschriftliche Quellen gedacht. \n In die unten stehenden Felder werden die Metadaten der Quelle eingetragen, in das große Textfeld der Quellentext. Die Datei wird im ausgewählten Ordner gespeichert.", wraplength=800,justify=LEFT)
labXMLmanualDescr.grid(row = 0, column = 0, padx = 5, pady = 5, columnspan= 2)

def setXMLDestinationFolder():
    global XMLdestinationFolderPath
    XMLdestinationFolderPath = filedialog.askdirectory()
    #print("Destination Folder: " + destinationFolderPath)
    labXMLDestinationFolder.config(text = XMLdestinationFolderPath)

btnChooseXMLDestFolder = tk.Button(tabXMLmanual, text = "Exportordner auswählen", command = lambda: [setXMLDestinationFolder()])
btnChooseXMLDestFolder.grid(row = 9, column = 1, padx = 5, pady = 5, sticky = "E")

global XMLlabDestinationFolder
labXMLDestinationFolder = tk.Label(tabXMLmanual, text = "")
labXMLDestinationFolder.grid(row = 9, column = 0, padx = 5, pady = 5, sticky = "W")

# 2. Daten der Quelle eingeben
labSRCID = tk.Label(tabXMLmanual, text = "Quellen-ID:", justify = LEFT)
labSRCID.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = "W")
SRCIDbox = Entry(tabXMLmanual, width = 50)
SRCIDbox.insert(END, "99999") #default value
SRCIDbox.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = "E")

labWHEN = tk.Label(tabXMLmanual, text = "Datum:", justify = LEFT)
labWHEN.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = "W")
WHENlabel = tk.Label(tabXMLmanual, text = datetime.now().strftime("%Y-%m-%d+%H:%M"), justify = LEFT)
WHENlabel.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = "E")

labSRCYEAR = tk.Label(tabXMLmanual, text = "Jahr der Quelle:", justify = LEFT)
labSRCYEAR.grid(row = 3, column = 0, padx = 5, pady = 5, sticky = "W")
SRCYEARbox = Entry(tabXMLmanual, width = 50)
SRCYEARbox.insert(END, "9999") #default value
SRCYEARbox.grid(row = 3, column = 1, padx = 5, pady = 5, sticky = "E")

labSRCBIBL = tk.Label(tabXMLmanual, text = "Quellennachweis (inkl. Seite):", justify = LEFT)
labSRCBIBL.grid(row = 4, column = 0, padx = 5, pady = 5, sticky = "W")
SRCBIBLbox = Entry(tabXMLmanual, width = 50)
SRCBIBLbox.insert(END, "Beispielzeitschrift, Ausgabe 9999, 01.01.9999, S. 99") #default value
SRCBIBLbox.grid(row = 4, column = 1, padx = 5, pady = 5, sticky = "E")

labSHORTTITLE = tk.Label(tabXMLmanual, text = "Kurztitel (AO_FIRMA_ORT_JAHR):", justify = LEFT)
labSHORTTITLE.grid(row = 5, column = 0, padx = 5, pady = 5, sticky = "W")
SHORTTITLEbox = Entry(tabXMLmanual, width = 50)
SHORTTITLEbox.insert(END, "AO_Beispielfirma_Beispielort_9999") #default value
SHORTTITLEbox.grid(row = 5, column = 1, padx = 5, pady = 5, sticky = "E")

labTITLE = tk.Label(tabXMLmanual, text = "Offizieller Titel:", justify = LEFT)
labTITLE.grid(row = 6, column = 0, padx = 5, pady = 5, sticky = "W")
TITLEbox = Entry(tabXMLmanual, width = 50)
TITLEbox.insert(END, "Arbeitsordnung der Beispielfirma am Beispielort vom 1.1.9999") #default value
TITLEbox.grid(row = 6, column = 1, padx = 5, pady = 5, sticky = "E")

labSRCTEXT = tk.Label(tabXMLmanual, text = "Text der Quelle:", justify = LEFT)
labSRCTEXT.grid(row = 7, column = 0, padx = 5, pady = 5, columnspan=2, sticky = "W")
SRCTEXTbox = scrolledtext.ScrolledText(tabXMLmanual, wrap=tk.WORD, width=100, height=20)
SRCTEXTbox.grid(row = 8, column = 0, padx = 5, pady = 5, columnspan=2)

# 4. Speichern-Button!
btnSaveXMLManual = tk.Button(tabXMLmanual, text = "Speichern", command = lambda: [saveXMLManual()])
btnSaveXMLManual.grid(row = 10, column = 1, padx = 5, pady = 5, columnspan = 2, sticky = "E")

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
        SRCTEXT = SRCTEXT.replace("§", "&#167;")

    elif os.name == "nt":
        SRCTEXT = SRCTEXT.replace("\r\n","<lb/>\r\n")
        SRCTEXT = SRCTEXT.replace("&", "&amp;")
        SRCTEXT = SRCTEXT.replace("§", "&#167;")

    global ManualTranscriptionText
    ManualTranscriptionText = TEIVorlage

    ManualTranscriptionText = ManualTranscriptionText.replace("$SRCID", SRCID)
    ManualTranscriptionText = ManualTranscriptionText.replace("$WHEN", WHEN)
    ManualTranscriptionText = ManualTranscriptionText.replace("$SRCYEAR", SRCYEAR)
    ManualTranscriptionText = ManualTranscriptionText.replace("$SRCBIBL", SRCBIBL)
    ManualTranscriptionText = ManualTranscriptionText.replace("$SHORTTITLE", SHORTTITLE)
    ManualTranscriptionText = ManualTranscriptionText.replace("$TITLE", TITLE)
    ManualTranscriptionText = ManualTranscriptionText.replace("$SRCTEXT", SRCTEXT)

    #5. Write new XML File for current source
    #open text file
    if os.name == "posix":
        newXMLSource = open((XMLdestinationFolderPath + "/" + SRCID + ".xml"), "w", encoding = "utf-8")
    elif os.name == "nt":
        newXMLSource = open((XMLdestinationFolderPath + "\\" + SRCID + ".xml"), "w", encoding = "utf-8")
    #write string to file
    newXMLSource.write(ManualTranscriptionText)
    #close file
    newXMLSource.close()

################################################################################
#TAB Annotation
# Grid bauen: jede Spalte bekommt ein Gewicht; so werden sie auf die Breite verteilt
tabAnnotation.columnconfigure(0, weight = 1)
tabAnnotation.columnconfigure(1, weight = 1)

#Mainloop-Methode --> "Eventloop" --> muss aufgerufen werden --> Endlosschleife, die Interaktionen mit GUI abfängt
mainWindow.mainloop()
#Was hier drunter steht, wird erstmal nicht ausgeführt!!!!