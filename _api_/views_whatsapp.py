import requests
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class SendWhatsappMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        template_name = request.data.get('template_name')
        language_code = request.data.get('language_code', 'en')
        components = request.data.get('components', [])  # Must be an array of component dicts if variables exist

        if not phone_number or not template_name:
            return Response(
                {"status": False, "message": "phone_number and template_name are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Pre-process phone number (remove +, -, spaces, ensuring country code)
        clean_phone = ''.join(filter(str.isdigit, phone_number))
        if not clean_phone.startswith('91') and len(clean_phone) == 10:
             clean_phone = '91' + clean_phone
             
        # User provided credentials
        PHONE_NUMBER_ID = "622736274257277"
        ACCESS_TOKEN = "EAAPaDcpO3VkBQZCAoo1WZBAoNJs3s48ws4VvjIoHtGZBwnt4hLC2SiMysFzos7l6EQ9TW40wfhaAimZCI9xPjUrkzmZAJD6vxRqIt3OAI3dfZBUqyMEByUk1VY0YOs7fveOM9bdEQuYS59yV8ZCmtJ8RETtRkskTONt6S3UbfgQx3ZAiNAFTAeSZBJRadZBZBBAxNa0QE5oXMlbp44WLxobwZC60C78ITmCdZAwuej8TLR3PfGI6ctlnUsGw1ZAxIrNMwsMcgW5TVhGrwCG8VhiNga33t9jWvYkw0ZD"
        url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components

        try:
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()

            if response.status_code == 200:
                return Response(
                    {"status": True, "message": "Message sent successfully!", "data": response_data},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"status": False, "message": "Failed to send message.", "error": response_data},
                    status=response.status_code
                )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
