"""sprint_mis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from App import views
from sprint_mis import settings

urlpatterns = [
    # path('__debug__/', include('debug_toolbar.urls')),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('', views.loginuser, name='loginuser'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # path('forgot/', views.forgot_password, name='forgot_password'),
    path('logout/', views.logout_user, name='logout'),
    path('search_emp/', views.search_emp, name='search_emp'),
    path('doctor_search/', views.doctor_search, name='doctor_search'),
    path('emp_list/', views.emp_list, name='emp_list'),
    path('bank_details/', views.bank_details, name='bank_details'),
    path('wrong_bank_details/', views.wrong_bank_details, name='wrong_bank_details'),
    path('pending_payment/', views.pending_payment, name='pending_payment'),
    path('payment_list/', views.payment_list, name='payment_list'),

    path('update_activity/', views.update_activity, name='update_activity'),
    path('ref_dashboard/', views.ref_dashboard, name='ref_dashboard'),
    path('processed_ref/', views.processed_ref, name='processed_ref'),
    path('doctor_agent_list/', views.doctor_agent_list, name='doctor_agent_list'),
    path('doctor_agent_list_dt/', views.doctor_agent_list_dt, name='doctor_agent_list_dt'),
    path('utr_update/', views.utr_update, name='utr_update'),
    path('utr_csv/', views.utr_csv, name='utr_csv'),
    # path('upload_utr_csv/', views.upload_utr_csv, name='upload_utr_csv'),
    path('pending_payment_csv/', views.pending_payment_csv, name='pending_payment_csv'),
    path('search_id/', views.search_id, name='search_id'),
    path('s_id/', views.s_id, name='s_id'),
    path('search_uid/', views.search_uid, name='search_uid'),
    path('pdf/', views.pdf, name='pdf'),



    # path('change_pwd/', views.change_pwd, name='change_pwd'),
#Total referral list

    path('total_referral_list/', views.total_referral_list, name='total_referral_list'),
    path('referral_details/', views.referral_details, name='referral_details'),
    path('new_referral_list/', views.new_referral_list, name='new_referral_list'),
    path('recent_updates/', views.recent_updates, name='recent_updates'),
    path('bifurcation_list/', views.bifurcation_list, name='bifurcation_list'),
    path('search_referral/', views.search_referral, name='search_referral'),
    path('search_reff/', views.search_reff, name='search_reff'),
    path('patient_referral/', views.patient_referral, name='patient_referral'),
    path('incomplete_referral/', views.incomplete_referral, name='incomplete_referral'),
    path('abc_report/', views.abc_report, name='abc_report'),
    path('allowance_report/', views.allowance_report, name='allowance_report'),
    path('inactive_allowance_report/', views.inactive_allowance_report, name='inactive_allowance_report'),
    path('bill_list/', views.bill_list, name='bill_list'),
    path('bill/', views.bill, name='bill'),
    # path('admission_list_filter/', views.admission_list_filter, name='admission_list_filter'),
    path('admission/', views.admission, name='admission'),

#Employee Details
    path('register/', views.register, name='register'),
    path('employee_list/', views.employee_list, name='employee_list'),
    path('attendance_list/', views.attendance_list, name='attendance_list'),
    path('employee_leave_list/', views.employee_leave_list, name='employee_leave_list'),


#call report
    path('call_report/', views.call_report, name='call_report'),
    path('call_reports/', views.call_reports, name='call_reports'),
    path('call_search/', views.call_search, name='call_search'),
    path('save_transfer/', views.save_transfer, name='save_transfer'),
    path('call_report_csv/', views.call_report_csv, name='call_report_csv'),
    path('daily_call_report/', views.daily_call_report, name='daily_call_report'),
    path('daily_call/', views.daily_call, name='daily_call'),
    path('day_report/', views.day_report, name='day_report'),
    path('day_reports/', views.day_reports, name='day_reports'),
    path('n_day_report/', views.n_day_report, name='n_day_report'),
    path('champion/', views.champion, name='champion'),
    path('admission_breakup/', views.admission_breakup, name='admission_breakup'),
    # path('search_upi/', views.search_upi, name='search_upi'),
    path('edit_list/', views.edit_list, name='edit_list'),




    path('camp_report/', views.camp_report, name='camp_report'),
    path('reject/', views.reject, name='reject'),
    path('neft_return_list/', views.neft_return_list, name='neft_return_list'),
    path('cash_payment/', views.cash_payment, name='cash_payment'),
    path('functional_approval_list/', views.functional_approval_list, name='functional_approval_list'),





]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
