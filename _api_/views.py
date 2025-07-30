from collections import defaultdict
from datetime import date, datetime, timedelta
from django.utils.timezone import now
import io
from django.http import FileResponse
from PIL import Image, ImageDraw, ImageFont
import json
from openpyxl import Workbook
import os
import requests
from rest_framework.throttling import ScopedRateThrottle
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage, send_mail
from django.db import transaction
from django.db.models import Count, F, Sum
from django.db.models.functions import ExtractWeekDay, TruncMonth
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .serializer import *
from api_swalook import settings
import subprocess
import datetime as dt
from django.utils.timezone import now
from django.utils import timezone
from datetime import timedelta
from io import BytesIO
FB_APP_ID = settings.IG_FB_APP_ID
FB_APP_SECRET = settings.IG_FB_APP_SECRET



class VendorSignin(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = signup_serializer

    def post(self, request):

        try:

            serializer_objects = self.serializer_class(data=request.data)

            if serializer_objects.is_valid():

                serializer_objects.save()

                return Response({
                    'success': True,
                    'status_code': status.HTTP_201_CREATED,
                    'error': {
                        'code': 'The request was successful',
                        'message': 'User_created'
                    },
                    'data': {
                        'user': serializer_objects.validated_data.get('salon_name'),
                        'mobileno': serializer_objects.validated_data.get('mobile_no'),
                    }
                }, status=status.HTTP_201_CREATED)
            else:

                return Response({
                    'success': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'error': {
                        'code': 'The request was unsuccessful',
                        'message': serializer_objects.errors
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:

            return Response({
                'success': False,
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'error': {
                    'code': 'Internal Server Error',
                    'message': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class vendor_update_profile(APIView):
    permission_classes = [IsAuthenticated]
    def put(self,request):
        serializer_objects           = UpdateProfileSerializer(request.data)                 # convertion of request.data into python native datatype
        json_data                    = JSONRenderer().render(serializer_objects.data)      # rendering the data into json
        stream_data_over_network     = io.BytesIO(json_data)                                 # streaming the data into bytes
        accept_json_stream           = JSONParser().parse(stream_data_over_network)            # prases json data types data
        ''' passing the json stream data into serializer '''

        serializer                   = UpdateProfileSerializer(data=accept_json_stream,context={'request':request})               # intializing serializer and
        if serializer.is_valid():                                                                   # check if serializer.data is valid
                                                                                    # all the .validate_fieldname in the serializer will call here
            ''' here the db call happen after accept  '''

            serializer.save()
            return Response({
                    'success': True,
                    'status_code': status.HTTP_201_CREATED,
                    'error': {
                        'code': 'The request was successful',
                        'message': 'User data updated'
                    },
                    'data':None
                }, status=status.HTTP_201_CREATED)
        return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'The request was successful',

                },
                'data':None
            }, status=status.HTTP_400_BAD_REQUEST)


class vendor_login(CreateAPIView):
    serializer_class = login_serializer
    permission_classes = [AllowAny]

    def post(self, request):
        ''' deserialization of register user'''
        serializer_objects = login_serializer(request.data)  # conversion of request.data into python native datatype
        json_data = JSONRenderer().render(serializer_objects.data)  # rendering the data into json
        stream_data_over_network = io.BytesIO(json_data)  # streaming the data into bytes
        accept_json_stream = JSONParser().parse(stream_data_over_network)  # parses json data types data
        ''' passing the json stream data into serializer '''

        serializer = login_serializer(data=accept_json_stream, context={"request": request})  # initializing serializer
        if serializer.is_valid():  # check if serializer.data is valid
            ''' here the db call happen after accept  '''
            serializer.save()  # the create method of serializer call here
            ''' returning the status and info as response'''
            user = User.objects.get(username=request.user)
            token = Token.objects.get_or_create(user=user)
            salon_name = SwalookUserProfile.objects.get(mobile_no=str(request.user))
            if salon_name.branches_created != 0:
                branch = SalonBranch.objects.get(vendor_name=user)
                return Response({
                    'status': True,  # corresponding to ---> 'key:value' for access data
                    'code': 302,
                    'text': "login successful!",
                    'token': str(token[0]),
                    'user': str(request.user),
                    'salon_name': salon_name,
                    'type': "vendor",
                    'branch_name': branch.branch_name,
                })
            else:
                return Response({
                    'status': True,  # corresponding to ---> 'key:value' for access data
                    'code': 302,
                    'text': "login successful!",
                    'token': str(token[0]),
                    'user': str(request.user),
                    'salon_name': salon_name,
                    'type': "vendor",
                })
        return Response({
            'status': False,
            'code': 500,
            'text': 'invalid user&pass'
        })

class staff_login(CreateAPIView):
    serializer_class = staff_login_serializer
    permission_classes = [AllowAny]

    def post(self, request):
        ''' deserialization of register user'''
        serializer_objects = staff_login_serializer(request.data)  # conversion of request.data into python native datatype
        json_data = JSONRenderer().render(serializer_objects.data)  # rendering the data into json
        stream_data_over_network = io.BytesIO(json_data)  # streaming the data into bytes
        accept_json_stream = JSONParser().parse(stream_data_over_network)  # parses json data types data
        ''' passing the json stream data into serializer '''

        serializer = staff_login_serializer(data=accept_json_stream, context={"request": request})  # initializing serializer and
        if serializer.is_valid():  # check if serializer.data is valid
            ''' here the db call happen after accept  '''
            u = serializer.save()  # the create method of serializer call here
            ''' returning the status and info as response'''
            use = SwalookUserProfile.objects.get(mobile_no=str(u.username))
            user = auth.authenticate(username=use.mobile_no, password=use.enc_pwd)
            auth.login(request, user)
            token = Token.objects.get_or_create(user=user)
            salon_name = SwalookUserProfile.objects.get(mobile_no=str(request.user))
            user = User.objects.get(username=salon_name.mobile_no)
            branch = SalonBranch.objects.get(vendor_name=user)

            return Response({
                'status': True,  # corresponding to ---> 'key:value' for access data
                'code': 302,
                'text': "login successful!",
                'token': str(token[0]),
                'user': str(request.user),
                'salon_name': salon_name.salon_name,
                'type': "staff",
                'branch_name': branch.branch_name,
            })
        return Response({
            'status': False,
            'code': 500,
            'text': 'invalid user&pass'
        })


class admin_login(CreateAPIView):
    serializer_class = admin_login_serializer
    permission_classes = [AllowAny]

    def post(self, request):
        ''' deserialization of register user'''
        serializer_objects = admin_login_serializer(request.data)  # conversion of request.data into python native datatype
        json_data = JSONRenderer().render(serializer_objects.data)  # rendering the data into json
        stream_data_over_network = io.BytesIO(json_data)  # streaming the data into bytes
        accept_json_stream = JSONParser().parse(stream_data_over_network)  # parses json data types data
        ''' passing the json stream data into serializer '''

        serializer = admin_login_serializer(data=accept_json_stream, context={"request": request})  # initializing serializer and
        if serializer.is_valid():  # check if serializer.data is valid
            ''' here the db call happen after accept  '''
            token = serializer.save()
            salon_name = SwalookUserProfile.objects.get(mobile_no=str(request.user))
            user = User.objects.get(username=salon_name.mobile_no)
            branch = SalonBranch.objects.get(vendor_name=user)

            return Response({
                'status': True,  # corresponding to ---> 'key:value' for access data
                'code': 302,
                'text': "login successful!",
                'token': str(token[0]),
                'user': str(request.user),
                'salon_name': salon_name,
                'type': "admin",
                'branch_name': branch.branch_name,
            })
        return Response({
            'status': False,
            'code': 500,
            'text': 'invalid user&pass'
        })


class Centralized_login(APIView):
    serializer_class = centralized_login_serializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})

        if serializer.is_valid():
            try:
                result = serializer.create(serializer.validated_data)
                user_type, token, salon_name, branch = result

                response_data = {
                    'success': True,
                    'status_code': status.HTTP_200_OK,
                    'error': {
                        'code': 'The request was successful',
                        'message': "login successful!",
                    },
                    'data': {
                        'token': str(token),
                        'user': str(request.user),
                        'salon_name': salon_name,
                        'type': user_type
                    }
                }

                if branch:
                    response_data['data'].update({
                        'branch_name': branch.branch_name,
                        'branch_id': branch.id
                    })

                return Response(response_data, status=status.HTTP_200_OK)

            except ValidationError as e:
                return Response({
                    'success': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'error': {
                        'code': 'The request was unsuccessful',
                        'message': str(e),
                    },
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success': False,
            'status_code': status.HTTP_400_BAD_REQUEST,
            'error': {
                'code': 'The request was unsuccessful',
                'message': 'Invalid input data',
            },
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
class VendorServices(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        branch_name = request.query_params.get('branch_name')

        queryset = VendorService.objects.filter(user=request.user, vendor_branch_id=branch_name).only("id", "service").order_by('service')

        serialized_data = service_name_serializer(queryset, many=True)

        return Response({
            'success': True,
            'status_code': status.HTTP_200_OK,
            'data': {
                'service': serialized_data.data,
            }
        }, status=status.HTTP_200_OK)


class Add_vendor_service(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = service_serializer

    def post(self, request):
        branch_name = request.query_params.get('branch_name')

        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'branch_name_missing',
                    'message': 'Branch name is required.',
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        v = VendorServiceCategory.objects.get(id=request.data.get('category'))
        service_obj = VendorService.objects.filter(
            user=request.user,
            vendor_branch_id=branch_name,
            service=request.data.get('service'),
            category= v
        )
        if service_obj.exists():
            return Response({
                'success': False,
                'status_code': status.HTTP_409_CONFLICT,
                'error': {
                    'code': 'service_exists',
                    'message': 'A service with the same name already exists on this branch.',
                },
                'data': None
            }, status=status.HTTP_409_CONFLICT)

        serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name})

        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'status_code': status.HTTP_201_CREATED,
                'error': {
                    'code': 'service_added',
                    'message': 'Service added successfully on this branch.',
                },
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'status_code': status.HTTP_400_BAD_REQUEST,
            'error': {
                'code': 'invalid_data',
                'message': 'Provided data is invalid.',
            },
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class Edit_service(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = service_update_serializer

    def put(self, request):
        id = request.query_params.get('id')
        branch_name = request.query_params.get('branch_name')

        service_obj = VendorService.objects.filter(user=request.user, vendor_branch_id=branch_name, service=request.data.get('service')).exclude(id=id)
        if service_obj.exists():
            return Response({
                'success': False,
                'status_code': status.HTTP_200_OK,
                'error': {
                    'code': 'The request was successful',
                    'message': 'Service with the same name already exists on this branch!'
                },
                'data': None
            }, status=status.HTTP_200_OK)

        try:
            service_instance = VendorService.objects.get(id=id, user=request.user, vendor_branch_id=branch_name)
        except VendorService.DoesNotExist:
            return Response({
                'success': False,
                'status_code': status.HTTP_404_NOT_FOUND,
                'error': {
                    'code': 'Not Found',
                    'message': 'Service not found!'
                },
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(instance=service_instance, data=request.data, context={'request': request, 'branch_id': branch_name})

        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'status_code': status.HTTP_200_OK,
                'error': {
                    'code': 'The request was successful',
                    'message': 'Service updated on this branch!'
                },
                'data': None
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'status_code': status.HTTP_400_BAD_REQUEST,
            'error': {
                'code': 'Validation Error',
                'message': 'Serializer data is invalid!'
            },
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class Delete_service(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        id = request.query_params.get('id')

        if not id:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'ID parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            queryset = VendorService.objects.get(id=id, user=request.user)
            queryset.delete()

            return Response({
                'success': True,
                'status_code': status.HTTP_200_OK,
                'error': {
                    'code': 'The request was successful',
                    'message': 'Service deleted successfully!'
                },
                'data': None
            }, status=status.HTTP_200_OK)

        except VendorService.DoesNotExist:
            return Response({
                'success': False,
                'status_code': status.HTTP_404_NOT_FOUND,
                'error': {
                    'code': 'Not Found',
                    'message': 'Service not found!'
                },
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)


class Delete_invoice(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        id = request.query_params.get('id')
        queryset = VendorInvoice.objects.get(id=id)
        queryset.delete()

        return Response({
            'success': True,
            'status_code': status.HTTP_200_OK,
            'error': {
                'code': 'The request was successful',
            },
            'data': None
        }, status=status.HTTP_200_OK)


class Table_service(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        query_set = VendorService.objects.filter(user=request.user).order_by('service')

        serializer_obj = service_serializer(query_set, many=True)

        return Response({
            "status": True,
            "data": serializer_obj.data
        }, status=status.HTTP_200_OK)


class get_slno(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def get(self, request):
        current_date = dt.date.today()
        current_month = current_date.month
        current_year = current_date.year

        try:
            user_profile = SwalookUserProfile.objects.get(mobile_no=str(request.user))

            user_profile.invoice_generated += 1
            user_profile.save()

            slno = (
                f"{user_profile.vendor_id.lower()}"
                f"{user_profile.invoice_generated}"
                f"{current_month}"
                f"{current_year}"
                f"{user_profile.invoice_generated}"
            )

            return Response({"slno": slno}, status=status.HTTP_200_OK)

        except SwalookUserProfile.DoesNotExist:
            return Response({
                "success": False,
                "error": {
                    "code": "Not Found",
                    "message": "User profile not found."
                }
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "success": False,
                "error": {
                    "code": "Server Error",
                    "message": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class vendor_billing(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = billing_serializer

    def __init__(self, **kwargs):
        self.cache_key = None
        super().__init__(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.cache_key = f"VendorBilling/{request.user.id}"
        return super().dispatch(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        

            
        serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name})

        if serializer.is_valid():
            slno = serializer.save()
            return Response({
                "status": True,
                "slno": slno,
                "message": "Billing record created successfully."
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": False,
            "errors": serializer.errors,
            "message": "Failed to create billing record."
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        date = request.query_params.get('date')
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = VendorInvoice.objects.filter(
            vendor_name=request.user,
            vendor_branch_id = branch_name,
            date=date
        ).order_by('-date')
       
        invoice_data = billing_serializer_get(queryset, many=True).data
        # for idx, invoice in enumerate(invoice_data):
        #             slno = invoice.get('slno')
        #             if slno:  
        #                 invoice_filename = f"Invoice-{slno}.pdf"
        #                 invoice_path = os.path.join('media/pdf', invoice_filename)
        #                 invoice_data[idx]['pdf_path'] = invoice_path
        #             else:
        #                 invoice_data[idx]['pdf_path'] = None 


        return Response({
            "status": True,
            "table_data": invoice_data,
            "message": "Billing records retrieved successfully."
        }, status=status.HTTP_200_OK)


    def put(self, request):
        ids = request.query_params.get('id')
        branch_name = request.query_params.get('branch_name')
    
        try:
            instance = VendorInvoice.objects.get(id=ids)
        except VendorInvoice.DoesNotExist:
            return Response({"status": False, "message": "Invoice not found"}, status=404)
    
        serializer = self.serializer_class(
            instance, data=request.data, partial=True, 
            context={'request': request, 'id': ids, 'branch_id': branch_name}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"status": True})
        else:
            return Response({"status": False, "errors": serializer.errors}, status=400)


class vendor_billing_pdf(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
        serializer.save()
       
        return Response({"status": True}, status=status.HTTP_201_CREATED)

       
    def get_serializer(self, *args, **kwargs):
        return Vendor_Pdf_Serializer(*args, **kwargs)

    def send_invoice_email(self, validated_data, request_data):
        try:
            subject = f"{validated_data.get('vendor_branch_name')} - Invoice"
            body = (
                f"Hi {request_data.get('customer_name')}!\n"
                f"We hope you had a pleasant experience at {request_data.get('vendor_branch_name')}.\n"
                "We are looking forward to servicing you again. Attached is the invoice.\n"
                f"Thanks and Regards,\nTeam {request_data.get('vendor_branch_name')}"
            )
            from_email = validated_data.get('vendor_email')
            recipient_list = [validated_data.get('email')]

            return self._send_email(subject, body, from_email, recipient_list, validated_data.get('invoice'))

        except Exception as e:
            return False

    def _send_email(self, subject, body, from_email, recipient_list, invoice_id):
        try:
            invoice_filename = f"Invoice-{invoice_id}.pdf"
            invoice_path = os.path.join(settings.MEDIA_ROOT, f"pdf/{invoice_filename}")

            if not os.path.exists(invoice_path):
                return False

            email = EmailMessage(subject, body, from_email, recipient_list)
            with open(invoice_path, 'rb') as invoice_file:
                email.attach(invoice_filename, invoice_file.read(), 'application/pdf')

            email.send()
            return True

        except FileNotFoundError as e:
            return False
        except Exception as e:
            return False


class VendorAppointments(CreateAPIView, ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = appointment_serializer

    def __init__(self):
        self.cache_key = None

    def dispatch(self, request, *args, **kwargs):
        self.cache_key = f"Vendorappointment/{request.user}"
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        branch_name = request.query_params.get("branch_name", "").replace("%20", " ")

        existing_appointments = VendorAppointment.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name,
            mobile_no=request.data.get('mobile_no'),
            booking_date=request.data.get("booking_date"),
            booking_time=request.data.get('booking_time')
        ).exclude(id=branch_name)

        if existing_appointments.exists():
            return Response({
                'status': False,
                'text': f"Appointment for this customer {request.data.get('mobile_no')} on {request.data.get('booking_date')} at {request.data.get('booking_time')} already exists."
            })

        serializer = appointment_serializer(data=request.data, context={"request": request, "branch_id": branch_name})
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True})

        return Response({"status": False, "errors": serializer.errors})

    def list(self, request):
        branch_name = request.query_params.get('branch_name')
        query_set = VendorAppointment.objects.filter(vendor_name=request.user, vendor_branch_id=branch_name, date=dt.date.today()).order_by('-id')
        serializer_obj = appointment_serializer(query_set[::-1], many=True)

        return Response({
            "status": True,
            "table_data": serializer_obj.data,
        })


class edit_appointment(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request):
        appointment_id = request.query_params.get('id')
        branch_name = request.query_params.get('branch_name', "").replace("%20", " ")

        if not branch_name or not appointment_id:
            return Response({
                'status': False,
                'error': 'Branch name and appointment ID are required.'
            }, status=400)

        existing_appointments = VendorAppointment.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name,
            mobile_no=request.data.get('mobile_no'),
            booking_date=request.data.get('booking_date'),
            booking_time=request.data.get('booking_time')
        ).exclude(id=appointment_id)

        if existing_appointments.exists():
            return Response({
                'status': False,
                'error': f"Appointment for customer {request.data.get('mobile_no')} on {request.data.get('booking_date')} at {request.data.get('booking_time')} already exists."
            }, status=409)

        try:
            appointment = VendorAppointment.objects.get(id=appointment_id, vendor_name=request.user)
        except VendorAppointment.DoesNotExist:
            raise NotFound('Appointment not found.')

        data = request.data.copy()
        data['vendor_branch_id'] = branch_name
        data['date'] = dt.date.today()

        serializer = UpdateAppointmentSerializer(appointment, data=data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': True,
                'message': "Appointment updated successfully."
            }, status=200)
        else:
            return Response({
                'status': False,
                'errors': serializer.errors
            }, status=400)


class delete_appointment(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        appointment_id = request.query_params.get('id')

        if not appointment_id:
            return Response({
                "status": False,
                "code": 400,
                "message": "Appointment ID is required."
            }, status=400)

        try:
            appointment = VendorAppointment.objects.get(id=appointment_id, vendor_name=request.user)
            appointment.delete()

            return Response({
                "status": True,
                "code": 200,
                "message": "Appointment successfully deleted.",
                "appointment_deleted_id": appointment_id,
            }, status=200)

        except VendorAppointment.DoesNotExist:
            return Response({
                "status": False,
                "code": 404,
                "message": f"Appointment with ID {appointment_id} does not exist.",
            }, status=404)

        except Exception as e:
            return Response({
                "status": False,
                "code": 500,
                "message": f"An error occurred: {str(e)}",
            }, status=500)


class edit_profile(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        mobile_no = request.query_params.get('id')

        if not mobile_no:
            return Response({
                'status': False,
                'code': 400,
                'text': "Mobile number is required."
            }, status=400)

        try:
            profile = SwalookUserProfile.objects.get(mobile_no=mobile_no)
        except SwalookUserProfile.DoesNotExist:
            return Response({
                'status': False,
                'code': 404,
                'text': "Profile not found."
            }, status=404)

        serializer = UpdateProfileSerializer(profile, data=request.data, context={"request": request}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': True,
                'code': 200,
                'text': "User profile updated successfully!",
                'data': serializer.data
            })

        return Response({
            'status': False,
            'code': 400,
            'text': "Validation failed.",
            'errors': serializer.errors
        }, status=400)

class VendorBranch(CreateAPIView, RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = branch_serializer

    def post(self, request):
        serializer_objects = branch_serializer(request.data)  # conversion of request.data into python native datatype
        json_data = JSONRenderer().render(serializer_objects.data)  # rendering the data into json
        stream_data_over_network = io.BytesIO(json_data)  # streaming the data into bytes
        accept_json_stream = JSONParser().parse(stream_data_over_network)  # parses json data types data

        serializer = self.serializer_class(data=accept_json_stream, context={"request": request})

        accept_json_stream = request.data
        test_if = SalonBranch.objects.filter(staff_name=accept_json_stream.get('staff_name'))
        if len(test_if) == 1:
            return Response({"status": "this mobileno is already registered with a licence !", })
        user_if = SalonBranch.objects.filter(staff_name=accept_json_stream.get('staff_name'), vendor_name=request.user)
        if len(user_if) == 1:
            return Response({"status": "this mobileno is already registered on this licence !", })
        branch_if = SalonBranch.objects.filter(branch_name=accept_json_stream.get('branch_name'), staff_name=accept_json_stream.get('staff_name'), vendor_name=request.user)
        if len(branch_if) == 1:
            return Response({"status": "this branch with this username is already exists !", })
        only_branch_if = SalonBranch.objects.filter(branch_name=accept_json_stream.get('branch_name'), vendor_name=request.user)
        if len(only_branch_if) == 1:
            return Response({"status": "this branch is already exists on this licence !", })
        user_profile = SwalookUserProfile.objects.get(mobile_no=str(request.user))
        if user_profile.branch_limit == user_profile.branches_created:
            return Response({"status": "this licence is reached its branch limit !", })

        queryset = SalonBranch()
        queryset.branch_name = accept_json_stream.get('branch_name')
        queryset.staff_name = accept_json_stream.get('staff_name')
        queryset.password = accept_json_stream.get('password')
        queryset.admin_password = accept_json_stream.get('branch_name')[:5] + str(request.user)[:7]
        queryset.staff_url = accept_json_stream.get('branch_name')
        queryset.admin_url = accept_json_stream.get('branch_name')
        queryset.vendor_name = request.user
        queryset.save()

        user_profile.branches_created = user_profile.branches_created + 1
        user_profile.save()

        return Response({
            "status": True,
            "admin_password": queryset.admin_password,
        })

    def get(self, request):
        query_set = SalonBranch.objects.filter(vendor_name=request.user)[::-1]
        serializer_obj = branch_serializer(query_set, many=True)
        return Response({
            "status": True,
            "table_data": serializer_obj.data,
        })


class edit_branch(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        id = request.query_params.get('id')
        accept_json_stream = request.data

        queryset = SalonBranch.objects.get(id=id)
        queryset.delete()
        queryset = SalonBranch()

        queryset.branch_name = accept_json_stream.get('branch_name')
        queryset.staff_name = accept_json_stream.get('staff_name')
        queryset.password = accept_json_stream.get('password')
        queryset.admin_password = accept_json_stream.get('admin_password')
        queryset.staff_url = accept_json_stream.get('staff_url')
        queryset.admin_url = accept_json_stream.get('admin_url')
        queryset.vendor_name = request.user
        queryset.save()

        return Response({
            'status': True,
            'code': 302,
            'text': "branch update!"
        })


class delete_branch(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        id = request.query_params.get('id')
        queryset = SalonBranch.objects.get(id=id)
        queryset.delete()

        user_profile = SwalookUserProfile.objects.get(mobile_no=str(request.user))
        user_profile.branches_created = user_profile.branches_created - 1
        user_profile.save()

        return Response({
            "status": True,
            'code': 302,
            "branch_deleted_id": id,
        })


class user_verify(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            salon_name = request.query_params.get('salon_name')
            branch_name = request.query_params.get('branch_name')
            sallon_name = SwalookUserProfile.objects.filter(salon_name=salon_name)
            user = User.objects.get(username=sallon_name[0].mobile_no)
            queryset = SalonBranch.objects.get(vendor_name=user, branch_name=branch_name)

            return Response({
                "status": True,
                'code': 302,
            })
        except Exception as e:
            return Response({
                "status": False,
                'code': 302,
            })


class present_day_appointment(APIView):
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        date = request.query_params.get('date')
        query_set = VendorAppointment.objects.filter(vendor_name=request.user, date=date, vendor_branch_id=branch_name).order_by("booking_time")
        serializer_obj = appointment_serializer(query_set, many=True)
        return Response({
            "status": True,
            "table_data": serializer_obj.data,
        })


class get_specific_appointment(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        id = request.query_params.get('id')
        query_set = VendorAppointment.objects.filter(id=id)
        serializer_obj = appointment_serializer(query_set, many=True)
        return Response({
            "status": True,
            "single_appointment_data": serializer_obj.data,
        })


class showendpoint(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "status": True,
            "endpoints": ""
        })





class update_files_pull(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        command = ['git', 'pull']
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            output = result.stdout
        except subprocess.CalledProcessError as e:
            output = f"Error: {e.stderr}"
        return Response({
            "server updated": output,
        })


class restart_server(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        os.chdir("/root/api_swalook/Swalook-master/")
        command = ['npm', 'run', 'build']
        command2 = ['PORT=80', 'serve', '-s', 'build']
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            output = result.stdout
            result_ = subprocess.run(command2, capture_output=True, text=True, check=True)
            output_ = result_.stdout
            return Response({
                "server build status": output,
                "server running": output_,
                "status": True,
            })
        except subprocess.CalledProcessError as e:
            output = f"Error: {e.stderr}"
            return Response({
                "error": output,
                "status": False,
            })


class get_current_user_profile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        id = request.query_params.get('id')
        data = SwalookUserProfile.objects.get(mobile_no=id)
        serializer_data = user_data_set_serializer(data)
        return Response({
            "status": True,
            "current_user_data": serializer_data.data,
        })


class get_present_day_bill(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        data = VendorInvoice.objects.filter(vendor_name=request.user, vendor_branch=branch_name, date=dt.date.today())
        serializer_data = billing_serializer_get(data, many=True)
        return Response({
            "status": True,
            "current_user_data": serializer_data.data,
        })


class get__bill(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        id = request.query_params.get('id')
        data = VendorInvoice.objects.select_related('vendor_customers_profile').get(id=id)
        serializer_data = billing_serializer_get(data)
        return Response({
            "status": True,
            "current_user_data": serializer_data.data,
        })


class render_branch_data(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self):
        self.cache_key = None

    def dispatch(self, request, *args, **kwargs):
        self.cache_key = f"Vendorbranchbill/{request.user}"
        self.cache_key2 = f"Vendorbranchapp/{request.user}"
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        date = request.query_params.get('date')
        if "%20" in branch_name:
            branch_name = branch_name.replace("%20", " ")

        main_user = SwalookUserProfile.objects.get(mobile_no=str(request.user))
        inv = VendorInvoice.objects.filter(vendor_name=request.user, vendor_branch_id=branch_name, date=date)
        app = VendorAppointment.objects.filter(vendor_name=request.user, vendor_branch_id=branch_name, date=str(date))

        serializer_data_bill = billing_serializer_get(inv, many=True)
        serializer_data_appo = appointment_serializer(app, many=True)

        return Response({
            "status": True,
            "branch_name": inv[0].vendor_branch,
            "salon_name": main_user.salon_name,
            "invoices": serializer_data_bill.data,
            "appointment": serializer_data_appo.data
        })


class ForgotPassword(APIView):
    permission_classes = [AllowAny]

    def __init__(self):
        self.otp = None

    def get(self, request):
        email = request.query_params.get('email')
        import random as r
        a = r.randint(0, 9)
        b = r.randint(0, 9)
        c = r.randint(0, 9)
        d = r.randint(0, 9)
        e = r.randint(0, 9)
        f = r.randint(0, 9)
        request.session[str(request.user)] = f"{a}{b}{c}{d}{e}{f}"

        user = SwalookUserProfile.objects.get(email=email)
        subject = "Swalook - OTP Verification"
        body = f"your 6 digit otp is {request.session.get(str(request.user))}. \n Thank you\n Swalook"
        send_mail(subject, body, 'info@swalook.in', [user.email])

        return Response({
            "status": True,
        })

    def post(self, request):
        otp = request.query_params.get('otp')
        if otp == request.session.get(str(request.user)):
            return Response({
                "status": True,
            })
        else:
            return Response({
                "status": False,
                "message": "Invalid OTP",
            })


class BusniessAnalysiss(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self):
        self.mon = dt.date.today()

    def get(self, request):
        pass


class help_desk(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HelpDesk_Serializer

    def post(self, request):
        serializer_objects = HelpDesk_Serializer(request.data)  # conversion of request.data into python native datatype
        json_data = JSONRenderer().render(serializer_objects.data)  # rendering the data into json
        stream_data_over_network = io.BytesIO(json_data)  # streaming the data into bytes
        accept_json_stream = JSONParser().parse(stream_data_over_network)  # parses json data types data

        serializer = HelpDesk_Serializer(data=accept_json_stream, context={'request': request})  # initializing serializer and
        if serializer.is_valid():  # check if serializer.data is valid
            serializer.save()  # the create method of serializer call here

            subject = "Swalook - Query form "
            body = f" {serializer.data}. \n Thank you\n Swalook"
            send_mail(subject, body, 'info@swalook.in', ["info@swalook.in"])
            return Response({
                "status": True,
                'from mail': 'info@swalook.in',
                'to mail': 'info@swalook.in',
            })


class Add_Inventory_Product(CreateAPIView, UpdateAPIView, ListAPIView, DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Inventory_Product_Serializer

    def post(self, request, *args, **kwargs):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({"status": False, "text": "Branch name is required."}, status=status.HTTP_400_BAD_REQUEST)

        product_id = request.data.get('product_id')
        product_name = request.data.get('product_name')

        filters = {'user': request.user, 'vendor_branch_id': branch_name}
        valid_1 = VendorInventoryProduct.objects.filter(**filters, product_id=product_id, product_name=product_name).exists()
        valid_2 = VendorInventoryProduct.objects.filter(**filters, product_id=product_id).exists()
        valid_3 = VendorInventoryProduct.objects.filter(**filters, product_name=product_name).exists()

        if valid_1:
            return Response({"status": False, "text": "Product already exists with the same name and ID"}, status=status.HTTP_400_BAD_REQUEST)
        if valid_2:
            return Response({"status": False, "text": "Product already exists with the same ID"}, status=status.HTTP_400_BAD_REQUEST)
        if valid_3:
            return Response({"status": False, "text": "Product already exists with the same name"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name})
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        id = request.query_params.get('id')
        branch_name = request.query_params.get('branch_name')

        if not id or not branch_name:
            return Response({"status": False, "text": "ID and branch name are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = VendorInventoryProduct.objects.get(user=request.user, id=id)
        except ObjectDoesNotExist:
            return Response({"status": False, "text": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = update_inventory_product_serializer(instance, data=request.data, context={'request': request, 'branch_id': branch_name})
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "text": "Data updated"}, status=status.HTTP_200_OK)
        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        id = request.query_params.get('id')
        if not id:
            return Response({"status": False, "text": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data_object = VendorInventoryProduct.objects.get(user=request.user, id=id)
            data_object.delete()
            return Response({"status": True, "text": "Product deleted."}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({"status": False, "text": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({"status": False, "text": "Branch name is required."}, status=status.HTTP_400_BAD_REQUEST)

        data_objects = VendorInventoryProduct.objects.filter(user=request.user, vendor_branch_id=branch_name).order_by('-id')
        serializer = self.serializer_class(data_objects, many=True)
        return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)


class Bill_Inventory(CreateAPIView,UpdateAPIView,RetrieveAPIView,DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Inventory_Product_Invoice_Serializer

    def post(self,request):
        ''' deserialization of register user'''
        branch_name = request.query_params.get('branch_name')
        serializer_objects           = self.serializer_class(request.data)                 # convertion of request.data into python native datatype
        json_data                    = JSONRenderer().render(serializer_objects.data)      # rendering the data into json
        stream_data_over_network     = io.BytesIO(json_data)                                 # streaming the data into bytes
        accept_json_stream           = JSONParser().parse(stream_data_over_network)            # prases json data types data
        ''' passing the json stream data into serializer '''

        serializer                   = self.serializer_class(data=accept_json_stream,context={'request':request,'branch_id':branch_name})               # intializing serializer and
        if serializer.is_valid():                                                                   # check if serializer.data is valid
                                                                                    # all the .validate_fieldname in the serializer will call here
            ''' here the db call happen after accept  '''

            serializer.save()                                                       # the create method of serializer call here
            ''' returning the status and info as response'''

            return Response({
            "status":True,
            "data":serializer.data
            })

    def put(self,request,id):
        pass
    def delete(self,request,id):
        pass

class Vendor_loyality_customer_profile(CreateAPIView, ListAPIView, UpdateAPIView, DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VendorCustomerLoyalityProfileSerializer

    def post(self, request):
        ''' deserialization of register user'''
        branch_name = request.query_params.get('branch_name')
        try:
            VendorCustomers.objects.get(user=request.user, mobile_no=request.data.get('mobile_no'))
            return Response({
                "status": False,
                "message": "vendor customer already exists"
            })
        except Exception:
            serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": True,
                })
            else:
                return Response({
                    "status": False,
                })

    def list(self, request):
        branch_name = request.query_params.get('branch_name')
        if "%20" in branch_name:
            branch_name = branch_name.replace("%20", " ")

        data_object = VendorCustomers.objects.filter(user=request.user).values()
        # serializer_obj = VendorCustomerLoyalityProfileSerializer_get(data_object, many=True)

        return Response({
            "status": True,
            "data": list(data_object)
        })

    def put(self, request):
        ids = request.query_params.get('id')
        branch_name = request.query_params.get('branch_name')
    
        try:
            instance = VendorCustomers.objects.get(id=ids)
        except VendorCustomers.DoesNotExist:
            return Response({"status": False, "message": "Customer not found"}, status=404)
    
        serializer = loyality_customer_update_serializer(
            instance, data=request.data, partial=True, 
            context={'request': request, 'id': ids, 'branch_id': branch_name}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"status": True})
        else:
            return Response({"status": False, "errors": serializer.errors}, status=400)


    def delete(self, request):
        ids = request.query_params.get('id')
        obj = VendorCustomers.objects.get(id=ids)
        try:
            clp = VendorCustomerLoyalityPoints.objects.get(id=obj.loyality_profile.id)
            clp.delete()
        except Exception:
            pass
        obj.delete()
       

        return Response({
            "status": True,
            "txt": f"object deleted of this id {id}"
        })


class Get_Profile(ListAPIView):

    def list(self, request):
        branch_name = request.query_params.get('branch_name')
        mobile_no = request.query_params.get('mobile_no')
        if "%20" in branch_name:
            branch_name = branch_name.replace("%20", " ")

        data_object = VendorCustomers.objects.filter(user=request.user, vendor_branch_id=branch_name, mobile_no=mobile_no)
        serializer_obj = VendorCustomerLoyalityProfileSerializer_get(data_object, many=True)

        return Response({
            "status": True,
            "data": serializer_obj.data
        })


class Vendor_loyality_type_add(CreateAPIView, UpdateAPIView, DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VendorLoyalityTypeSerializer

    def post(self, request):
        branch_name = request.query_params.get('branch_name')
        try:
            VendorLoyalityProgramTypes.objects.get(user=request.user, vendor_branch_id=branch_name, program_type=request.data.get('json_data')[0].get('type'))
            return Response({
                "status": False,
                "txt": "loyality program type already exists!"
            })
        except Exception:
            serializer_objects = self.serializer_class(request.data)
            json_data = JSONRenderer().render(serializer_objects.data)
            stream_data_over_network = io.BytesIO(json_data)
            accept_json_stream = JSONParser().parse(stream_data_over_network)
            serializer = self.serializer_class(data=accept_json_stream, context={'request': request, 'branch_id': branch_name})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": True,
                })

    def put(self, request):
        id = request.query_params.get('id')
        branch_name = request.query_params.get('branch_name')
        serializer_objects = Vendor_Type_Loyality_Update_Serializer(request.data)
        json_data = JSONRenderer().render(serializer_objects.data)
        stream_data_over_network = io.BytesIO(json_data)
        accept_json_stream = JSONParser().parse(stream_data_over_network)
        serializer = Vendor_Type_Loyality_Update_Serializer(data=accept_json_stream, context={'request': request, 'id': id, 'branch_id': branch_name})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "txt": "loyality type updated"
            })

    def delete(self, request):
        id = request.query_params.get('id')
        obj = VendorLoyalityProgramTypes.objects.get(id=id)
        obj.delete()
        return Response({
            "status": True,
            "txt": f"object deleted of this id {id}"
        })


class Vendor_loyality_type_add_get(ListAPIView):
    def list(self, request):
        branch_name = request.query_params.get('branch_name')
        if "%20" in branch_name:
            branch_name = branch_name.replace("%20", " ")

        data_object = VendorLoyalityProgramTypes.objects.filter(user=request.user, vendor_branch_id=branch_name)[::-1]
        serializer_obj = VendorLoyalityTypeSerializer_get(data_object, many=True)

        return Response({
            "status": True,
            "data": serializer_obj.data
        })


class Check_Loyality_Customer_exists(APIView):
    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        customer_mobile_no = request.query_params.get('customer_mobile_no')

        if "%20" in branch_name:
            branch_name = branch_name.replace("%20", " ")
        try:
            obj = VendorCustomers.objects.get(user=request.user, vendor_branch_id=branch_name, mobile_no=customer_mobile_no)
            serializer_obj = VendorCustomerLoyalityProfileSerializer(obj)
            return Response({
                "status": True,
                "membership_type": obj.membership_type.program_type,
                "points": obj.loyality_profile.current_customer_points
            })
        except Exception:
            return Response({
                "status": False,
                "data": "user does not exists"
            })


class Inventory_Products_get(APIView):
    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        if "%20" in branch_name:
            branch_name = branch_name.replace("%20", " ")
        product_obj = VendorInventoryProduct.objects.filter(user=request.user, vendor_branch_id=branch_name).values('id', 'product_name')
        return Response({
            "status": True,
            "data": list(product_obj)
        })


class MembershipTypesLoyality_get(APIView):
    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        if "%20" in branch_name:
            branch_name = branch_name.replace("%20", " ")
        product_obj = VendorLoyalityProgramTypes.objects.filter(user=request.user, vendor_branch_id=branch_name).values('program_type')
        return Response({
            "status": True,
            "data": list(product_obj)
        })


class update_minimum_amount(CreateAPIView, RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = update_minuimum_amount_serializer

    def post(self, request):
        ''' deserialization of register user'''
        branch_name = request.query_params.get('branch_name')
        serializer_objects = self.serializer_class(request.data)  # convertion of request.data into python native datatype
        json_data = JSONRenderer().render(serializer_objects.data)  # rendering the data into json
        stream_data_over_network = io.BytesIO(json_data)  # streaming the data into bytes
        accept_json_stream = JSONParser().parse(stream_data_over_network)  # prases json data types data
        ''' passing the json stream data into serializer '''

        serializer = self.serializer_class(data=accept_json_stream, context={'request': request, 'branch_id': branch_name})  # intializing serializer and
        if serializer.is_valid():  # check if serializer.data is valid
            ''' here the db call happen after accept  '''

            serializer.save()  # the create method of serializer call here
            ''' returning the status and info as response'''

            return Response({
                "status": True,
                # "data":serializer.data
            })

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        obj_user = SalonBranch.objects.get(id=branch_name)
        return Response({
            "status": True,
            "data": obj_user.minimum_purchase_loyality
        })


class vendor_staff(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = staff_serializer

    def __init__(self, **kwargs):
        self.cache_key = None
        super().__init__(**kwargs)

    # def dispatch(self, request, *args, **kwargs):
    #     self.cache_key = f"VendorBilling/{request.user.id}"
    #     return super().dispatch(request, *args, **kwargs)
    @transaction.atomic
    def post(self, request):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name})

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "staff added successfully."
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": False,
            "errors": serializer.errors,
            "message": "Failed to add staff."
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        queryseet = VendorStaff.objects.filter(
             vendor_name=request.user,
             vendor_branch_id=branch_name
        ).order_by('-id')
        # queryset_2 = StaffAdvanceModel.objects.filter(
        #     vendor_name=request.user,
        #     vendor_branch_id=branch_name
        # ).values("staff__mobile_no","advance_amount","created_at")
        # serializer = self.serializer_class(queryset, many=True)
        from django.db.models import Prefetch
        from django.utils import timezone
        
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        staff_advances = StaffAdvanceModel.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name
        ).only("staff__mobile_no", "advance_amount", "created_at")
        
        queryset = VendorStaff.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name
        ).prefetch_related(
            Prefetch('staffadvancemodel_set', queryset=staff_advances, to_attr='advances')
        ).order_by('-id')
        
        response = []
        for staff in queryset:
            advances_data = [
                {"advance_amount": adv.advance_amount, "created_at": adv.created_at}
                for adv in staff.advances
            ]
        
            current_month_total = sum(
                adv.advance_amount
                for adv in staff.advances
                if adv.created_at.month == current_month and adv.created_at.year == current_year
            )
        
            response.append({
                "staff_data":self.serializer_class(staff).data,
                "staff_name": staff.staff_name,
                "id": staff.id,
                "mobile_no": staff.mobile_no,
                "current_month_total": current_month_total,
                "advances": advances_data,
            })


        return Response({
            "status": True,
            "table_data": response,
            
            "message": "Staff records retrieved successfully."
        }, status=status.HTTP_200_OK)

    @transaction.atomic
    def put(self, request):
        staff_id = request.query_params.get('id')
        branch_name = request.query_params.get('branch_name', "").replace("%20", " ")

        if not staff_id:
            return Response({
                'status': False,
                'error': 'staff ID are required.'
            }, status=400)

        try:
            staff = VendorStaff.objects.get(id=staff_id, vendor_name=request.user)
        except VendorStaff.DoesNotExist:
            raise NotFound('Staff not found.')

        data = request.data.copy()
        data['vendor_branch_id'] = branch_name
        data['date'] = dt.date.today()

        serializer = self.serializer_class(staff, data=data, partial=True, context={"request": request, "branch_id": branch_name, "staff_id": staff_id})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': True,
                'message': "staff updated successfully.",
                'data': serializer.data,
            }, status=200)
        else:
            return Response({
                'status': False,
                'errors': serializer.errors
            }, status=400)

    def delete(self, request):
        id = request.query_params.get('id')

        clp = VendorStaff.objects.get(id=id)
        clp.delete()

        return Response({
            "status": True,
            "txt": f"object deleted of this id {id}"
        })

class vendor_staff_setting_slabs(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = staff_update_earning_deduction_serializer

    def __init__(self, **kwargs):
        self.cache_key = None
        super().__init__(**kwargs)

    @transaction.atomic
    def post(self, request):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        s_s = StaffSetting.objects.filter(vendor_name=request.user,vendor_branch_id=branch_name)
   
        if len(s_s) != 0:
            
            s_s.delete()
       
        time_object = StaffAttendanceTime.objects.filter(vendor_name=request.user,vendor_branch_id=branch_name)
        if len(time_object) != 0:
            time_object.delete()
        
              
        serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name})

        if serializer.is_valid():
            data_validate = serializer.save()

            return Response({
                "status": True,
                "message": "staff setting added successfully.",
                "data": data_validate
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": False,
            "errors": serializer.errors,
            "message": "Failed to add staff."
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = StaffSetting.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name
        ).order_by('-id')

        serializer = staff_setting_serializer_get(queryset, many=True)

        return Response({
            "status": True,
            "table_data": serializer.data,
            "message": "Staff Setting records retrieved successfully."
        }, status=status.HTTP_200_OK)


class vendor_staff_attendance(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = staff_attendance_serializer

    def __init__(self, **kwargs):
        self.cache_key = None
        super().__init__(**kwargs)

    @transaction.atomic
    def post(self, request):
        branch_name = request.query_params.get('branch_name')

        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        for i in request.data.get('json_data'):
            try:
                VendorStaffAttendance.objects.get(date=i.get('date'), staff_id=request.query_params.get('staff_id'))
                return Response({
                    "status": True,
                    "message": "staff attendance already exists"
                })
            except Exception:
                pass
        serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name})

        serializer.create(validated_data=request.data)
        prefered_in_time = StaffAttendanceTime.objects.get(vendor_name=request.user,vendor_branch_id=branch_name)
        # calculation remaining. 
        return Response({
            "status": True,
            "message": "staff attendance added successfully.",
            "in_time":request.data.get('json_data')[0].get('in_time'),
            "late_time":""
            
        }, status=status.HTTP_201_CREATED)
   
    
    
    
    
    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        month = request.query_params.get('month')
        staff_id = request.query_params.get('staff_id')

        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        current_date = dt.date.today()

        
        if staff_id:
            staff = VendorStaff.objects.filter(id=staff_id, vendor_name=request.user, vendor_branch_id=branch_name)
            if not staff.exists():
                return Response({
                    'success': False,
                    'status_code': status.HTTP_404_NOT_FOUND,
                    'error': {
                        'code': 'Not Found',
                        'message': 'Staff with the provided ID does not exist in this branch.'
                    },
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            staff = VendorStaff.objects.filter(vendor_name=request.user, vendor_branch_id=branch_name)

        attendance_queryset = VendorStaffAttendance.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name,
            of_month=month,
            year=current_date.year,
            staff_id__in=staff
        )

        attendance_data = {}
        for record in attendance_queryset:
            sid = record.staff.id
            if sid not in attendance_data:
                attendance_data[sid] = {
                    "present_dates": [],
                    "in_time": [],
                    "out_time": [],
                    "leave_dates": [],
                    "number_of_days_present": 0,
                    "no_of_days_absent": 0,
                }

            if record.attend:
                attendance_data[sid]["present_dates"].append(record.date)
                attendance_data[sid]["in_time"].append(record.in_time)
                attendance_data[sid]["out_time"].append(record.out_time)
                attendance_data[sid]["number_of_days_present"] += 1
            if record.leave:
                attendance_data[sid]["leave_dates"].append(record.date)
                attendance_data[sid]["no_of_days_absent"] += 1

        
        all_staff_attendance = {}
        for staff_member in staff:
            sid = staff_member.id
            data = attendance_data.get(sid, {
                "present_dates": [],
                "in_time": [],
                "out_time": [],
                "leave_dates": [],
                "number_of_days_present": 0,
                "no_of_days_absent": 0,
            })
            all_staff_attendance[staff_member.mobile_no] = {
                "id": sid,
                "month": month,
                **data
            }

      
        staff_settings_obj = StaffSetting.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name,
            month=month,
        ).first()

        time_obj = StaffAttendanceTime.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name
        ).first()

        return Response({
            "status": True,
            "table_data": all_staff_attendance,
            "current_month_days": staff_settings_obj.number_of_working_days if staff_settings_obj else 0,
            "in_time": time_obj.in_time if time_obj else None,
            "out_time": time_obj.out_time if time_obj else None,
            "message": "Attendance records retrieved successfully."
        }, status=status.HTTP_200_OK)

    def put(self, request):
        
        id = request.query_params.get('staff_id')
        branch_name = request.query_params.get('branch_name')
        type = request.query_params.get('type')
       
        if not id or not branch_name:
            return Response({"status": False, "text": "ID and branch name are required."}, status=status.HTTP_400_BAD_REQUEST)
        if type == "admin":
            for i in request.data.get('json_data'):
                try:
                    instance = VendorStaffAttendance.objects.get(staff_id=id, date=i.get('date'))
                    instance.in_time = i.get('in_time')
                    instance.out_time = i.get('out_time')
                    instance.attend = i.get('attend')
                    instance.leave = i.get('leave')
                    instance.of_month = i.get('of_month')
                    instance.year = i.get('year')
                    instance.save()
                except VendorStaffAttendance.DoesNotExist:
         
                    instance = VendorStaffAttendance(
                        staff_id=id,
                        vendor_name=request.user,
                        vendor_branch_id=request.query_params.get('branch_name'),
                        date=i.get('date'),  
                        in_time=i.get('in_time'),
                        out_time=i.get('out_time'),
                        attend=i.get('attend'),
                        leave=i.get('leave'),
                        of_month=i.get('of_month'),
                        year=i.get('year'),
                    )
                    instance.save()
                except Exception as e:
                    return Response({"status": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
            
            
            
            return Response({"status": True})
        else:
    
            try:
                instance = VendorStaffAttendance.objects.get(staff_id=id,date=dt.date.today())
            except ObjectDoesNotExist:
                return Response({"status": False, "text": "Attendance not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = staff_attendance_serializer(instance, data=request.data, context={'request': request, 'branch_id': branch_name})
        if serializer.is_valid():
            serializer.save()
            out_time = request.data.get('json_data')[0].get('out_time')
            prefered_out_time = StaffAttendanceTime.objects.get(vendor_name=request.user,vendor_branch_id=branch_name)
            # calculation remaining. 
            return Response({"status": True, "out_time":request.data.get('json_data')[0].get('out_time'),"late_time":"" }, status=status.HTTP_200_OK)
        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pass


# class salary_disburse(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = staff_salary_serializer

#     def __init__(self, **kwargs):
#         self.cache_key = None

#     def get(self, request):
#         id = request.query_params.get('id')
#         staff_attendance = VendorStaffAttendance.objects.filter(staff_id=id, of_month=dt.date.today().month)
#         staff_setting = StaffSetting.objects.select_related('vendor_name').get(vendor_name=request.user, month=dt.date.today().month)
#         staff_slab = StaffSettingSlab.objects.select_related('vendor_name').filter(vendor_name=request.user).values_list('staff_target_business', 'staff_slab').order_by('-staff_target_business')

#         def calculate_commission(business_amount, slabs):
#             commission = 0
#             for threshold, percentage in slabs:
#                 if business_amount > int(threshold):
#                     extra_amount = int(business_amount) - int(threshold)
#                     commission += (extra_amount * float(percentage)) / 100
#             return commission

#         commission = calculate_commission(int(staff_attendance[0].staff.business_of_the_current_month), staff_slab)
#         staff_salary = StaffSalary()

#         staff_salary.of_month = dt.date.today().month
#         staff_salary.salary_payble_amount = (int(staff_attendance[0].staff.staff_salary_monthly) / staff_setting.number_of_working_days) * int(staff_attendance.count())
#         staff_salary.salary_payble_amount = staff_salary.salary_payble_amount + commission
#         staff_salary.staff_id = id
#         staff_salary.year = dt.date.today().year
#         staff_salary.save()

#         serializer = staff_salary_serializer(staff_salary)

#         if commission == 0:
#             commission = int(staff_salary.salary_payble_amount)

#         return Response({
#             "status": True,
#             "id": id,
#             "net_payble_amount": int(staff_salary.salary_payble_amount),
#             "no_of_working_days": staff_attendance.count(),
#             "earning": commission,
#             "message": "staff salary records retrieved successfully."
#         }, status=status.HTTP_200_OK)


from datetime import datetime

class salary_disburse(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = staff_salary_serializer

    def get(self, request):
        id = request.query_params.get('id')
        branch_name = request.query_params.get('branch_name')
        if not id:
            return Response({"status": False, "message": "Staff ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        today = dt.date.today()
        month = today.month
        year = today.year

        staff_attendance = VendorStaffAttendance.objects.filter(staff_id=id, of_month=month)
        if not staff_attendance.exists():
            return Response({"status": False, "message": "No attendance found for this staff."}, status=status.HTTP_404_NOT_FOUND)

        staff_setting = StaffSetting.objects.get(vendor_name=request.user, month=month)
        staff_slab = StaffSettingSlab.objects.filter(vendor_name=request.user,vendor_branch_id=branch_name).values_list('staff_target_business', 'staff_slab').order_by('-staff_target_business')
        working_days = staff_attendance.count()

       
        business_amount = int(staff_attendance[0].staff.business_of_the_current_month)
        def calculate_commission(business_amount, slabs):
            commission = 0
            for threshold, percentage in slabs:
                if business_amount > int(threshold):
                    extra_amount = business_amount - int(threshold)
                    commission += (extra_amount * float(percentage)) / 100
            return commission

        commission = calculate_commission(business_amount, staff_slab)

   
        try:
            attendance_time = StaffAttendanceTime.objects.get(vendor_name=request.user, vendor_branch_id=branch_name)
            required_in_time = datetime.strptime(attendance_time.in_time, "%H:%M")
        except StaffAttendanceTime.DoesNotExist:
            return Response({"status": False, "message": "Attendance time not set for this branch."}, status=status.HTTP_400_BAD_REQUEST)

        working_hours_per_day = (datetime.strptime(attendance_time.out_time, "%H:%M") - required_in_time).seconds / 3600
        total_required_minutes = int(working_hours_per_day * working_days * 60)

        
        late_minutes_total = 0
        for entry in staff_attendance:
            try:
                if entry.in_time:
                    actual_in = datetime.strptime(entry.in_time, "%H:%M")
                    late_diff = (actual_in - required_in_time).total_seconds() / 60
                    if late_diff > 0:
                        late_minutes_total += int(late_diff)
            except Exception:
                pass  
     
        base_salary = int(staff_attendance[0].staff.staff_salary_monthly)
        salary_per_minute = base_salary / total_required_minutes
        late_fine = late_minutes_total * salary_per_minute
        payable_salary = ((base_salary / staff_setting.number_of_working_days) * working_days) + commission - late_fine

        
        staff_salary = StaffSalary.objects.create(
            of_month=month,
            year=year,
            staff_id=id,
            salary_payble_amount=payable_salary
        )

        serializer = staff_salary_serializer(staff_salary)
       
        advance_paid = StaffAdvanceModel.objects.filter(staff_id=id,created_at__month=month)
        days = []
        total = 0
        if len(advance_paid) == 1:
            if int(payable_salary) > int(advance_paid[0].advance_amount):
                payable_salary -= int(advance_paid[0].advance_amount)
            else:
                payable_salary = int(advance_paid[0].advance_amount) - payable_salary
            total = int(advance_paid[0].advance_amount)
            days.append(advance_paid[0].created_at)
        if len(advance_paid) > 1:
         
            for i in advance_paid:
                total += int(i.advance_amount)
                days.append(i.created_at)
            if payable_salary > total:
                payable_salary -= total
            else:
                payble_salary = total - payable_salary
                
            
            
        return Response({
            "status": True,
            "id": id,
            "advance_taken":total,
            "date_of_advance":days,
            "net_payble_amount": round(payable_salary, 2),
            "no_of_working_days": working_days,
            "total_required_minutes": total_required_minutes,
            "late_minutes": late_minutes_total,
            "salary_per_minute": round(salary_per_minute, 2),
            "late_fine": round(late_fine, 2),
            "commission": round(commission, 2),
            "message": "Staff salary calculated successfully."
        }, status=status.HTTP_200_OK)


class Sales_Per_Customer(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        week = request.query_params.get('week')
        branch_name = request.query_params.get('branch_name')
        billing_data_weekly_customer = VendorInvoice.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name,
            date__year=year,
            date__month=month,
            date__week=week
        ).values('customer_name').annotate(weekly_total=Sum('grand_total')).order_by('customer_name')

        return Response({
            "data": billing_data_weekly_customer,
        })


class Sales_Per_Customer_monthly(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        branch_name = request.query_params.get('branch_name')

        billing_data_monthly_customer = VendorInvoice.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name,
            date__year=year,
            date__month=month,
        ).values('customer_name').annotate(weekly_total=Sum('grand_total')).order_by('customer_name')

        return Response({
            "data": billing_data_monthly_customer,
        })


class Sales_in_a_month(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models.functions import ExtractWeek

        month = request.query_params.get('month')
        year = request.query_params.get('year')
        branch_name = request.query_params.get('branch_name')
        billing_data_weekly_month = VendorInvoice.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name,
            date__month=month,
            date__year=year
        ).annotate(
            week_number=ExtractWeek('date')
        ).values(
            'week_number'
        ).annotate(
            weekly_total=Sum('grand_total')
        ).order_by('week_number')

        weekly_totals = [
            {"week": f"Week {item['week_number']}", "weekly_total": item['weekly_total']}
            for item in billing_data_weekly_month
        ]

        return Response({
            "data2": weekly_totals,
        })


class Sales_in_a_year(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models.functions import ExtractMonth
        year = request.query_params.get('year')
        branch_name = request.query_params.get('branch_name')
        billing_data_monthly_year = VendorInvoice.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name,
            date__year=year
        ).annotate(
            month_number=ExtractMonth('date')
        ).values(
            'month_number'
        ).annotate(
            monthly_total=Sum('grand_total')
        ).order_by('month_number')

        monthly_totals = [
            {"month": f"Month {item['month_number']}", "monthly_total": item['monthly_total']}
            for item in billing_data_monthly_year
        ]

        return Response({
            "data": monthly_totals,
        })


class Sales_in_a_week(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        today = date.today()
        current_week = today.isocalendar()[1]
        if request.query_params.get('start_date') and request.query_params.get('end_date'):
              sales_by_day = VendorInvoice.objects.filter(
                    vendor_name=request.user,
                    vendor_branch_id=branch_name,
                    date__range = [request.query_params.get('start_date'),request.query_params.get('end_date')]
              ).annotate(
                    day_of_week=ExtractWeekDay('date')
              ).values(
                    'day_of_week'
              ).annotate(
                    total_sales=Sum('grand_total')
              ).order_by('day_of_week')
        else:
            
            sales_by_day = VendorInvoice.objects.filter(
                vendor_name=request.user,
                vendor_branch_id=branch_name,
                date__week=current_week,
                date__lte=today
            ).annotate(
                day_of_week=ExtractWeekDay('date')
            ).values(
                'day_of_week'
            ).annotate(
                total_sales=Sum('grand_total')
            ).order_by('day_of_week')

        return Response({
            "data": sales_by_day,
        })


class Sales_in_a_day_by_customer(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        billing_data_monthly_year = VendorInvoice.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name,
            date=dt.date.today()
        ).values('customer_name').annotate(daily_total=Sum('grand_total'))

        return Response({
            "data": list(billing_data_monthly_year),
        })


class Sales_in_a_day_by_customer_time(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')

        billing_data_monthly_year = VendorInvoice.objects.filter(
            vendor_name=request.user,
            date=dt.date.today(),
            timestamp__range=(start_time, end_time)
        )

        billing_data_monthly_year_time = billing_serializer_get(billing_data_monthly_year, many=True)
        return Response({
            "data": billing_data_monthly_year_time.data,
        })


class service_analysis(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        selected_week = int(request.query_params.get('week', 0))
        selected_year = int(request.query_params.get('year', 0))
        selected_month = int(request.query_params.get('month', 0))
        branch_name = request.query_params.get('branch_name')

        start_of_year = datetime(selected_year, 1, 1)
        days_to_week_start = (selected_week - 1) * 7
        start_date = start_of_year + timedelta(days=days_to_week_start)
        end_date = start_date + timedelta(days=6)

        weekly_invoices = VendorInvoice.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name,
            date__range=(start_date, end_date),
        )

        total_amount = 0
        total_services_count = 0
        services_list = defaultdict(int)
        service_revenue = defaultdict(float)

        for invoice in weekly_invoices:
            services = json.loads(invoice.services) if isinstance(invoice.services, str) else invoice.services
            for service in services:
                if service['Description'] != 'None':
                    service_description = service['Description']
                    service_price = float(service['Price'])

                    total_amount += service_price
                    total_services_count += 1
                    services_list[service_description] += 1
                    service_revenue[service_description] += service_price

        weekly_average = total_amount / total_services_count if total_services_count > 0 else 0

        response_data = {
            "week": selected_week,
            "month": selected_month,
            "year": selected_year,
            "total_amount": total_amount,
            "average_per_service": weekly_average,
            "services_list": {
                service: {
                    "occurrences": count,
                    "revenue": service_revenue[service]
                }
                for service, count in services_list.items()
            },
        }
        return Response({"data": response_data})


class top5_header_staff_revenue(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.utils.timezone import now
        from django.db.models import Sum
        branch_name = request.query_params.get('branch_name')

        current_date = now().date()
        invoices_today_count = VendorInvoice.objects.filter(
            date=current_date,
            vendor_name=request.user,
            vendor_branch_id=branch_name
        ).count()
        appointmet_today_count = VendorAppointment.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name,
            date=current_date
        ).count()

        revenue_today = VendorInvoice.objects.filter(
            vendor_name=request.user,
            date=current_date,
            vendor_branch_id=branch_name
        ).aggregate(
            total_revenue=Sum('grand_total')
        )['total_revenue'] or 0

        today = dt.date.today()
        current_date = dt.date.today()
        current_week = today.isocalendar()[1]
        current_month = today.month
        current_year = today.year

        grouped_data = defaultdict(lambda: {
            "staff_data": defaultdict(lambda: {
                "total_invoices": 0,
                "total_sales": 0,
                "services": defaultdict(lambda: {"total_sales": 0, "total_services": 0})
            })
        })

        time_key = ""
        if request.query_params.get('filter') == 'day':
            invoices = VendorInvoice.objects.filter(
                vendor_name=request.user,
                vendor_branch_id=request.query_params.get('branch_name'),
                date=current_date
            )
            time_key = current_date.strftime("%A")
        elif request.query_params.get('filter') == 'week':
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            invoices = VendorInvoice.objects.filter(
                vendor_name=request.user,
                vendor_branch_id=request.query_params.get('branch_name'),
                date__range=(start_of_week, end_of_week)
            )
            time_key = f"Week {current_week}"
        elif request.query_params.get('filter') == 'month':
            invoices = VendorInvoice.objects.filter(
                vendor_name=request.user,
                vendor_branch_id=request.query_params.get('branch_name'),
                date__month=current_month,
                date__year=current_year
            )
            time_key = f"Month {today.strftime('%B')}"
        elif request.query_params.get('filter') == 'year':
            invoices = VendorInvoice.objects.filter(
                vendor_name=request.user,
                vendor_branch_id=request.query_params.get('branch_name'),
                date__year=current_year
            )
            time_key = f"Year {current_year}"
        else:
            return Response({"error": "Invalid filter. Use 'day', 'week', 'month', or 'year'."}, status=400)

        for invoice in invoices:
            services = json.loads(invoice.services) if isinstance(invoice.services, str) else invoice.services
            for service in services:
                staff_name = service.get('Staff')
                service_name = service.get('Description')
                price = float(service.get('Price', 0))

                if staff_name and service_name:
                    staff_data = grouped_data[time_key]["staff_data"][staff_name]
                    staff_data["total_invoices"] += 1
                    staff_data["total_sales"] += price
                    staff_data["services"][service_name]["total_sales"] += price
                    staff_data["services"][service_name]["total_services"] += 1

        response_datas = [
            {
                "time_key": time_key,
                "staff_data": [
                    {
                        "staff_name": staff_name,
                        "total_invoices": staff_data["total_invoices"],
                        "total_sales": staff_data["total_sales"],
                        "services": [
                            {
                                "service_name": service_name,
                                "total_sales": service_data["total_sales"],
                                "total_services": service_data["total_services"]
                            }
                            for service_name, service_data in staff_data["services"].items()
                        ]
                    }
                    for staff_name, staff_data in time_data["staff_data"].items()
                ]
            }
            for time_key, time_data in grouped_data.items()
        ]

        bills_by_month_and_payment = VendorInvoice.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name
        ).annotate(
            month_is=TruncMonth('date')
        ).values(
            'month_is', 'mode_of_payment'
        ).annotate(
            total_revenue=Sum('grand_total')
        ).order_by('month_is', '-total_revenue')

        monthly_data = defaultdict(list)
        for item in bills_by_month_and_payment:
            month_name = item['month_is'].strftime('%m')
            monthly_data[month_name].append({
                "payment_mode": item['mode_of_payment'],
                "total_revenue": item['total_revenue'],
            })

        response_data = [
            {"month": month, "payment_modes": payment_modes}
            for month, payment_modes in monthly_data.items()
        ]

        previous_day = now().date() - timedelta(days=1)
        previous_day_revenue = VendorInvoice.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name,
            date=previous_day
        ).aggregate(
            total_revenue=Sum('grand_total')
        )['total_revenue'] or 0

        return Response({
            "staff_data": response_datas,
            "today_no_of_invoices": invoices_today_count,
            "today_revenue": revenue_today,
            "previous_day_rev": previous_day_revenue,
            "mode_of_payment": response_data,
            "today_no_of_app": appointmet_today_count,
        })
class GetCustomerBillAppDetails_copy(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mobile_no = request.query_params.get('mobile_no')
        branch_name = request.query_params.get('branch_name')

        if not mobile_no:
            return Response({
                "status": False,
                "message": "Mobile number is required."
            }, status=400)
        if not branch_name:
            return Response({
                "status": False,
                "message": "Branch_name is required."
            }, status=400)

        appointments_all = VendorAppointment.objects.filter(mobile_no=mobile_no, vendor_name=request.user, vendor_branch_id=branch_name)
        invoice_all = VendorInvoice.objects.filter(
            mobile_no=mobile_no, vendor_name=request.user, vendor_branch_id=branch_name
        )


        # if invoice_all.exists():
        #     customer_name = invoice_all[0].customer_name
        #     customer_email = invoice_all[0].email
        #     try:
        #         customer_dob = invoice_all[0].vendor_customers_profile.d_o_b
        #         customer_doa = invoice_all[0].vendor_customers_profile.d_o_a
        #     except Exception:
        #         customer_dob = ""
        #         customer_doa = ""
        # else:
        #     return Response({
        #         "status": False,
        #         "message": "No invoices found for this customer."
        #     }, status=404)

        count_1 = appointments_all.count()
        count_2 = invoice_all.count()
        total_billing_amount = invoice_all.aggregate(total=Sum('grand_total'))['total']

        # appointment_data = appointment_serializer(appointments_all, many=True).data
        # invoice_data = billing_serializer_get(invoice_all, many=True).data
        data_object = VendorCustomers.objects.filter(user=request.user, vendor_branch_id=branch_name, mobile_no=mobile_no)
        serializer_obj = VendorCustomerLoyalityProfileSerializer_get(data_object, many=True)

        
        return Response({
            "status": True,
            "total_appointment": count_1,
            "total_invoices": count_2,
            # "previous_appointments": appointment_data,
            # "previous_invoices": invoice_data,
            "data": serializer_obj.data,
            # "customer_name": customer_name,
            # "customer_mobile_no": mobile_no,
            # "customer_email": customer_email,
            # "customer_dob": customer_dob,
            # "customer_doa": customer_doa,
            "total_billing_amount": total_billing_amount,})

class GetCustomerBillAppDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mobile_no = request.query_params.get('mobile_no')
        branch_name = request.query_params.get('branch_name')
        

        if not mobile_no:
            return Response({
                "status": False,
                "message": "Mobile number is required."
            }, status=400)
        if not branch_name:
            return Response({
                "status": False,
                "message": "Branch_name is required."
            }, status=400)

       
        appointments_all = VendorAppointment.objects.filter(mobile_no=mobile_no, vendor_name=request.user, vendor_branch_id=branch_name)
        
        
        invoice_all = VendorInvoice.objects.filter(
            mobile_no=mobile_no, vendor_name=request.user, vendor_branch_id=branch_name
        )
        if invoice_all.exists():
            customer_name = invoice_all[0].customer_name
            customer_email = invoice_all[0].email
            try:
                customer_dob = invoice_all[0].vendor_customers_profile.d_o_b
                customer_doa = invoice_all[0].vendor_customers_profile.d_o_a
            except Exception:
                customer_dob = ""
                customer_doa = ""
        else:
            return Response({
                "status": False,
                "message": "No invoices found for this customer."
            }, status=404)

        count_1 = appointments_all.count()
        count_2 = invoice_all.count()
        total_billing_amount = invoice_all.aggregate(total=Sum('grand_total'))['total']

        appointment_data = appointment_serializer(appointments_all, many=True).data
        invoice_data = billing_serializer_get(invoice_all, many=True).data
        

     
        return Response({
            "status": True,
            "total_appointment": count_1,
            "total_invoices": count_2,
            "previous_appointments": appointment_data,
            "previous_invoices": invoice_data,
            # "customer_data": serializer_obj.data
            "customer_name": customer_name,
            "customer_mobile_no": mobile_no,
            "customer_email": customer_email,
            "customer_dob": customer_dob,
            "customer_doa": customer_doa,
            "total_billing_amount": total_billing_amount,
        })

class GetCustomerBillAppDetails_copy_details(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mobile_no = request.query_params.get('mobile_no')
        branch_name = request.query_params.get('branch_name')
        type = request.query_params.get('type')
       

        if not mobile_no:
            return Response({
                "status": False,
                "message": "Mobile number is required."
            }, status=400)
        if not branch_name:
            return Response({
                "status": False,
                "message": "Branch_name is required."
            }, status=400)

        if type == "appointment":
           
            appointments_all = VendorAppointment.objects.filter(mobile_no=mobile_no, vendor_name=request.user, vendor_branch_id=branch_name)
           
            appointment_data = appointment_serializer(appointments_all, many=True).data
            return Response({
                "status": True,
                
                "previous_appointments": appointment_data,
            })

           
        if type == "invoice":
            
            invoice_all = VendorInvoice.objects.filter(
                mobile_no=mobile_no, vendor_name=request.user, vendor_branch_id=branch_name
            )
            
       
            invoice_data = billing_serializer_get(invoice_all, many=True).data
                
    
            return Response({
                        "status": True,
                        "previous_invoices": invoice_data,
                        
             })
            
            
           


class abc_123(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        pass


class expense_category(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VendorExpenseCategorySerializer

    def __init__(self, **kwargs):
        self.cache_key = None
        super().__init__(**kwargs)

    @transaction.atomic
    def post(self, request):
        branch_name = request.query_params.get('branch_name')

        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name,})

        serializer.create(validated_data=request.data)
        return Response({
            "status": True,
            "message": "Vendor Expense category Added Succesfully"
        }, status=status.HTTP_201_CREATED)

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        data = VendorExpenseCategory.objects.filter(user=request.user,)
        serializer = self.serializer_class(data, many=True)

        return Response({
            "status": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class expense_management(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VendorExpenseSerializer

    def __init__(self, **kwargs):
        self.cache_key = None
        super().__init__(**kwargs)

    @transaction.atomic
    def post(self, request):
        branch_name = request.query_params.get('branch_name')

        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name,})

        serializer.create(validated_data=request.data)
        return Response({
            "status": True,
            "message": "Vendor Expense Added Succesfully"
        }, status=status.HTTP_201_CREATED)

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        data = VendorExpense.objects.filter(user=request.user, vendor_branch_id=branch_name)
        serializer = VendorExpenseSerializer_get(data, many=True)

        return Response({
            "status": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request):
        pass

    def delete(self, request):
        pass




class busniess_headers(APIView):
    def get(self, request):
        today = date.today()
        branch_name = request.query_params.get('branch_name')

        monthly_earning = VendorInvoice.objects.filter(vendor_name=request.user, vendor_branch_id=branch_name, date__month=today.month).aggregate(
            total_revenue=Sum('grand_total')
        )['total_revenue'] or 0
        monthly_expense = VendorExpense.objects.filter(user=request.user, vendor_branch_id=branch_name, date__month=today.month).aggregate(
            total_expense=Sum('expense_amount')
        )['total_expense'] or 0
        daily_expense = VendorExpense.objects.filter(user=request.user, vendor_branch_id=branch_name, date=today).aggregate(
            total_expense=Sum('expense_amount')
        )['total_expense'] or 0

        daily_earning = VendorInvoice.objects.filter(vendor_name=request.user, vendor_branch_id=branch_name, date=today).aggregate(
            total_revenue=Sum('grand_total')
        )['total_revenue'] or 0

        sales_by_staff = VendorInvoice.objects.filter(vendor_name=request.user, vendor_branch_id=branch_name, date=today).values('service_by').annotate(
            total_sales=Sum('grand_total'),
            service_count=Count('id')
        )

        billing_by_customer = VendorInvoice.objects.filter(vendor_name=request.user, vendor_branch_id=branch_name, date=today).values('customer_name').annotate(
            total_billing=Sum('grand_total')
        )

        monthly_revenue = monthly_earning - monthly_expense
        daily_revenue = daily_earning - daily_expense
        analysis = {
            'monthly_revenue': monthly_revenue,
            'daily_revenue': daily_revenue,
            'daily_expense': daily_expense,
            'monthly_expense': monthly_expense,
            'monthly_earning': monthly_earning,
            'daily_earning': daily_earning,
            'sales_by_staff': list(sales_by_staff),
            'billing_by_customer': list(billing_by_customer),
        }

        return Response({
            "status": True,
            "analysis": analysis
        })


class ProductAnalysis(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        branch_name = request.query_params.get('branch_name')

        daily_invoices = VendorInvoice.objects.filter(vendor_name=request.user, vendor_branch_id=branch_name, date=today).values_list('json_data', flat=True)
        monthly_invoices = VendorInvoice.objects.filter(vendor_name=request.user, vendor_branch_id=branch_name, date__month=today.month).values_list('json_data', flat=True)

        def aggregate_products(invoices):
            from collections import defaultdict
            product_summary = defaultdict(lambda: {"total_quantity": 0, "unit": None})
            for invoice in invoices:
                if invoice:
                    for product in invoice:
                        p = VendorInventoryProduct.objects.filter(user=request.user, vendor_branch_id=branch_name)
                        description = ""
                        for i in p:
                            if str(i.id) == product.get('id'):
                                description = i.product_name
                            else:
                                pass
                        quantity = product.get("quantity", 0)
                        unit = product.get("unit", "")

                        if description:
                            product_summary[description]["total_quantity"] += int(quantity)
                            product_summary[description]["unit"] = unit
            return product_summary

        daily_products = aggregate_products(daily_invoices)
        monthly_products = aggregate_products(monthly_invoices)

        analysis = {
            "daily_product_analysis": dict(daily_products),
            "monthly_product_analysis": dict(monthly_products),
        }

        return Response(analysis)


class service_category(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VendorServiceCategorySerializer

    def __init__(self, **kwargs):
        self.cache_key = None
        super().__init__(**kwargs)

    @transaction.atomic
    def post(self, request):
        branch_name = request.query_params.get('branch_name')

        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name,})

        serializer.create(validated_data=request.data)
        return Response({
            "status": True,
            "message": "Vendor Service category Added Succesfully"
        }, status=status.HTTP_201_CREATED)

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        data = VendorServiceCategory.objects.filter(user=request.user,)
        serializer = self.serializer_class(data, many=True)

        return Response({
            "status": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request):
        id = request.query_params.get('id')
        branch_name = request.query_params.get('branch_name')

        service_obj = VendorServiceCategory.objects.filter(user=request.user, vendor_branch_id=branch_name, service_category=request.data.get('category')).exclude(id=id)
        if service_obj.exists():
            return Response({
                'success': False,
                'status_code': status.HTTP_200_OK,
                'error': {
                    'code': 'The request was successful',
                    'message': 'Service with the same name already exists on this branch!'
                },
                'data': None
            }, status=status.HTTP_200_OK)

        try:
            service_instance = VendorServiceCategory.objects.get(id=id, user=request.user, vendor_branch_id=branch_name)
        except VendorService.DoesNotExist:
            return Response({
                'success': False,
                'status_code': status.HTTP_404_NOT_FOUND,
                'error': {
                    'code': 'Not Found',
                    'message': 'Service not found!'
                },
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(instance=service_instance, data=request.data, context={'request': request, 'branch_id': branch_name})

        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'status_code': status.HTTP_200_OK,
                'error': {
                    'code': 'The request was successful',
                    'message': 'Service updated on this branch!'
                },
                'data': None
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'status_code': status.HTTP_400_BAD_REQUEST,
            'error': {
                'code': 'Validation Error',
                'message': 'Serializer data is invalid!'
            },
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        id = request.query_params.get('id')

        if not id:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'ID parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            queryset = VendorServiceCategory.objects.get(id=id, user=request.user)
            queryset.delete()

            return Response({
                'success': True,
                'status_code': status.HTTP_200_OK,
                'error': {
                    'code': 'The request was successful',
                    'message': 'Service deleted successfully!'
                },
                'data': None
            }, status=status.HTTP_200_OK)

        except VendorService.DoesNotExist:
            return Response({
                'success': False,
                'status_code': status.HTTP_404_NOT_FOUND,
                'error': {
                    'code': 'Not Found',
                    'message': 'Service not found!'
                },
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

class product_category(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VendorProductCategorySerializer

    def __init__(self, **kwargs):
        self.cache_key = None
        super().__init__(**kwargs)

    @transaction.atomic
    def post(self, request):
        branch_name = request.query_params.get('branch_name')

        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name,})

        serializer.create(validated_data=request.data)
        return Response({
            "status": True,
            "message": "Vendor Product category Added Succesfully"
        }, status=status.HTTP_201_CREATED)

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        data = VendorProductCategory.objects.filter(user=request.user,)
        serializer = self.serializer_class(data, many=True)

        return Response({
            "status": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request):
        id = request.query_params.get('id')
        branch_name = request.query_params.get('branch_name')

        service_obj = VendorProductCategory.objects.filter(user=request.user, vendor_branch_id=branch_name, service_category=request.data.get('category')).exclude(id=id)
        if service_obj.exists():
            return Response({
                'success': False,
                'status_code': status.HTTP_200_OK,
                'error': {
                    'code': 'The request was successful',
                    'message': 'Service with the same name already exists on this branch!'
                },
                'data': None
            }, status=status.HTTP_200_OK)

        try:
            service_instance = VendorProductCategory.objects.get(id=id, user=request.user, vendor_branch_id=branch_name)
        except VendorProductCategory.DoesNotExist:
            return Response({
                'success': False,
                'status_code': status.HTTP_404_NOT_FOUND,
                'error': {
                    'code': 'Not Found',
                    'message': 'product not found!'
                },
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(instance=service_instance, data=request.data, context={'request': request, 'branch_id': branch_name})

        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'status_code': status.HTTP_200_OK,
                'error': {
                    'code': 'The request was successful',
                    'message': 'Service updated on this branch!'
                },
                'data': None
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'status_code': status.HTTP_400_BAD_REQUEST,
            'error': {
                'code': 'Validation Error',
                'message': 'Serializer data is invalid!'
            },
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        id = request.query_params.get('id')

        if not id:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'ID parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            queryset = VendorProductCategory.objects.get(id=id, user=request.user)
            queryset.delete()

            return Response({
                'success': True,
                'status_code': status.HTTP_200_OK,
                'error': {
                    'code': 'The request was successful',
                    'message': 'Product Category deleted successfully!'
                },
                'data': None
            }, status=status.HTTP_200_OK)

        except VendorProductCategory.DoesNotExist:
            return Response({
                'success': False,
                'status_code': status.HTTP_404_NOT_FOUND,
                'error': {
                    'code': 'Not Found',
                    'message': 'Service not found!'
                },
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)



class Table_servicess(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        branch_name = request.query_params.get('branch_name')

        services_data = VendorService.objects.filter(user=request.user).select_related('category').values(
            'category__id', 'category__service_category',
            'id', 'service', 'service_price', 'service_duration',
            'for_men', 'for_women', 'vendor_branch__id', 'vendor_branch__branch_name'
        ).order_by('category__id')

        grouped_data = defaultdict(list)
        for service in services_data:
            category_id = service['category__id']
            category_name = service['category__service_category']
            grouped_data[category_name].append({
                "id": service['id'],
                "service": service['service'],
                "price": service['service_price'],
                "duration": service['service_duration'],
                "for_men": service['for_men'],
                "for_women": service['for_women'],
                "branch": {
                    "id": service['vendor_branch__id'],
                    "name": service['vendor_branch__branch_name'],
                },
            })

        response_data = [
            {"category": category, "services": services}
            for category, services in grouped_data.items()
        ]
        return Response({
            "data": response_data
        })


class CouponView(APIView):

    serializer_class = CouponSerializer

    def __init__(self, **kwargs):
        self.cache_key = None
        super().__init__(**kwargs)

    @transaction.atomic
    def post(self, request):
        branch_name = request.query_params.get('branch_name')

        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name})

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "Coupon added successfully."
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": False,
            "errors": serializer.errors,
            "message": "Failed to add coupon."
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        data = VendorCoupon.objects.filter(user=request.user, vendor_branch_id=branch_name)
        serializer = self.serializer_class(data, many=True)

        return Response({
            "status": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)



    def put(self, request):
        id = request.query_params.get('id')
        branch_name = request.query_params.get('branch_name')

        service_obj = VendorCoupon.filter(user=request.user, vendor_branch_id=branch_name, coupon_name=request.data.get('coupon_name')).exclude(id=id)
        if service_obj.exists():
            return Response({
                'success': False,
                'status_code': status.HTTP_200_OK,
                'error': {
                    'code': 'The request was successful',
                    'message': 'Service with the same name already exists on this branch!'
                },
                'data': None
            }, status=status.HTTP_200_OK)

        try:
            service_instance = VendorCoupon.objects.get(id=id, user=request.user, vendor_branch_id=branch_name)
        except VendorService.DoesNotExist:
            return Response({
                'success': False,
                'status_code': status.HTTP_404_NOT_FOUND,
                'error': {
                    'code': 'Not Found',
                    'message': 'Couopon not found!'
                },
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(instance=service_instance, data=request.data, context={'request': request, 'branch_id': branch_name})

        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'status_code': status.HTTP_200_OK,
                'error': {
                    'code': 'The request was successful',
                    'message': 'Coupon updated on this branch!'
                },
                'data': None
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'status_code': status.HTTP_400_BAD_REQUEST,
            'error': {
                'code': 'Validation Error',
                'message': 'Serializer data is invalid!'
            },
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        id = request.query_params.get('id')

        if not id:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'ID parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            queryset = VendorCoupon.objects.get(id=id, user=request.user)
            queryset.delete()

            return Response({
                'success': True,
                'status_code': status.HTTP_200_OK,
                'error': {
                    'code': 'The request was successful',
                    'message': 'Coupon deleted successfully!'
                },
                'data': None
            }, status=status.HTTP_200_OK)

        except VendorCoupon.DoesNotExist:
            return Response({
                'success': False,
                'status_code': status.HTTP_404_NOT_FOUND,
                'error': {
                    'code': 'Not Found',
                    'message': 'Coupon not found!'
                },
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)




# class LoyalityTemplate(APIView):

#     serializer_class = TemplateSerializer
#     def get(self, request):
#         branch_name = request.query_params.get('branch_name')
#         if not branch_name:
#             return Response({
#                 'success': False,
#                 'status_code': status.HTTP_400_BAD_REQUEST,
#                 'error': {
#                     'code': 'Bad Request',
#                     'message': 'branch_name parameter is missing!'
#                 },
#                 'data': None
#             }, status=status.HTTP_400_BAD_REQUEST)

#         data = VendorLoyalityTemplates.objects.filter(user=request.user, vendor_branch_id=branch_name)
#         serializer = self.serializer_class(data, many=True)

#         return Response({
#             "status": True,
#             "data": serializer.data
#         }, status=status.HTTP_200_OK)


#     @transaction.atomic
#     def post(self, request):
#         branch_name = request.query_params.get('branch_name')

#         if not branch_name:
#             return Response({
#                 'success': False,
#                 'status_code': status.HTTP_400_BAD_REQUEST,
#                 'error': {
#                     'code': 'Bad Request',
#                     'message': 'branch_name parameter is missing!'
#                 },
#                 'data': None
#             }, status=status.HTTP_400_BAD_REQUEST)

#         serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name})

#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 "status": True,
#                 "message": "Message Recieved successfully."
#             }, status=status.HTTP_201_CREATED)

#         return Response({
#             "status": False,
#             "errors": serializer.errors,
#             "message": "Failed to send messages."
#         }, status=status.HTTP_400_BAD_REQUEST)

class DailyAppointmentsView(APIView):
   
    def get(self, request):
        today = now().date()
        appointments = VendorAppointment.objects.filter(vendor_name=request.user,vendor_branch_id=request.query_params.get('branch_name'),date=today).order_by('booking_time')
        serializer = app_serailizer_get(appointments, many=True)
        return Response(serializer.data)

class WeeklyAppointmentsView(APIView):
  
    def get(self, request):
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        appointments = VendorAppointment.objects.filter(vendor_name=request.user,vendor_branch_id=request.query_params.get('branch_name'),
            date__range=[start_of_week,end_of_week]
        ).order_by('date', 'booking_time')

        serializer = app_serailizer_get(appointments, many=True)
        return Response(serializer.data)

class PreviousWeekAppointmentsView(APIView):
    
    def get(self, request):
        
        today = now().date()
        start_of_previous_week = today - timedelta(days=today.weekday() + 7)
        end_of_previous_week = start_of_previous_week + timedelta(days=6)

        appointments = VendorAppointment.objects.filter(vendor_name=request.user,vendor_branch_id=request.query_params.get('branch_name'),
            date__range=[start_of_previous_week, end_of_previous_week]
        ).order_by('date', 'booking_time')

        serializer = app_serailizer_get(appointments, many=True)
        return Response(serializer.data)


class AppointmentsBystaffView(APIView):
    def get(self,request):
        today = now().date()
        start_of_previous_week = today - timedelta(days=today.weekday() + 7)
        end_of_previous_week = start_of_previous_week + timedelta(days=6)
        staff_name = request.query_params.get('staff_name')
        appointments_previous_week = VendorAppointment.objects.filter(vendor_name=request.user,vendor_branch_id=request.query_params.get('branch_name'),
            date__range=[start_of_previous_week, end_of_previous_week],service_by=staff_name
        ).order_by('date', 'booking_time')


        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        appointments_weekly = VendorAppointment.objects.filter(vendor_name=request.user,vendor_branch_id=request.query_params.get('branch_name'),
            date__range=[start_of_week, end_of_week],service_by=staff_name
        ).order_by('date', 'booking_time')


        today = now().date()
        appointments = VendorAppointment.objects.filter(vendor_name=request.user,vendor_branch_id=request.query_params.get('branch_name'),date=today,service_by=staff_name).order_by('booking_time')
        serializer1 = app_serailizer_get(appointments_previous_week, many=True)
        serializer2 = app_serailizer_get(appointments_weekly, many=True)
        serializer3 = app_serailizer_get(appointments, many=True)
        return Response(
            {"previous_week":serializer1.data,
            "current_week":serializer2.data,
            "daily":serializer3.data
            }
        )


class enquery(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VendorEnquerySerializer

    def __init__(self, **kwargs):
        self.cache_key = None
        super().__init__(**kwargs)

    @transaction.atomic
    def post(self, request):
        branch_name = request.query_params.get('branch_name')

        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name,})

        serializer.create(validated_data=request.data)
        return Response({
            "status": True,
            "message": "Vendor Enquery Added Succesfully"
        }, status=status.HTTP_201_CREATED)

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        data = VendorEnquery.objects.filter(user=request.user, vendor_branch_id=branch_name)
        serializer = VendorEnquerySerializer_get(data, many=True)

        return Response({
            "status": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request):
        id = request.query_params.get('id')
        branch_name = request.query_params.get('branch_name')

        

        try:
            service_instance = VendorEnquery.objects.get(id=id, user=request.user, vendor_branch_id=branch_name)
        except VendorEnquery.DoesNotExist:
            return Response({
                'success': False,
                'status_code': status.HTTP_404_NOT_FOUND,
                'error': {
                    'code': 'Not Found',
                    'message': 'Enquery not found!'
                },
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(instance=service_instance, data=request.data, context={'request': request, 'branch_id': branch_name})

        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'status_code': status.HTTP_200_OK,
                'error': {
                    'code': 'The request was successful',
                    'message': 'Enquery updated on this branch!'
                },
                'data': None
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'status_code': status.HTTP_400_BAD_REQUEST,
            'error': {
                'code': 'Validation Error',
                'message': 'Serializer data is invalid!'
            },
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        id = request.query_params.get('id')

        if not id:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'ID parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            queryset = VendorEnquery.objects.get(id=id, user=request.user)
            queryset.delete()

            return Response({
                'success': True,
                'status_code': status.HTTP_200_OK,
                'error': {
                    'code': 'The request was successful',
                    'message': 'Enquery deleted successfully!'
                },
                'data': None
            }, status=status.HTTP_200_OK)

        except VendorEnquery.DoesNotExist:
            return Response({
                'success': False,
                'status_code': status.HTTP_404_NOT_FOUND,
                'error': {
                    'code': 'Not Found',
                    'message': 'Enquery not found!'
                },
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        
        





class StaffRevenueAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        filter_type = request.query_params.get('filter')
        date_value = request.query_params.get('date')

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        month_value = request.query_params.get('month')
        year_value = request.query_params.get('year')
        
        invoices = VendorInvoice.objects.filter(vendor_name=request.user, vendor_branch_id=branch_name)
        
        if filter_type == 'day' and date_value:
            invoices = invoices.filter(date=date_value)
        elif filter_type == 'week':
            # today = dt.date.today()
            # current_date = dt.date.today()
            # current_week = today.isocalendar()[1]
            # current_month = today.month
            # current_year = today.year
            # start_of_week = today - timedelta(days=today.weekday())
            # end_of_week = start_of_week + timedelta(days=6)
            invoices = invoices.filter(date__range=[start_date,end_date])
        elif filter_type == 'month' and month_value and year_value:
            invoices = invoices.filter(date__month=month_value, date__year=year_value)
        elif filter_type == 'year' and year_value:
            invoices = invoices.filter(date__year=year_value)
        else:
            return Response({"error": "Invalid filter parameters."}, status=400)
        
        grouped_data = defaultdict(lambda: {
            "staff_data": defaultdict(lambda: {
                "total_invoices": 0,
                "total_sales": 0,
                "services": defaultdict(lambda: {"total_sales": 0, "total_services": 0})
            })
        })
        
        for invoice in invoices:
            services = json.loads(invoice.services) if isinstance(invoice.services, str) else invoice.services
            for service in services:
                staff_name = service.get('Staff')
                service_name = service.get('Description')
                price = float(service.get('Price', 0))
                
                if staff_name and service_name:
                    staff_data = grouped_data[filter_type]["staff_data"][staff_name]
                    staff_data["total_invoices"] += 1
                    staff_data["total_sales"] += price
                    staff_data["services"][service_name]["total_sales"] += price
                    staff_data["services"][service_name]["total_services"] += 1
                    
        response_data = [
            {
                "filter_type": filter_type,
                "staff_data": [
                    {
                        "staff_name": staff_name,
                        "total_invoices": staff_data["total_invoices"],
                        "total_sales": staff_data["total_sales"],
                        "services": [
                            {
                                "service_name": service_name,
                                "total_sales": service_data["total_sales"],
                                "total_services": service_data["total_services"]
                            }
                            for service_name, service_data in staff_data["services"].items()
                        ]
                    }
                    for staff_name, staff_data in grouped_data[filter_type]["staff_data"].items()
                ]
            }
        ]
        
        return Response(response_data)

# class ModeOfPaymentAPI(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         branch_name = request.query_params.get('branch_name')
#         filter_type = request.query_params.get('filter')
#         date_value = request.query_params.get('date')
#         start_date = request.query_params.get('start_date')
#         end_date = request.query_params.get('end_date')
#         month_value = request.query_params.get('month')
#         year_value = request.query_params.get('year')
        
#         invoices = VendorInvoice.objects.filter(vendor_name=request.user, vendor_branch_id=branch_name)
        
#         if filter_type == 'day' and date_value:
#             invoices = invoices.filter(date=date_value)
#         elif filter_type == 'week':
#             # today = dt.date.today()
#             # current_date = dt.date.today()
#             # current_week = today.isocalendar()[1]
#             # current_month = today.month
#             # current_year = today.year
#             # start_of_week = today - timedelta(days=today.weekday())
#             # end_of_week = start_of_week + timedelta(days=6)
#             invoices = invoices.filter(date__range=[start_date,end_date])
           
#         elif filter_type == 'month' and month_value and year_value:
#             invoices = invoices.filter(date__month=month_value, date__year=year_value)
#         elif filter_type == 'year' and year_value:
#             invoices = invoices.filter(date__year=year_value)
#         else:
#             return Response({"error": "Invalid filter parameters."}, status=400)
        
#         bills_by_payment = invoices.values('mode_of_payment').annotate(total_revenue=Sum('grand_total'))
#         bills_by_payment_2 = invoices.values('new_mode').annotate(total_revenue=Sum('grand_total'))
#         response_data = [
#             {
#                 "payment_mode": item['mode_of_payment'],
#                 "total_revenue": item['total_revenue'],
#             }
#             for item in bills_by_payment
#         ]
#         response_data_1 = [
#             {
#                 "payment_mode": item['new_mode'],
#                 "total_revenue": item['total_revenue'],
#             }
#             for item in bills_by_payment_2
#         ]
        
        
#         return Response({"data_of_mode_of_payment":response_data,
#                         "data_of_new_mode":response_data_1})





class ModeOfPaymentAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        filter_type = request.query_params.get('filter')
        date_value = request.query_params.get('date')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        month_value = request.query_params.get('month')
        year_value = request.query_params.get('year')

        invoices = VendorInvoice.objects.filter(vendor_name=request.user, vendor_branch_id=branch_name)

        if filter_type == 'day' and date_value:
            invoices = invoices.filter(date=date_value)
        elif filter_type == 'week' and start_date and end_date:
            invoices = invoices.filter(date__range=[start_date, end_date])
        elif filter_type == 'month' and month_value and year_value:
            invoices = invoices.filter(date__month=month_value, date__year=year_value)
        elif filter_type == 'year' and year_value:
            invoices = invoices.filter(date__year=year_value)
        else:
            return Response({"error": "Invalid filter parameters."}, status=400)

        mode_totals = defaultdict(float)
        new_mode_totals = defaultdict(float)

        for invoice in invoices:
          
            mode = invoice.mode_of_payment
            if mode and isinstance(mode, str):
                mode_clean = mode.strip().lower()
                mode_totals[mode_clean] += float(invoice.grand_total)

            if isinstance(invoice.new_mode, list):
                for item in invoice.new_mode:
                    if isinstance(item, dict):
                        new_mode = item.get("mode", "").strip().lower()
                        amount = item.get("amount", 0)
                        new_mode_totals[new_mode] += float(amount)

        response_data = [{"mode": mode, "amount": round(amount, 2)} for mode, amount in mode_totals.items()]
        response_data_1 = [{"mode": mode, "amount": round(amount, 2)} for mode, amount in new_mode_totals.items()]

        return Response({
            "data_of_mode_of_payment": response_data,
            "data_of_new_mode": response_data_1
        })



class RevenueSummaryAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        current_date = now().date()
        previous_day = current_date - timedelta(days=1)
        
        invoices_today_count = VendorInvoice.objects.filter(
            date=current_date,
            vendor_name=request.user,
            vendor_branch_id=branch_name
        ).count()
        
        revenue_today = VendorInvoice.objects.filter(
            vendor_name=request.user,
            date=current_date,
            vendor_branch_id=branch_name
        ).aggregate(
            total_revenue=Sum('grand_total')
        )['total_revenue'] or 0
        
        previous_day_revenue = VendorInvoice.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name,
            date=previous_day
        ).aggregate(
            total_revenue=Sum('grand_total')
        )['total_revenue'] or 0
        
        appointmet_today_count = VendorAppointment.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name,
            date=current_date
        ).count()
        
        return Response({
            "today_no_of_invoices": invoices_today_count,
            "today_revenue": revenue_today,
            "previous_day_rev": previous_day_revenue,
            "today_no_of_app": appointmet_today_count,
        })





class VendorCustomerStatsAPIView(APIView):
    def get(self, request):
        today = now().strftime("%Y-%m-%d")  # Get today's date in YYYY-MM-DD format

        # New Customers (Last 30 Days)
        recent_customers = VendorCustomers.objects.filter(vendor_branch_id=request.query_params.get('branch_name'),user=request.user,created_at__gte=now() - timedelta(days=30)).count()

        # Active Memberships
        active_memberships = VendorCustomers.objects.filter(vendor_branch_id=request.query_params.get('branch_name'),user=request.user,memberships__isnull=False).count()

        # Active Coupons (Customers with at least one coupon)
        active_coupons = VendorCustomers.objects.filter(vendor_branch_id=request.query_params.get('branch_name'),user=request.user,coupon__isnull=False).distinct()

        # Birthdays Today
        birthdays = VendorCustomers.objects.filter(vendor_branch_id=request.query_params.get('branch_name'),user=request.user,d_o_b=today)

        # Anniversaries Today
        anniversaries = VendorCustomers.objects.filter(vendor_branch_id=request.query_params.get('branch_name'),user=request.user,d_o_a=today)

        data = {
            "new_customers": recent_customers,
            "active_memberships": active_memberships,
            "active_coupons": active_coupons.count(),
            "birthdays": VendorCustomerLoyalityProfileSerializer_get(birthdays,many=True).data,
            "anniversaries": VendorCustomerLoyalityProfileSerializer_get(anniversaries,many=True).data,
            "birthday_count": birthdays.count(),
            "anniversaries_count": anniversaries.count()
        }

        return Response(data)



class ExpiringProductsAPIView(APIView):
    def get(self, request):
        today = now().date()
        next_month = today + timedelta(days=30)  # Get the date one month from today
        

        expiring_products = VendorInventoryProduct.objects.filter(vendor_branch_id=request.query_params.get('branch_name'),user=request.user,expiry_date__lte=next_month, expiry_date__gte=today).values('product_name','expiry_date')
        import datetime as dt

        expiring_expenses = VendorExpense.objects.filter(
            vendor_branch_id=request.query_params.get('branch_name'),
            user=request.user,
            date__month=dt.date.today().month
        ).values('due_amount', 'due_date', 'expense_type')
        data = {
            "expiring_products": list(expiring_products),
            "due_amount": list(expiring_expenses)
        }

        return Response(data)



class SalesTargetSettingListCreateView(APIView):
    def get(self, request):
        month = request.query_params.get("month")
        year = request.query_params.get("year")
        report_type = request.query_params.get("type")
        branch_id = request.query_params.get("branch_name")

        try:
            current_month = int(month)
            current_year = int(year)
            month_name = datetime(current_year, current_month, 1).strftime('%B')
        except (TypeError, ValueError):
            return Response({"error": "Invalid or missing 'month' or 'year' in query parameters."},
                            status=status.HTTP_400_BAD_REQUEST)

        if report_type == "admin":
           
            sales_targets = (
                SalesTargetSetting.objects
                .filter(vendor_name=request.user,month=current_month,year=current_year)
                .values('vendor_branch__branch_name')
                .annotate(
                    total_service_target=Sum('service_target'),
                    total_product_target=Sum('product_target'),
                    total_membership_coupon_target=Sum('membership_coupon_target'),
                    total_overall_target=Sum('overall_target')
                )
                .order_by('vendor_branch__branch_name')
            )

            # Staff Targets (raw)
            staff_targets = SalesTargetSetting.objects.filter(
                vendor_name=request.user,month=current_month,year=current_year
            ).values('vendor_branch__branch_name', 'staff_targets')

            # Monthly Branch Revenue
            branch_revenue_qs = VendorInvoice.objects.filter(
                vendor_name=request.user,
                date__year=current_year,
                date__month=current_month
            ).values('vendor_branch__branch_name').annotate(
                monthly_total=Sum('grand_total')
            )

            branch_revenue = [
                {
                    "branch_name": item['vendor_branch__branch_name'],
                    "monthly_total": item['monthly_total']
                }
                for item in branch_revenue_qs
            ]

            
            invoices = VendorInvoice.objects.filter(
                vendor_name=request.user,
                date__year=current_year,
                date__month=current_month
            )

            grouped_data = defaultdict(lambda: {
                "staff_data": defaultdict(lambda: {
                    "total_invoices": 0,
                    "total_sales": 0,
                    "services": defaultdict(lambda: {
                        "total_sales": 0,
                        "total_services": 0
                    })
                })
            })

            for invoice in invoices:
                branch_name = invoice.vendor_branch.branch_name if invoice.vendor_branch else "Unknown Branch"
                try:
                    services = json.loads(invoice.services) if isinstance(invoice.services, str) else invoice.services
                except json.JSONDecodeError:
                    services = []

                for service in services:
                    staff_name = service.get('Staff')
                    service_name = service.get('Description')
                    price = float(service.get('Price', 0))

                    if staff_name and service_name:
                        staff_data = grouped_data[branch_name]["staff_data"][staff_name]
                        staff_data["total_invoices"] += 1
                        staff_data["total_sales"] += price
                        staff_data["services"][service_name]["total_sales"] += price
                        staff_data["services"][service_name]["total_services"] += 1

            staff_revenue = {
                "month": month_name,
                "year": current_year,
                "branches": [
                    {
                        "branch_name": branch_name,
                        "staff_data": [
                            {
                                "staff_name": staff_name,
                                "total_invoices": staff_data["total_invoices"],
                                "total_sales": staff_data["total_sales"],
                                "services": [
                                    {
                                        "service_name": service_name,
                                        "total_sales": service_data["total_sales"],
                                        "total_services": service_data["total_services"]
                                    }
                                    for service_name, service_data in staff_data["services"].items()
                                ]
                            }
                            for staff_name, staff_data in branch_data["staff_data"].items()
                        ]
                    }
                    for branch_name, branch_data in grouped_data.items()
                ]
            }

            return Response({
                "list": list(sales_targets),
                "staff_targets_by_branch": list(staff_targets),
                "month": month_name,
                "year": current_year,
                "branch_revenue": branch_revenue,
                "staff_revenue": staff_revenue
            }, status=status.HTTP_200_OK)
    
   
        sales_targets = SalesTargetSetting.objects.filter(
            vendor_branch_id=branch_id,
            vendor_name=request.user,
            month=current_month,
            year=current_year
        ).values()
        branch_revenue_qs = VendorInvoice.objects.filter(
                vendor_name=request.user,
                vendor_branch_id=branch_id,
                date__year=current_year,
                date__month=current_month
            ).values('vendor_branch__branch_name').annotate(
                monthly_total=Sum('grand_total')
            )

        branch_revenue = [
            {
            "branch_name": item['vendor_branch__branch_name'],
            "monthly_total": item['monthly_total']
            }
            for item in branch_revenue_qs
        ]

            
        invoices = VendorInvoice.objects.filter(
                vendor_name=request.user,
                date__year=current_year,
                vendor_branch_id=branch_id,
                date__month=current_month
        )

        grouped_data = defaultdict(lambda: {
                "staff_data": defaultdict(lambda: {
                "total_invoices": 0,
                "total_sales": 0,
                "services": defaultdict(lambda: {
                "total_sales": 0,
                "total_services": 0
                })
            })
        })

        for invoice in invoices:
            branch_name = invoice.vendor_branch.branch_name if invoice.vendor_branch else "Unknown Branch"
            try:
                services = json.loads(invoice.services) if isinstance(invoice.services, str) else invoice.services
            except json.JSONDecodeError:
                services = []

            for service in services:
                staff_name = service.get('Staff')
                service_name = service.get('Description')
                price = float(service.get('Price', 0))

                if staff_name and service_name:
                    staff_data = grouped_data[branch_name]["staff_data"][staff_name]
                    staff_data["total_invoices"] += 1
                    staff_data["total_sales"] += price
                    staff_data["services"][service_name]["total_sales"] += price
                    staff_data["services"][service_name]["total_services"] += 1

        staff_revenue = {
            "month": month_name,
            "year": current_year,
            "branches": [
                {
                    "branch_name": branch_name,
                    "staff_data": [
                        {
                            "staff_name": staff_name,
                            "total_invoices": staff_data["total_invoices"],
                            "total_sales": staff_data["total_sales"],
                            "services": [
                                {
                                    "service_name": service_name,
                                    "total_sales": service_data["total_sales"],
                                    "total_services": service_data["total_services"]
                                }
                                for service_name, service_data in staff_data["services"].items()
                            ]
                        }
                        for staff_name, staff_data in branch_data["staff_data"].items()
                    ]
                }
                for branch_name, branch_data in grouped_data.items()
            ]
        }

        return Response({
                "list": list(sales_targets),
               
                "month": month_name,
                "year": current_year,
                "branch_revenue": branch_revenue,
                "staff_revenue": staff_revenue
            }, status=status.HTTP_200_OK)
    def post(self, request):
        branch_name = request.query_params.get('branch_name')
        obj = SalesTargetSetting.objects.filter(vendor_branch_id=request.query_params.get('branch_name'),vendor_name=request.user)
        if len(obj) != 0:
            obj.delete()
            
        serializer = SalesTargetSettingSerializer(data=request.data,context={'request': request, 'branch_id': branch_name})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SalesTargetSettingDetailView(APIView):
    def get(self, request, pk):
        
        sales_target = get_object_or_404(SalesTargetSetting, pk=pk)
        serializer = SalesTargetSettingSerializer(sales_target)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        sales_target = get_object_or_404(SalesTargetSetting, pk=pk)
        serializer = SalesTargetSettingSerializer(sales_target, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        sales_target = get_object_or_404(SalesTargetSetting, pk=pk)
        sales_target.delete()
        return Response({"message": "Sales target deleted successfully"}, status=status.HTTP_204_NO_CONTENT)





class PictureUploadView(APIView):
  

    def get(self, request, *args, **kwargs):
        branch_name  = request.query_params.get('branch_name')
        pictures = Picture.objects.filter(user=request.user,vendor_branch_id=branch_name)
        serializer = PictureSerializer(pictures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        branch_name  = request.query_params.get('branch_name')
        serializer = PictureSerializer(data=request.data, context={'request': request,'branch_id':branch_name})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class MergeImagesAPIView(APIView):
   

    def add_footer_box(self,original_image_file, logo_image_file, salon_name, mobile_number, text,address):
    
        original_img = Image.open(original_image_file).convert("RGB")
        width, original_height = original_img.size

    
        logo_img = Image.open(logo_image_file).convert("RGBA")
        logo_img.thumbnail((50, 50))  
        footer_height = 75
        footer = Image.new("RGB", (width, footer_height), color="white")
        logo_y = (footer_height - logo_img.height) // 2
        footer.paste(logo_img, (20, 16), logo_img)
        draw = ImageDraw.Draw(footer)
        # font = ImageFont.truetype("arial.ttf", 20)
        
        font = ImageFont.load_default()
        
        text_x = 119
        
        draw.text((135, 4), text, fill="black", font=font)
        draw.text((text_x, 17), salon_name, fill="black", font=font)
        draw.text((text_x, 31), f"Mobile: {mobile_number}", fill="black", font=font)
        draw.text((text_x, 45), address, fill="black", font=font)
        combined_img = Image.new("RGB", (width, original_height + footer_height), color="white")
        combined_img.paste(original_img, (0, 0))
        combined_img.paste(footer, (0, original_height))
        
        
        output = io.BytesIO()
        combined_img.save(output, format='JPEG')
        output.seek(0)
        output

        return output

   
    def post(self, request, *args, **kwargs):
        
        image = request.data.get('image')
        logo = request.data.get('logo')
    
    
        salon_name = request.data.get('salon_name')
        mobile_number = request.data.get('mobile_no')
        address = request.data.get('address')
    

        final_image = self.add_footer_box(image, logo, salon_name, mobile_number, request.data.get('text'),address)
        
    
        return FileResponse(final_image, content_type='image/jpeg')
           
       
class FacebookTokenExchange(APIView):
    # throttle_classes = [ScopedRateThrottle]
    # throttle_scope = 'upload_instagram'
    def post(self, request):
        short_token = request.data.get('access_token')
        url = 'https://graph.facebook.com/v22.0/oauth/access_token'
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': FB_APP_ID,
            'client_secret': FB_APP_SECRET,
            'fb_exchange_token': short_token
        }
        response = requests.get(url, params=params)
        return Response(response.json(), status=response.status_code)


class FacebookPages(APIView):
    # throttle_classes = [ScopedRateThrottle]
    # throttle_scope = 'upload_instagram'
    def post(self, request):
        access_token = request.data.get('access_token')
        url = 'https://graph.facebook.com/v22.0/me/accounts'
        response = requests.get(url, params={'access_token': access_token})
        return Response(response.json(), status=response.status_code)


class InstagramBusinessID(APIView):
    # throttle_classes = [ScopedRateThrottle]
    # throttle_scope = 'upload_instagram'
    def post(self, request):
        page_id = request.data.get('page_id')
        access_token = request.data.get('access_token')
        url = f'https://graph.facebook.com/v22.0/{page_id}'
        params = {
            'fields': 'instagram_business_account',
            'access_token': access_token
        }
        response = requests.get(url, params=params)
        return Response(response.json(), status=response.status_code)



class InstagramUpload(APIView):
    # throttle_classes = [ScopedRateThrottle]
    # throttle_scope = 'upload_instagram'
    def add_footer_box(self,original_image_file, logo_image_file, salon_name, mobile_number, text,address):
    
        original_img = Image.open(original_image_file).convert("RGB")
        width, original_height = original_img.size

    
        logo_img = Image.open(logo_image_file).convert("RGBA")
        logo_img.thumbnail((50, 50))  
        footer_height = 75
        footer = Image.new("RGB", (width, footer_height), color="white")
        logo_y = (footer_height - logo_img.height) // 2
        footer.paste(logo_img, (20, 16), logo_img)
        draw = ImageDraw.Draw(footer)
        # font = ImageFont.truetype("arial.ttf", 20)
        
        font = ImageFont.load_default()
        
        text_x = 119
        
        draw.text((135, 4), text, fill="black", font=font)
        draw.text((text_x, 17), salon_name, fill="black", font=font)
        draw.text((text_x, 31), f"Mobile: {mobile_number}", fill="black", font=font)
        draw.text((text_x, 45), address, fill="black", font=font)
        combined_img = Image.new("RGB", (width, original_height + footer_height), color="white")
        combined_img.paste(original_img, (0, 0))
        combined_img.paste(footer, (0, original_height))
        
        
        output = io.BytesIO()
        combined_img.save(output, format='JPEG')
        output.seek(0)
        output
        output.name = 'final_instagram_image.jpg'

        return output
    def post(self, request):
        instagram_id = request.data.get('instagram_id')
        
       
        caption = request.data.get('caption')
        access_token = request.data.get('access_token')
        image = request.data.get('image')
        logo = request.data.get('logo')
    
    
        salon_name = request.data.get('salon_name')
        mobile_number = request.data.get('mobile_no')
        address = request.data.get('address')
    

        final_image = self.add_footer_box(image, logo, salon_name, mobile_number, request.data.get('text'),address)
        
        from django.core.files.uploadedfile import InMemoryUploadedFile
        import sys

        final_image_file = self.add_footer_box(image, logo, salon_name, mobile_number, request.data.get('text'), address)

        in_memory_file = InMemoryUploadedFile(
            file=final_image_file,
            field_name='image',
            name='final_instagram_image.jpg',
            content_type='image/jpeg',
            size=final_image_file.getbuffer().nbytes,
            charset=None
        )
        
        obj = IG_FB_shared_picture.objects.create(
            user=request.user,
            vendor_branch_id=request.query_params.get('branch_name'),
            image=in_memory_file
        )
        domain = 'https://app.swalookcrm.in'
        full_image_url = f"{domain}{obj.image.url}"
        create_url = f'https://graph.facebook.com/v22.0/{instagram_id}/media'
        create_data = {
            'image_url': full_image_url,
            'caption': caption,
            'access_token': access_token
        }
        create_res = requests.post(create_url, data=create_data).json()
        creation_id = create_res.get("id")

        if not creation_id:
            return Response({'error': 'Failed to create media'}, status=400)

        
        publish_url = f'https://graph.facebook.com/v22.0/{instagram_id}/media_publish'
        publish_data = {
            'creation_id': creation_id,
            'access_token': access_token
        }
        publish_res = requests.post(publish_url, data=publish_data).json()
        return Response(publish_res)




class VendorpurchaseView(APIView):

    serializer_class = VendorExpensePurchase

    def __init__(self, **kwargs):
        self.cache_key = None
        super().__init__(**kwargs)

    @transaction.atomic
    def post(self, request):
        branch_name = request.query_params.get('branch_name')

        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name})

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "vendor added successfully."
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": False,
            "errors": serializer.errors,
            "message": "Failed to add vendor."
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        data = Vendor_ExpensePurchase.objects.filter(user=request.user, vendor_branch_id=branch_name)
        serializer = self.serializer_class(data, many=True)

        return Response({
            "status": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)



class UtilizationInventory(APIView):
    serializer_class = VendorInventoryUtilization

    def __init__(self, **kwargs):
        self.cache_key = None
        super().__init__(**kwargs)

    @transaction.atomic
    def post(self, request):
        branch_name = request.query_params.get('branch_name')

        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name})

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "vendor added successfully."
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": False,
            "errors": serializer.errors,
            "message": "Failed to add vendor."
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        data = Utilization_Inventory.objects.filter(user=request.user, vendor_branch_id=branch_name)
        serializer = self.serializer_class(data, many=True)

        return Response({
            "status": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

        
    



class DownloadInvoiceExcelView(APIView):
    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        date = request.query_params.get('date')
        
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = VendorInvoice.objects.filter(
            vendor_name=request.user,
            vendor_branch=branch_name,
            date=date
        ).order_by('-date')

        wb = Workbook()
        ws = wb.active
        ws.title = "Vendor Invoices"
        ws.append([
            'Invoice No', 'Customer Name', 'Mobile No', 'Email',
            'Service Description', 'Category', 'Price', 'Quantity',
            'Discount', 'Tax Amt', 'Total Amount', 'Payment Mode',
            'Date', 'Grand Total'
        ])
        for invoice in queryset:
            try:
                services = json.loads(invoice.services)
            except (TypeError, json.JSONDecodeError):
                services = []

            for service in services:
                ws.append([
                    invoice.slno,
                    invoice.customer_name,
                    invoice.mobile_no,
                    invoice.email,
                    service.get('Description', ''),
                    service.get('category', ''),
                    service.get('Price', ''),
                    service.get('Quantity', ''),
                    service.get('Discount', ''),
                    service.get('Tax_amt', ''),
                    service.get('Total_amount', ''),
                    invoice.new_mode[0]['mode'] if invoice.new_mode else '',
                    invoice.date.strftime('%Y-%m-%d') if invoice.date else '',
                    invoice.grand_total
                ])

     
        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)
        filename = f"invoices_{date}.xlsx"
        response = HttpResponse(
            stream,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response




class VendorPurchaseView_vp(APIView):
    serializer_class = VendorPurchaseConnect

    def __init__(self, **kwargs):
        self.cache_key = None
        super().__init__(**kwargs)

    @transaction.atomic
    def post(self, request):
        branch_name = request.query_params.get('branch_name')

        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data, context={'request': request, 'branch_id': branch_name})

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "purchase added successfully."
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": False,
            "errors": serializer.errors,
            "message": "Failed to add vendor."
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        branch_name = request.query_params.get('branch_name')
        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        data = Purchase_entry.objects.filter(user=request.user, vendor_branch_id=branch_name)
        serializer = VendorPurchaseConnect_get(data, many=True)

        return Response({
            "status": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)



class SingleStaffAttendance(APIView):
      def get(self, request):
        branch_name = request.query_params.get('branch_name')
        month = request.query_params.get('month')
        staff_id = request.query_params.get('staff_id')

        if not branch_name:
            return Response({
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'error': {
                    'code': 'Bad Request',
                    'message': 'branch_name parameter is missing!'
                },
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        current_date = dt.date.today()

        
        if staff_id:
            staff = VendorStaff.objects.filter(mobile_no=staff_id,vendor_branch_id=branch_name)
            if not staff.exists():
                return Response({
                    'success': False,
                    'status_code': status.HTTP_404_NOT_FOUND,
                    'error': {
                        'code': 'Not Found',
                        'message': 'Staff with the provided ID does not exist in this branch.'
                    },
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
      
        attendance_queryset = VendorStaffAttendance.objects.filter(
    
            vendor_branch_id=branch_name,
            of_month=month,
            year=current_date.year,
            staff_id__in=staff
        )

        attendance_data = {}
        for record in attendance_queryset:
            sid = record.staff.staff_name
            if sid not in attendance_data:
                attendance_data[sid] = {
                    "present_dates": [],
                    "in_time": [],
                    "out_time": [],
                    "leave_dates": [],
                    "number_of_days_present": 0,
                    "no_of_days_absent": 0,
                }

            if record.attend:
                attendance_data[sid]["present_dates"].append(record.date)
                attendance_data[sid]["in_time"].append(record.in_time)
                attendance_data[sid]["out_time"].append(record.out_time)
                attendance_data[sid]["number_of_days_present"] += 1
            if record.leave:
                attendance_data[sid]["leave_dates"].append(record.date)
                attendance_data[sid]["no_of_days_absent"] += 1

        
       

      
        staff_settings_obj = StaffSetting.objects.filter(
        
            vendor_branch_id=branch_name,
            month=month,
        ).first()

        time_obj = StaffAttendanceTime.objects.filter(

            vendor_branch_id=branch_name
        ).first()

        return Response({
            "status": True,
            "table_data": attendance_data,
            "current_month_days": staff_settings_obj.number_of_working_days if staff_settings_obj else 0,
            "in_time": time_obj.in_time if time_obj else None,
            "out_time": time_obj.out_time if time_obj else None,
            "message": "Attendance records retrieved successfully."
        }, status=status.HTTP_200_OK)
        
    


