class Product:
    def __init__(self):
        self._id = None
        self._marketplace_key = None
        self._name = None
        self._price = None
        self._currency = None
        self._etl_date = None

    def __str__(self):
        return f"Product: name = {self._name}, price = {self._price}"

    def get_id(self):
        return self._id
    
    def set_id(self, id):
        self._id = id

    def get_marketplace_key(self):
        return self._marketplace_key
    
    def set_marketplace_key(self, marketplace_key):
        self._marketplace_key = marketplace_key

    def get_name(self):
        return self._name
    
    def set_name(self, name):
        self._name = name

    def get_price(self):
        return self._price
    
    def set_price(self, price):
        self._price = price

    def get_currency(self):
        return self._currency
    
    def set_currency(self, currency):
        self._currency = currency

    def set_etl_date(self, date_time):
        self._etl_date = date_time
    
    def get_etl_date(self):
        return self._etl_date
