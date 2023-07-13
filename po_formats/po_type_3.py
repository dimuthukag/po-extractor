import re
from datetime import datetime
from po_formats.po_base import PO_BASE
from po_formats.text_extract import extract

class PO_TYPE_3(PO_BASE):
    def __init__(self, poDocFilepath: str, poDocContent:list,scalingFactor:float) -> None:
        super().__init__(poDocFilepath,poDocContent,scalingFactor)
        self.__dataPartition = self.__dataPartitioning()

    def __dataPartitioning(self)->dict:
        """
            Partitioning data into segments
        """
        partitions = {1:"",2:""}
        for pageNumber in range(1,4):
            partitions[1] += self.getPage(pageNumber)
        for pageNumber in range(4,self._num_pages()+1):
            partitions[2] += self.getPage(pageNumber)
        return partitions

    def __buyer(self)->str:
        """
            Returns the buyer name 
        """
        return re.findall(r"^(.*)\n",self.getPage(1))[0].strip().upper()

    def __company(self)->str:
        """
            Returns the company name
        """
        return re.findall(r"To\s?:\s?(.*)\s+FOB",self.getPage(1))[0].strip().upper()

    def __season(self)->str:
        """
            Returns the season
        """
        try:
            return re.findall(r"Season\s?:\s?([A-Z0-9]+)\n",self.getPage(3))[0].strip()
        except IndexError:
            try:
                return re.findall(r"WK\s+Code\s?:\s?([0-9]+)\n",self.getPage(3))[0].strip()
            except IndexError:
                return ""

    def __poNumber(self)->int:
        """
            Returns the purchase order number
        """
        return int(re.findall(r"Purchase\s+Order\s+No\.?\s?:\s?(\d+)\s?",self.getPage(1).replace("Purchase Order Nc.:","Purchase Order No.:"))[0].strip())

    def __style(self)->str:
        """
            Returns the style
        """
        return re.findall(r"SUPPLIER\s+REF\.?\s?:\s?([A-Z0-9\-\—]+)\s?",self.getPage(3))[0]

    def __totalQuantity(self)->int:
        """
            Returns the total quantity
        """
        try:
            return int(re.findall(r"Total\s+Units\s+(\d+)\s+",self.__dataPartition[2].replace("Un1ts","Units"))[0])
        except IndexError:
            return int(re.findall(r"Total\s+(\d+)\s+",self.__dataPartition[2])[0])

    def __currency(self)->str:
        """
            Returns the currency type
        """
        return self.getCurrencySymbol(re.findall(r"\s+Order\s+Value\s+([A-Z]+)\s+",self.__dataPartition[2])[0])

    def __factory(self)->str:
        """
            Returns the factory name
        """
        return re.findall(r"Factory\s?:\s?(.*)\n",self.__dataPartition[1])[0].strip().upper()

    def __shipmentMode(self)->str:
        """
            Returns the shipment mode
        """
        return re.findall(r"Transport\s?:\s?([A-Z\s]+)\s+Carrier",self.__dataPartition[1])[0]

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
            sizeList = set(str(currentSizes).split(" - "))
        elif newSizes!=None:
            sizeList = set(str(currentSizes).split(" - ") + str(newSizes).split(" "))
        try:
            sizeDict = {size : sizeWeightDict[size] for size in sizeList}
            sortedSizeList = sorted(sizeDict.items(), key=lambda x:x[1])
            if len(sortedSizeList)==1:
                return f"{sortedSizeList[0][0]}"
            elif len(sortedSizeList)>1:
                return f"{sortedSizeList[0][0]} - {sortedSizeList[-1][0]}"

        except KeyError:
            if newSizes==None:
                sizeList = list(set(str(currentSizes).split(" - ")))
            elif newSizes!=None:
                sizeList = list(set(str(currentSizes).split(" - ") + str(newSizes).split(" ")))
            try:
                sizeList = [int(size) for size in sizeList]
                sizeList = sorted(sizeList)
                if len(sizeList)==1:
                    return sizeList[0]
                elif len(sizeList)>1:
                    return f"{sizeList[0]} - {sizeList[-1]}"
            except IndexError:
                return "-"

    def __purchaseOrders(self)->dict:
        """
            Returns the purchase orders details
        """
        poDict = {}
        dest = re.findall(r"Arrival\s+Port\s?:\s?([A-Z]+)\s+",self.__dataPartition[1])[0]
        shipdate = datetime.strptime(re.findall(r"Est\.?\s?time\s+Depart\s?:\s?.*\s+\d+\s+[A-Z]+\s+\d+\s+(\d+\s+[A-Z]+\s+\d+)",self.__dataPartition[1])[0] ,"%d %b %y").strftime("%d-%b-%y")

        #size correction
        def __sizeCorrection(data:str):
            data = data.replace(" l "," 1 ").upper()
            for sizeNumber in range(0,7):
                data = data.replace(" SXL "," 5XL ")
                if sizeNumber==0:
                    pass
                elif sizeNumber==1:
                    data = data.replace(f" KS ",f" XS ")
                    data = data.replace(f" KL ",f" XL ")
                    data = data.replace(f" K ",f" XL ")
                else:
                    data = data.replace(f" {sizeNumber}KS ",f" {sizeNumber}XS ")
                    data = data.replace(f" {sizeNumber}KL ",f" {sizeNumber}XL ")
                    data = data.replace(f" {sizeNumber}X ",f" {sizeNumber}XL ")
                    data = data.replace(f" {sizeNumber}K ",f" {sizeNumber}XL ")

            for sizeNumber in range(0,10):
                data = data.replace(f" L{sizeNumber} ", f" 1{sizeNumber} ")
                data = data.replace(f" {sizeNumber}L ", f" {sizeNumber}1 ")

            return data

        data = __sizeCorrection(self.__dataPartition[2])
        tempDataPartition = data.split("COMPONENTS OF BUYING PACK")[1:]

        nPacksList = re.findall(r"BUYING\s+PACK\s+(\d+)\s+PACKS",data)

        supplierCostBasedComponentData = {}
        sizeRangeList =[]

        nTotal_1 = 0

        for index,nPack in enumerate(nPacksList):
            componentsList = re.findall(r"\d+\-?\—?\d+\-?\—?\d+\s+(\d+)\s+\$?[\d\.]+[A-Z0-9\s]+\s+([A-Z/]+)\s+([0-9]*[SMXL]*)\s+[A-Z0-9]*\s?(\d+\.\d+)",tempDataPartition[index].replace("&",""))
            for component in componentsList:
                n=int(component[0])
                colour=component[1]
                size=component[2]
                supplierCost = float(component[3])
                sizeRangeList.append(size)
                nTotal_1 += n*int(nPack)
                if supplierCost not in supplierCostBasedComponentData.keys():
                    colourBasedComponentData={}
                    colourBasedComponentData[colour]={
                        'pack_sizes': self.__getSizeRange(size),
                        'pack_colour': colour,
                        'n_packs':None,
                        'n_units':n*int(nPack),
                        "supplier_cost":supplierCost
                    }
                    supplierCostBasedComponentData[supplierCost] = colourBasedComponentData
                elif supplierCost in supplierCostBasedComponentData.keys():
                    colourBasedComponentData = supplierCostBasedComponentData[supplierCost]
                    if colour not in colourBasedComponentData.keys():
                        colourBasedComponentData[colour]={
                            'pack_sizes': self.__getSizeRange(size),
                            'pack_colour': colour,
                            'n_packs':None,
                            'n_units':n*int(nPack),
                            "supplier_cost":supplierCost
                        }
                    elif colour in colourBasedComponentData.keys():
                        current = colourBasedComponentData[colour]
                        colourBasedComponentData[colour]={
                            'pack_sizes': self.__getSizeRange(current['pack_sizes'],size),
                            'pack_colour': colour,
                            'n_packs':None,
                            'n_units':n*int(nPack) + current['n_units'],
                            "supplier_cost":supplierCost
                        }
                    supplierCostBasedComponentData[supplierCost] = colourBasedComponentData
        scalingFactor = self.scallingFactor()
        while True:
            nTotal_2 = 0
            componentsList = re.findall(r"[A-Z0-9\-\—]+\s+(\d+)\s+\d+\s+\d+\s+[\d\.]+\s+[A-Z0-9]*\s?(\d+\.\d+)\s+[\d\.]+\s?\n\n?[\d\.]+\s+[\d\.]+\s?\n\n?[0-9\-\—]+\s+\$?[\d\.]+.*\s+([A-Z/]+)\s+([0-9]*[SMXL]*)\s+[0-9]+",data)
            tempSupplierCostBasedComponentData = {}

            for component in componentsList:
                n=int(component[0])
                supplierCost = float(component[1])
                colour=component[2]
                size=component[3]
                sizeRangeList.append(size)
                nTotal_2 += n
                if supplierCost not in tempSupplierCostBasedComponentData.keys():
                    colourBasedComponentData={}
                    colourBasedComponentData[colour]={
                        'pack_sizes': self.__getSizeRange(size),
                        'pack_colour': colour,
                        'n_packs':None,
                        'n_units':n,
                        "supplier_cost":supplierCost
                    }
                    tempSupplierCostBasedComponentData[supplierCost] = colourBasedComponentData
                elif supplierCost in tempSupplierCostBasedComponentData.keys():
                    colourBasedComponentData = tempSupplierCostBasedComponentData[supplierCost]
                    if colour not in colourBasedComponentData.keys():
                        colourBasedComponentData[colour]={
                            'pack_sizes': self.__getSizeRange(size),
                            'pack_colour': colour,
                            'n_packs':None,
                            'n_units':n,
                            "supplier_cost":supplierCost
                        }
                    elif colour in colourBasedComponentData.keys():
                        current = colourBasedComponentData[colour]
                        colourBasedComponentData[colour]={
                            'pack_sizes': self.__getSizeRange(current['pack_sizes'],size),
                            'pack_colour': colour,
                            'n_packs':None,
                            'n_units':n + current['n_units'],
                            "supplier_cost":supplierCost
                        }
                    tempSupplierCostBasedComponentData[supplierCost] = colourBasedComponentData

            if (nTotal_1+nTotal_2) == self.__totalQuantity():
                for supplierCost in tempSupplierCostBasedComponentData.keys():
                    if supplierCost not in supplierCostBasedComponentData.keys():
                        supplierCostBasedComponentData[supplierCost] = tempSupplierCostBasedComponentData[supplierCost]
                    elif supplierCost in supplierCostBasedComponentData.keys():
                        for colour in tempSupplierCostBasedComponentData[supplierCost].keys():
                            if colour not in supplierCostBasedComponentData[supplierCost].keys():
                                supplierCostBasedComponentData[supplierCost][colour] = tempSupplierCostBasedComponentData[supplierCost][colour]
                            elif colour in supplierCostBasedComponentData[supplierCost].keys():
                                current = supplierCostBasedComponentData[supplierCost][colour]
                                supplierCostBasedComponentData[supplierCost][colour] = {
                                    'pack_sizes': self.__getSizeRange(current['pack_sizes'],tempSupplierCostBasedComponentData[supplierCost][colour]['pack_sizes'].replace(" - "," ")),
                                    'pack_colour': colour,
                                    'n_packs':None,
                                    'n_units':tempSupplierCostBasedComponentData[supplierCost][colour]['n_units'] + current['n_units'],
                                    "supplier_cost":supplierCost
                                } 
                break
            else:
                scalingFactor += 0.01
                pdf_content = extract(self.poDocFilepath(),4,self.numPages(),scalingFactor)

                data = __sizeCorrection("\n".join(pdf_content))

        packs_data = []
        for supplierCost in supplierCostBasedComponentData.keys():
            for colour in supplierCostBasedComponentData[supplierCost].keys():
                packs_data.append(supplierCostBasedComponentData[supplierCost][colour])

        poDict[0]={
            "dest":dest,
            "dest_num":self.__poNumber(),
            "n_units":self.__totalQuantity(),
            "n_packs":0,
            "ship_date":shipdate,
            "size_range":self.__getSizeRange(" - ".join(sizeRangeList)),
            "packs_data":packs_data
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
            "consignee":self.__buyer(),
            "buyer":self.__buyer(),
            "category":"",
            "dept":"",
            "season_year":"",
            "season":self.__season(),
            "style":self.__style(),
            "style_desc":self.__style(),
            "gmt_item":"",
            "uom":"",
            "ratio":"",
            "total_qty":self.__totalQuantity(),
            "currency":self.__currency(),
            "factory":self.__factory(),
            "fabric_src":"",
            "fabric": "",
            "fabric_mill":"",
            "sust_fabric":"",
            "po_num":self.__poNumber(),
            "po_date":"",
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