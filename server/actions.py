import requests

AIRTABLE_KEY = "patyjrXyuEd0LrzQb.83ff7f70e581cc327659451936edac78fa2e0eb054d08fb44127ee3f5a2d70ec"

def add_appointment_to_airtable(
        client_name: str,
        appointment_details: str,
        appointment_date: str,
    ):
    print("INVOKED")
    url = "https://api.airtable.com/v0/appmpmkSlWjONxzOO/Table%201"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_KEY}",
        "Content-Type": "application/json",
    }
    body = { "records": [
                { "fields": {
                    "Client Name": client_name,
                    "Appointment Details": appointment_details,
                    "Appointment Date": appointment_date,
                }
            }
        ]
    }
    
    return requests.post(
        url=url,
        headers=headers,
        json=body,
    )

if __name__=="__main__":
    add_appointment_to_airtable("daniil", "general check-up", "01/01/2025")