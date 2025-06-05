from django.contrib.auth.models import User
from django.core import validators
from django.db import models
import datetime as dt
import uuid


class SalonBranch(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    vendor_name = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    staff_name = models.CharField(max_length=255)
    branch_name = models.CharField(max_length=255)
    password = models.CharField(max_length=20, blank=True)
    admin_password = models.CharField(max_length=20, blank=True)
    staff_url = models.CharField(max_length=255)
    admin_url = models.CharField(max_length=255)
    minimum_purchase_loyality = models.IntegerField(default=40, null=True)

    class Meta:
        ordering = ['vendor_name']
        verbose_name = "Vendor Branch"
        indexes = [
            models.Index(fields=['vendor_name', 'branch_name']),
        ]

    def __str__(self) -> str:
        return str(self.branch_name)


class SwalookUserProfile(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    salon_name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)
    profile_pic = models.ImageField(blank=True, null=True)
    mobile_no = models.CharField(max_length=10, db_index=True)
    email = models.EmailField(blank=True, db_index=True)
    vendor_id = models.CharField(max_length=6)
    invoice_limit = models.IntegerField(default=0, null=True)
    account_created_date = models.DateField(null=True)
    user_ip = models.CharField(max_length=200, blank=True)
    gst_number = models.CharField(max_length=20, blank=True)
    pan_number = models.CharField(max_length=20, blank=True)
    pincode = models.CharField(max_length=20, blank=True)
    number_of_staff = models.IntegerField(default=0)
    s_gst_percent = models.CharField(max_length=30)
    c_gst_percent = models.CharField(max_length=30)
    current_billslno = models.CharField(max_length=50)
    appointment_limit = models.IntegerField(default=0, null=True)
    invoice_generated = models.IntegerField()
    appointment_generated = models.IntegerField()
    enc_pwd = models.CharField(max_length=400)
    branch_limit = models.IntegerField(default=1, null=True)
    branches_created = models.IntegerField(default=0, null=True)

    class Meta:
        ordering = ['salon_name']
        verbose_name = "Vendor Profile"
        unique_together = [["salon_name", "mobile_no"]]
        indexes = [
            models.Index(fields=['salon_name', 'mobile_no']),
        ]

    def __str__(self):
        return str(self.salon_name)


class VendorLoyalityProgramTypes(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    program_type = models.CharField(max_length=255)
    price = models.IntegerField()
    expiry_duration = models.IntegerField()
    points_hold = models.IntegerField(blank=True)
    discount = models.IntegerField(blank=True)
    limit = models.IntegerField(blank=True)
    active = models.BooleanField(default=True,blank=True)


    class Meta:
        indexes = [
            models.Index(fields=['user', 'vendor_branch', 'program_type']),
        ]

    def __str__(self) -> str:
        return str(self.user)


class VendorCustomerLoyalityPoints(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_index=True)
    customer_id = models.CharField(max_length=25555)
    current_customer_points = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    issue_date = models.DateField(null=True, blank=True)
    expire_date = models.DateField(blank=True, null=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    active = models.BooleanField(default=True,blank=True)

    class Meta:
        ordering = ['user']
        verbose_name = "Vendor Customers Points"
        indexes = [
            models.Index(fields=['user', 'vendor_branch', 'customer_id']),

        ]
class VendorCoupon(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    coupon_name = models.CharField(max_length=160)
    coupon_price = models.IntegerField()
    coupon_points_hold = models.IntegerField()
    active = models.BooleanField(default=True,blank=True)
    class Meta:
        ordering = ['coupon_name']
        verbose_name = "Vendor Coupons"
        indexes = [
            models.Index(fields=['user', 'vendor_branch', 'coupon_name']),
        ]

    def __str__(self):
        return f"coupon {self.coupon_name} from branch {self.vendor_branch}"

class CustomerCoupon(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    customer_id = models.CharField(max_length=10000)
    coupon_name = models.ForeignKey(VendorCoupon, on_delete=models.SET_NULL, null=True, db_index=True)
    issue_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True,blank=True)
    
    expiry_date = models.DateField()

    class Meta:
        ordering = ['coupon_name']
        verbose_name = "Vendor Coupons"
        indexes = [
            models.Index(fields=['user', 'vendor_branch', 'coupon_name']),
        ]

    def __str__(self):
        return f"coupon {self.coupon_name} from customer {self.vendor_branch}"




class VendorCustomers(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    loyality_profile = models.ManyToManyField(VendorCustomerLoyalityPoints,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_index=True)
    name = models.CharField(max_length=30, blank=True, null=True)
    mobile_no = models.CharField(max_length=30, blank=True, null=True)
    d_o_b = models.CharField(max_length=30, blank=True, null=True)
    d_o_a = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=30, blank=True)
    membership = models.CharField(max_length=30, blank=True, null=True)
    membership_type = models.ManyToManyField(VendorLoyalityProgramTypes,blank=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    coupon = models.ManyToManyField(CustomerCoupon,blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Vendor Customers"
        indexes = [
            models.Index(fields=['user', 'vendor_branch', 'mobile_no',]),
        ]

    def __str__(self):
        return f"user {self.name} from branch {self.vendor_branch}"


class VendorServiceCategory(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_index=True)
    service_category = models.CharField(max_length=300, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)

    class Meta:
        ordering = ['service_category']
        verbose_name = "Vendor Service Category"
        indexes = [
            models.Index(fields=['user', 'vendor_branch', 'service_category']),
        ]

    def __str__(self):
        return str(self.service_category)


class VendorService(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_index=True)
    category = models.ForeignKey(VendorServiceCategory, on_delete=models.SET_NULL, null=True, db_index=True)
    service = models.CharField(max_length=300, db_index=True)
    service_price = models.CharField(max_length=30)
    service_duration = models.CharField(max_length=30, blank=True)
    for_men = models.BooleanField(blank=True)
    for_women = models.BooleanField(blank=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)

    class Meta:
        ordering = ['service']
        verbose_name = "Vendor Service"
        indexes = [
            models.Index(fields=['user', 'vendor_branch', 'service']),
        ]

    def __str__(self):
        return str(self.service)


class VendorInvoice(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    slno = models.CharField(max_length=50, blank=True)
    customer_name = models.CharField(max_length=255)
    address = models.CharField(max_length=200, blank=True)
    mobile_no = models.CharField(max_length=10, blank=True)
    email = models.CharField(max_length=50, blank=True)
    services = models.CharField(max_length=50000, blank=True)
    service_by = models.CharField(max_length=40000, blank=True)
    total_prise = models.DecimalField(default=0, max_digits=40, decimal_places=2, blank=True)
    total_tax = models.DecimalField(default=0, max_digits=40, decimal_places=2, blank=True)
    total_discount = models.DecimalField(max_digits=40, decimal_places=2, default=0, blank=True)
    time_stamp = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    gst_number = models.CharField(max_length=20, blank=True)
    total_quantity = models.IntegerField(default=0)
    total_cgst = models.DecimalField(default=0, max_digits=40, decimal_places=2, blank=True)
    total_sgst = models.DecimalField(default=0, max_digits=40, decimal_places=2, blank=True)
    grand_total = models.DecimalField(default=0, max_digits=40, decimal_places=2, blank=True)
    vendor_name = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_index=True)
    date = models.DateField()
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    vendor_customers_profile = models.ForeignKey(VendorCustomers, on_delete=models.SET_NULL, null=True)
    json_data = models.JSONField(default=list, blank=True)
    new_mode= models.JSONField(default=list, blank=True)
    comment = models.CharField(max_length=255, blank=True)
    mode_of_payment = models.CharField(max_length=200, blank=True)
    loyalty_points = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    loyalty_points_deducted = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    coupon_points_used = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    pdf_url = models.TextField(blank=True,null=True)
    
   

    class Meta:
        ordering = ['date']
        verbose_name = "Vendor Invoice"
        indexes = [
            models.Index(fields=['vendor_name', 'vendor_branch', 'date']),
        ]

    def __str__(self):
        return str(self.vendor_name)


class VendorPdf(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    invoice = models.CharField(max_length=400)
    mobile_no = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="pdf", blank=True, null=True)
    date = models.DateField()
    vendor_email = models.CharField(max_length=255)
    vendor_password = models.CharField(max_length=255)
    pdf_url = models.TextField(blank=True,null=True)

    class Meta:
        ordering = ['date']
        verbose_name = "Vendor Invoice Pdf"
        indexes = [
            models.Index(fields=['vendor_branch', 'date']),
        ]

    def __str__(self):
        return str(self.vendor_branch)


class VendorAppointment(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    vendor_name = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    customer_name = models.CharField(max_length=255)
    services = models.CharField(max_length=255)
    service_by = models.CharField(max_length=255)
    booking_date = models.CharField(max_length=255)
    date = models.DateField()
    booking_time = models.CharField(max_length=255)
    email = models.CharField(max_length=50,blank=True,null=True)
    mobile_no = models.CharField(max_length=10, blank=True)
    comment = models.CharField(max_length=255, blank=True)
    d_o_b = models.CharField(max_length=30, blank=True, null=True)
    d_o_a = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        ordering = ['booking_date']
        verbose_name = "Vendor Appointment"
        indexes = [
            models.Index(fields=['vendor_name', 'vendor_branch', 'booking_date']),
        ]

    def __str__(self):
        return str(self.vendor_name)


class VendorStaff(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    vendor_name = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    staff_name = models.CharField(max_length=400)
    mobile_no = models.CharField(max_length=13, null=True, blank=True)
    staff_role = models.CharField(max_length=400)
    staff_salary_monthly = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    base = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    house_rent_allownance = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    meal_allowance = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    incentive_pay = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    pf = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    staff_slab = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    staff_target_business = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    staff_commision_cap = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    staff_joining_date = models.DateField(blank=True, null=True)
    staff_provident_fund = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    staff_professional_tax = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    business_of_the_current_month = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2, default=0)

    class Meta:
        indexes = [
            models.Index(fields=['vendor_name', 'vendor_branch', 'staff_name']),
        ]

class SalesTargetSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_target = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_target = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    membership_coupon_target = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    overall_target = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    staff_targets = models.TextField(blank=True,null=True)
    # staff_target = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # commission_cap = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.CharField(max_length=200, blank=True,null=True)
    month = models.CharField(max_length=200, blank=True,null=True)
    year = models.CharField(max_length=200, blank=True,null=True)
    updated_at = models.CharField(max_length=200, blank=True,null=True)
    vendor_name = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    

    
    
class VendorStaffAttendance(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    vendor_name = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    of_month = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    date = models.CharField(max_length=200, blank=True)
    attend = models.BooleanField(default=False, blank=True, null=True)
    leave = models.BooleanField(default=False, blank=True, null=True)
    staff = models.ForeignKey(VendorStaff, on_delete=models.CASCADE, null=True)
    in_time =  models.CharField(max_length=200, blank=True)
    out_time =  models.CharField(max_length=200, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['vendor_name', 'vendor_branch', 'date']),
        ]


class StaffSalary(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    vendor_name = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    staff = models.ForeignKey(VendorStaff, on_delete=models.CASCADE, null=True)
    of_month = models.IntegerField(blank=True, null=True)
    salary_payble_amount = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    business_of_the_month = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    year = models.IntegerField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['vendor_name', 'vendor_branch', 'of_month']),
        ]


class StaffSetting(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    vendor_name = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    number_of_working_days = models.IntegerField()
    signature = models.FileField(upload_to="staff-sign", blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    

    class Meta:
        indexes = [
            models.Index(fields=['vendor_name', 'vendor_branch', 'month']),
        ]
class StaffAttendanceTime(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    vendor_name = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    in_time = models.CharField(max_length=200)
    out_time = models.CharField(max_length=200)
    

class StaffSettingSlab(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    vendor_name = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    staff_slab = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    staff_target_business = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    staff_commision_cap = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=['vendor_name', 'vendor_branch']),
        ]


class BusinessAnalysis(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    monthly_analysis = models.ImageField(upload_to="analysis", null=True, blank=True)
    month = models.CharField(max_length=400)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'month']),
        ]

    def __str__(self) -> str:
        return str(self.user)


class HelpDesk(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    first_name = models.CharField(max_length=400)
    last_name = models.CharField(max_length=400)
    email = models.EmailField(max_length=400)
    mobile_no = models.CharField(max_length=400)
    message = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=['user', 'email']),
        ]

    def __str__(self) -> str:
        return str(self.user)

class VendorProductCategory(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_index=True)
    product_category = models.CharField(max_length=300, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)

    class Meta:
        ordering = ['product_category']
        verbose_name = "Vendor Product Category"
        indexes = [
            models.Index(fields=['user', 'vendor_branch', 'product_category']),
        ]

    def __str__(self):
        return str(self.product_category)

class VendorInventoryProduct(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    product_id = models.CharField(max_length=400)
    product_name = models.CharField(max_length=400)
    product_price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    product_description = models.TextField()
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    category = models.ForeignKey(VendorProductCategory, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
    stocks_in_hand = models.IntegerField(default=0)
    
    unit = models.CharField(max_length=400)
    date = models.DateField()
    expiry_date = models.DateField()
    month = models.CharField(max_length=30, null=True, blank=True)
    week = models.CharField(max_length=30, null=True, blank=True)
    year = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'vendor_branch', 'product_name']),
        ]

    def __str__(self) -> str:
        return str(self.product_name)


class VendorInventoryInvoice(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    slno = models.CharField(max_length=400)
    customer = models.ForeignKey(VendorCustomers, on_delete=models.SET_NULL, null=True)
    mobile_no = models.CharField(max_length=13, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    product = models.ForeignKey(VendorInventoryProduct, on_delete=models.SET_NULL, null=True)
    unit = models.CharField(max_length=255)
    product_price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    product_quantity = models.IntegerField()
    loyalty_points = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    loyalty_points_deducted = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    total_price = models.DecimalField(default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    total_tax = models.DecimalField(default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    total_discount = models.DecimalField(default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    total_quantity = models.IntegerField(default=0)
    total_cgst = models.DecimalField(default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    total_sgst = models.DecimalField(default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    grand_total = models.DecimalField(default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    date = models.DateField()
    month = models.CharField(max_length=30, null=True, blank=True)
    week = models.CharField(max_length=30, null=True, blank=True)
    year = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'vendor_branch', 'date']),
        ]

    def __str__(self) -> str:
        return str(self.product)


class VendorCustomerLoyalityLedger(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    customer = models.ForeignKey(VendorCustomerLoyalityPoints, on_delete=models.SET_NULL, null=True)
    point_spend = models.IntegerField()
    point_available = models.IntegerField()
    point_gain = models.IntegerField()
    invoice_obj = models.CharField(max_length=400)
    inventory_invoice_obj = models.CharField(max_length=400)
    date = models.DateField()
    month = models.CharField(max_length=30, null=True, blank=True)
    week = models.CharField(max_length=30, null=True, blank=True)
    year = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'vendor_branch', 'date']),
        ]

    def __str__(self) -> str:
        return str(self.user)


class VendorExpenseCategory(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    vendor_expense_type = models.CharField(max_length=400)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'vendor_branch', 'vendor_expense_type']),
        ]

    def __str__(self) -> str:
        return str(self.vendor_expense_type)


class VendorExpense(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    expense_type = models.CharField(max_length=200, null=True, blank=True)
    inventory_item = models.CharField(max_length=200, null=True, blank=True)
    expense_account = models.CharField(max_length=200, null=True, blank=True)
    expense_category = models.ManyToManyField(VendorExpenseCategory, blank=True)
    expense_amount = models.DecimalField(default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    due_amount = models.DecimalField(default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    invoice_id = models.TextField(null=True, blank=True)  
    amount_paid = models.TextField(null=True, blank=True)  
    completed_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    date = models.DateField()
    month = models.CharField(max_length=30, null=True, blank=True)
    week = models.CharField(max_length=30, null=True, blank=True)
    year = models.CharField(max_length=30, null=True, blank=True)
    comment = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'vendor_branch', 'date']),
        ]


# class VendorLoyalityTemplates(models.Model):
#     id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
#     vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
#     text = models.CharField(max_length=8000, null=True, blank=True)

#     class Meta:
#         indexes = [
#             models.Index(fields=['user', 'vendor_branch']),
#         ]



class VendorEnquery(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    query_for = models.CharField(max_length=200, null=True, blank=True)
    customer_name = models.CharField(max_length=200, null=True, blank=True)
    mobile_no = models.CharField(max_length=200, null=True, blank=True)
    comment = models.CharField(max_length=200, null=True, blank=True)




class Picture(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    image_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='clp')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image_name


class IG_FB_shared_picture(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    image = models.ImageField(upload_to='clp')
    uploaded_at = models.DateTimeField(auto_now_add=True)



class VendorExpense(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    vendor_branch = models.ForeignKey(SalonBranch, on_delete=models.SET_NULL, null=True, db_index=True)
    vendor_name = models.CharField(max_length=200, null=True, blank=True)
    vendor_address = models.CharField(max_length=200, null=True, blank=True)
    vendor_mobile_no = models.CharField(max_length=200, null=True, blank=True)
    vendor_email = models.CharField(max_length=200, null=True, blank=True)






    

    
    
    

   
