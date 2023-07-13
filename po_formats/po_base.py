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
            self.__poDoc = pypdfium2.PdfDocument(self.__poDocFilepath)
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