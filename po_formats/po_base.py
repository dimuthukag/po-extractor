import os
import re
import pypdfium2
from PyPDF2 import PdfReader
import svgwrite

class PO_BASE:
    """
        Base class for all the purchase order document types
    """
    def __init__(self,poDocFilepath:str,poDocContent:list=None,scalingFactor:float=None) -> None:
        if not os.path.exists(poDocFilepath):
            raise FileNotFoundError
        self.__poDocFilepath = poDocFilepath
        self.__scalingFactor = scalingFactor
        if poDocContent==None:
            if os.path.basename(self.__poDocFilepath).upper().endswith(".PDF"):
                self.__poDoc = pypdfium2.PdfDocument(self.__poDocFilepath)
            elif os.path.basename(self.__poDocFilepath).upper().endswith(".TXT"):
                poDocContent = ""
                with open(self.__poDocFilepath,'r') as poFile:
                    poDocContent = poFile.read()
                self.__poDoc = [poDocContent]
        elif poDocContent!=None and type(poDocContent)==list:
            self.__poDoc = poDocContent

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
    
    def poDocFilepath(self)->str:
        """
            Returns the absolute filepath of po file
        """
        return self.__poDocFilepath
    
    def scallingFactor(self)->float|None:
        """
            Returns the scaling factor used for a image based po file
        """
        return self.__scalingFactor
    
    def getCurrencySymbol(self,currency:str)->str:
        """
            Returns the currency symbol for a given currency type
        """
        currencySymbolDict = {
            "USD":"$"
        }
        try:
            return currencySymbolDict[currency]
        except KeyError:
            return "-"
    
    def updatePoData(self,poDocContent:list)->None:
        """
            Update the existing po file content using given po file content
        """
        if type(poDocContent)==list:
            self.__poDoc = poDocContent

    def getSvgData(self,pageNumber:int)->str:
        """
            Returns the svg data of a given page number of the PDF file
        """
        if type(pageNumber)==int and pageNumber>0 and pageNumber<=self.numPages():
            os.makedirs(f"{os.path.dirname(self.poDocFilepath())}/temp",exist_ok=True)
            reader = PdfReader(self.poDocFilepath())
            page = reader.pages[pageNumber-1]

            tempSvgFilepath = f"{os.path.dirname(self.poDocFilepath())}/temp/{os.path.basename(self.poDocFilepath()).replace('.PDF,','.svg')}"
            dwg = svgwrite.Drawing(tempSvgFilepath, profile="tiny")

            def visitor_svg_rect(op, args, cm, tm):
                if op == b"re":
                    (x, y, w, h) = (args[i].as_numeric() for i in range(4))
                    dwg.add(dwg.rect((x, y), (w, h), stroke="red", fill_opacity=0.05))

            def visitor_svg_text(text, cm, tm, fontDict, fontSize):
                (x, y) = (tm[4], tm[5])
                dwg.add(dwg.text(text, insert=(x, y), fill="blue"))


            page.extract_text(
                visitor_operand_before=visitor_svg_rect, visitor_text=visitor_svg_text
            )
            dwg.save()

            with open(tempSvgFilepath,'rb') as _svg_file:
                _svg_content = _svg_file.read()
            os.remove(tempSvgFilepath)
            os.removedirs(f"{os.path.dirname(self.poDocFilepath())}/temp")
            return _svg_content.decode('utf-8')
    
    def getPageByPyPDF2(self,pageNumber:int)->str:
        """
            Returns the content of a given page number of the PDF using PyPDF2 library
        """
        if type(pageNumber)==int and pageNumber>0 and pageNumber<=self.numPages():
            return PdfReader(self.poDocFilepath()).pages[pageNumber-1].extract_text()
        return None