import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_swalook.settings')
django.setup()

from django.conf import settings

ACCESS_TOKEN = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
PHONE_NUMBER_ID = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')

url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("SUCCESS: Token is valid and connection established.")
        print(f"Details: {response.json()}")
    else:
        print(f"FAILED: status={response.status_code}")
        print(f"Error: {response.json()}")
except Exception as e:
    print(f"ERROR: {str(e)}")
