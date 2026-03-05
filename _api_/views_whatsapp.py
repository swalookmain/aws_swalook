import requests
import json
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class SendWhatsappMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        message_body = request.data.get('message_body')
        template_name = request.data.get('template_name') # Added support for official templates

        if not phone_number:
            return Response({"status": False, "message": "phone_number is required."}, status=status.HTTP_400_BAD_REQUEST)

        clean_phone = ''.join(filter(str.isdigit, phone_number))
        if not clean_phone.startswith('91') and len(clean_phone) == 10:
            clean_phone = '91' + clean_phone

        PHONE_NUMBER_ID = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
        ACCESS_TOKEN = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')

        url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
        
        # Build payload dynamically based on whether it's a template or raw text
        if template_name:
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": request.data.get('language_code', 'en_US')},
                    "components": request.data.get('components', [])
                }
            }
        else:
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": "text",
                "text": {"body": message_body}
            }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response_data = response.json()
            if response.status_code == 200:
                return Response({"status": True, "message": "Sent!", "data": response_data}, status=status.HTTP_200_OK)
            return Response({"status": False, "message": response_data.get('error', {}).get('message', 'Failed'), "error": response_data}, status=response.status_code)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(f"[WA] Exception: {str(e)}")
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
