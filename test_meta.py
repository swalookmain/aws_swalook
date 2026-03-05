import requests
import json

ACCESS_TOKEN = "EAAPaDcpO3VkBQwa3IgzvqufDG43gOOywKZBnscqvpZBju3hCt66A5KISX2SoUVHIGNCHn7znhk0TXus2WT25KRXY3JSFMIcBREg9X7GnlDyxZAizZBDyJ6OCtEYss46JqA2VeNQCRGYLfk4edkofmUSzCnDNC5wl73qxjRpFaCpjbCFUp5HKWuVa7T2fCpPtFgZDZD"
PHONE_NUMBER_ID = "622736274257277" 
url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}

payload = {
    "messaging_product": "whatsapp",
    "to": "917984490823",
    "type": "template",
    "template": {
        "name": "happy_birthday_offer",
        "language": {"code": "en"},
        "components": [
            {
                "type": "header",
                "parameters": [{"type": "text", "parameter_name": "customer_name", "text": "Het Dalal"}]
            },
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "parameter_name": "salon_name", "text": "Swalook"},
                    {"type": "text", "parameter_name": "special_offer", "text": "20% OFF"},
                    {"type": "text", "parameter_name": "phone_number", "text": "+91-7984490823"},
                    {"type": "text", "parameter_name": "salon_name_footer", "text": "Swalook"}
                ]
            }
        ]
    }
}

response = requests.post(url, headers=headers, json=payload)
print(json.dumps(response.json(), indent=2))
