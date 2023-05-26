## About This Tool
The **AnnotationTool** is a tool facilitating the work at the Nichtstaatliches Recht der Metallindustrie project at the Max Planck Institute for Legal History and Legal Theory (https://www.lhlt.mpg.de/forschungsprojekt/nichtstaatliches-recht-der-wirtschaft). It's current functions are:

1. Splitting a pdf into single image files, which can be worked on further with other tools such as ScanTailor Advanced (https://github.com/4lex4/scantailor-advanced).
2. Uploading the images to a server via ssh. In our project, we use ocr4all (https://www.ocr4all.org/) to do the OCR work.
3. Download the OCR data from a server via ssh. **Attention:** The program will try to execute a shell script located on said server, which is not provided here. You should disable that part of the code if you want to use the application yourself.
4. Automatically annotate TEI XML files according to a list of signal words for respective tags.
5. Provide a manual transcription interface to work on sources which cannot be processed with ocr4all (e.g. handwritten sources). **Attention:** The script uses a template for the TEI XML file which contains the header of the project. You need to change the template file /source/teivorlage.py according to your own needs.

## Downloads

**Windows:**
https://github.com/bspendrin/AnnotationTool/tree/main/build/windows
**Linux:**
Not available yet.
**MacOS:**
Not available yet.

## Build

Windows: After installing dependencies, `pyinstaller.exe --clean -F source\AnnotationToolGUI.py` would build a single executabl file.

## ToDo
- add @resp/@cert attributes for automated annotations
- tag words containing linebreaks

## Example Files
You can find example files from the project here:  
https://github.com/bspendrin/AnnotationTool/tree/main/examples

## Comments/Suggestions
Feel free to give comments and/or suggestions here or privately to benjamin.spendrin@posteo.de
