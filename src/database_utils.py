from sqlalchemy import create_engine, Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


# Define the Header table
class Header(Base):
    __tablename__ = "header"
    invoice_no = Column(String, primary_key=True)
    invoice_date = Column(String)
    seller = Column(String)
    client = Column(String)
    seller_tax_id = Column(String)
    client_tax_id = Column(String)
    iban = Column(String)


# Define the Items table
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_no = Column(String, ForeignKey("header.invoice_no"))
    item_desc = Column(String)
    item_qty = Column(Numeric)
    item_net_price = Column(Numeric)
    item_net_worth = Column(Numeric)
    item_vat = Column(Numeric)
    item_gross_worth = Column(Numeric)


# Define the Summary table
class Summary(Base):
    __tablename__ = "summary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_no = Column(String, ForeignKey("header.invoice_no"))
    total_net_worth = Column(Numeric)
    total_vat = Column(Numeric)
    total_gross_worth = Column(Numeric)


class InvoiceDatabase:
    def __init__(self, uri):
        self.engine = create_engine(uri)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def push_data(self, data):
        # Insert data into the Header table
        header = Header(
            invoice_no=data["header"]["invoice_no"],
            invoice_date=data["header"]["invoice_date"],
            seller=data["header"]["seller"],
            client=data["header"]["client"],
            seller_tax_id=data["header"]["seller_tax_id"],
            client_tax_id=data["header"]["client_tax_id"],
            iban=data["header"]["iban"],
        )
        self.session.add(header)

        # Insert data into the Items table
        for item in data["items"]:
            new_item = Item(
                invoice_no=data["header"]["invoice_no"],
                item_desc=item["item_desc"],
                item_qty=self.convert_to_numeric(item["item_qty"]),
                item_net_price=self.convert_to_numeric(item["item_net_price"]),
                item_net_worth=self.convert_to_numeric(item["item_net_worth"]),
                item_vat=self.convert_percentage(item["item_vat"]),
                item_gross_worth=self.convert_to_numeric(item["item_gross_worth"]),
            )
            self.session.add(new_item)

        # Insert data into the Summary table
        summary = Summary(
            invoice_no=data["header"]["invoice_no"],
            total_net_worth=self.convert_to_numeric(data["summary"]["total_net_worth"]),
            total_vat=self.convert_to_numeric(data["summary"]["total_vat"]),
            total_gross_worth=self.convert_to_numeric(
                data["summary"]["total_gross_worth"]
            ),
        )
        self.session.add(summary)

        # Commit the session
        self.session.commit()

    def convert_to_numeric(self, value):
        """Converts a string with currency symbols or commas to a numeric value."""
        if value is None:
            return None
        value = (
            value.replace("$", "").replace(",", ".").replace(" ", "")
        )  # Remove spaces
        try:
            return float(value)
        except ValueError:
            return None

    def convert_percentage(self, value):
        """Converts a percentage string to a numeric value."""
        if value is None:
            return None
        value = (
            value.replace("%", "").replace(",", ".").replace(" ", "")
        )  # Remove spaces
        try:
            return float(value)
        except ValueError:
            return None

    def fetch_record(self, invoice_no):
        header = self.session.query(Header).filter_by(invoice_no=invoice_no).first()
        items = self.session.query(Item).filter_by(invoice_no=invoice_no).all()
        summary = self.session.query(Summary).filter_by(invoice_no=invoice_no).first()

        if not header:
            return None

        return {
            "header": {
                "invoice_no": header.invoice_no,
                "invoice_date": header.invoice_date,
                "seller": header.seller,
                "client": header.client,
                "seller_tax_id": header.seller_tax_id,
                "client_tax_id": header.client_tax_id,
                "iban": header.iban,
            },
            "items": [
                {
                    "item_desc": item.item_desc,
                    "item_qty": float(item.item_qty),
                    "item_net_price": float(item.item_net_price),
                    "item_net_worth": float(item.item_net_worth),
                    "item_vat": float(item.item_vat),
                    "item_gross_worth": float(item.item_gross_worth),
                }
                for item in items
            ],
            "summary": {
                "total_net_worth": float(summary.total_net_worth),
                "total_vat": float(summary.total_vat),
                "total_gross_worth": float(summary.total_gross_worth),
            },
        }

    def clear_all_tables(self):
        with self.engine.connect() as connection:
            connection.execute(
                "TRUNCATE TABLE header, items, summary RESTART IDENTITY CASCADE;"
            )
