import re
from datetime import datetime
from po_formats.po_base import PO_BASE

class PO_TYPE_8(PO_BASE):
    def __init__(self, poDocFilepath: str) -> None:
        super().__init__(poDocFilepath)

    def __buyer(self)->str:
        """
            Returns the buyer name 
        """
        return 'RENFOLD LTD'

    def __company(self)->str:
        """
            Returns the company name
        """
        return 'CENTRO INTERNATIONAL SOURCING LIMITED'

    def __poNumber(self)->int:
        """
            Returns the purchase order number
        """
        return int(re.findall(r"PURCHASE\s+ORDER\s+NUMBER\s?\n\s?PO\-(\d+)\s?\n",self.getPage(1).upper())[0])

    def __poDate(self)->str:
        """
            Returns the purchase order date
        """
        (_d,_m,_y) = re.findall(r"PURCHASE\s+ORDER\s+DATE\s?\n\s?(\d{1,2})[\s\.,\-/]{1,3}([A-Z]*\d{0,2})[\s\.,\-/]{1,3}(\d{2,4})\s?\n",self.getPage(1).upper())[0]

        try:
            return datetime.strptime(f"{_d}.{_m[0:3]}.{_y[-2:]}","%d.%b.%y").strftime("%d-%b-%y")
        except ValueError:
            return datetime.strptime(f"{_d}.{_m}.{_y[-2:]}","%d.%m.%y").strftime("%d-%b-%y")

    def __currency(self)->str:
        """
            Returns the currency type
        """
        return "$"

    def __shipDate(self)->str:
        """
            Returns the ship date
        """
        (_d,_m,_y) = re.findall(r"DELIVERY\s+DATE\s?\n\s?(\d{1,2})[\s\.,\-/]{1,3}([A-Z]*\d{0,2})[\s\.,\-/]{1,3}(\d{2,4})\s?\n",self.getPage(1).upper())[0]

        try:
            return datetime.strptime(f"{_d}.{_m[0:3]}.{_y[-2:]}","%d.%b.%y").strftime("%d-%b-%y")
        except ValueError:
            return datetime.strptime(f"{_d}.{_m}.{_y[-2:]}","%d.%m.%y").strftime("%d-%b-%y")

    def __shipmentMode(self)->str:
        """
            Returns the shipment mode
        """
        return "SEA"

    def __getRecords(self)->list[tuple]:
        _all_content = "".join([self.getPage(pageNumber) for pageNumber in range(1,self.numPages()+1)])
        return re.findall(r"([0-9A-Z]+)\s+\-\s+([A-Z\-\s]+\n?[A-Z\-\s]*)\n?([\d\.]+)\s+([\d\.]+)\s+([\d,]+)",_all_content.upper())

    def __style(self,record_index:int)->str:
        """
            Returns the style
        """
        _records = self.__getRecords()
        if record_index>=0 and record_index<len(_records):
            _record = _records[record_index]
            return _record[0].strip()

    def __styleDescription(self,record_index:int)->str:
        """
            Returns the style description
        """
        _records = self.__getRecords()
        if record_index>=0 and record_index<len(_records):
            _record = _records[record_index]
            return _record[1].replace("\n",' ').strip()

    def __totalQuantity(self,recordIndex:int)->int:
        """
            Returns the total quantity
        """
        _records = self.__getRecords()
        if recordIndex>=0 and recordIndex<len(_records):
            _record = _records[recordIndex]
            return int(float(_record[2]))
        return None

    def __purchaseOrders(self,recordIndex:int)->dict:
        """
            Returns the purchase orders details
        """
        dest = "UNITED KINGDOM"
        poDict = {}
        records = self.__getRecords()
        if recordIndex>=0 and recordIndex<len(records):
            record = records[recordIndex]
            poDict[0] = {
                "dest":dest,
                "dest_num":0,
                "n_units":int(float(record[2])),
                "n_packs":0,
                "ship_date":self.__shipDate(),
                "size_range":'',
                "packs_data":[
                    {
                        'pack_sizes': '',
                        'pack_colour': self.__style(recordIndex)[-2:],
                        'n_packs':None,
                        'n_units':int(float(record[2])),
                        "supplier_cost":float(record[3])
                    }
                ]
            }
            return poDict

    def __poDetails(self)->list:
        """
            Returns a list of purchase order data details
        """
        def getPoDetailsDict(recordIndex:int)->dict:
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
                "style":self.__style(recordIndex),
                "style_desc":self.__styleDescription(recordIndex),
                "gmt_item":"",
                "uom":"",
                "ratio":"",
                "total_qty":self.__totalQuantity(recordIndex),
                "currency":self.__currency(),
                "factory":"",
                "fabric_src":"",
                "fabric": '',
                "fabric_mill":"",
                "sust_fabric":"",
                "po_num":self.__poNumber(),
                "po_date":self.__poDate(),
                "po_status":"",
                "shipment_mode":self.__shipmentMode(),
                "purchase_orders":self.__purchaseOrders(recordIndex)
            }
            return poDetails

        poDetailsList = []
        records = self.__getRecords()
        for recordIndex in range(0,len(records)):
            poDetailsList.append(getPoDetailsDict(recordIndex))

        return poDetailsList

    def output(self)->tuple:
        """
            Returns the extracted data
        """
        return (self.__poDetails())