import re
from datetime import datetime
from po_formats.po_base import PO_BASE
import po_formats.image as img

class PO_TYPE_9(PO_BASE):
    def __init__(self, poDocFilepath: str,) -> None:
        super().__init__(poDocFilepath)
        self.__image_filepath = self.savePageAsImage(1)
        self.__param = {
            'y_t_1': img.text_coordinates(img.read_image(self.__image_filepath),'SUMMARY')[2],
            'y_t_2': img.text_coordinates(img.read_image(self.__image_filepath),'DETAILED')[2],
            'y_t_3': img.text_coordinates(img.read_image(self.__image_filepath),'FACTORY:')[2]
        }

    def __buyer(self)->str:
        """
            Returns the buyer name 
        """
        return 'WM MORRISON SUPERMARKETS PLC'

    def __company(self)->str:
        """
            Returns the company name
        """
        return 'CENTRO INTERNATIONAL SOURCING LIMITED'

    def __po_number(self)->int:
        """
            Returns the purchase order number
        """
        return int(re.findall(r"PURCHASE\s+ORDER\s+REFERENCE\s?:\s+(\d+)",self.getPage(1).upper())[0])

    def __shipment_mode(self)->str:
        """
            Returns the shipment mode
        """
        return "SEA"

    def __style(self)->str:
        """
            Returns the style
        """
        y_t = self.__param['y_t_1']
        cropped_image = img.crop_image(self.__image_filepath,50,300,y_t+260,y_t+340)
        return img.image_to_text(cropped_image,2.3).strip().replace(' ','')

    def __style_description(self)->str:
        """
            Returns the style description
        """
        y_t = self.__param['y_t_1']
        cropped_image = img.crop_image(self.__image_filepath,1200,1800,y_t+260,y_t+340)
        text = img.image_to_text(cropped_image,2.32).strip()
        words = text.split(" ")
        if len(words[0])==1:
            return text.replace(' ','',1)
        return text

    def __gmt_item(self)->str:
        """
            Returns the gmt item
        """
        return self.__style_description().split(" ")[-1]

    def __currency(self)->str:
        """
            Returns the currency type
        """
        return "$"

    def __factory(self)->str:
        """
            Returns the factory name
        """
        y_t = self.__param['y_t_3']
        cropped_image = img.crop_image(self.__image_filepath,1000,2000,y_t+60,y_t+120)
        return img.image_to_text(cropped_image).strip()

    def __supplier_cost(self)->str:
        """
            Returns the ship date
        """
        y_t = self.__param['y_t_1']
        cropped_image = img.crop_image(self.__image_filepath,3400,3700,y_t+260,y_t+340)
        return float(img.image_to_text(cropped_image).strip().replace(' ',''))

    def __ship_date(self)->str:
        """
            Returns the size range
        """

        (_d,_m,_y) = re.findall(r"Dates.*\n\s?\d+\s?\d{0,}\s+(\d{1,2})[\s\.\-,/]{1,3}(\d{1,2})[\s\.\-,/]{1,3}(\d{2,4})\s+",self.getPage(1))[0]
        return datetime.strptime(f"{_d}.{_m}.{_y[-2:]}","%d.%m.%y").strftime("%d-%b-%y")

    def __rearrange_sizes(self,currentSizes:str,newSizes:str=None):
        """
            Returns the rearranged sizes
        """
        sizeFormat = 1 # default 2XL
        # size correction

        def changeFormat(sizes:str):
            sizes = " " + sizes + " "
            for sizeNumber in range(0,7):
                if sizeNumber ==0:
                    pass
                elif sizeNumber ==1:
                    pass
                elif sizeNumber>=2:
                    sizes = sizes.replace(f" {sizeNumber*'X'}S ",f" {sizeNumber}XS ")
                    sizes = sizes.replace(f" {sizeNumber*'X'}L ",f" {sizeNumber}XL ")
            return sizes.strip()

        def reverseChangeFormat(sizes:str):
            sizes = " " + sizes + " "
            for sizeNumber in range(0,7):
                if sizeNumber ==0:
                    pass
                elif sizeNumber ==1:
                    pass
                elif sizeNumber>=2:
                    sizes = sizes.replace(f" {sizeNumber}XS ",f" {sizeNumber*'X'}S ")
                    sizes = sizes.replace(f" {sizeNumber}XL ",f" {sizeNumber*'X'}L ")
            return sizes.strip()

        sizeWeightDict = {
            '7XS':-8,
            '6XS':-7,
            '5XS':-6,
            '4XS':-5,
            '3XS':-4,
            '2XS':-3,
            'XS':-2,
            'S':-1,
            'M':0,
            'L':1,
            'XL':2,
            '2XL':3,
            '3XL':4,
            '4XL':5,
            '5XL':6,
            '6XL':7,
            '7XL':8
        }

        if newSizes==None:
            if changeFormat(str(currentSizes))!=str(currentSizes):
                sizeFormat=2
                currentSizes = changeFormat(str(currentSizes))
            sizeList = set(str(currentSizes).split(" - "))
        elif newSizes!=None:
            if changeFormat(str(currentSizes))!=str(currentSizes) and changeFormat(str(newSizes))!=str(newSizes):
                sizeFormat=2
                currentSizes = changeFormat(str(currentSizes))
                newSizes = changeFormat(str(newSizes))
            sizeList = set(str(currentSizes).split(" - ") + str(newSizes).split(" "))
        try:
            sizeDict = {size : sizeWeightDict[size] for size in sizeList}
            sortedSizeList = sorted(sizeDict.items(), key=lambda x:x[1])

            # size rearrange
            _fisrt = sortedSizeList[0][0]
            _last = sortedSizeList[-1][0]
            if sizeFormat ==2 :
                _fisrt = reverseChangeFormat(f" {_fisrt} ")
                _last = reverseChangeFormat(f" {_last} ")

        except KeyError:
            try:
                sortedSizeList = sorted([int(size) for size in list(filter(None,sizeList))])
                _fisrt = sortedSizeList[0]
                _last = sortedSizeList[-1]
            except IndexError:
                return " - "

        if len(sortedSizeList)==1:
            return f"{_fisrt}"
        elif len(sortedSizeList)>1:
            return f"{_fisrt} - {_last}"

    def __color(self)->str:
        """
            Returns the color
        """
        y_t = self.__param['y_t_1']
        cropped_image = img.crop_image(self.__image_filepath,1800,2200,y_t+260,y_t+340)
        return img.image_to_text(cropped_image,2.32).strip()

    def __size_range(self)->str:
        """
            Returns the size range
        """
        segment = self.getPage(1).upper().split(f"TOTAL: {self.__total_quantity()}")[0].split('RETAIL')[1].strip()
        sizes = re.findall(r"\s+([X]{0,}[SML]{0,1}[0-9]*)\s+\d+\s+[\d\.]+\s+",segment)
        return self.__rearrange_sizes(" - ".join(sizes))

    def __total_quantity(self)->int:
        """
            Returns the total quantity
        """
        return int(re.findall(r"TOTAL\s?:\s+(\d+)\s+",self.getPage(1).upper())[0])

    def __purchase_orders(self)->dict:
        """
            Returns the purchase orders details
        """
        po_dict = {}
        dest = 'SOUTHAMPTON'
        po_dict[0] = {
            "dest":dest,
            "dest_num":0,
            "n_units":'',
            "n_packs":0,
            "ship_date":self.__ship_date(),
            "size_range":self.__size_range(),
            "packs_data":[
                {
                    'pack_sizes': self.__size_range(),
                    'pack_colour': self.__color(),
                    'n_packs':None,
                    'n_units':self.__total_quantity(),
                    "supplier_cost":self.__supplier_cost()
                }
            ]
        }
        return po_dict

    def __po_details(self)->list:
        """
            Returns a list of purchase order data details
        """
        po_details = {
            "team":"",
            "src_merc":"",
            "company":self.__company(),
            "consignee":self.__buyer(),
            "buyer":self.__buyer(),
            "category":"",
            "dept":"",
            "season_year":"",
            "season":"",
            "style":self.__style(),
            "style_desc":self.__style_description(),
            "gmt_item":self.__gmt_item(),
            "uom":"",
            "ratio":"",
            "total_qty":'',
            "currency":self.__currency(),
            "factory":self.__factory(),
            "fabric_src":"",
            "fabric":"",
            "fabric_mill":"",
            "sust_fabric":"",
            "po_num":self.__po_number(),
            "po_date":'',
            "po_status":"",
            "shipment_mode":self.__shipment_mode(),
            "purchase_orders":self.__purchase_orders()
        }
        self.deleteTempFolder()
        return [po_details]

    def output(self)->tuple:
        """
            Returns the extracted data
        """
        return (self.__po_details())