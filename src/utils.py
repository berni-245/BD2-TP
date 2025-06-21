from datetime import datetime

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
