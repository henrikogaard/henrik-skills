"""Customer records."""

CUSTOMERS = {
    "acme": {"name": "ACME AS", "email": "ap@acme.example", "kind": "business"},
    "nordlys": {"name": "Nordlys Kommune", "email": "faktura@nordlys.example", "kind": "government"},
    "fjord": {"name": "Fjord Consulting", "email": "post@fjord.example", "kind": "partner"},
    "berg": {"name": "Berg Bakeri", "email": "berg@berg.example", "kind": "business"},
}


def get_customer(customer_id):
    return CUSTOMERS[customer_id]
