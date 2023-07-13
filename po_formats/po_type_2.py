import re
from datetime import datetime
from po_formats.po_base import PO_BASE

class PO_TYPE_2(PO_BASE):
    """
        Class for TYPE 2 purchase order document
    """
    def __init__(self, poDocFilepath: str) -> None:
        super().__init__(poDocFilepath)
        self.__dataPartition = self.__dataPartitioning()

    def __dataPartitioning(self)->dict:
        """
            Partitioning data into segments
        """
        poDocContent = ""
        for pageNumber in range(1,self.numPages()+1):
             poDocContent += self.getPage(pageNumber)
        partitions = {}
        packNumList = re.findall(r"PACK\s?:\s?(\d+)\s+TOTAL\s+QTY\s+:",poDocContent)
        for index,packNumber in enumerate(packNumList):
            try:
                partitions[int(packNumber)]= f"PACK: {packNumber} TOTAL QTY :" + poDocContent.split(f"PACK: {packNumber} TOTAL QTY :")[1].split(f"PACK: {packNumList[index+1]} TOTAL QTY :")[0]
            except IndexError:
                partitions[int(packNumber)]= f"PACK: {packNumber} TOTAL QTY :" + poDocContent.split(f"PACK: {packNumber} TOTAL QTY :")[1]

        return partitions

    def __buyer(self)->str:
        """
            Returns the buyer name 
        """
        return re.findall(r"(.*)\s+[A-Z]+-[A-Z\s]*\s?PORT\s+SPLIT",self.getPage(1))[0].strip().upper()

    def __company(self)->str:
        """
            Returns the company name
        """
        return re.findall(r"\s?SUPPLIER\s?\n\s?\d+\s+(.*)\s?\n",self.getPage(1))[0].strip().upper()

    def __poNumber(self)->int:
        """
            Returns the purchase order number
        """
        return int(re.findall(r"ORDER\s?NUMBER\s?:\s?(\d+)",self.getPage(1))[0].strip())

    def __poDate(self)->str:
        """
            Returns the purchase order date
        """
        return datetime.strptime(re.findall(r"\s?DATE:\s?([0-9]+/[0-9]+/[0-9]+)",self.getPage(1))[0],"%d/%m/%y").strftime("%d-%b-%y")

    def __style(self,partitionNumber:int)->str:
        """
            Returns the style
        """
        try:
            return re.findall(r"KEYCODE\s?:\s?\d+\s+([A-Z0-9]+)\s?",self.__dataPartition[partitionNumber])[0]
        except IndexError:
            return re.findall(r"STYLE\s+PACK\s?:\s?\d+\s+([A-Z0-9]+)\s?",self.__dataPartition[partitionNumber])[0]

    def __gmtItem(self,partitionNumber:int)->str:
        """
            Returns the gmt item
        """
        try:
            return re.findall(r"KEYCODE\s?:\s?\d+\s+[A-Z0-9]+\s+([A-Z\s]+)\s+FLAT\s+PACK",self.__dataPartition[partitionNumber])[0]
        except IndexError:
            return re.findall(r"STYLE\s+PACK\s?:\s?\d+\s+[A-Z0-9]+\s+([A-Z\s]+)\s+FLAT\s+PACK",self.__dataPartition[partitionNumber])[0]

    def __totalQuantity(self,partitionNumber:int)->int:
        """
            Returns the total quantity
        """
        return int(re.findall(r"PACK\s?:\s?\d+\s+TOTAL\s+QTY\s?:\s?(\d+)\s+",self.__dataPartition[partitionNumber])[0])

    def __currency(self,partitionNumber:int)->str:
        """
            Returns the currency type
        """
        return self.getCurrencySymbol(re.findall(r"\s+CURRENCY\s?:\s?([A-Z]+)\s?",self.__dataPartition[partitionNumber])[0])

    def __getSizeRange(self,currentSizes:str,newSizes:str=None)->str:
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

        if newSizes==None:
            sizeList = set(currentSizes.split(" - "))
        elif newSizes!=None:
            sizeList = set(currentSizes.split(" - ") + newSizes.split(" "))
        try:
            sizeDict = {size : sizeWeightDict[size] for size in sizeList}
            sortedSizeList = sorted(sizeDict.items(), key=lambda x:x[1])
            return f"{sortedSizeList[0][0]} - {sortedSizeList[-1][0]}"
        except KeyError:
            if newSizes==None:
                sizeList = re.findall(r"([0-9]+)",currentSizes)
            elif newSizes!=None:
                sizeList = re.findall(r"([0-9]+)",currentSizes)+re.findall(r"([0-9]+)",newSizes)
            sizeList = sorted([int(size) for size in sizeList])
            if len(sizeList)==1:
                return f"{sizeList[0]}"
            if len(sizeList)>1:
                return f"{sizeList[0]} - {sizeList[-1]}"

    def __purchaseOrders(self,partitionNumber:int)->dict:
        """
            Returns the purchase orders details
        """
        poDict = {}

        supplierCost = float(re.findall(r"COST\s+PER\s+UNIT\s?-\s?HOME\s+COST\s?:\s?([0-9\.]+)\s+",self.__dataPartition[partitionNumber])[0])
        shipDate = datetime.strptime(re.findall(r"\s?DLV\s+CONS\s+DATE\s?:\s?([0-9]+/[0-9]+/[0-9]+)",self.getPage(1))[0],"%d/%m/%y").strftime("%d-%b-%y")

        destList = re.findall(r"(.*)\n\s?LOCN\s?:\s?QTY\s?",self.__dataPartition[partitionNumber])[0].strip().split(" ")
        destNumberList = re.findall(r"(\d+)\s?:\s?\d+",self.__dataPartition[partitionNumber])
        destQuantityList = re.findall(r"\d+\s?:\s?(\d+)",self.__dataPartition[partitionNumber])

        try:
            packColour = re.findall(r"\d+\s+\d+\s+\d+\s+UNITS\s+([A-Z]+)\s?",self.__dataPartition[partitionNumber])[0]
        except IndexError:
            packColour = re.findall(r"COLOUR\s?:\s?([A-Z]+)\s+",self.__dataPartition[partitionNumber])[0]

        partitionData:str = self.__dataPartition[partitionNumber]
        # Remove
        partitionData = partitionData.replace(" CAMO "," ")
        # size data refactoring
        for sizeNumber in range(0,7):
            if sizeNumber ==0:
                partitionData = partitionData.replace(f" SMALL",f" S")
                partitionData = partitionData.replace(f" LARGE",f" L")
                partitionData = partitionData.replace(f" MEDIUM",f" M")
            elif sizeNumber ==1:
                # Small
                partitionData = partitionData.replace(f" {sizeNumber*'X'}S",f" XS")
                partitionData = partitionData.replace(f" {sizeNumber*'X'} S",f" XS")
                partitionData = partitionData.replace(f" {sizeNumber*'X'} SMALL",f" XS")

                # Large
                partitionData = partitionData.replace(f" {sizeNumber*'X'}L",f" XL")
                partitionData = partitionData.replace(f" {sizeNumber*'X'} L",f" XL")
                partitionData = partitionData.replace(f" {sizeNumber*'X'} LARGE",f" XL")   
            else:
                # small
                partitionData = partitionData.replace(f" {sizeNumber*'X'}S",f" {sizeNumber}XS")
                partitionData = partitionData.replace(f" {sizeNumber}X S",f" {sizeNumber}XS")
                partitionData = partitionData.replace(f" {sizeNumber*'X'} SMALL",f" {sizeNumber}XS")
                partitionData = partitionData.replace(f" {sizeNumber}X SMALL",f" {sizeNumber}XS")

                # Large
                partitionData = partitionData.replace(f" {sizeNumber*'X'}L",f" {sizeNumber}XL")
                partitionData = partitionData.replace(f" {sizeNumber}X L",f" {sizeNumber}XL")
                partitionData = partitionData.replace(f" {sizeNumber*'X'} LARGE",f" {sizeNumber}XL")
                partitionData = partitionData.replace(f" {sizeNumber}X LARGE",f" {sizeNumber}XL")      

        packSizes = re.findall(r"\d+\s+\d+\s+\d+\s+UNITS\s+[A-Z]+\s+([A-Z0-9]+)",partitionData)
        if len(packSizes)!=0:
            packSizes = self.__getSizeRange(" - ".join(packSizes))
        elif len(packSizes)==0:
            packSizes = re.findall(r"SIZE\s?:\s?(\d+)\s+",self.__dataPartition[partitionNumber])[0]

        for index, destNumber in enumerate(destNumberList):
            poDict[destNumber]={
                "dest":destList[index],
                "dest_num":self.__poNumber(),
                "n_units":self.__totalQuantity(partitionNumber),
                "n_packs":0,
                "ship_date":shipDate,
                "size_range":"",
                "packs_data":[{
                    'pack_sizes': packSizes,
                    'pack_colour': packColour,
                    'n_packs':None,
                    'n_units':int(destQuantityList[index]),
                    "supplier_cost":supplierCost
                }]
            }
        return poDict

    def __poDetails(self)->list:
        """
            Returns a list of purchase order data details
        """
        poDetails = []

        # Calculating size range and assigning to destination dictionary
        partitionBasedDestDict = {}
        sizeRange = ""
        for partitionNumber in self.__dataPartition.keys():
            purchaseOrders = self.__purchaseOrders(partitionNumber)
            for destNumber in purchaseOrders.keys():
                packSizes = purchaseOrders[destNumber]['packs_data'][0]['pack_sizes']
                sizeRange += packSizes + " - "

        sizeRange = self.__getSizeRange( " - ".join(sizeRange.split(" - ")[:-1]))
        for partitionNumber in self.__dataPartition.keys():
            purchaseOrders = self.__purchaseOrders(partitionNumber)
            for destNumber in purchaseOrders.keys():
                purchaseOrders[destNumber]["size_range"] = sizeRange
            partitionBasedDestDict[partitionNumber] = purchaseOrders

        for partitionNumber in self.__dataPartition.keys():
            poDetail = {
                "team":"",
                "src_merc":"",
                "company":self.__company(),
                "consignee":self.__buyer(),
                "buyer":self.__buyer(),
                "category":"",
                "dept":"",
                "season_year":"",
                "season":"",
                "style":self.__style(partitionNumber),
                "style_desc":self.__style(partitionNumber),
                "gmt_item":self.__gmtItem(partitionNumber),
                "uom":"",
                "ratio":"",
                "total_qty":self.__totalQuantity(partitionNumber),
                "currency":self.__currency(partitionNumber),
                "factory":"",
                "fabric_src":"",
                "fabric": "",
                "fabric_mill":"",
                "sust_fabric":"",
                "po_num":self.__poNumber(),
                "po_date":self.__poDate(),
                "po_status":"",
                "shipment_mode":"",
                "purchase_orders":partitionBasedDestDict[partitionNumber]
            }
            poDetails.append(poDetail)
        return poDetails

    def output(self)->tuple:
        """
            Returns the extracted data
        """
        return (self.__poDetails())