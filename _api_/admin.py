from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(VendorService)
admin.site.register(VendorServiceCategory)
admin.site.register(VendorExpenseMainCategory)
admin.site.register(VendorExpenseCategory)
admin.site.register(VendorCoupon)
admin.site.register(VendorPdf)
admin.site.register(VendorAppointment)
admin.site.register(VendorInvoice)
admin.site.register(VendorStaff)
admin.site.register(SwalookUserProfile)
admin.site.register(SalonBranch)
admin.site.register(VendorLoyalityProgramTypes)
admin.site.register(VendorCustomers)
admin.site.register(StaffSetting)
admin.site.register(StaffSettingSlab)
admin.site.register(VendorStaffAttendance)
admin.site.register(combo_services)

admin.site.register(VendorInventoryProduct)
admin.site.register(VendorCustomerLoyalityPoints)

