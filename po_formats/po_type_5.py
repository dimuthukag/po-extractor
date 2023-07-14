import re
from datetime import datetime
from po_formats.po_base import PO_BASE

class PO_TYPE_5(PO_BASE):
    def __init__(self, poDocFilepath: str) -> None:
        super().__init__(poDocFilepath)

    def __buyer(self)->str:
        """
            Returns the buyer name 
        """
        return "SALLING GROUP"

    def __company(self)->str:
        """
            Returns the company name
        """
        return "CENTRO TEX LIMITED"

    def __season(self)->str:
        """
            Returns the season
        """
        try:
            return re.findall(r"\s?STYLE\s+NAME\s?:\s?[A-Z0-9\s]+\s+([A-Z]{1}[0-9]{1}\s+[0-9]{2,4})\s?\n",self.getPage(1).upper())[0]
        except IndexError:
            return ""

    def __poNumber(self)->int:
        """
            Returns the purchase order number
        """
        try:
            return int(re.findall(r"\s?STYLE\s+NUMBER\s?:\s?\n\s?(\d+)\s+",self.getPage(1).upper())[0])
        except IndexError:
            return int(re.findall(r"PO\s+NUMBER\s?:?\s?(\d+)\s?",self.getPage(1).upper())[0])

    def __poDate(self)->str:
        """
            Returns the purchase order date
        """
        try:
            return datetime.strptime(re.findall(r"\s?PRINT\s+DATE\s?:\s?(\d+/\d+/\d+)\s+",self.getPage(1).upper())[0] ,"%d/%m/%Y").strftime("%d-%b-%y")
        except IndexError:
            return datetime.strptime(re.findall(r"\s?ORDER\s+DATE\s?:\s?(\d+\.\d+\.\d+)\s+",self.getPage(1).upper())[0] ,"%d.%m.%Y").strftime("%d-%b-%y")

    def __currency(self)->str:
        """
            Returns the currency type
        """
        return "$"

    def __fabric(self)->str:
        """
            Returns the fabric type
        """
        fabricList = re.findall(r"([0-9]{1,3}%\s?[A-Z\s\-\(\)/]+)",self.getPage(1).upper())
        fabricList = [fabric.replace("-","").replace("%","% ").replace("%  ","% ").strip().split("COLOR COMBINATION")[0] for fabric in fabricList]
        if len(fabricList)==0:
            fabricList = re.findall(r"[0-9]{1,3}%\s?[A-Z\-\s\(\)/]+\s?",self.getPage(2).upper())
            fabricList = list(set([fabric.replace("%","% ").replace("%  ","% ").strip().split("COLOR COMBINATION")[0] for fabric in fabricList]))
        return  ", ".join(fabricList).replace("\r","").replace("\n","")

    def __shipmentMode(self)->str:
        """
            Returns the shipment mode
        """
        return "SEA"

    def __style(self)->str:
        """
            Returns the style
        """
        try:
            return re.findall(r"\s?STYLE\s+NAME\s?:\s?([A-Z0-9\s]+)\s+[A-Z]{1}[0-9]{1}\s+[0-9]{2,4}\s?\n",self.getPage(1).upper())[0].replace("SHIPMENT DATE","").strip()
        except IndexError:
            try:
                return re.findall(r"\s?STYLE\s+NAME\s?:\s?([A-Z0-9\s]+)\s?.*\n?",self.getPage(1).upper())[0].replace("SHIPMENT DATE","").strip()
            except IndexError:
                return re.findall(r"\n\d+\s+[0-9A-Z\s]+\s+\d+\s+([0-9A-Z\s\-]+),\s?[A-Z\.]+,\s+[0-9]*X?[SML]?\s+\d+\s+[\d\.]+",self.getPage(2).upper())[0].replace("SHIPMENT DATE","").strip()

    def __styleDescription(self)->str:
        """
            Returns the style description
        """
        try:
            return re.findall(r"\s?STYLE\s?:\s?(.*)\n",self.getPage(1).upper())[0].strip()
        except IndexError:
            return ""

    def __getSizeRange(self,currentSizes:str,newSizes:str=None)->str:
        """
            Returns the size range
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

    def __purchaseOrders(self)->dict:
        """
            Returns the purchase orders details
        """
        poDict = {}
        dest = "AARHUS"

        allContent = "".join([self.getPage(pageNumber) for pageNumber in range(1,self.numPages()+1)])

        # ship date
        try:
            (_d,_m,_y) = re.findall(r"\s?ETD\s?:?\s?.*[NEW]?\s?:?\s+(\d{0,2})[\.|\-]{1}(\d{0,2})[\.|\-]{1}(\d{0,4})",allContent.upper())[0]
        except IndexError:
            try:
                (_d,_m,_y) = re.findall(r"\s?ETD\s?:?\s?.*[NEW]?\s?:?\s+(\d{0,2})[\.|\-]{1}([A-Z]{3})[\.|\-]{1}(\d{0,4})",allContent.upper())[0]
            except IndexError:
                try:
                    (_d,_m,_y) = re.findall(r"\s?SHIPMENT\s+DATE\s?:?\s?(\d{0,2})[\.|\-]{1}(\d{0,2})[\.|\-]{1}(\d{0,4})",allContent.upper())[0]
                except IndexError:
                    (_d,_m,_y) = re.findall(r"\s?SHIPMENT\s+DATE\s?:?\s?(\d{0,2})[\.|\-]{1}([A-Z]{3})[\.|\-]{1}(\d{0,4})",allContent.upper())[0]

        try:
            shipDate = datetime.strptime(f"{_d}/{_m}/{_y[-2:]}","%d/%m/%y").strftime("%d-%b-%y")
        except ValueError:
            shipDate = datetime.strptime(f"{_d}/{_m}/{_y[-2:]}","%d/%b/%y").strftime("%d-%b-%y")

        # supplier cost
        try:
            supplierCost = float(re.findall(r"\s?NET\s+PRICE\s?:\s?([\d\.]+)\s?[A-Z]+",allContent.upper())[0])
        except IndexError:
            supplierCost = None

        nTotal = 0
        colourBasedOrderDict = {}
        sizeRange = ""
        orderTableList = [re.sub(r"PRINT\s+DATE\s+.*\n?.*\n?.*\n?.*\n?.*\n?.*\n?.*\n?.*\n?.*\n?",'',orderTable) for orderTable in allContent.upper().split("COLOR COMBINATION")[1:]]
        orderTableList = ["COLOR COMBINATION" + orderTable for orderTable in orderTableList]

        for orderTable in orderTableList:
            sizes = re.findall(r"COLOR\s+COMBINATION\s+ARTICLE\s+NO\s+ARTICLE\s+EAN\s+CARTON\s+EAN([0-9SMXL\s/\n]+)PCS\s+CRT\s+TOTAL",orderTable)[0].replace("/"," ").replace("\r","").replace("\n"," ").strip()

            # size corrections
            sizes:str = sizes.replace("  "," ")
            if sizes.replace(" ","").isdigit():
                sizes:list = sizes.split(" ")
                lastSize = ""
                lastSizeCharLen = 0
                newSizes = []

                for size in sizes:
                    if len(size)<lastSizeCharLen:
                        lastSize = size
                    else:
                        newSizes.append(f"{lastSize}{size}")
                        lastSize=""
                    lastSizeCharLen = len(size)
                sizes = " ".join(newSizes)

            sizeRange += sizes + " "
            orderList = re.findall(r"[A-Z\s\.]*\s?\d*\s?\d+\s+\d+\s+\d*\s?\d+\s+\d+\s+\d+",orderTable)
            prevColour = ""
            for order in orderList:
                (colour,n) = re.findall(r"\s?([A-Z\s\.\n]*)\s+.*\s+(\d+)",order.replace("TCX","").strip())[0]
                #_colour = _colour.split("\n")[-1].strip()
                colour = colour.split("PCS CRT TOTAL")[-1].strip()
                colour = colour.replace("\n"," ")
                nTotal += int(n)
                if colour != "" and colour not in colourBasedOrderDict.keys():
                    colourBasedOrderDict[colour] = {
                        'pack_sizes': self.__getSizeRange(sizes.replace(" "," - ")),
                        'pack_colour': colour,
                        'n_packs':None,
                        'n_units':int(n),
                        "supplier_cost":supplierCost                  
                    }
                elif colour !="" and colour in colourBasedOrderDict.keys():
                    current = colourBasedOrderDict[colour]
                    colourBasedOrderDict[colour] = {
                        'pack_sizes': self.__getSizeRange(current['pack_sizes'],sizes),
                        'pack_colour': colour,
                        'n_packs':None,
                        'n_units':int(n) + current['n_units'],
                        "supplier_cost":supplierCost                  
                    }
                elif colour == "":
                    current = colourBasedOrderDict[prevColour]
                    colourBasedOrderDict[prevColour] = {
                        'pack_sizes': self.__getSizeRange(current['pack_sizes'],sizes),
                        'pack_colour': prevColour,
                        'n_packs':None,
                        'n_units':int(n) + current['n_units'],
                        "supplier_cost":supplierCost                  
                    }
                prevColour = colour

        packsData = []
        for colour in colourBasedOrderDict.keys():
            packsData.append(colourBasedOrderDict[colour])     

        orders = re.findall(r"\n(\d{0,5})\s+[0-9A-Z\s]+\s+\d+\s+[0-9A-Z\s\-]+,\s?([A-Z\.]+),\s+([0-9]*X?[SML]?)\s+(\d+)\s+([\d\.]+)",allContent.upper())

        for order in orders:
            n1,colour,size,n2,supplierCost = order

            sizeRange += size + " "
            nTotal += int(n1)*int(n2)   
            if colour not in colourBasedOrderDict:
                colourBasedOrderDict[colour] = { supplierCost: {
                        'pack_sizes': self.__getSizeRange(size),
                        'pack_colour': colour,
                        'n_packs':None,
                        'n_units':int(n1)*int(n2),
                        "supplier_cost":float(supplierCost)                  
                    }}
            elif colour in colourBasedOrderDict:
                if supplierCost not in colourBasedOrderDict[colour].keys():
                    colourBasedOrderDict[colour][supplierCost] = {
                        'pack_sizes': self.__getSizeRange(size),
                        'pack_colour': colour,
                        'n_packs':None,
                        'n_units':int(n1)*int(n2),
                        "supplier_cost":float(supplierCost)                  
                    }
                elif supplierCost in colourBasedOrderDict[colour].keys():
                    current = colourBasedOrderDict[colour][supplierCost]
                    colourBasedOrderDict[colour][supplierCost] = {
                        'pack_sizes': self.__getSizeRange(current['pack_sizes'], size),
                        'pack_colour': colour,
                        'n_packs':None,
                        'n_units':int(n1)*int(n2) + current['n_units'],
                        "supplier_cost":float(supplierCost)                  
                    }

        if len(packsData)==0:
            for colour in colourBasedOrderDict.keys():
                for supplierCost in colourBasedOrderDict[colour].keys():
                    packsData.append(colourBasedOrderDict[colour][supplierCost])

        poDict[0]={
            "dest":dest,
            "dest_num":0,
            "n_units":nTotal,
            "n_packs":0,
            "ship_date":shipDate,
            "size_range":self.__getSizeRange(" - ".join(sizeRange.strip().split(" "))),
            "packs_data":packsData
        }
        return poDict

    def __poDetails(self)->list:
        """
            Returns a list of purchase order data details
        """
        poDetails = {
            "team":"",
            "src_merc":"",
            "company":self.__company(),
            "consignee":self.__buyer() + " A/S",
            "buyer":self.__buyer(),
            "category":"",
            "dept":"",
            "season_year":self.__season().split(" ")[-1],
            "season":self.__season().split(" ")[0],
            "style":self.__style(),
            "style_desc":self.__styleDescription(),
            "gmt_item":"",
            "uom":"",
            "ratio":"",
            "total_qty":self.__purchaseOrders()[0]["n_units"],
            "currency":self.__currency(),
            "factory":"",
            "fabric_src":"",
            "fabric": self.__fabric(),
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