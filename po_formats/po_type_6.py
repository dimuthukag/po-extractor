import re
from datetime import datetime
from po_formats.po_base import PO_BASE

class PO_TYPE_6(PO_BASE):
    def __init__(self, poDocFilepath: str) -> None:
        super().__init__(poDocFilepath)
        self.__allContent = "".join([self.getPage(page_num) for page_num in range(1,self.numPages()+1)])
        self.__svgData = "".join([self.getSvgData(page_num) for page_num in range(1,self.numPages()+1)])
        self.__dataPartition = self.__dataPartitioning()
        self.__docRegexPatterns = {
            "po_num":r"\d{5,10}",
            "ship_date":r"[A-Z]{0,3}\s*\d{1,2}\s*[A-Z]{0,2}\s*[A-Z]{0,2}\s*[\s\-/\.,]{1,3}[A-Z]*\d{0,2}[\s\-/\.,]{1,3}\d{2,4}[0-9\s\-/\.,]*",
            "style_desc":r"[0-9A-Z\s\.\-'/\´]+",
            "style":r"[0-9A-Z\s]+",
            "fabric":r"\d{1,3}[\s|%]{1}\s{0,}[\|]?\s?[0-9A-Z\s\*/\-,%]+",
            "colour":r"[A-Z0-9\s\.\-/]+",
            "size":r"\d*[X]{0,10}[SML]?"
        }

    def __dataPartitioning(self)->dict:
        """
            Partitioning data into segments
        """
        partitions = {}
        svgData = re.sub(r'</text><text\s+fill=\"[a-z]+\"\s+x=\"[\d\.]+\"\s+y=\"[\d\.]+\"\s?>'," | ",self.__svgData)
        svgData = re.sub(r'</text><text\s+fill=\"[a-z]+\"\s+x=\"[\d\.]+\"\s+y=\"[\d\.]+\"\s?/?>\s?<text fill=\"[a-z]+\"\s+x=\"[\d\.]+\"\s+y=\"[\d\.]+\"\s?>'," | ",svgData)
        svgData = re.sub(r'</text><rect\s+fill\-opacity=\"[\d\.]+\"\s+height=\"[\d\.]+\"\s+stroke=\"[a-z]+\"\s+width=\"[\d\.]+\"\s+x=\"[\d\.]+\"\s+y=\"[\d\.]+\"\s+/><text\s+fill=\"[a-z]+\"\s+x=\"[\d\.]+\"\s+y=\"[\d\.]+\"\s+/><text\s+fill=\"[a-z]+\"\s+x=\"[\d\.]+\"\s+y=\"[\d\.]+\"> ',' | ',svgData)
        svgData = re.sub(r'</text><rect\s+fill\-opacity=\"[\d\.]+\"\s+height=\"[\d\.]+\"\s+stroke=\"[a-z]+\"\s+width=\"[\d\.]+\"\s+x=\"[\d\.]+\"\s+y=\"[\d\.]+\"\s+/><text\s+fill=\"[a-z]+\"\s+x=\"[\d\.]+\"\s+y=\"[\d\.]+\"\s+/><text\s+fill=\"[a-z]+\"\s+x=\"[\d\.]+\"\s+y=\"[\d\.]+\">',' | ', svgData)

        partitionList = svgData.upper().split(" | ASSORTMENT: | DELIVERY  | ")[1:]
        for index, partition in enumerate(partitionList):
            partitions[index+1] = partition
        return partitions

    def __buyer(self)->str:
        """
            Returns the buyer name 
        """
        return "TOKMANNI OY"

    def __company(self)->str:
        """
            Returns the company name
        """
        return "CENTRO TEX LIMITED"

    def __poNumber(self,dataPartition:str)->tuple[str,str]:
        """
            Returns the purchase order number
        """
        try:
            pattern = r"\s+\|\s+("+ self.__docRegexPatterns['po_num'] + r")\s+\|\s+" + self.__docRegexPatterns['ship_date'] + r"\s+\|\s+"
            poNumber_1 = re.findall(pattern,dataPartition)[0]
        except IndexError:
            poNumber_1 =""

        try:
            pattern = r"\s+\|\s+" + r"PACKED\s+BY\s+SIZES\s?:?\s?.*" + r"\s+\|\s+" +"\n" + r"\s+\|\s+(" + self.__docRegexPatterns['po_num'] + r")\s+\|\s+"
            poNumber_2 = re.findall(pattern,dataPartition)[0]
        except IndexError:
            poNumber_2 = ""
        return (poNumber_1,poNumber_2)

    def __poDate(self)->str:
        """
            Returns the purchase order date
        """
        try:
            (_d,_m,_y) = re.findall(r"ORDER\s+SENT\s?:?\s?(\d{1,2})[A-Z]{0,2}[\s|\-|/|\.|,]{1,3}([A-Z]*\d{0,2})[\s|\-|/|\.|,]{1,3}(\d{2,4})",self.__allContent.upper())[0]
        except IndexError:
            (_d,_m,_y) = re.findall(r"DATE\s?:?\s?(\d{1,2})[A-Z]{0,2}[\s|\-|/|\.|,]{1,3}([A-Z]*\d{0,2})[\s|\-|/|\.|,]{1,3}(\d{2,4})",self.__allContent.upper())[0]

        try:
            return datetime.strptime(f"{_d}.{_m[0:3]}.{_y[-2:]}","%d.%b.%y").strftime("%d-%b-%y")
        except ValueError:
            return datetime.strptime(f"{_d}.{_m}.{_y[-2:]}","%d.%m.%y").strftime("%d-%b-%y")

    def __currency(self)->str:
        """
            Returns the currency type
        """
        return "$"

    def __fabric(self,dataPartition:str)->str:
        """
            Returns the fabric type
        """
        fabricList = []
        try:
            pattern = r"\s+\|\s+" + r"PACKED\s+BY\s+SIZES\s?:?\s?" + r"\s+\|\s+(" + self.__docRegexPatterns['fabric'] + r")\s+\|\s+"
            fabricStr = re.sub(r"\s+\d{1,3}\-\d{1,3}G/M2","",re.findall(pattern,dataPartition)[0])
            fabricList = re.findall(r"\d{1,3}[0-9A-Z\s%\*]+",fabricStr)
        except IndexError:
            try:
                pattern = r"\s+\|\s+"+ self.__docRegexPatterns['po_num'] + r"\s+\|\s+" + self.__docRegexPatterns['ship_date'] + r"\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+(" + self.__docRegexPatterns['fabric'] + r")\s+\|\s+"
                fabricStr = re.findall(pattern,dataPartition)[0]
            except IndexError:
                pattern = r"\s+\|\s+" + self.__docRegexPatterns['ship_date'] + r"\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+(" + self.__docRegexPatterns['fabric'] + r")\s+\|\s+"
                fabricStr = re.findall(pattern,dataPartition)[0]

            percentageNumberList = re.findall(r"(\d{1,3})[%|\s]{1}",fabricStr)
            for index,_ in enumerate(percentageNumberList):
                try:
                    fabricList.append(f"{percentageNumberList[index]}%{''.join(fabricStr.split(percentageNumberList[index])[1:]).split(percentageNumberList[index+1])[0]}".replace("/","").replace("|","").replace("  "," ").replace("%%","% ").replace("  "," ").strip()) 
                except IndexError:
                    fabricList.append(f"{percentageNumberList[index]}%{''.join(fabricStr.split(percentageNumberList[index-1])[1:]).split(percentageNumberList[index])[-1]}".replace("/","").replace("|","").replace("  "," ").replace("%%","% ").replace("  "," ").strip()) 
        return ", ".join(fabricList)

    def __shipDate(self,dataPartition:str)->str:
        """
            Returns the ship date
        """
        try:
            pattern = r"\s+\|\s+"+ self.__docRegexPatterns['po_num'] + r"\s+\|\s+(" + self.__docRegexPatterns['ship_date'] + r")\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+" + self.__docRegexPatterns['fabric'] + r"\s+\|\s+" + self.__docRegexPatterns['colour'] + r"\s+\|\s+"
            shipDateStr = re.findall(pattern,dataPartition)[0]
        except IndexError:
            try:
                pattern = r"\s+\|\s+"+ self.__docRegexPatterns['po_num'] + r"\s+\|\s+(" + self.__docRegexPatterns['ship_date'] + r")\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+" + self.__docRegexPatterns['colour'] + r"\s+\|\s+"
                shipDateStr = re.findall(pattern,dataPartition)[0]
            except IndexError:
                try:
                    pattern = r"\s+\|\s+(" + self.__docRegexPatterns['ship_date'] + r")\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+" + self.__docRegexPatterns['fabric'] + r"\s+\|\s+" + self.__docRegexPatterns['colour'] + r"\s+\|\s+"
                    shipDateStr = re.findall(pattern,dataPartition)[0]
                except IndexError:
                    pattern = r"\s+\|\s+(" + self.__docRegexPatterns['ship_date'] + r")\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+" + self.__docRegexPatterns['colour'] + r"\s+\|\s+"
                    shipDateStr = re.findall(pattern,dataPartition)[0]
        (_d,_m,_y) = re.findall(r"[A-Z]{0,3}\s*(\d{1,2})\s*[A-Z]{0,2}\s*[A-Z]{0,2}\s*[\s|\-|/|\.|,]{1,3}([A-Z]*\d{0,2})[\s|\-|/|\.|,]{1,3}(\d{2,4})",shipDateStr)[0]

        try:
            return datetime.strptime(f"{_d}/{_m}/{_y[-2:]}","%d/%m/%y").strftime("%d-%b-%y")
        except ValueError:
            return datetime.strptime(f"{_d}/{_m[0:3]}/{_y[-2:]}","%d/%b/%y").strftime("%d-%b-%y")

    def __shipment_mode(self)->str:
        """
            Returns the shipment mode
        """
        return "SEA"

    def __style(self,dataPartition:str)->str:
        """
            Returns the style
        """
        try:
            pattern = r"\s+\|\s+"+ self.__docRegexPatterns['po_num'] + r"\s+\|\s+" + self.__docRegexPatterns['ship_date'] + r"\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+(" + self.__docRegexPatterns['style'] + r")\s+\|\s+"
            return re.findall(pattern,dataPartition)[0].replace("  "," ")
        except IndexError:
            pattern = r"\s+\|\s+" + self.__docRegexPatterns['ship_date'] + r"\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+(" + self.__docRegexPatterns['style'] + r")\s+\|\s+"
            return re.findall(pattern,dataPartition)[0].replace("  "," ")

    def __styleDescription(self,dataPartition:str)->str:
        """
            Returns the style description
        """
        try:
            pattern = r"\s+\|\s+"+ self.__docRegexPatterns['po_num'] + r"\s+\|\s+" + self.__docRegexPatterns['ship_date'] + r"\s+\|\s+(" + self.__docRegexPatterns['style_desc'] + r")\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+"
            return re.findall(pattern,dataPartition)[0].replace("  "," ")
        except IndexError:
            pattern = r"\s+\|\s+" + self.__docRegexPatterns['ship_date'] + r"\s+\|\s+(" + self.__docRegexPatterns['style_desc'] + r")\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+"
            return re.findall(pattern,dataPartition)[0].replace("  "," ")

    def __colour(self,dataPartition:str)->str:
        """
            Returns the colour
        """
        try:
            pattern = r"\s+\|\s+"+ self.__docRegexPatterns['po_num'] + r"\s+\|\s+" + self.__docRegexPatterns['ship_date'] + r"\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+" + self.__docRegexPatterns['fabric'] + r"\s+\|\s+(" + self.__docRegexPatterns['colour'] + r")\s+\|\s+"
            return re.findall(pattern,dataPartition)[0]
        except IndexError:
            try:
                pattern = r"\s+\|\s+"+ self.__docRegexPatterns['po_num'] + r"\s+\|\s+" + self.__docRegexPatterns['ship_date'] + r"\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+(" + self.__docRegexPatterns['colour'] + r")\s+\|\s+"
                return re.findall(pattern,dataPartition)[0]
            except IndexError:
                try:
                    pattern = r"\s+\|\s+" + self.__docRegexPatterns['ship_date'] + r"\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+" + self.__docRegexPatterns['fabric'] + r"\s+\|\s+(" + self.__docRegexPatterns['colour'] + r")\s+\|\s+"
                    return re.findall(pattern,dataPartition)[0]
                except IndexError:
                    pattern = r"\s+\|\s+" + self.__docRegexPatterns['ship_date'] + r"\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+(" + self.__docRegexPatterns['colour'] + r")\s+\|\s+"
                    return re.findall(pattern,dataPartition)[0]

    def __sizes(self, dataPartition:str)->list:
        pattern = r"\s+\|\s+" + r"\d{5,}" + r"\s+\|\s+(" + self.__docRegexPatterns['size'] + r")\s+\|\s+"
        sizes = re.findall(pattern,dataPartition)
        return sizes

    def __getSizeRange(self,dataPartition:str)->str:
        """
            Returns the size range
        """
        try:
            pattern = r"\s+\|\s+" + self.__docRegexPatterns['po_num'] + r"\s+\|\s+" + self.__docRegexPatterns['ship_date'] + r"\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+" + self.__docRegexPatterns['fabric'] + r"\s+\|\s+" + self.__docRegexPatterns['colour'] + r"\s+\|\s+" + r"\d{5,}" + r"\s+\|\s+(" + self.__docRegexPatterns['size'] + r"[\s|\-|\.|/]{1,3}" + self.__docRegexPatterns['size'] + r")\s+\|\s+"
            return re.findall(pattern,dataPartition)[0]
        except IndexError:
            try:
                pattern = r"\s+\|\s+" + self.__docRegexPatterns['po_num'] + r"\s+\|\s+" + self.__docRegexPatterns['ship_date'] + r"\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+" + self.__docRegexPatterns['colour'] + r"\s+\|\s+" + r"\d{5,}" + r"\s+\|\s+(" + self.__docRegexPatterns['size'] + r"[\s|\-|\.|/]{1,3}" + self.__docRegexPatterns['size'] + r")\s+\|\s+"
                return re.findall(pattern,dataPartition)[0]
            except IndexError:
                return f"{self.__sizes(dataPartition)[0]}-{self.__sizes(dataPartition)[-1]}"

    def __nTotal(self, data_partition:str)->list[int]:
        n1,n2 = 0,0
        try:
            pattern = r"\s+\|\s+" + self.__docRegexPatterns['po_num'] + r"\s+\|\s+" + self.__docRegexPatterns['ship_date'] + r"\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+" + self.__docRegexPatterns['fabric'] + r"\s+\|\s+" + self.__docRegexPatterns['colour'] + r"\s+\|\s+" + r"\d{5,}" + r"\s+\|\s+" + self.__docRegexPatterns['size'] + r"[\s|\-|\.|/]{1,3}" + self.__docRegexPatterns['size'] + r"\s+\|\s+" + r"[\d\-]+" + r"\s+\|\s+" + r"\d+" + r"\s+\|\s+" + r"\d+" + r"\s+\|\s+(" + r"\d+" + r")\s+\|\s+"
            n1 = int(re.findall(pattern,data_partition)[0])
        except IndexError:
            try:
                pattern = r"\s+\|\s+" + self.__docRegexPatterns['po_num'] + r"\s+\|\s+" + self.__docRegexPatterns['ship_date'] + r"\s+\|\s+" + self.__docRegexPatterns['style_desc'] + r"\s+\|\s+" + self.__docRegexPatterns['style'] + r"\s+\|\s+" + self.__docRegexPatterns['colour'] + r"\s+\|\s+" + r"\d{5,}" + r"\s+\|\s+" + self.__docRegexPatterns['size'] + r"[\s|\-|\.|/]{1,3}" + self.__docRegexPatterns['size'] + r"\s+\|\s+" + r"[\d\-]+" + r"\s+\|\s+" + r"\d+" + r"\s+\|\s+" + r"\d+" + r"\s+\|\s+(" + r"\d+" + r")\s+\|\s+"
                n1 = int(re.findall(pattern,data_partition)[0])
            except IndexError:
                n1 = 0

        pattern = r"\d{5,}" + r"\s+\|\s+" + self.__docRegexPatterns['size'] + r"\s+\|\s+" + r"\d+" + r"\s+\|\s+" + r"\d+" + r"\s+\|\s+(" + r"\d+" + r")\s+\|\s+"
        n2 = sum([int(n) for n in re.findall(pattern,data_partition)])
        return [n1,n2]

    def __totalQuantity(self)->int:
        """
            Returns the total quantity
        """
        return sum([sum(self.__nTotal(self.__dataPartition[data_partition_key])) for data_partition_key in self.__dataPartition.keys()])

    def __purchaseOrders(self, dataPartition:str)->dict:
        """
            Returns the purchase orders details
        """
        dest = "FINLAND"
        pattern = r"\s+\|\s+" + r"TOTAL\s+PRICE" + r"\s+\|\s+(" + r"[\d,.]+" + r")\s+\|\s+"
        supplierCost = float(re.findall(pattern,dataPartition)[0].replace(",",".").replace(" ",""))

        poDict = {}
        for itt in range(0,2):
            if self.__poNumber(dataPartition)[itt]!="":
                poDict[self.__poNumber(dataPartition)[itt]] = {
                    self.__poNumber(dataPartition)[itt]:{
                        "dest":dest,
                        "dest_num":0,
                        "n_units":self.__nTotal(dataPartition)[itt],
                        "n_packs":0,
                        "ship_date":self.__shipDate(dataPartition),
                        "size_range":self.__getSizeRange(dataPartition),
                        "packs_data":[
                            {
                                'pack_sizes': f"{self.__sizes(dataPartition)[0]}-{self.__sizes(dataPartition)[-1]}",
                                'pack_colour': self.__colour(dataPartition),
                                'n_packs':None,
                                'n_units':self.__nTotal(dataPartition)[itt],
                                "supplier_cost":supplierCost
                            }
                        ]
                    }
                }
        return poDict

    def __poDetails(self)->list:
        """
            Returns a list of purchase order data details
        """
        def _getPoDetailsDict(data_partition:str,poNumber:str)->dict:
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
                "style":self.__style(data_partition),
                "style_desc":self.__styleDescription(data_partition),
                "gmt_item":"",
                "uom":"",
                "ratio":"",
                "total_qty":self.__totalQuantity(),
                "currency":self.__currency(),
                "factory":"",
                "fabric_src":"",
                "fabric": self.__fabric(data_partition),
                "fabric_mill":"",
                "sust_fabric":"",
                "po_num":poNumber,
                "po_date":self.__poDate(),
                "po_status":"",
                "shipment_mode":self.__shipment_mode(),
                "purchase_orders":self.__purchaseOrders(data_partition)[poNumber]
            }
            return po_details

        poDetailsDict = {}
        for dataPartitionNumber in self.__dataPartition.keys():
            for itt in range(0,2):
                _poNumber = self.__poNumber(self.__dataPartition[dataPartitionNumber])[itt]
                if _poNumber!="" and _poNumber not in poDetailsDict.keys():
                    poDetailsDict[_poNumber] = []
                if _poNumber!="":
                    poDetailsDict[_poNumber].append(_getPoDetailsDict(self.__dataPartition[dataPartitionNumber],_poNumber))

        poDetailsList = []
        for poNumber in poDetailsDict.keys():
            poDetailsList.extend(poDetailsDict[poNumber])

        return poDetailsList

    def output(self)->tuple:
        """
            Returns the extracted data
        """
        return (self.__poDetails())