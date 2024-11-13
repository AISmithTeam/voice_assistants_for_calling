import requests

AIRTABLE_KEY = ""

def add_appointment_to_airtable(
        client_name: str,
        appointment_details: str,
        appointment_date: str,
    ):
    url = "https://api.airtable.com/v0/appmpmkSlWjONxzOO/Table%201"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "Client Name": client_name,
        "Appointment Details": appointment_details,
        "Appointment Date": appointment_date,
    }
    
    return requests.post(
        url=url,
        headers=headers,
        json=body,
    )