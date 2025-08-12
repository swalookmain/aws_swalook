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
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

v = Vendor_loyality_customer_profile()
urlpatterns = [
    path('silk/', include('silk.urls', namespace='silk')),
    path('swalook_admin_sql/', admin.site.urls, name='admin'),
    path('update_file/', update_files_pull.as_view(), name='update_file'),
    path("restart_server/", restart_server.as_view(), name='restart_server'),
    # path('swalook_token_ii091/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('swalook_token_ii091/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/swalook/endpoints/', showendpoint.as_view(), name='show_endpoints'),
    path('api/swalook/create_account/', VendorSignin.as_view(), name='create_account'),
    path('api/swalook/centralized/login/', Centralized_login.as_view(), name='centralized_login'),
    path('api/swalook/login/', vendor_login.as_view(), name='vendor_login'),
    path('api/swalook/staff/login/', staff_login.as_view(), name='staff_login'),
    path('api/swalook/admin/login/', admin_login.as_view(), name='admin_login'),
    path('api/swalook/billing/', vendor_billing.as_view(), name='vendor_billing'),

    path('api/swalook/save-pdf/', vendor_billing_pdf.as_view(), name='save_pdf'),
    path('api/swalook/appointment/', VendorAppointments.as_view(), name='appointment'),
    
    path('api/swalook/appointment/daily/', DailyAppointmentsView.as_view(), name='appointment-daily'),
    path('api/swalook/appointment/current-week/', WeeklyAppointmentsView.as_view(), name='appointment-week'),
    path('api/swalook/appointment/previous-week/', PreviousWeekAppointmentsView.as_view(), name='appointment-previous-week'),
    path('api/swalook/appointment/staff/', AppointmentsBystaffView.as_view(), name='appointment-staff-week'),

    
    path('api/swalook/view-appointment/', VendorAppointments.as_view(), name='view_appointment'),
    path('api/swalook/edit/appointment/', edit_appointment.as_view(), name='edit_appointment'),
    path('api/swalook/delete/appointment/', delete_appointment.as_view(), name='delete_appointment'),
    path('api/swalook/delete/invoice/', Delete_invoice.as_view(), name='delete_invoice'),
    path('api/swalook/edit/profile/', edit_profile.as_view(), name='edit_profile'),
    path('api/swalook/preset-day-appointment/', present_day_appointment.as_view(), name='preset_day_appointment'),
    path('api/swalook/services/', VendorServices.as_view(), name='services'),
    path('api/swalook/add/services/', Add_vendor_service.as_view(), name='add_services'),
    path('api/swalook/table/services/', Table_service.as_view(), name='table_services'),
    path('api/swalook/edit/services/', Edit_service.as_view(), name='edit_services'),
    path('api/swalook/delete/services/', Delete_service.as_view(), name='delete_services'),
    path('api/swalook/get_specific/appointment/', get_specific_appointment.as_view(), name='get_specific_appointment'),
    path('api/swalook/get_specific_slno/', get_slno.as_view(), name='get_specific_slno'),
    path('api/swalook/get_current_user/', get_current_user_profile.as_view(), name='get_current_user'),
    path('api/swalook/get_present_day_bill/', get_present_day_bill.as_view(), name='get_present_day_bill'),
    path('api/swalook/get_bill_data/', get__bill.as_view(), name='get_bill_data'),
    path('api/swalook/get_branch_data/', render_branch_data.as_view(), name='get_branch_data'),
    path('api/swalook/help_desk/', help_desk.as_view(), name='help_desk'),
    path('api/swalook/salonbranch/', VendorBranch.as_view(), name='salonbranch'),
    path('api/swalook/edit/salonbranch/', edit_branch.as_view(), name='edit_salonbranch'),
    path('api/swalook/delete/salonbranch/', delete_branch.as_view(), name='delete_salonbranch'),
    path('api/swalook/verify/', user_verify.as_view(), name='verify'),
    path('api/swalook/send/otp/', ForgotPassword.as_view(), name='send_otp'),
    path('api/swalook/verify/', ForgotPassword.as_view(), name='forgot_password_verify'),
    path('api/swalook/analysis/month/business/_01/', BusniessAnalysiss.as_view(), name='business_analysis_month'),
    path('api/swalook/inventory/product/', Add_Inventory_Product.as_view(), name='inventory_product'),
    path('api/swalook/inventory/invoice/', Bill_Inventory.as_view(), name='inventory_invoice'),
    path('api/swalook/inventory/products/', Inventory_Products_get.as_view(), name='inventory_products'),
    path('api/swalook/loyality_program/customer/', Vendor_loyality_customer_profile.as_view(), name='loyality_program_customer'),
    path('api/swalook/loyality_program/customer/get_details/', Get_Profile.as_view(), name='loyality_program_customer_details'),
    path('api/swalook/loyality_program/', Vendor_loyality_type_add.as_view(), name='loyality_program'),
    path('api/swalook/loyality_program/view/', Vendor_loyality_type_add_get.as_view(), name='loyality_program_view'),
    path('api/swalook/loyality_program/verify/', Check_Loyality_Customer_exists.as_view(), name='loyality_program_verify'),
    path('api/swalook/loyality_program/types/', MembershipTypesLoyality_get.as_view(), name='loyality_program_types'),
    path('api/swalook/loyality_program/get_minimum_value/', update_minimum_amount.as_view(), name='loyality_program_minimum_value'),
    path('api/swalook/staff/', vendor_staff.as_view(), name='staff'),
    path('api/swalook/staff/setting/', vendor_staff_setting_slabs.as_view(), name='staff_setting'),
    path('api/swalook/staff/attendance/', vendor_staff_attendance.as_view(), name='staff_attendance'),
    path('api/swalook/staff/generate-payslip/', salary_disburse.as_view(), name='generate_payslip'),
    path('api/swalook/business-analysis/week-customer/', Sales_Per_Customer.as_view(), name='business_analysis_week_customer'),
    path('api/swalook/business-analysis/month-customer/', Sales_Per_Customer_monthly.as_view(), name='business_analysis_month_customer'),
    path('api/swalook/business-analysis/daily-customer/', Sales_in_a_day_by_customer.as_view(), name='business_analysis_daily_customer'),
    path('api/swalook/business-analysis/products/', ProductAnalysis.as_view(), name='business_analysis_products'),
    path('api/swalook/business-analysis/month/', Sales_in_a_month.as_view(), name='business_analysis_month'),
    path('api/swalook/business-analysis/year/', Sales_in_a_year.as_view(), name='business_analysis_year'),
    path('api/swalook/business-analysis/week/', Sales_in_a_week.as_view(), name='business_analysis_week'),
    path('api/swalook/business-analysis/time/', Sales_in_a_day_by_customer_time.as_view(), name='business_analysis_time'),
    path('api/swalook/business-analysis/service/', service_analysis.as_view(), name='business_analysis_service'),
    path('api/swalook/business-analysis/headers/', busniess_headers.as_view(), name='business_analysis_headers'),
    path('api/swalook/get-customer-bill-app-data/', GetCustomerBillAppDetails.as_view(), name='get_customer_bill_app_data'),
    path('api/swalook/get-customer-bill-app-data/2/', GetCustomerBillAppDetails_copy.as_view(), name='get_customer_bill_app_data_copy'),
    path('api/swalook/get-customer-bill-app-data/3/', GetCustomerBillAppDetails_copy_details.as_view(), name='get_customer_bill_app_details_data_copy'),
    path('api/swalook/expense_management/', expense_management.as_view(), name='expense_management'),
    path('api/swalook/expense_category/', expense_category.as_view(), name='expense_category'),
    path('api/swalook/service_category/', service_category.as_view(), name='service_category'),
    path('api/swalook/product_category/', product_category.as_view(), name='product_category'),
    path('api/swalook/coupon/', CouponView.as_view(), name='coupon'),
    path('api/swalook/enquery/', enquery.as_view(), name='enquery'),
    path('api/swalook/staff-analysis/', StaffRevenueAPI.as_view(), name='staff_revenue'),
    path('api/swalook/mode-of-payment-analysis/', ModeOfPaymentAPI.as_view(), name='mode_of_payment_revenue'),
    path('api/swalook/revenue-analysis/', RevenueSummaryAPI.as_view(), name='daily_previous_revenue'),
    # path('api/swalook/loyality/template/', LoyalityTemplate.as_view(), name='templates'),
    path('api/swalook/staff-header-mode-of-payment/', top5_header_staff_revenue.as_view(), name='staff_header_mode_of_payment'),
    path('api/swalook/vendor-customers/stats/', VendorCustomerStatsAPIView.as_view(), name='vendor-customer-stats'),
    path('api/swalook/inventory/expiring-products/', ExpiringProductsAPIView.as_view(), name='expiring-products'),
    path('api/swalook/test-error/', Table_servicess.as_view(), name='test_error'),
    path('api/swalook/sales-targets/', SalesTargetSettingListCreateView.as_view(), name='sales-target-list-create'),
    path('api/swalook/sales-targets/<uuid:pk>/', SalesTargetSettingDetailView.as_view(), name='sales-target-detail'),
    path('api/swalook/upload/image/', PictureUploadView.as_view(), name='upload-picture'),
    path('merge-images/', MergeImagesAPIView.as_view(), name='merge-images'),
    path('api/swalook/fb/exchange-token/', FacebookTokenExchange.as_view(),name='authentication-instagram'),
    path('api/swalook/fb/pages/', FacebookPages.as_view(),name='pages-instagram'),
    path('api/swalook/fb/instagram-id/', InstagramBusinessID.as_view(),name='getting-id-for-page-instagram'),
    path('api/swalook/fb/upload-instagram/', InstagramUpload.as_view(),name='image-upload-instagram'),
    path('api/swalook/vendor/expense-purchase/',  VendorpurchaseView.as_view(),name='vendor-expense-purchase'),
    path('api/swalook/inventory/utilizationinventory/', UtilizationInventory.as_view(),name='vendor-inventory-utilization'),
    path('api/swalook/download-invoice-excel/', DownloadInvoiceExcelView.as_view()),
    path('api/swalook/vendor-expense-purchase/', VendorPurchaseView_vp.as_view()),
    path('api/swalook/single_staff_attendance/', SingleStaffAttendance.as_view()),
    path('api/swalook/staff_attendance_mobile/punch-out/', Attendance_mobile_staff.as_view()),
    path('api/swalook/single_staff_advance/', singlestaffadvancedata.as_view()),
    path('api/swalook/get-type-expense/',get_sub_category_of_expense.as_view()),
    
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}, name='media'),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_URL}, name='static'),
]


