from src.database_utils import InvoiceDatabase
from config import connection_url, database_info_dict

database_object = InvoiceDatabase(uri=connection_url)
database_object.create_tables()
database_object.clear_all_tables()
