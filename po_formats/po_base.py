import os
import pypdfium2

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
            if os.path.basename(self.__poDocFilepath).endswith(".PDF"):
                self.__poDoc = pypdfium2.PdfDocument(self.__poDocFilepath)
            elif os.path.basename(self.__poDocFilepath).endswith(".TXT"):
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