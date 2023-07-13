import os
import pypdfium2
import pdf2image
import cv2
import pytesseract

class PO_BASE:
    """
        Base class for all the purchase order document types
    """
    def __init__(self,poDocFilepath:str) -> None:
        if not os.path.exists(poDocFilepath):
            raise FileNotFoundError
        self.__poDocFilepath = poDocFilepath
        self.__poDoc = self.__getPoDocContent()

    def __getPoDocContent(self)->list:
        self.__poDoc = pypdfium2.PdfDocument(self.__poDocFilepath)

        if self.getPage(1)!="":
            return self.__poDoc
        else:
            poDocContent= []
            os.makedirs("../../temp",exist_ok=True)
            try:
                pages = pdf2image.pdf2image.convert_from_path(self.__poDocFilepath,500,poppler_path=r"./poppler-0.68.0/bin")
            except pdf2image.exceptions.PDFInfoNotInstalledError:
                pages = pdf2image.pdf2image.convert_from_path(self.__poDocFilepath,500,poppler_path=r"../poppler-0.68.0/bin")

            try:
                pytesseract.pytesseract.tesseract_cmd = r"./Tesseract-OCR/tesseract.exe"
            except pytesseract.pytesseract.TesseractNotFoundError:
                pytesseract.pytesseract.tesseract_cmd = r"../Tesseract-OCR/tesseract.exe"

            for pageIndex in range(len(pages)):
                tempImageFilepath = f'../../temp/{os.path.basename(self.__poDocFilepath)} - {pageIndex+1}.jpeg'
                pages[pageIndex].save(tempImageFilepath, 'JPEG')

                tempImage = cv2.imread(tempImageFilepath)
                tempImage = cv2.resize(tempImage,None, fx=2.2, fy=2.2)
                tempImage = cv2.cvtColor(tempImage, cv2.COLOR_BGR2GRAY)
                pageText = pytesseract.image_to_string(tempImage)
                poDocContent.append(pageText)
                os.remove(tempImageFilepath)
            os.removedirs("../../temp")
            return poDocContent

    def numPages(self) -> int:
        """
            Returns the number of pages in the purchase order document
        """
        return len(self.__poDoc)

    def getPage(self,pageNumber:int) -> str:
        """
            Returns a specific page of the purchase order document
        """
        if type(pageNumber)==int and pageNumber>=0 and pageNumber<=self.numPages():
            try:
                return self.__poDoc[pageNumber-1].get_textpage().get_text_range()
            except AttributeError:
                return self.__poDoc[pageNumber-1]
        return None