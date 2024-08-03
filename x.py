from collections.abc import Mapping
from difflib import SequenceMatcher


def flatten_dict(d, parent_key="", sep="."):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, Mapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def calculate_metrics(dict1, dict2):
    flat_dict1 = flatten_dict(dict1)
    flat_dict2 = flatten_dict(dict2)

    total_fields = len(flat_dict1)
    matches = 0
    predicted_matches = 0
    actual_matches = 0

    for key in flat_dict1:
        if key in flat_dict2:
            actual_matches += 1
            if flat_dict1[key] == flat_dict2[key]:
                matches += 1
                predicted_matches += 1
            else:
                if isinstance(flat_dict1[key], str) and isinstance(
                    flat_dict2[key], str
                ):
                    similarity = SequenceMatcher(
                        None, flat_dict1[key], flat_dict2[key]
                    ).ratio()
                    if similarity > 0.8:  # Similarity threshold
                        predicted_matches += 1

    accuracy = matches / total_fields
    precision = matches / predicted_matches if predicted_matches else 0
    recall = matches / actual_matches if actual_matches else 0

    return accuracy, precision, recall


x = {
    "header": {
        "invoice_no": "65321852",
        "invoice_date": "04/11/2021",
        "seller": "Kaufman, Cooper and Young 83451 Johnson Lake New Ann, NE 54138",
        "client": "Wells-Carlson 148 Carroll Village Suite 393 South Allisonstad, TX 72090",
        "seller_tax_id": "930-79-7845",
        "client_tax_id": "957-82-7504",
        "iban": "GB85YPMM58300597200061",
    },
    "items": [
        {
            "item_desc": 'New KID CUDI "WZRD" Rap Hip Hop Soul Music Men\'s Black T-Shirt Size S to 3XL',
            "item_qty": "2,00",
            "item_net_price": "22,49",
            "item_net_worth": "44,98",
            "item_vat": "10%",
            "item_gross_worth": "49,48",
        },
        {
            "item_desc": "boys bogs waterproof boots youth size 3",
            "item_qty": "1,00",
            "item_net_price": "9,80",
            "item_net_worth": "9,80",
            "item_vat": "10%",
            "item_gross_worth": "10,78",
        },
        {
            "item_desc": "Joma Boys Youth Gol-102 Soccer Cleats Wool Size 3.5 White Red Futbol NEW",
            "item_qty": "2,00",
            "item_net_price": "19,99",
            "item_net_worth": "39,98",
            "item_vat": "10%",
            "item_gross_worth": "43,98",
        },
        {
            "item_desc": "Nike Oncore High Jr 6.0 (Kids) Size 4Y Black, Red, White",
            "item_qty": "4,00",
            "item_net_price": "25,00",
            "item_net_worth": "100,00",
            "item_vat": "10%",
            "item_gross_worth": "110,00",
        },
    ],
    "summary": {
        "total_net_worth": "$194,76",
        "total_vat": "$ 19,48",
        "total_gross_worth": "214,24",
    },
}

y = {
    "header": {
        "invoice_no": "65321852",
        "invoice_date": "04/11/2021",
        "seller": "Kaufman, Cooper and Young 33451 Johnson Lake New Ann, NE 54138",
        "client": "Wells-Carlson 148 Carroll Village Suite 393 South Allisonstad, TX 72090",
        "seller_tax_id": "930-79-7845",
        "client_tax_id": "957-82-7504",
        "iban": "GB85XPMM58300597200061",
    },
    "items": [
        {
            "item_desc": 'New KID CUDI "WZRD" Rap Hip Hop Soul Music Men\'s Black T-Shirt Size S to 3XL',
            "item_qty": "2,00",
            "item_net_price": "22,49",
            "item_net_worth": "44,98",
            "item_vat": "10%",
            "item_gross_worth": "49,48",
        },
        {
            "item_desc": "boys bogs waterproof boots youth size 3",
            "item_qty": "1,00",
            "item_net_price": "9,80",
            "item_net_worth": "9,80",
            "item_vat": "10%",
            "item_gross_worth": "10,78",
        },
        {
            "item_desc": "Joma Boys Youth Gol-102 Soccer Cleats Shoes Size 3.5 White Red Futbol NEW",
            "item_qty": "2,00",
            "item_net_price": "19,99",
            "item_net_worth": "39,98",
            "item_vat": "10%",
            "item_gross_worth": "43,98",
        },
        {
            "item_desc": "Nike Oncore High Jr 6.0 (Kids) Size 4Y Black, Red, White",
            "item_qty": "4,00",
            "item_net_price": "25,00",
            "item_net_worth": "100,00",
            "item_vat": "10%",
            "item_gross_worth": "110,00",
        },
    ],
    "summary": {
        "total_net_worth": "$ 194,76",
        "total_vat": "$ 19,48",
        "total_gross_worth": "$ 214,24",
    },
}

accuracy, precision, recall = calculate_metrics(x, y)
print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
