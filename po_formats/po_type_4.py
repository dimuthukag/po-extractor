import re
from datetime import datetime
from po_formats.po_base import PO_BASE
import pycountry

class PO_TYPE_4(PO_BASE):
    def __init__(self, poDocFilepath: str) -> None:
        super().__init__(poDocFilepath)
        self.__pageSplit()

    def __pageSplit(self)->None:
        """
            Split the document content for pages
        """
        poDocContent = self.getPage(1).upper().split(" PURCHASE ORDER ")[1:]
        poDocContent = [" PURCHASE ORDER " + poPageData for poPageData in poDocContent]
        self.updatePoData(poDocContent)

    def __buyer(self)->str:
        """
            Returns the buyer name 
        """
        #return re.findall(r".*PURCHASE\s+ORDER\s+\([A-Z]+\)\s+PAGE\s+[0-9]+\s+\n+\s+([A-Z\s]+)\s+ \s+",self.getPage(1))[0].strip()
        return 'JUST GROUP LIMITED'

    def __company(self)->str:
        """
            Returns the company name
        """
        return re.findall(r"DELIVER\s+TO\s?:\s+\n\s+([A-Z\s]+)\s+[A-Z]+",self.getPage(1))[0].strip() + " LIMITED"

    def __poNumber(self)->int:
        """
            Returns the purchase order number
        """
        return int(re.findall(r"\s+ORDER\s?:\s?([0-9]+)\s+",self.getPage(1))[0])

    def __poDate(self)->str:
        """
            Returns the purchase order date
        """
        return datetime.strptime(re.findall(r"PRINT\s+DATE\s?:\s+(\d+/\d+/\d+)\s+",self.getPage(1))[0].strip(),"%d/%m/%y").strftime("%d-%b-%y")

    def __style(self)->str:
        """
            Returns the style
        """
        return re.findall(r"\s+LINE\s?:\s?([0-9]+)\s+",self.getPage(1))[0]

    def __styleDescription(self)->str:
        """
            Returns the style description
        """
        return re.findall(r"\s+DESCRIPTION\s?:\s?(.*)\n",self._get_page(self._num_pages()).upper())[0].strip()

    def __totalQuantity(self)->int:
        """
            Returns the total quantity
        """
        return int(re.findall(r"\n\s+TOTAL\s+[0-9\s]+\s+([0-9]+)\s+",self.getPage(self.numPages()).upper())[0])

    def __currency(self)->str:
        """
            Returns the currency type
        """
        return self.getCurrencySymbol(re.findall(r"\s?INSTRUCTIONS\s?:\s?FOB\s+([A-Z]+)\s+",self.getPage(1))[0])

    def __shipmentMode(self)->str:
        """
            Returns the shipment mode
        """
        """try:
            return re.findall(r"\s?INSTRUCTIONS\s?:\s?FOB\s?[A-Z]+\s+\$?[\d\.]+\s+ETD\s+[0-9/]+\s+ETA\s+[0-9/]+\s+([A-Z]+)\s+",self.getPage(self.numPages()).upper())[0]
        except IndexError:
            return """""
        return 'SEA'
        
    def __getSizeRange(self,currentSize:str,newSize:str=None)->str:
        """
            Returns the size range
        """
        sizeWeightDict = {
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
        }

        if newSize==None:
            sizeList = set(str(currentSize).split(" - "))
        elif newSize!=None:
            sizeList = set(str(currentSize).split(" - ") + str(newSize).split(" "))
        try:
            sizeDict = {size : sizeWeightDict[size] for size in sizeList}
            sortedSizeList = sorted(sizeDict.items(), key=lambda x:x[1])
            if len(sortedSizeList)==1:
                return f"{sortedSizeList[0][0]}"
            elif len(sortedSizeList)>1:
                return f"{sortedSizeList[0][0]} - {sortedSizeList[-1][0]}"

        except KeyError:
            sizeList = [int(size) for size in sizeList]
            sortedSizeList = sorted(sizeList)
            if len(sortedSizeList)==1:
                return f"{sortedSizeList[0]}"
            elif len(sortedSizeList)>1:
                return f"{sortedSizeList[0]} - {sortedSizeList[-1]}"

    def __purchaseOrders(self)->dict:
        """
            Returns the purchase orders details
        """
        poDict = {}
        countryCode = re.findall(r"\s+PURCHASE\s+ORDER\s+\(?([A-Z]+)\)?\s+PAGE\s+[0-9]+",self.getPage(1))[0][:2]
        dest = pycountry.countries.get(alpha_2=countryCode).name.upper()
        shipdate = datetime.strptime(re.findall(r"\s?INSTRUCTIONS\s?:\s?.*\s+ETD\s+(\d+/\d+)\s*",self.getPage(1))[0].strip(),"%d/%m").strftime("%d-%b") + "-" +self.__poDate().split("-")[-1]
        supplierCost = float(re.findall(r"\s?INSTRUCTIONS\s?:\s?FOB\s?[A-Z]+\s+\$?([\d\.]+)\s+",self.getPage(self.numPages()).upper())[0])
        sizes = re.findall("COLOUR\s+DESC([0-9SMXL\s]+)\s+TOTAL\s?",self.getPage(self.numPages()).upper())[0]
        # size correction

        for sizeNumber in range(0,7):
            if sizeNumber==0:
                pass
            elif sizeNumber==1:
                pass
            elif sizeNumber >= 2:
                sizes = sizes.replace(f" {sizeNumber*'X'}S ",f" {sizeNumber}XS ")
                sizes = sizes.replace(f" {sizeNumber*'X'}L ",f" {sizeNumber}XL ")
        sizeList = list(filter(None,sizes.split(" ")))
        sizeRange = self.__getSizeRange(" - ".join(sizeList))

        colourBasedPackData = re.findall(r"TOTAL\s+([0-9A-Z\s/]+)\n\s+TOTAL",self.getPage(self.numPages()).upper())[0]
        colourBasedPackData = re.findall(r"\s?([0-9]*\s?[A-Z\s]+)\s+[0-9\s]*\s+([0-9]+)\s+\n",colourBasedPackData)

        packsData = []
        for eachPo in colourBasedPackData:
            colour = eachPo[0].strip()
            n = int(eachPo[1])
            packData = {
                'pack_sizes': sizeRange,
                'pack_colour': colour,
                'n_packs':"",
                'n_units':n,
                "supplier_cost":supplierCost
                }
            packsData.append(packData)

        destSummary = {
            "dest":dest,
            "dest_num":0,
            "n_units":"",
            "n_packs":"",
            "ship_date":shipdate,
            "size_range":sizeRange,
            "packs_data":packsData
        }
        poDict[0] = destSummary
        return poDict

    def __poDetails(self)->list:
        """
            Returns a list of purchase order data details
        """
        poDetails = {
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
            "style_desc":self.__styleDescription(),
            "gmt_item":"",
            "uom":"",
            "ratio":"",
            "total_qty":self.__totalQuantity(),
            "currency":self.__currency(),
            "factory":"",
            "fabric_src":"",
            "fabric": "",
            "fabric_mill":"",
            "sust_fabric":"",
            "po_num":self.__poNumber(),
            "po_date":self.__poDate(),
            "po_status":"",
            "shipment_mode":self.__shipmentMode(),
            "purchase_orders":self.__purchaseOrders()
        }
        return [poDetails]

    def output(self)->tuple:
        """
            Returns the extracted data
        """
        return (self.__poDetails())