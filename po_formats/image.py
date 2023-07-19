import cv2
import pytesseract

def read_image(image_filepath:str):
    return cv2.imread(image_filepath)

def crop_image(image_filepath:str,x_l:int,x_r:int,y_t:int,y_b:int):
    """
        Returns the cropped image
    """
    image = cv2.imread(image_filepath)
    image_height = image.shape[0]
    image_width = image.shape[1]
    if x_l < x_r and x_l>=0 and x_r>=0 and x_l<=image_width and x_r<=image_width:
        if y_t < y_b and y_t>=0 and y_b>=0 and y_t<=image_height and y_b<=image_height:
            cropped_image = image[y_t:y_b,x_l:x_r]
            #cv2.imwrite(image_filepath,cropped_image) # comment this line later
            return cropped_image
        else:
            pass
    else:
        pass
    raise Exception(f'Error: Arguments out of range. {0}<= x_* <= {image_width} | {0}<= y_* <= {image_height}')


def image_to_text(image,scalling_factor:float=2.2)->str:
    """
        Returns the text from image
    """
    try:
        pytesseract.pytesseract.tesseract_cmd = r"./Tesseract-OCR/tesseract.exe"
    except pytesseract.pytesseract.TesseractNotFoundError:
        pytesseract.pytesseract.tesseract_cmd = r"../Tesseract-OCR/tesseract.exe"

    image = cv2.resize(image,None, fx=scalling_factor, fy=scalling_factor)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(image)

def image_to_binary_image(image):
    """
        Returns the binary image
    """
    #_thres = cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    _, binary_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binary_image

def image_to_data(image):
    """
        Returns the OCR data of the image
    """
    ocr_result = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    return ocr_result

def text_coordinates(image,text_to_search:str)->tuple:
    coordinates = ()
    #binary_image = image_to_binary_image(image)
    ocr_result = image_to_data(image)
    for index, text in enumerate(ocr_result['text']):
        if text.strip() == text_to_search.strip():
            x_l = ocr_result['left'][index]
            y_t = ocr_result['top'][index]
            width = ocr_result['width'][index]
            height = ocr_result['height'][index]
            x_r = x_l + width
            y_b = y_t + height
            coordinates = (x_l, x_r, y_t, y_b)
    return coordinates