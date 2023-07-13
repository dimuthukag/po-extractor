import re
from datetime import datetime
from po_formats.po_base import PO_BASE

class PO_TYPE_1(PO_BASE):
    """
        Class for TYPE 1 purchase order document
    """
    def __init__(self,poDocFilepath:str) -> None:
        super().__init__(poDocFilepath)
        self.__dataPartition = self.__dataPartitioning()

    def __dataPartitioning(self)->dict:
        """
            Partitioning data into segments
        """
        partitions = {1:"",2:"",3:""}
        styleInfoPageNumber = 2
        for pageNumber in range(1,self.numPages()+1):
            pageContent = self.getPage(pageNumber)
            if re.findall(r"SUPPLIER\s+COPY\s+STYLE\s+INFORMATION\s+Kimball",pageContent):
                styleInfoPageNumber = pageNumber
                break

        for pageNumber in range(1, styleInfoPageNumber):
            partitions[1] += self.getPage(pageNumber)
        partitions[2] = self.getPage(styleInfoPageNumber)
        for pageNumber in range(styleInfoPageNumber, self.numPages()+1):
            partitions[3] += self.getPage(pageNumber)
        return partitions

    def __buyer(self)->str:
        """
            Returns the buyer name 
        """
        return re.findall(r"^.*\n.*\n(.*)\n",self.getPage(1))[0].strip().upper()

    def __company(self)->str:
        """
            Returns the company name
        """
        return re.findall(r"\nSupplier.*\n(.*)\n",self.getPage(1))[0].strip().upper()

    def __season(self)->str:
        """
            Returns the season
        """
        return re.findall(r"\nSeason/Year\s?:\s?([A-Z0-9]+)\s+",self.getPage(1))[0].strip().upper()

    def __poNumber(self)->int:
        """
            Returns the purchase order number
        """
        return int(re.findall(r"\nPurchase\s?Order\s?:\s+(\d+)\s?",self.getPage(1))[0].strip())

    def __poDate(self)->str:
        """
            Returns the purchase order date
        """
        return  datetime.strptime(re.findall(r"Order\s+Date\s?:\s?(\d+)\s+",self.getPage(1))[0].strip(),"%Y%m%d").strftime("%d-%b-%y")

    def __kimball(self)->int:
        """
            Returns the kimball value
        """
        return int(re.findall(r"\s+Kimball\s?:\s?(\d+)\s+",self.getPage(1))[0].strip())

    def __style(self)->str:
        """
            Returns the style
        """
        description = re.findall(r"\s+Description\s?:\s?([0-9&A-Z\s/-]+)\s+Kimball",self.getPage(1))[0].strip().upper()
        return f"{description}/{self.__poNumber()}/{self.__kimball()}"

    def __gmtItem(self)->str:
        """
            Returns the gmt item
        """
        return re.findall(r"\-?\s?Contains\s?-\s?(.*)\n",self.__dataPartition[2])[0].strip().upper()

    def __uom(self)->str:
        """
            Returns the uom
        """
        if "pieces" in self.__dataPartition[2]:
            return "Pcs"
        else:
            return ""

    def __totalQuantity(self)->int:
        """
            Returns the total quantity
        """
        return int(re.findall(r"\s+Total\s+Units\s?\(Inc\.\s?TBC\)\s?:\s?(\d+)\s?",self.getPage(1).replace(",",""))[0].strip())

    def __currency(self)->str:
        """
            Returns the currency type
        """
        return re.findall(r"Currency:\s+([a-zA-Z]+)",self.getPage(1))[0].strip().upper()

    def __factory(self)->str:
        """
            Returns the factory name
        """
        return re.findall(r"Factory.*\n(.*)\n",self.getPage(1))[0].strip().upper()

    def __fabric(self)->str:
        """
            Returns the fabric type
        """
        fabricList = list(set(re.findall(r"\-?\s?Fibre\s?-\s?(.*)\n",self.__dataPartition[2])))
        return ", ".join(fabricList).upper()

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
                sizeList = re.findall(r"([0-9\.]+/[0-9\.]+)",currentSizes)
            elif newSizes!=None:
                sizeList = re.findall(r"([0-9\.]+/[0-9\.]+)",currentSizes)+re.findall(r"([0-9\.]+/[0-9\.]+)",newSizes)
            try:
                return f"{sizeList[0]} - {sizeList[-1]}"
            except IndexError:
                if newSizes==None:
                    sizeList = re.findall(r"([0-9]+\s?-\s?[0-9]+M)",currentSizes)
                elif newSizes!=None:
                    sizeList = re.findall(r"([0-9]+\s?-\s?[0-9]+M)",currentSizes)+re.findall(r"([0-9]+\s?-\s?[0-9]+M)",newSizes)
                try:
                    return f"{sizeList[0].split('-')[0]} - {sizeList[-1].split('-')[-1]}"
                except IndexError:
                    if newSizes==None:
                        sizeList = re.findall(r"(ONE\s?-?\s?SIZE)",currentSizes)
                    elif newSizes!=None:
                        sizeList = re.findall(r"(ONE\s?-?\s?SIZE)",currentSizes)+re.findall(r"(ONE\s?-?\s?SIZE)",newSizes)
                    return sizeList[0].replace(" - "," ")

    def __purchaseOrders(self)->dict:
        """
            Returns the purchase orders details
        """
        poDict = {}
        dests = {
            "S":"SPAIN",
            "G":"GERMANY",
            "C":"CZECH REPUBLIC",
            "D":"DUBLIN-IRELAND",
            "N":"NETHERLAND",
            "B":"UNITED KINGDOM",
            "A":"USA",
            "Z":"UNITED KINGDOM",
            "F":"USA",
        } 
        shipdatesList =  re.findall(r"HANDOVER\s+DATE\s?:\s?(\d+)\s+",self.__dataPartition[1])

        for index, shipdate in enumerate(shipdatesList):
            for item in self.__dataPartition[1].split("HANDOVER DATE")[-len(shipdatesList):][index].split("\n"):
                try:
                    rawDestData = re.findall(r".*\s+([A-Z]{1}[0-9]{8})\s+(\d+)\s+(\d+)\s+(\d+)\r",item.replace(",",""))[0]
                    if rawDestData:
                        destSummary = {
                            "dest":dests[rawDestData[0][0]],
                            "dest_num":rawDestData[0],
                            "n_units":int(rawDestData[2]),
                            "n_packs":int(rawDestData[3]),
                            "ship_date":datetime.strptime(shipdate,"%Y%m%d").strftime("%d-%b-%y"),
                            "size_range":"",
                            "supplier_cost":None,
                            "packs_data":[]
                        }
                        poDict[rawDestData[0]] = destSummary
                except IndexError:
                    pass
        deliveriesList = re.findall(r"([A-Z]{1}[0-9]{8})\s+.*\${1}\s?([0-9\.]+)\s+\${1}\s?",self.__dataPartition[3].replace(",",""))

        correctionIndex = 0
        for index, delivery in enumerate(deliveriesList):
            destNumber = delivery[0]
            supplierCost = delivery[1]
            sizeList = []
            colourBasedPurchaseOrderDataDict = {}

            if poDict[destNumber]["n_packs"]==0:
                correctionIndex +=1
            else:
                purchaseOrderData = re.findall(r"(\d+)\s+(.*)\s+([a-zA-Z]+)\s+SOLID\s+COLOUR\s+(\d+)\s+(\d+)",self.__dataPartition[3].split("Pack Id Pack Sizes Pack Colours Pack Type Packs Units")[index+1-correctionIndex].replace(",","").upper())
                if len(purchaseOrderData)==0:
                    purchaseOrderData = re.findall(r"(\d+)\s+(.*)\s+([a-zA-Z]+)\s+SOLID\s+COLOUR/SOLID\s+SIZE\s+(\d+)\s+(\d+)",self.__dataPartition[3].split("Pack Id Pack Sizes Pack Colours Pack Type Packs Units")[index+1-correctionIndex].replace(",","").upper())

                for purchaseOrder in purchaseOrderData:
                    if purchaseOrder[2] not in colourBasedPurchaseOrderDataDict.keys():
                        if int(purchaseOrder[4]) != 0:
                            colourBasedPurchaseOrderDataDict[purchaseOrder[2]] = {
                                'pack_sizes': self.__getSizeRange(purchaseOrder[1].strip().replace(" "," - ")),
                                'pack_colour': purchaseOrder[2],
                                'n_packs':int(purchaseOrder[3]),
                                'n_units':int(purchaseOrder[4])
                            }
                            sizeList.append(self.__getSizeRange(purchaseOrder[1].strip().replace(" "," - ")))
                    elif purchaseOrder[2] in colourBasedPurchaseOrderDataDict.keys():
                        currentPurchaseOrder = colourBasedPurchaseOrderDataDict[purchaseOrder[2]]
                        colourBasedPurchaseOrderDataDict[purchaseOrder[2]] = {
                            'pack_sizes': self.__getSizeRange(currentPurchaseOrder['pack_sizes'],purchaseOrder[1]),
                            'pack_colour': purchaseOrder[2],
                            'n_packs':currentPurchaseOrder['n_packs'] + int(purchaseOrder[3]),
                            'n_units':currentPurchaseOrder['n_units'] + int(purchaseOrder[4])
                        }
                        sizeList.append(self.__getSizeRange(purchaseOrder[1].strip().replace(" "," - ")))
                sizeRange = self.__getSizeRange(" - ".join(sizeList))
                if sizeRange.split(' - ')[0] != sizeRange.split(' - ')[-1]:
                    poDict[destNumber]['size_range'] =  f"{sizeRange.split(' - ')[0]} - {sizeRange.split(' - ')[-1]}"
                elif sizeRange.split(' - ')[0] == sizeRange.split(' - ')[-1]:
                    poDict[destNumber]['size_range'] =  f"{sizeRange.split(' - ')[0]}"
                poDict[destNumber]["supplier_cost"]=float(supplierCost)
                poDict[destNumber]['packs_data'] = list(colourBasedPurchaseOrderDataDict.values())
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
            "season_year":int(self.__season()[2:]),
            "season":self.__season()[:2]+self.__season()[-2:],
            "style":self.__style(),
            "style_desc":self.__style(),
            "gmt_item":self.__gmtItem(),
            "uom":self.__uom(),
            "ratio":"",
            "total_qty":self.__totalQuantity(),
            "currency":self.__currency(),
            "factory":self.__factory(),
            "fabric_src":"",
            "fabric": self.__fabric(),
            "fabric_mill":"",
            "sust_fabric":"",
            "po_num":self.__poNumber(),
            "po_date":self.__poDate(),
            "po_status":"",
            "shipment_mode":"",
            "purchase_orders":self.__purchaseOrders()
        }
        return [poDetails]

    def output(self)->tuple:
        """
            Returns the extracted data
        """
        return (self.__poDetails())