connection_url = "postgresql://postgres:@localhost:5432/invoice_db"
database_info_dict = {
    "host_name": "localhost",
    "port": 5432,
    "username": "postgres",
    "database_name": "invoice_db",
    "database_type": "PostgreSQL",
    "password": None,
}


################## Models ##########################

# model trained for 10 epochs
tokenizer_name_10 = "Rajan/AIMT-invoices-donut_10Epochs"
model_name_10 = "Rajan/AIMT-invoices-donut_10Epochs"


# model trained for 30 epochs

tokenizer_name_30 = "Rajan/AIMT-invoices-donut_30Epochs"
model_name_30 = "Rajan/AIMT-invoices-donut_30Epochs"


# base comparison model
model_name_base = "katanaml-org/invoices-donut-model-v1"
