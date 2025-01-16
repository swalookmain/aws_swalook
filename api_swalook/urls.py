"""api_swalook URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.static import serve
from django.contrib import admin
from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from _api_.views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns # new

v = Vendor_loyality_customer_profile()
#/api/items/?id=id&branch_name=branch_name
urlpatterns = [
    path('silk/', include('silk.urls', namespace='silk')),
    path('swalook_admin_sql/', admin.site.urls),
    path('update_file/', update_files_pull.as_view()),
    path("restart_server/", restart_server.as_view()),
    # path('swalook_token_ii091/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('swalook_token_ii091/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/swalook/endpoints/',showendpoint.as_view()),
    path('api/swalook/create_account/',VendorSignin.as_view()),
    path('api/swalook/centralized/login/',Centralized_login.as_view()),
    path('api/swalook/login/',vendor_login.as_view()),
    path('api/swalook/staff/login/',staff_login.as_view()),
    path('api/swalook/admin/login/',admin_login.as_view()),

    path('api/swalook/billing/',vendor_billing.as_view()),
    path('api/swalook/save-pdf/',vendor_billing_pdf.as_view()),
    path('api/swalook/appointment/',VendorAppointments.as_view()),
    path('api/swalook/view-appointment/',VendorAppointments.as_view()), #
    path('api/swalook/edit/appointment/',edit_appointment.as_view()), #
    path('api/swalook/delete/appointment/',delete_appointment.as_view()), #
    path('api/swalook/delete/invoice/',Delete_invoice.as_view()), #
    path('api/swalook/edit/profile/',edit_profile.as_view()), #
    path('api/swalook/preset-day-appointment/',present_day_appointment.as_view()),
    path('api/swalook/services/',VendorServices.as_view()),
    path('api/swalook/add/services/',Add_vendor_service.as_view()),
    path('api/swalook/table/services/',Table_service.as_view()),
    path('api/swalook/edit/services/',Edit_service.as_view()), #
    path('api/swalook/delete/services/',Delete_service.as_view()), #
    path('api/swalook/get_specific/appointment/',get_specific_appointment.as_view()), #
    path('api/swalook/get_specific_slno/',get_slno.as_view()),
    path('api/swalook/get_current_user/',get_current_user_profile.as_view()), #

    path('api/swalook/get_present_day_bill/',get_present_day_bill.as_view()),
    path('api/swalook/get_bill_data/',get__bill.as_view()), #
    path('api/swalook/get_branch_data/',render_branch_data.as_view()), #

    path('api/swalook/help_desk/',help_desk.as_view()),

    path('api/swalook/salonbranch/',VendorBranch.as_view()),
    path('api/swalook/edit/salonbranch/',edit_branch.as_view()), #
    path('api/swalook/delete/salonbranch/',delete_branch.as_view()),#
    path('api/swalook/verify/',user_verify.as_view()), #
    path('api/swalook/send/otp/',ForgotPassword.as_view()), #
    path('api/swalook/verify/',ForgotPassword.as_view()), #
    path('api/swalook/analysis/month/business/_01/',BusniessAnalysiss.as_view()),
    path('api/swalook/inventory/product/',Add_Inventory_Product.as_view()),
    path('api/swalook/inventory/invoice/',Bill_Inventory.as_view()),
    path('api/swalook/inventory/products/',Inventory_Products_get.as_view()), #
    path('api/swalook/loyality_program/customer/',Vendor_loyality_customer_profile.as_view()), #
    path('api/swalook/loyality_program/customer/get_details/',Get_Profile.as_view()), #
    path('api/swalook/loyality_program/',Vendor_loyality_type_add.as_view()),
    path('api/swalook/loyality_program/view/',Vendor_loyality_type_add_get.as_view()), #
    path('api/swalook/loyality_program/verify/',Check_Loyality_Customer_exists.as_view()), #
    path('api/swalook/loyality_program/types/',MembershipTypesLoyality_get.as_view()), #

    path('api/swalook/loyality_program/get_minimum_value/',update_minimum_amount.as_view()), #
    path('api/swalook/staff/',vendor_staff.as_view()), #
    path('api/swalook/staff/setting/',vendor_staff_setting_slabs.as_view()), #
    path('api/swalook/staff/attendance/',vendor_staff_attendance.as_view()), #
    path('api/swalook/staff/generate-payslip/',salary_disburse.as_view()), #
    path('api/swalook/business-analysis/week-customer/',Sales_Per_Customer.as_view()), #
    path('api/swalook/business-analysis/month-customer/',Sales_Per_Customer_monthly.as_view()), #
    path('api/swalook/business-analysis/daily-customer/', Sales_in_a_day_by_customer.as_view()), #
    path('api/swalook/business-analysis/products/', ProductAnalysis.as_view()), #
    path('api/swalook/business-analysis/month/',Sales_in_a_month.as_view()), #
    path('api/swalook/business-analysis/year/',Sales_in_a_year.as_view()), #
    path('api/swalook/business-analysis/week/',Sales_in_a_week.as_view()), #
    path('api/swalook/business-analysis/time/',Sales_in_a_day_by_customer_time.as_view()), #
    path('api/swalook/business-analysis/service/',service_analysis.as_view()), #
    path('api/swalook/business-analysis/headers/',busniess_headers.as_view()), #
    path('api/swalook/get-customer-bill-app-data/',GetCustomerBillAppDetails.as_view()), #
 
    path('api/swalook/expense_management/',expense_management.as_view()), #
    path('api/swalook/expense_category/',expense_category.as_view()), #
    path('api/swalook/service_category/',service_category.as_view()), #
    path('api/swalook/staff-header-mode-of-payment/',top5_header_staff_revenue.as_view()), #
    path('api/swalook/test-error/',Table_servicess.as_view()), #


    re_path(r'^media/{}/(?P<path>.*)$'.format(settings.MEDIA_URL_PREFIX), serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/{}/(?P<path>.*)$'.format(settings.STATIC_URL_PREFIX), serve, {'document_root': settings.STATIC_URL}),





]


