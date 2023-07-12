import glob
import datetime
from tkinter import Tk, Button, Text, font, END, filedialog

class PO_Extractor:
    """
        PO Extractor GUI
    """
    def __init__(self) -> None:

        self.__root = Tk()

        # Application properties
        self.__aspectRatio = (16,9)
        self.__sizeFactor = 70
        self.__windowSize = (
            self.__aspectRatio[0]*self.__sizeFactor,
            self.__aspectRatio[1]*self.__sizeFactor
            )

        # Application Theme
        self.__fonts = (
            font.Font(family="Courier New",size=10, weight='normal'),
            font.Font(family="Courier New",size=12, weight='normal')
            )
        self.__colors = (
            '#DDE6ED',  #Light
            '#9DB2BF',
            '#526D82',
            '#27374D'   #Dark
            )

        self.__root.title("PO Extractor")
        self.__root.geometry(f"{self.__windowSize[0]}x{self.__windowSize[1]}")
        self.__root.resizable(False, False)
        self.__root.configure(background=self.__colors[1])
        self.__srcDir = "C:/PDFextract"
        self.__poFilesList = []
        self.__buildLayout()

    def __buildLayout(self)->None:
        """
            Create the tkinter GUI layout of the application
        """
        self.__createButton_selectDirectory()
        self.__createButton_extractData()
        self.__createTextField_log()

    def __createButton_selectDirectory(self)->None:
        """
            Create the tkinter button for 'Select Directory'
        """
        self.__buttonSelect = Button(
            self.__root, 
            text="Select Source Directory",
            font=self.__fonts[1],
            bg = self.__colors[0],
            fg = self.__colors[3],
            activebackground=self.__colors[1],
            width=50,
            relief='groove',
            command=self.__selectDirectory
            )
        self.__buttonSelect.grid(
            row=0,column=0,
            ipadx=10,ipady=10,
            padx=10,pady=10)

    def __createButton_extractData(self)->None:
        """
            Create the tkinter button for 'Extract PO Data'
        """
        self.__buttonExtract = Button(
            self.__root, 
            text="Extract PO Data",
            font=self.__fonts[1],
            bg = self.__colors[0],
            fg = self.__colors[3],
            activebackground=self.__colors[1],
            width=50,
            relief='groove'
            )
        self.__buttonExtract.grid(
            row=0,column=1,
            ipadx=10,ipady=10,
            padx=10,pady=10)

    def __createTextField_log(self)->None:
        """
            Create the tkinter text field for log printing
        """
        self.__textFieldLog = Text(
            self.__root, 
            font=self.__fonts[0],
            bg = self.__colors[0],
            fg = self.__colors[3],
            width=134,
            height=32,
            relief='flat',
            state='disabled'
            )
        self.__textFieldLog.grid(
            row=1,column=0,columnspan=2,
            ipadx=10,ipady=10,
            padx=10,pady=10)

    def __loadFiles(self)->None:
        """
            Load purchase order documents from default/selected directory
        """
        self.__poFilesList = glob.glob(self.__srcDir + "/*.pdf")
        if len(self.__poFilesList)==0:
            self.__log(f"No pdf files found from directory {self.__srcDir}.")
        else:
            self.__log(f"{len(self.__poFilesList)} pdf files loaded from directory {self.__srcDir}.")

    def __selectDirectory(self)->None:
        """
            Select a source directory path
        """
        self.__srcDir = filedialog.askdirectory()
        self.__loadFiles()

    def __log(self, message:str)->None:
        """
            Create the log message with event details
        """
        self.__textFieldLog.configure(state='normal')
        self.__textFieldLog.insert(END,f'{datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")} | {message}\n')
        self.__textFieldLog.configure(state='disabled')

    def run(self)->None:
        """
            Run the application
        """
        self.__log('PO Extractor started.')
        self.__loadFiles()
        self.__root.mainloop()

if __name__ == "__main__":
    app = PO_Extractor()
    app.run()