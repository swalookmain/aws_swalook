from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from django.contrib import auth
from rest_framework import serializers
from .models import *
from rest_framework.response import Response
import datetime as dt
from datetime import datetime
import random as r
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password, check_password
from api_swalook.settings import WP_INS_TOKEN, WP_INS_ID, WP_API_URL, BASE_DIR
from django.db import transaction
from rest_framework.serializers import ValidationError
from dateutil.relativedelta import relativedelta
from django.utils.translation import gettext_lazy as _
import re
from django.contrib.auth import authenticate
import uuid

class signup_serializer(serializers.ModelSerializer):
    class Meta:
        model = SwalookUserProfile
        fields = ["salon_name", "mobile_no", "email", "owner_name"]

    def validate_mobile_no(self, value):
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Mobile number must be exactly 10 digits.")
        return value

    def validate_email(self, value):
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', value):
            raise serializers.ValidationError("Invalid email address format.")
        return value

    def validate(self, data):
        if SwalookUserProfile.objects.filter(mobile_no=data.get('mobile_no')).exists():
            raise serializers.ValidationError("A user with this mobile number already exists.")
        if SwalookUserProfile.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError("A user with this email address already exists.")
        return data

    def create(self, validated_data):
        a, b, c = [r.randint(0, 9) for _ in range(3)]
        validated_data['vendor_id'] = f"{validated_data['salon_name'][:2]}{a}{b}{c}"
        validated_data.setdefault('invoice_limit', 100)
        validated_data.setdefault('account_created_date', dt.date.today())
        validated_data.setdefault('number_of_staff', "0")
        validated_data.setdefault('s_gst_percent', "0")
        validated_data.setdefault('c_gst_percent', "0")
        validated_data.setdefault('current_billslno', "0")
        validated_data.setdefault('appointment_limit', 100)
        validated_data.setdefault('invoice_generated', 0)
        validated_data.setdefault('appointment_generated', 0)
        validated_data.setdefault('gst_number', "0")
        validated_data.setdefault('pan_number', "0")
        validated_data.setdefault('pincode', "0")
        validated_data.setdefault('profile_pic', "/data/inv.png/")
        validated_data.setdefault('enc_pwd', "w!==?0id")

        request = self.context.get('request')
        if request:
            get_ip = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = get_ip.split(',')[0] if get_ip else request.META.get('REMOTE_ADDR')
        else:
            ip = "unknown"

        validated_data['user_ip'] = str(ip)

        user = User(username=validated_data['mobile_no'])
        user.set_password(validated_data['enc_pwd'])
        user.save()

        return super().create(validated_data)


class login_serializer(serializers.Serializer):
    mobileno = serializers.CharField()
    password = serializers.CharField()

    def create(self, validated_data):
        user = auth.authenticate(username=validated_data['mobileno'], password=validated_data['password'])
        if user is not None:
            auth.login(self.context.get('request'), user)
        return "ok!"


class centralized_login_serializer(serializers.Serializer):
    mobileno = serializers.CharField()
    password = serializers.CharField()

    def validate_mobileno(self, value):
        if not value:
            raise serializers.ValidationError("Mobile number is required.")
        return value

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("Password is required.")
        return value

    def create(self, validated_data):
        mobileno = validated_data['mobileno']
        password = validated_data['password']

        user = authenticate(username=mobileno, password=password)
        if user:
            auth.login(self.context.get('request'), user)
            token, created = Token.objects.get_or_create(user=user)
            return ["owner", token, "Owner", ""]

        staff_object = SalonBranch.objects.filter(staff_name=mobileno, password=password).select_related('vendor_name').first()
        if staff_object:
            user_profile = SwalookUserProfile.objects.filter(mobile_no=staff_object.vendor_name).first()
            if user_profile:
                user = authenticate(username=user_profile.mobile_no, password=user_profile.enc_pwd)
                if user:
                    auth.login(self.context.get('request'), user)
                    token, created = Token.objects.get_or_create(user=user)
                    self.context.get('request').session[f"{user_profile.mobile_no}branch_name_14"] = staff_object.branch_name
                    self.context.get('request').session[f"{user_profile.mobile_no}salon_name_13"] = user_profile.salon_name
                    return ["staff", token, user_profile.salon_name, staff_object]
                raise ValidationError("Invalid credentials for staff.")
            raise ValidationError("Staff profile not found.")

        user = User.objects.filter(username=mobileno).first()
        if user:
            admin_obj = SalonBranch.objects.filter(vendor_name=user, admin_password=password).select_related('vendor_name').first()
            if admin_obj:
                user_profile = SwalookUserProfile.objects.filter(mobile_no=mobileno).first()
                if user_profile:
                    user = authenticate(username=user_profile.mobile_no, password=user_profile.enc_pwd)
                    if user:
                        auth.login(self.context.get('request'), user)
                        token, created = Token.objects.get_or_create(user=user)
                        self.context.get('request').session[f"{user_profile.mobile_no}branch_name_14"] = admin_obj.branch_name
                        self.context.get('request').session[f"{user_profile.mobile_no}salon_name_13"] = user_profile.salon_name
                        return ["admin", token, user_profile.salon_name, admin_obj]
                    raise ValidationError("Invalid credentials for admin.")
                raise ValidationError("Admin profile not found.")
            raise ValidationError("Admin password mismatch.")

        raise ValidationError("User not found.")


class admin_login_serializer(serializers.Serializer):
    mobileno = serializers.CharField()
    password = serializers.CharField()

    def create(self, validated_data):
        u = SwalookUserProfile.objects.get(mobile_no=validated_data.get('mobileno'))
        branch = SalonBranch.objects.get(admin_password=validated_data.get('password'))
        user = auth.authenticate(username=u.mobile_no, password=u.enc_pwd)
        auth.login(self.context.get('request'), user)
        token = Token.objects.get_or_create(user=user)
        return token


class staff_login_serializer(serializers.Serializer):
    mobileno = serializers.CharField()
    password = serializers.CharField()

    def create(self, validated_data):
        user_sub = SalonBranch.objects.get(staff_name=validated_data['mobileno'], password=validated_data['password'])
        return user_sub.vendor_name


class UpdateProfileSerializer(serializers.Serializer):
    gst_number = serializers.CharField()
    profile_pic = serializers.ImageField(required=False)
    s_gst_percent = serializers.CharField()
    c_gst_percent = serializers.CharField()

    def update(self, instance, validated_data):
        instance.gst_number = validated_data.get('gst_number', instance.gst_number)
        instance.s_gst_percent = validated_data.get('s_gst_percent', instance.s_gst_percent)
        instance.c_gst_percent = validated_data.get('c_gst_percent', instance.c_gst_percent)

        profile_pic = self.context.get('request').FILES.get('profile_pic')
        if profile_pic:
            instance.profile_pic = profile_pic

        instance.save()
        return instance


class billing_serializer(serializers.ModelSerializer):
    json_data = serializers.ListField(child=serializers.DictField(child=serializers.CharField()))
    new_mode = serializers.ListField(child=serializers.DictField(child=serializers.CharField()))
    class Meta:
        model = VendorInvoice
        fields = ["customer_name", "mobile_no", "email", "address", "services", "mode_of_payment", "new_mode","service_by", "json_data", "loyalty_points_deducted", "total_prise", "total_quantity", "total_tax", "total_discount", "grand_total", "total_cgst", "total_sgst", "gst_number", "comment", "slno",]
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        date = dt.date.today()
        validated_data['vendor_name'] = self.context.get('request').user
        validated_data['date'] = date
        validated_data['vendor_branch_id'] = self.context.get('branch_id')
        self.update_inventory(validated_data['json_data'])
        # self.handle_loyalty_points(validated_data)
        # self.update_staff_business_to_month(validated_data['service_by'],validated_data['grand_total'],validated_data['total_tax'])
        super().create(validated_data)
        return validated_data['slno']

    def handle_loyalty_points(self, validated_data):
        if int(validated_data['grand_total']) > 100:
            try:
                customer = VendorCustomers.objects.select_related('membership_type').select_for_update().get(
                    mobile_no=validated_data['mobile_no'],
                    vendor_branch_id=self.context.get('branch_id'),
                    user=self.context.get('request').user
                )
                clp_object = VendorCustomerLoyalityPoints.objects.select_for_update().get(
                    user=self.context.get('request').user,
                    vendor_branch_id=self.context.get('branch_id'),
                    customer_id=customer.mobile_no
                )
                validated_data['vendor_customers_profile'] = customer
                if int(customer.membership_type.points_hold) != 0:
                    if float(validated_data['loyalty_points_deducted']) > float(clp_object.current_customer_points):
                        raise serializers.ValidationError("Loyalty points deducted cannot exceed current customer points.")
                    validated_data['loyalty_points'] = float(validated_data['grand_total']) / float(customer.membership_type.points_hold)
                    clp_object.current_customer_points = float(clp_object.current_customer_points) - float(validated_data['loyalty_points_deducted'])
                    clp_object.current_customer_points = float(clp_object.current_customer_points) + float(validated_data['loyalty_points'])
                    clp_object.save()
                    clp_object.refresh_from_db()
                    self.create_ledger_entry(validated_data, clp_object)

                else:
                    validated_data['loyalty_points'] = 0
                # if int(customer.coupon.coupon_points_hold) != 0:
                #     if float(validated_data['coupon_points_used']) > float(customer.coupon.coupon_points_hold):
                #         raise serializers.ValidationError("Coupon points deducted cannot exceed current customer points.")
                #     customer.coupon.coupon_points_hold = float(customer.coupon.coupon_points_hold) - float(validated_data['coupon_points_used'])
                #     customer.save()
                #     customer.refresh_from_db()

            except VendorCustomers.DoesNotExist:
                pass

    def create_ledger_entry(self, validated_data, clp_object):
        date = dt.date.today()
        ledger_object = VendorCustomerLoyalityLedger(
            vendor_branch_id=validated_data['vendor_branch_id'],
            user=self.context.get('request').user,
            customer=clp_object,
            point_spend=validated_data['loyalty_points_deducted'],
            point_gain=validated_data['loyalty_points'],
            point_available=clp_object.current_customer_points,
            inventory_invoice_obj=validated_data['slno'],
            date=dt.date.today(),

        )
        ledger_object.save()

    def update_inventory(self, json_data):
        products_to_update = []
        for item in json_data:
            try:
                product = VendorInventoryProduct.objects.get(id=item.get('id'))
                product.stocks_in_hand -= int(item.get('quantity'))
                products_to_update.append(product)
            except VendorInventoryProduct.DoesNotExist:
                pass

        if products_to_update:
            VendorInventoryProduct.objects.bulk_update(products_to_update, ['stocks_in_hand'])

    def update_staff_business_to_month(self, staff, grand_total, total_tax):
        staff_obj = VendorStaff.objects.get(staff_name=staff, vendor_name=self.context.get('request').user)
        staff_obj.business_of_the_current_month = float(staff_obj.business_of_the_current_month) + (float(grand_total) - float(total_tax))
        staff_obj.save()

class app_serailizer_get(serializers.ModelSerializer):
    class Meta:
        model = VendorAppointment
        fields = "__all__"


class appointment_serializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAppointment
        fields = ["id", "customer_name", "mobile_no", "email", "services", "booking_date", "booking_time", "comment"]
        extra_kwargs = {'id': {'read_only': True},}

    def create(self, validated_data):
        def send_appointment_email(subject, body, recipient_email):
            send_mail(subject, body, 'info@swalook.in', [recipient_email])

        with transaction.atomic():
            validated_data['vendor_name'] = self.context.get('request').user
            validated_data['vendor_branch_id'] = self.context.get('branch_id')
            validated_data['date'] = dt.date.today()

            appointment = super().create(validated_data)

            # if validated_data['email'] and validated_data['email'].strip():
            #     name = f"{str(self.context.get('request').user)}branch_name_14"
            #     subject = f"{self.context.get('request').session.get('name')}" + " - Appointment"
            #     body = f"Hi {validated_data['customer_name']}!\nYour appointment is booked and finalized for: {validated_data['booking_time']} | {validated_data['booking_date']}\nFor the following services: {validated_data['services']}\nSee you soon!\nThanks and Regards\nTeam {self.context.get('request').session.get(f'{name}')}"

            #     send_appointment_email(subject, body, validated_data['email'])

            return appointment


class UpdateAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAppointment
        fields = [
            'customer_name',
            'mobile_no',
            'email',
            'services',
            'booking_date',
            'booking_time',
            'comment',
        ]

    def validate(self, data):
        request = self.context.get('request')
        branch_name = self.context.get('branch_name')
        appointment_id = self.instance.id if self.instance else None

        conflicting_appointments = VendorAppointment.objects.filter(
            vendor_name=request.user,
            vendor_branch_id=branch_name,
            mobile_no=data['mobile_no'],
            booking_date=data['booking_date'],
            booking_time=data['booking_time'],
        ).exclude(id=appointment_id)

        if conflicting_appointments.exists():
            raise serializers.ValidationError(
                f"An appointment for this customer on {data['booking_date']} at {data['booking_time']} already exists."
            )

        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.date = dt.date.today()
        instance.save()
        return instance


class Vendor_Pdf_Serializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)

    class Meta:
        model = VendorPdf
        fields = [
            "customer_name",
            "mobile_no",
            "file",
            "email",
            "invoice",
        ]
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def validate_email(self, value):
        from django.core.exceptions import ValidationError
        from django.core.validators import validate_email

        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email address.")
        return value

    def validate_vendor_email(self, value):
        if not value:
            raise serializers.ValidationError("Vendor email is required.")
        return value

    def validate_vendor_password(self, value):
        if not value:
            raise serializers.ValidationError("Vendor password is required.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['vendor_branch_id'] = self.context.get('branch_id')
        validated_data['date'] = dt.date.today()
        validated_data['file'] = request.FILES.get('file')

        return super().create(validated_data)


class VendorServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorServiceCategory
        fields = ['id', 'service_category']
        extra_kwargs = {'id': {'read_only': True},}

    def create(self, validated_data):
        validated_data['user'] = self.context.get('request').user
        validated_data['vendor_branch_id'] = self.context.get('branch_id')
        return super().create(validated_data)


    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)


        instance.save()
        return instance


class service_serializer(serializers.ModelSerializer):
    category = serializers.UUIDField(write_only=True, format='hex_verbose')
    category_details = VendorServiceCategorySerializer(read_only=True, source='category')


    class Meta:
        model = VendorService
        fields = ["id", "service", "service_price", "service_duration", "category","category_details", "for_men", "for_women"]
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        validated_data['user'] = self.context.get('request').user
        validated_data['vendor_branch_id'] = self.context.get('branch_id')
        category_uuid = validated_data.pop('category')
        validated_data['category'] = VendorServiceCategory.objects.get(id=category_uuid)
        return super().create(validated_data)


class service_update_serializer(serializers.ModelSerializer):
    class Meta:
        model = VendorService
        fields = ["service", "service_price", "service_duration", "category"]

    def update(self, instance, validated_data):
        if 'category' in validated_data:
            category_uuid = validated_data.pop('category')
            instance.category = VendorServiceCategory.objects.get(id=category_uuid)
        instance.service = validated_data.get("service", instance.service)
        instance.service_duration = validated_data.get("service_duration", instance.service_duration)
        instance.service_price = validated_data.get("service_price", instance.service_price)
        instance.save()
        return instance


class service_name_serializer(serializers.ModelSerializer):
    category = VendorServiceCategorySerializer(read_only=True)
    class Meta:
        model = VendorService
        fields = ["id", "service", "category", "for_men", "for_women"]


class staff_serializer(serializers.ModelSerializer):
    class Meta:
        model = VendorStaff
        fields = "__all__"
        extra_kwargs = {'id': {'read_only': True}, 'vendor_name': {'read_only': True}, 'vendor_branch': {'read_only': True}}

    def create(self, validated_data):
        validated_data['vendor_name'] = self.context.get('request').user
        validated_data['vendor_branch_id'] = self.context.get('branch_id')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.date = dt.date.today()
        instance.save()
        return instance


class staff_attendance_serializer(serializers.Serializer):
    json_data = serializers.ListField(child=serializers.DictField(child=serializers.CharField()))

    def create(self, validated_data):
        for objects in validated_data['json_data']:
            attendance_staff_object = VendorStaffAttendance()
            attendance_staff_object.vendor_name = self.context.get('request').user
            attendance_staff_object.vendor_branch_id = self.context.get('branch_id')
            attendance_staff_object.of_month = objects.get('of_month')
            attendance_staff_object.year = objects.get('year')
            attendance_staff_object.attend = objects.get('attend')
            attendance_staff_object.staff_id = self.context.get('request').query_params.get('staff_id')
            attendance_staff_object.date = objects.get('date')
            attendance_staff_object.save()

        return "ok"


class staff_setting_serializer(serializers.ModelSerializer):
    class Meta:
        model = VendorStaffAttendance
        fields = "__all__"
        extra_kwargs = {'id': {'read_only': True}, 'vendor_name': {'read_only': True}, 'vendor_branch': {'read_only': True},}

    def create(self, validated_data):
        validated_data['signature'] = self.context.get('request').FILES.get('signature')
        validated_data['staff_id'] = validated_data['staff']
        return super().create(validated_data)


class staff_salary_serializer(ModelSerializer):
    staff = staff_serializer()

    class Meta:
        model = StaffSalary
        fields = "__all__"

# class TemplateSerializer(ModelSerializer):


#     class Meta:
#         model = VendorLoyalityTemplates
#         fields = "__all__"


#     def create(self,validated_data):
#         validated_data['user'] = self.context.get('request').user
#         validated_data['vendor_branch_id'] = self.context.get('branch_id')
#         return super().create(validated_data)


class staff_update_earning_deduction_serializer(ModelSerializer):
    json_data = serializers.DictField(child=serializers.CharField())
    slab_data = serializers.ListField(child=serializers.DictField(child=serializers.CharField()))

    class Meta:
        model = StaffSetting
        fields = ["slab_data", "json_data"]

    def create(self, validated_data):
        staff_settings = []

        for i in range(1, 13):
            s = StaffSetting(
                vendor_name=self.context.get('request').user,
                month=i,
                number_of_working_days=validated_data['json_data'].get(str(i)),
            )
            staff_settings.append(s)

        staff_slabs = []
        slab_data = validated_data['slab_data']
        for i in validated_data['slab_data']:
            s = StaffSettingSlab(
                vendor_name=self.context.get('request').user,
                staff_slab=i.get("staff_slab"),
                staff_target_business=i.get("staff_target_business"),
                staff_commision_cap=i.get("staff_commision_cap"),
            )
            staff_slabs.append(s)

        StaffSetting.objects.bulk_create(staff_settings)
        StaffSettingSlab.objects.bulk_create(staff_slabs)

        return validated_data


class user_data_set_serializer(serializers.ModelSerializer):
    class Meta:
        model = SwalookUserProfile
        fields = "__all__"


class staff_serializer_get(serializers.ModelSerializer):
    class Meta:
        model = VendorStaff
        fields = "__all__"

class branch_serializer(serializers.ModelSerializer):
    class Meta:
        model = SalonBranch
        fields = ["id", "staff_name", "branch_name", "password", "admin_password", "staff_url", "admin_url"]
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        validated_data['vendor_name'] = self.context.get('request').user
        validated_data['admin_password'] = str(self.context.get('request').user)[:3] + str(validated_data['branch_name'])[:3]
        validated_data['staff_url'] = validated_data['branch_name'] + "/staff/"
        validated_data['admin_url'] = validated_data['branch_name'] + "/admin/"
        validated_data['password'] = validated_data['password']
        validated_data['branch_name'] = validated_data['branch_name']
        validated_data['staff_name'] = validated_data['staff_name']

        return super().create(validated_data)


class HelpDesk_Serializer(serializers.ModelSerializer):
    class Meta:
        model = HelpDesk
        fields = ["id", "first_name", "last_name", "mobile_no", "email", "message"]
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        validated_data['user'] = self.context.get('request').user
        return super().create(validated_data)


class Inventory_Product_Serializer(serializers.ModelSerializer):
    class Meta:
        model = VendorInventoryProduct
        fields = ["id", "product_name", "product_price", "product_description", "product_id", "stocks_in_hand", "unit"]
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        date = dt.date.today()
        day_of_month = date.day

        if 1 <= day_of_month <= 7:
            validated_data['week'] = "1"
        elif 8 <= day_of_month <= 15:
            validated_data['week'] = "2"
        elif 16 <= day_of_month <= 23:
            validated_data['week'] = "3"
        else:
            validated_data['week'] = "4"

        validated_data['date'] = date
        validated_data['month'] = date.month
        validated_data['year'] = date.year
        validated_data['user'] = self.context.get('request').user
        validated_data['vendor_branch_id'] = self.context.get('branch_id')

        return super().create(validated_data)


class update_inventory_product_serializer(serializers.Serializer):
    product_id = serializers.CharField()
    product_name = serializers.CharField()
    product_description = serializers.CharField()
    product_price = serializers.CharField()
    stocks_in_hand = serializers.CharField()
    unit = serializers.CharField()

    def update(self, instance, validated_data):
        instance.product_id = validated_data.get('product_id', instance.product_id)
        instance.product_name = validated_data.get('product_name', instance.product_name)
        instance.product_description = validated_data.get('product_description', instance.product_description)
        instance.product_price = validated_data.get('product_price', instance.product_price)
        instance.stocks_in_hand = validated_data.get('stocks_in_hand', instance.stocks_in_hand)
        instance.unit = validated_data.get('unit', instance.unit)
        instance.save()
        return instance

    def create(self, validated_data):
        instance = VendorInventoryProduct.objects.get(id=self.context.get('id'))
        return self.update(instance, validated_data)


class Inventory_Product_Invoice_Serializer(serializers.ModelSerializer):
    class Meta:
        model = VendorInventoryInvoice
        fields = ["id", "product_price", "product_quantity", "total_prise", "total_quantity", "loyality_points_deducted", "total_tax", "total_discount", "grand_total", "total_cgst", "total_sgst", "gst_number", "slno", "unit"]
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        date = dt.date.today()
        mon = dt.date.today()

        if 1 <= mon.day <= 7:
            validated_data['week'] = "1"
        elif 8 <= mon.day <= 15:
            validated_data['week'] = "2"
        elif 16 <= mon.day <= 23:
            validated_data['week'] = "3"
        else:
            validated_data['week'] = "4"

        validated_data['date'] = date
        validated_data['month'] = mon.month
        validated_data['year'] = mon.year
        validated_data['user'] = self.context.get('request').user
        validated_data['vendor_branch_id'] = self.context.get('branch_id')

        if int(validated_data['grand_total']) > 100:
            try:
                customer = VendorCustomers.objects.get(mobile_no=validated_data['mobile_no'])
                clp_object = VendorCustomerLoyalityPoints.objects.get(user=self.context.get('request').user, branch_name=validated_data['branch_name'], program_type=customer.membership_type)
                validated_data['customer'] = clp_object
                validated_data['loyality_points'] = int(validated_data['grand_total']) / customer.membership_type.points_hold
                validated_data['grand_total'] = int(validated_data['grand_total']) - validated_data['loyality_points_deducted']
                if validated_data['loyality_points_deducted']:
                    clp_object.current_customer_points -= int(validated_data['loyality_points_deducted'])
                    clp_object.current_customer_points += int(validated_data['loyality_points'])
                    clp_object.save()
                    ledger_object = VendorCustomerLoyalityLedger(
                        vendor_branch_id=validated_data['vendor_branch_id'],
                        user=self.context.get('request').user,
                        customer=clp_object,
                        point_spend=validated_data['loyality_points_deducted'],
                        point_available=clp_object.current_customer_points,
                        inventory_invoice_obj=validated_data['slno'],
                        date=dt.date.today(),
                        month=mon.month,
                        year=mon.year,
                        week=validated_data["week"]
                    )
                    ledger_object.save()
            except Exception:
                pass

        product = VendorInventoryProduct.objects.get(product_id=validated_data['product_id'])
        product.stocks_in_hand -= int(validated_data['product_quantity'])
        product.save()

        return super().create(validated_data)


class LoyalityPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorCustomerLoyalityPoints
        fields = "__all__"
        extra_kwargs = {'id': {'read_only': True}}


# class CouponSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = VendorCoupon
#         fields = "__all__"
#         extra_kwargs = {'id': {'read_only': True}}


#     def create(self,arg):
#         arg['user'] = self.context.get('request').user
#         arg['vendor_branch_id'] = self.context.get('branch_id')

#         return super().create(arg)


#     def update(self, instance, validated_data):
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         instance.save()
#         return instance

class VendorCustomerLoyalityProfileSerializer_get(serializers.ModelSerializer):
    loyality_profile = LoyalityPointsSerializer(read_only=True)
    # coupon = CouponSerializer(read_only=True)

    class Meta:
        model = VendorCustomers
        fields = "__all__"
        extra_kwargs = {'id': {'read_only': True}}


class billing_serializer_get(serializers.ModelSerializer):
    vendor_customers_profile = VendorCustomerLoyalityProfileSerializer_get(read_only=True)

    class Meta:
        model = VendorInvoice
        fields = "__all__"


class VendorCustomerLoyalityProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorCustomers
        fields = ["id", "name", "mobile_no", "email", "membership", "d_o_a", "d_o_b",]
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        validated_data['user'] = self.context.get('request').user
        validated_data['vendor_branch_id'] = self.context.get('branch_id')
        validated_data['membership_type'] = VendorLoyalityProgramTypes.objects.get(program_type=validated_data['membership'], vendor_branch_id=self.context.get('branch_id'), user=self.context.get('request').user)

        obj_loyality = VendorCustomerLoyalityPoints()
        clp_object = VendorLoyalityProgramTypes.objects.get(program_type=validated_data['membership'], vendor_branch_id=self.context.get('branch_id'), user=self.context.get('request').user)
        obj_loyality.current_customer_points = 0

        def get_date_after_six_months(input_date_str, month):
            input_date = datetime.strptime(input_date_str, '%Y-%m-%d')
            date_after_six_months = input_date + relativedelta(months=month)
            return date_after_six_months.strftime('%Y-%m-%d')

        date = dt.date.today()
        result = get_date_after_six_months(str(date), int(clp_object.expiry_duration) + 1)
        obj_loyality.issue_date = dt.date.today()
        obj_loyality.expire_date = result
        obj_loyality.user = self.context.get('request').user
        obj_loyality.vendor_branch_id = self.context.get('branch_id')
        obj_loyality.customer_id = validated_data['mobile_no']
        obj_loyality.save()
        validated_data['loyality_profile'] = obj_loyality

        return super().create(validated_data)


class VendorLoyalityTypeSerializer_get(serializers.ModelSerializer):
    class Meta:
        model = VendorLoyalityProgramTypes
        fields = "__all__"
        extra_kwargs = {'id': {'read_only': True}}


class VendorLoyalityTypeSerializer(serializers.Serializer):
    json_data = serializers.ListField(child=serializers.DictField(child=serializers.CharField()))

    def create(self, validated_data):
        types = validated_data['json_data'][0].get('type')
        points = validated_data['json_data'][0].get('points')
        expiry = validated_data['json_data'][0].get('expiry')
        charge = validated_data['json_data'][0].get('charges')
        discount = validated_data['json_data'][0].get('discount')
        limit = validated_data['json_data'][0].get('limit')
        active = validated_data['json_data'][0].get('active')
        if discount:
            clp = VendorLoyalityProgramTypes(
                program_type=types,
                expiry_duration=expiry,
                points_hold = 0,
                discount = discount,
                limit = limit,
                price=charge,
                active=active,
                user=self.context.get('request').user,
                vendor_branch_id=self.context.get('branch_id')
            )
            clp.save()
        else:
            clp = VendorLoyalityProgramTypes(
            program_type=types,
            expiry_duration=expiry,
            points_hold=points,
            discount = 0,
            limit = 0,
            price=charge,
            active=active,
            user=self.context.get('request').user,
            vendor_branch_id=self.context.get('branch_id')
            )
            clp.save()
        return "ok"


class Vendor_Type_Loyality_Update_Serializer(serializers.Serializer):
    json_data = serializers.ListField(child=serializers.DictField(child=serializers.CharField()))

    def create(self, validated_data):
        types = validated_data['json_data'][0].get('type')
        points = validated_data['json_data'][0].get('points')
        expiry = validated_data['json_data'][0].get('expiry')
        charge = validated_data['json_data'][0].get('charges')
        discount = validated_data['json_data'][0].get('discount')
        limit = validated_data['json_data'][0].get('limit')
        active = validated_data['json_data'][0].get('active')
        clp = VendorLoyalityProgramTypes.objects.get(id=self.context.get('id'))
        if discount:
            clp.program_type = types
            clp.expiry_duration = expiry
            clp.discount = discount
            clp.limit = limit
            clp.points_hold = 0
            clp.price = charge
            clp.user = self.context.get('request').user
            clp.vendor_branch_id = self.context.get('branch_id')
            clp.save()
            return "ok"
        else:

            clp.program_type = types
            clp.expiry_duration = expiry
            clp.points_hold = points
            clp.discount = 0
            clp.limit = 0
            clp.price = charge
            clp.user = self.context.get('request').user
            clp.vendor_branch_id = self.context.get('branch_id')
            clp.save()
            return "ok"


class loyality_customer_update_serializer(serializers.Serializer):
    name = serializers.CharField()
    mobile_no = serializers.CharField()
    email = serializers.CharField()

    def create(self, validated_data):
        clp_obj = VendorCustomers.objects.get(id=self.context.get('id'))
        clp_obj.name = validated_data['name']
        clp_obj.mobile_no = validated_data['mobile_no']
        clp_obj.email = validated_data['email']
        clp_obj.save()
        return "ok"


class update_minuimum_amount_serializer(serializers.Serializer):
    minimum_amount = serializers.IntegerField()

    def create(self, validated_data):
        user = SalonBranch.objects.get(id=self.context.get('branch_id'))
        user.minimum_purchase_loyality = validated_data['minimum_amount']
        user.save()
        return user


class VendorExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorExpenseCategory
        fields = ['id', 'vendor_expense_type']
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        validated_data['user'] = self.context.get('request').user
        validated_data['vendor_branch_id'] = self.context.get('branch_id')
        return super().create(validated_data)


class VendorServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorServiceCategory
        fields = ['id', 'service_category']
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        validated_data['user'] = self.context.get('request').user
        validated_data['vendor_branch_id'] = self.context.get('branch_id')
        return super().create(validated_data)


class VendorExpenseSerializer(serializers.ModelSerializer):
    expense_category = VendorExpenseCategorySerializer(many=True, read_only=True)
    inventory_item = serializers.ListField(child=serializers.DictField(child=serializers.CharField()))

    class Meta:
        model = VendorExpense
        fields = ['id', 'expense_type', 'inventory_item', 'expense_account', 'expense_category', 'expense_amount', 'invoice_id', "date", "comment"]
        extra_kwargs = {'id': {'read_only': True}}

    def get_week_number(self, day):
        if 1 <= day <= 7:
            return "1"
        elif 8 <= day <= 15:
            return "2"
        elif 16 <= day <= 23:
            return "3"
        else:
            return "4"

    def create(self, validated_data):
        date = dt.date.today()
        validated_data['user'] = self.context.get('request').user
        validated_data['vendor_branch_id'] = self.context.get('branch_id')
        validated_data['month'] = date.month
        validated_data['week'] = self.get_week_number(date.day)
        validated_data['year'] = date.year
        return super().create(validated_data)


class VendorExpenseSerializer_get(serializers.ModelSerializer):
    expense_category = VendorExpenseCategorySerializer(many=True, read_only=True)

    class Meta:
        model = VendorExpense
        fields = "__all__"


