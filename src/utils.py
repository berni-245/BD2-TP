from datetime import datetime
from typing import Dict, Tuple

def parse_phone(raw_str: str) -> Tuple[bool, Dict]:
    split_args = raw_str.split(";")
    if not len(split_args) == 3:
        return (False, {})
    phone = {
        "area_code": split_args[0],
        "phone_number": split_args[1],
        "phone_type": split_args[2]
    }
    return (True, phone)

def validate_future_date(date):
    try:
        date_obj = datetime.strptime(date, "%d/%m/%Y").date()
        today = datetime.today().date()

        if date_obj <= today:
            print("La fecha debe ser en el futuro.")
            return None
        else:
            return date_obj

    except ValueError:
        print("Formato inválido.")
        return None
