import re
from datetime import datetime
from po_formats.po_base import PO_BASE

class PO_TYPE_7(PO_BASE):
    def __init__(self, poDocFilepath: str) -> None:
        super().__init__(poDocFilepath)
        self.__dataPartition = self.__dataPartitioning()

    def __dataPartitioning(self)->dict:
        """
            Partitioning data into segments
        """
        partitions = {'order_details':None,"packs_details":None}
        (_c2_r1,_c2_r2,_c2_r3,_c2_r4,_c2_r5) = re.findall(r"STORE\s+READY\s+PACKING\s+INSTRUCTIONS\s*\n([A-Z\s]*)\n([0-9A-Z\&\s\-]*)\n([A-Z\s]*)\n([0-9A-Z\s]*)\n([0-9A-Z\s]*)\n",self.getPage(1).upper())[0]
        (_c4_r1,_c4_r2) = re.findall(r"PURCHASE\s+ORDER\s+DATE\s+PLACED\s?:?\s?\nPURCHASE\s+ORDER\s+NUMBER\s?:?\s?\nBULK\s+ORDER\s+NUMBER\s?:?\s?\nPAGE\s?:?\s?\n(\d{1,2}[,\.\-/]{1,3}[A-Z]*\d{0,2}[,\.\-/]{1,3}\d{2,4})\s?\n(\d+)\-\d+\s?\n",self.getPage(1).upper())[0]
        (_c4_r3,_c4_r4,_c4_r5,_c4_r6) = re.findall(r"STORE\s+READY\s+PACKING\s+INSTRUCTIONS\s*\n[A-Z\s]*\n[0-9A-Z\&\s\-]*\n[A-Z\s]*\n[0-9A-Z\s]*\n[0-9A-Z\s]*\n([0-9,\s]*)\n([0-9,\s]*)\n(\$?[0-9,\.\s]*)\n(\d{1,2}[,\.\-/]{1,3}[A-Z]*\d{0,2}[,\.\-/]{1,3}\d{2,4})\s?\n",self.getPage(1).upper())[0]
        _c4_r8 = re.findall(r"PLANNED\s+ETD\s+DATE\s?:?\s?(\d{1,2}[,\.\-/]{1,3}[A-Z]*\d{0,2}[,\.\-/]{1,3}\d{2,4})\s?\n",self.getPage(1).upper())[0]
        orderDetails = {
            'col-2':{
                'buyer':_c2_r1,
                'department':_c2_r2,
                'business_unit':_c2_r3,
                'style':_c2_r4,
                'style_desc':_c2_r5
            },
            'col-4':{
                'po_date':_c4_r1,
                'po_num':_c4_r2,
                'total_units':_c4_r3,
                'total_packs':_c4_r4,
                'total_cost_price':_c4_r5,
                'planned_in_dc_week':_c4_r6,
                'ship_date':_c4_r8
            }
        }

        partitions['order_details'] = orderDetails

        return partitions

    def __buyer(self)->str:
        """
            Returns the buyer name 
        """
        return "BEST AND LESS"

    def __company(self)->str:
        """
            Returns the company name
        """
        return "CENTRO TEX LIMITED"

    def __poNumber(self)->int:
        """
            Returns the purchase order number
        """
        try:
            return int(re.findall(r"PURCHASE\s+ORDER\s+NUMBER\s?:?\s?(\d+)\-\d+",self.getPage(1).upper())[0])
        except IndexError:
            return int(self.__dataPartition['order_details']['col-4']['po_num'].replace(",",""))

    def __poDate(self)->str:
        """
            Returns the purchase order date
        """
        (_d,_m,_y) = re.findall(r"(\d{1,2})[\s\-/\.,]{1,3}([A-Z]*\d{0,2})[\s\-/\.,]{1,3}(\d{2,4})",self.__dataPartition['order_details']['col-4']['po_date'])[0]

        try:
            return datetime.strptime(f"{_d}/{_m}/{_y[-2:]}","%d/%m/%y").strftime("%d-%b-%y")
        except ValueError:
            return datetime.strptime(f"{_d}/{_m[0:3]}/{_y[-2:]}","%d/%b/%y").strftime("%d-%b-%y")

    def __totalQuantity(self)->int:
        """
            Returns the total quantity
        """
        try:
            return int(re.findall(r"TOTAL\s+UNITS\s?:?\s?([0-9,\.]+)\s?\n",self.getPage(1).upper())[0].replace(",",""))
        except IndexError:
            return int(self.__dataPartition['order_details']['col-4']['total_units'].replace(",",""))

    def __currency(self)->str:
        """
            Returns the currency type
        """
        return "$"

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
            return re.findall(r"VENDOR\s+STYLE\s+NUMBER\s?:?\s?([0-9A-Z]+)",self.getPage(1).upper())[0]
        except IndexError:
            return self.__dataPartition['order_details']['col-2']['style']

    def __styleDescription(self)->str:
        """
            Returns the style description
        """
        try:
            return re.findall(r"STYLE\s+DESCRIPTION\s?:?\s?([0-9A-Z]+)",self.getPage(1).upper())[0]
        except IndexError:
            return self.__dataPartition['order_details']['col-2']['style_desc']

    def __shipDate(self)->str:
        """
            Returns the ship date
        """
        (_d,_m,_y) = re.findall(r"(\d{1,2})[\s\-/\.,]{1,3}([A-Z]*\d{0,2})[\s\-/\.,]{1,3}(\d{2,4})",self.__dataPartition['order_details']['col-4']['ship_date'])[0]

        try:
            return datetime.strptime(f"{_d}/{_m}/{_y[-2:]}","%d/%m/%y").strftime("%d-%b-%y")
        except ValueError:
            return datetime.strptime(f"{_d}/{_m[0:3]}/{_y[-2:]}","%d/%b/%y").strftime("%d-%b-%y")

    def __purchaseOrders(self)->dict:
        """
            Returns the purchase orders details
        """
        dest = "AUSTRALIA"
        allContent = "".join([self.getPageByPyPDF2(pageNumber) for pageNumber in range(1,self.numPages()+1)])
        poDict = {}

        # corrections
        allContent = allContent.upper()
        allContent = allContent.replace("NEW BABY","0-0 MONTHS")

        packsData = re.split(r"PACK\s+\d+\s?",allContent)[1:]
        for tabelIndex,pack in enumerate(packsData):
            sample = pack.replace('ONLINE PACK:\nNO\nBUYERS COLOUR\nPRINT\nSIZE\nSKU\nPACK RATIO\nUNITS\n','')
            table = re.findall(r"([A-Z\s]+)\n([A-Z\s]+)\n(.*)\n(\d+)\n(\d+)\n(.*)",sample)

            colour = re.sub(r"\s{2,}",' ',table[0][0].replace("\n"," ").strip())
            n = sum([int(row[5].replace(",",'')) for row in table])
            try:
                _first = re.findall(r"SIZE\s?:?\s?(\d+)",table[0][2])[0]
                _last = re.findall(r"SIZE\s?:?\s?(\d+)",table[-1][2])[0]
            except IndexError:
                _first = re.findall(r"(\d+)[\s\-]{1,3}\d+\s+MONTHS",table[0][2])[0]
                _last = re.findall(r"\d+[\s\-]{1,3}(\d+)\s+MONTHS",table[-1][2])[0] + ' M'
            sizeRange = f'{_first} - {_last}'
            poDict[tabelIndex] = {
                    "dest":dest,
                    "dest_num":0,
                    "n_units":n,
                    "n_packs":0,
                    "ship_date":self.__shipDate(),
                    "size_range":sizeRange,
                    "packs_data":[
                        {
                            'pack_sizes': sizeRange,
                            'pack_colour':colour,
                            'n_packs':None,
                            'n_units':n,
                            "supplier_cost":""
                        }
                    ]
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
            "fabric":"",
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