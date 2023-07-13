import os
import pdf2image
import cv2
import pytesseract

def extract(pdfFilepath:str,fromPage:int,toPage:int,scalingFactor:float)->list:
    """
        Returns a list of page content extracted from a image based pdf
    """
    pdfContent= []
    os.makedirs(f"{os.path.dirname(pdfFilepath)}/temp",exist_ok=True)
    try:
        pages = pdf2image.pdf2image.convert_from_path(pdfFilepath,500,poppler_path=r"./poppler-0.68.0/bin")
    except pdf2image.exceptions.PDFInfoNotInstalledError:
        pages = pdf2image.pdf2image.convert_from_path(pdfFilepath,500,poppler_path=r"../poppler-0.68.0/bin")

    try:
        pytesseract.pytesseract.tesseract_cmd = r"./Tesseract-OCR/tesseract.exe"
    except pytesseract.pytesseract.TesseractNotFoundError:
        pytesseract.pytesseract.tesseract_cmd = r"../Tesseract-OCR/tesseract.exe"

    for pageNumber in range(fromPage,toPage+1):
        tempImageFilepath = f'{os.path.dirname(pdfFilepath)}/temp/{os.path.basename(pdfFilepath)} - {pageNumber}.jpeg'
        pages[pageNumber-1].save(tempImageFilepath, 'JPEG')

        tempImage = cv2.imread(tempImageFilepath)
        tempImage = cv2.resize(tempImage,None, fx=scalingFactor, fy=scalingFactor)
        tempImage = cv2.cvtColor(tempImage, cv2.COLOR_BGR2GRAY)
        pageText = pytesseract.image_to_string(tempImage)
        pdfContent.append(pageText)
        os.remove(tempImageFilepath)
    os.removedirs(f"{os.path.dirname(pdfFilepath)}/temp")
    return pdfContent