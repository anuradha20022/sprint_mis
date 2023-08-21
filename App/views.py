import json
from builtins import UnicodeDecodeError
from datetime import date
import ast
import csv
import os

import bcrypt
import numpy as np
import pandas as pd
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import connection
from django.db.models import Q, Count, Min, Sum
from django.http import JsonResponse, HttpResponse, FileResponse, HttpResponseRedirect, response
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated

from App.serializers import HomeSampleVisitsSerializer
from .models import *


def decode_utf8(input_iterator):
    for l in input_iterator:
        try:
            yield l.decode('utf-8')
        except UnicodeDecodeError:
            yield l.decode('ISO-8859-1')


def loginuser(request):
    for logins in WebLogins.objects.all():
        WebLogins.objects.filter(emp_id=logins.emp_id).update(is_staff=True, is_active=True)

    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        password = request.POST.get('password')
        user = authenticate(username=emp_id, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'invalid emp_id and password')
            return redirect('loginuser')
    return render(request, 'login.html')


@login_required(login_url="/")
def dashboard(request):
    cur = connection.cursor()
    cur.execute('''SELECT COUNT(DISTINCT (`emp_id`)) FROM `call_report_master` WHERE `date` = CURRENT_DATE ;''')
    present_data = cur.fetchall()[0][0]
    total_count = Logins.objects.filter(~Q(branch='Test') & Q(job_status='Active')).count()

    context = {
        'master_list': DoctorAgentList.objects.filter(~Q(emp_id='1234')).count(),
        'present': present_data,
        'total_count': total_count,
        'absent': total_count - present_data,
        'total': Logins.objects.filter(~Q(branch='Test') & Q(job_status='Active')),
        'master': DoctorAgentList.objects.filter(~Q(emp_id='1234')),

    }

    return render(request, 'dashboard.html', context)


def logout_user(request):
    logout(request)
    return redirect('loginuser')


@login_required(login_url="/")
def register(request):
    result = []
    for branch in list(CallReportMaster.objects.values('branch').distinct()):
        if branch['branch']:
            result.append(
                {'branch': branch['branch'], 'count': CallReportMaster.objects.filter(branch=branch['branch']).count()})

    # for emp in Logins.objects.all():
    #     try:
    #         WebLogins.objects.get(emp_id=emp.emp_id)
    #     except WebLogins.DoesNotExist:
    #         print(emp.emp_id)
    #         WebLogins.objects.create(emp_name=emp.emp_name, emp_id=emp.emp_id, password=make_password(emp.password),
    #                                  mpassword=emp.mpassword,
    #                                  personal_number=emp.personal_number, office_number=emp.office_number,
    #                                  branch=emp.branch,
    #                                  old_branch=emp.old_branch,
    #                                  page=emp.page, designation=emp.designation, original_type=emp.original_type,
    #                                  orginal_design=emp.orginal_design,
    #                                  head=emp.head, type=emp.type, branch_access=emp.branch_access,
    #                                  new_type=emp.new_type,
    #                                  # date=emp.date,
    #                                  time=emp.time,
    #                                  # join_date=emp.join_date,
    #                                  visibility=emp.visibility,
    #                                  job_status=emp.job_status, levels=emp.levels, bank_acc=emp.bank_acc, ifsc=emp.ifsc,
    #                                  pan=emp.pan,
    #                                  last_location=emp.last_location,
    #                                  # last_loc_datetime=emp.last_loc_datetime,
    #                                  allow=emp.allow,
    #                                  img_link=emp.img_link, is_staff=True,
    #                                  model=emp.model, version=emp.version, firebase_token=emp.firebase_token,
    #                                  deviceid=emp.deviceid, accesskey=emp.accesskey, state=emp.state,
    #                                  ref_count=emp.ref_count,
    #                                  androidpermissions=emp.androidpermissions,
    #                                  androidsubmenu=emp.androidsubmenu,
    #                                  loginstatus=emp.loginstatus)

    if 'empname' in request.POST:
        empname = request.POST.get('empname')
        empid = request.POST.get('empid')
        mobile = request.POST.get('mobile')
        designation = request.POST.get('designation')
        branch = request.POST.get('branch')
        department = request.POST.get('department')
        category = request.POST.get('category')
        reporting_to = request.POST.get('reporting_to')
        old_branch = Logins.objects.filter(branch=branch).exclude(branch='').first()

        password = mobile.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password_bytes = bcrypt.hashpw(password, salt)
        hashed_password = hashed_password_bytes.decode('utf-8')
        current_date = timezone.now().date()

        if designation == 'Executive' or designation == 'Senior Executive':
            get_menu_details = LoginPermissions.objects.filter(designation__contains='Executive').first()
            if get_menu_details:
                menu = get_menu_details.menu
                submenu = get_menu_details.submenu
                Logins.objects.create(emp_name=empname, emp_id=empid, password=mobile, mpassword=hashed_password,
                                      personal_number=mobile, office_number=mobile, branch=branch,
                                      old_branch=old_branch.old_branch,
                                      page='Marketing', designation='Executive', original_type=department,
                                      orginal_design=designation,
                                      head=reporting_to, type=department, branch_access=branch, new_type=category,
                                      date=timezone.now().date(), time=timezone.now().time(),
                                      join_date=current_date,
                                      visibility='Hidden',
                                      job_status='Active', levels='0', bank_acc='', ifsc='', pan='', last_location='',
                                      last_loc_datetime=timezone.now(), allow='250',
                                      img_link='',
                                      model='', version='', firebase_token='',
                                      deviceid='', accesskey='', state='', ref_count='0', androidpermissions=menu,
                                      androidsubmenu=submenu,
                                      loginstatus='0')
                WebLogins.objects.create(emp_name=empname, emp_id=empid, password=make_password(mobile),
                                         mpassword=mobile,
                                         personal_number=mobile, office_number=mobile, branch=branch,
                                         old_branch=old_branch.old_branch,
                                         page='Marketing', designation='Executive', original_type=department,
                                         orginal_design=designation,
                                         head=reporting_to, type=department, branch_access=branch, new_type=category,
                                         date=timezone.now().date(), time=timezone.now().time(),
                                         join_date=current_date,
                                         visibility='Hidden',
                                         job_status='Active', levels='0', bank_acc='', ifsc='', pan='',
                                         last_location='',
                                         last_loc_datetime=timezone.now(), allow='250',
                                         img_link='', is_staff=True,
                                         model='', version='', firebase_token='',
                                         deviceid='', accesskey='', state='', ref_count='0', androidpermissions=menu,
                                         androidsubmenu=submenu,
                                         loginstatus='0')

        elif designation == 'Manager' or designation == 'Assistant Manager' or designation == 'Deputy Manager' or designation == 'Senior Manager' \
                or designation == 'Team Lead':
            get_menu_details = LoginPermissions.objects.filter(designation__contains='Manager').first()
            if get_menu_details:
                menu = get_menu_details.menu
                submenu = get_menu_details.submenu
                Logins.objects.create(emp_name=empname, emp_id=empid, password=mobile, mpassword=hashed_password,
                                      personal_number=mobile, office_number=mobile, branch=branch,
                                      old_branch=old_branch.old_branch,
                                      page='Marketing', designation='Manager', original_type=department,
                                      orginal_design=designation,
                                      head=reporting_to, type=department, branch_access=branch, new_type=category,
                                      date=timezone.now().date(), time=timezone.now().time(),
                                      join_date=current_date,
                                      visibility='Hidden',
                                      job_status='Active', levels='0', bank_acc='', ifsc='', pan='', last_location='',
                                      last_loc_datetime=timezone.now(), allow='300',
                                      img_link='',
                                      model='', version='', firebase_token='',
                                      deviceid='', accesskey='', state='', ref_count='0', androidpermissions=menu,
                                      androidsubmenu=submenu,
                                      loginstatus='0')
                WebLogins.objects.create(emp_name=empname, emp_id=empid, password=make_password(mobile),
                                         mpassword=mobile,
                                         personal_number=mobile, office_number=mobile, branch=branch,
                                         old_branch=old_branch.old_branch, is_staff=True,
                                         page='Marketing', designation='Manager', original_type=department,
                                         orginal_design=designation,
                                         head=reporting_to, type=department, branch_access=branch, new_type=category,
                                         date=timezone.now().date(), time=timezone.now().time(),
                                         join_date=current_date,
                                         visibility='Hidden',
                                         job_status='Active', levels='0', bank_acc='', ifsc='', pan='',
                                         last_location='',
                                         last_loc_datetime=timezone.now(), allow='300',
                                         img_link='',
                                         model='', version='', firebase_token='',
                                         deviceid='', accesskey='', state='', ref_count='0', androidpermissions=menu,
                                         androidsubmenu=submenu,
                                         loginstatus='0')

        elif designation == 'General Manager' or designation == 'Deputy General Manager':
            get_menu_details = LoginPermissions.objects.filter(designation__contains='Marketing Head').first()
            if get_menu_details:
                menu = get_menu_details.menu
                submenu = get_menu_details.submenu
                Logins.objects.create(emp_name=empname, emp_id=empid, password=mobile, mpassword=hashed_password,
                                      personal_number=mobile, office_number=mobile, branch=branch,
                                      old_branch=old_branch.old_branch,
                                      page='Marketing', designation='Marketing Head', original_type=department,
                                      orginal_design=designation,
                                      head=reporting_to, type=department, branch_access=branch, new_type=category,
                                      date=timezone.now().date(), time=timezone.now().time(),
                                      join_date=current_date,
                                      visibility='Hidden',
                                      job_status='Active', levels='0', bank_acc='', ifsc='', pan='', last_location='',
                                      last_loc_datetime=timezone.now(), allow='300',
                                      img_link='',
                                      model='', version='', firebase_token='',
                                      deviceid='', accesskey='', state='', ref_count='0', androidpermissions=menu,
                                      androidsubmenu=submenu,
                                      loginstatus='0')
                WebLogins.objects.create(emp_name=empname, emp_id=empid, password=make_password(mobile),
                                         mpassword=mobile,
                                         personal_number=mobile, office_number=mobile, branch=branch,
                                         old_branch=old_branch.old_branch,
                                         page='Marketing', designation='Marketing Head', original_type=department,
                                         orginal_design=designation,
                                         head=reporting_to, type=department, branch_access=branch, new_type=category,
                                         date=timezone.now().date(), time=timezone.now().time(),
                                         join_date=current_date,
                                         visibility='Hidden',
                                         job_status='Active', levels='0', bank_acc='', ifsc='', pan='',
                                         last_location='', is_staff=True,
                                         last_loc_datetime=timezone.now(), allow='300',
                                         img_link='',
                                         model='', version='', firebase_token='',
                                         deviceid='', accesskey='', state='', ref_count='0', androidpermissions=menu,
                                         androidsubmenu=submenu,
                                         loginstatus='0')

        elif designation == 'Center Head':
            get_menu_details = LoginPermissions.objects.filter(designation__contains='Center Head').first()
            if get_menu_details:
                menu = get_menu_details.menu
                submenu = get_menu_details.submenu
                Logins.objects.create(emp_name=empname, emp_id=empid, password=mobile, mpassword=hashed_password,
                                      personal_number=mobile, office_number=mobile, branch=branch,
                                      old_branch=old_branch.old_branch,
                                      page='Marketing', designation='Center Head', original_type=department,
                                      orginal_design=designation,
                                      head=reporting_to, type=department, branch_access=branch, new_type=category,
                                      date=timezone.now().date(), time=timezone.now().time(),
                                      join_date=current_date,
                                      visibility='Hidden',
                                      job_status='Active', levels='0', bank_acc='', ifsc='', pan='', last_location='',
                                      last_loc_datetime=timezone.now(), allow='300',
                                      img_link='',
                                      model='', version='', firebase_token='',
                                      deviceid='', accesskey='', state='', ref_count='0', androidpermissions=menu,
                                      androidsubmenu=submenu,
                                      loginstatus='0')
                WebLogins.objects.create(emp_name=empname, emp_id=empid, password=make_password(mobile),
                                         mpassword=mobile,
                                         personal_number=mobile, office_number=mobile, branch=branch,
                                         old_branch=old_branch.old_branch,
                                         page='Marketing', designation='Center Head', original_type=department,
                                         orginal_design=designation, is_staff=True,
                                         head=reporting_to, type=department, branch_access=branch, new_type=category,
                                         date=timezone.now().date(), time=timezone.now().time(),
                                         join_date=current_date,
                                         visibility='Hidden',
                                         job_status='Active', levels='0', bank_acc='', ifsc='', pan='',
                                         last_location='',
                                         last_loc_datetime=timezone.now(), allow='300',
                                         img_link='',
                                         model='', version='', firebase_token='',
                                         deviceid='', accesskey='', state='', ref_count='0', androidpermissions=menu,
                                         androidsubmenu=submenu,
                                         loginstatus='0').save()

        else:
            get_menu_details = LoginPermissions.objects.filter(designation=designation).first()
            if get_menu_details:
                menu = get_menu_details.menu
                submenu = get_menu_details.submenu
                Logins.objects.create(emp_name=empname, emp_id=empid, password=mobile, mpassword=hashed_password,
                                      personal_number=mobile, office_number=mobile, branch=branch,
                                      old_branch=old_branch.old_branch,
                                      page=department, designation=designation, original_type=department,
                                      orginal_design=designation,
                                      head=reporting_to, type=department, branch_access=branch, new_type=category,
                                      date=timezone.now().date(), time=timezone.now().time(),
                                      join_date=current_date,
                                      visibility='Hidden',
                                      job_status='Active', levels='0', bank_acc='', ifsc='', pan='', last_location='',
                                      last_loc_datetime=timezone.now(), allow='250',
                                      img_link='',
                                      model='', version='', firebase_token='',
                                      deviceid='', accesskey='', state='', ref_count='0', androidpermissions=menu,
                                      androidsubmenu=submenu,
                                      loginstatus='0')
                WebLogins.objects.create(emp_name=empname, emp_id=empid, password=make_password(mobile),
                                         mpassword=mobile,
                                         personal_number=mobile, office_number=mobile, branch=branch,
                                         old_branch=old_branch.old_branch,
                                         page=department, designation=designation, original_type=department,
                                         orginal_design=designation, is_staff=True,
                                         head=reporting_to, type=department, branch_access=branch, new_type=category,
                                         date=timezone.now().date(), time=timezone.now().time(),
                                         join_date=current_date,
                                         visibility='Hidden',
                                         job_status='Active', levels='0', bank_acc='', ifsc='', pan='',
                                         last_location='',
                                         last_loc_datetime=timezone.now(), allow='250',
                                         img_link='',
                                         model='', version='', firebase_token='',
                                         deviceid='', accesskey='', state='', ref_count='0', androidpermissions=menu,
                                         androidsubmenu=submenu,
                                         loginstatus='0')

        messages.success(request, 'Employee Account has been created')
        return redirect('register')

    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test')),
        'branch_wise_count': result,
        'total_count': CallReportMaster.objects.count(),
    }
    return render(request, 'Employee/register.html', context)


@login_required(login_url="/")
def inactive_emp(request):
    if 'branch_name' in request.POST:
        branch = request.POST.get('branch_name')
        BranchListDum.objects.create(branch_name=branch)
        messages.success(request, "branch added")
        return redirect('register')

    if 'emp_search' in request.POST and 'branch_name' not in request.POST:
        emp_search = request.POST.get('emp_search')
        status = request.POST.get('status')
        current_date = timezone.now().date()
        user = Logins.objects.filter(emp_id=emp_search).update(job_status=status, inactive_dt=current_date)
        if user:
            messages.success(request, "updated successfully..")
        else:
            messages.error(request, "You have entered incorrect Emp_ID")

        return redirect('register')


@login_required(login_url="/")
def employee_list(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test')),
        'agent_type': DoctorAgentList.objects.filter(~Q(agent_type='Type')).values('agent_type').distinct(),
        'designation': Logins.objects.all()
    }

    if 'delete' in request.GET:
        delete = request.GET.get('delete')
        data = WebLogins.objects.get(emp_id=delete)
        data.delete()
        messages.success(request, 'Deleted succesfully')
        return redirect('employee_list')

    if 'employee_update' in request.POST:
        emp_name = request.POST.get("emp_name")
        emp_id = request.POST.get("emp_id")
        designation = request.POST.get("designation")
        mobile_number = request.POST.get("mobile_number")
        office_number = request.POST.get("office_number")
        bank_ac = request.POST.get("bank_ac")
        ifsc = request.POST.get("ifsc")
        pancard = request.POST.get("pancard")
        reporting = request.POST.get("reporting")
        branch = request.POST.get("branch")
        department = request.POST.get("department")
        Logins.objects.filter(emp_id=emp_id).update(emp_name=emp_name, orginal_design=designation,
                                                    original_type=department,
                                                    office_number=office_number, personal_number=mobile_number,
                                                    bank_acc=bank_ac, pan=pancard, ifsc=ifsc, head=reporting,
                                                    branch=branch)

        messages.success(request, "Details updated successfully")

    if 'branch' in request.POST and 'employee_update' not in request.POST:
        branch = request.POST.get('branch')
        if branch:
            context['emp_list'] = Logins.objects.filter(
                Q(job_status='Active', page='Marketing', branch=branch) & (~Q(branch="Test"))).order_by(
                'branch', 'emp_id').exclude(emp_id='10101')

    else:
        context['emp_list'] = Logins.objects.filter(
            Q(job_status='Active', page='Marketing') & (~Q(branch="Test"))).order_by(
            'branch', 'emp_id').exclude(emp_id='10101')

    if request.method == "GET" and request.is_ajax():
        emp_id = request.GET.get('emp_id')
        res = list(Logins.objects.filter(emp_id=emp_id).values())[0]
        return JsonResponse(res)

    return render(request, 'Employee/employee_list.html', context)


@login_required(login_url="/")
def search_emp(request):
    if 'term' in request.GET:
        result = []
        term = request.GET.get('term')
        new = Logins.objects.filter(Q(emp_id__istartswith=term) | Q(emp_name__istartswith=term))
        for emp in new:
            result.append({'id': emp.emp_id, 'name': emp.emp_name, 'desg': emp.designation})
        if not result:
            result.append({'name': "No data found", 'id': '', 'desg': ''})

        return JsonResponse(result, safe=False)


def doctor_search(request):
    if 'term' in request.GET:
        result = []
        term = request.GET.get('term')
        new = DoctorAgentList.objects.filter(Q(unique_id__istartswith=term) | Q(agent_name__istartswith=term))
        for emp in new:
            result.append({'id': emp.unique_id, 'name': emp.agent_name, 'desg': emp.designation})
        if not result:
            result.append({'name': '', 'id': '', 'desg': 'No data found'})

        return JsonResponse(result, safe=False)


def transfer_doctor_search(request):
    if 'term' in request.GET:
        result = []
        term = request.GET.get('term')
        new = DoctorAgentList.objects.filter(Q(emp_id__istartswith=term) | Q(agent_name__istartswith=term))
        for emp in new:
            result.append({'id': emp.emp_id, 'name': emp.agent_name, 'desg': emp.designation})
        if not result:
            result.append({'name': '', 'id': '', 'desg': 'No data found'})

        return JsonResponse(result, safe=False)


@login_required(login_url="/")
def pending_payment(request):
    common_filter = Q(referralstatus='Yes', chapproval='approved')
    branch_name = request.POST.get('branch')
    print(branch_name)
    if branch_name == 'All':
        filtered_data = PatientData.objects.filter(Q(common_filter) & (~Q(paymentmode=None)))
    else:
        filtered_data = PatientData.objects.filter(Q(common_filter, branch=branch_name) & (~Q(paymentmode=None)))
    status = filtered_data
    cash = filtered_data.filter(Q(paymentmode='CASH') & (~Q(paymentmode=None)))
    upi = filtered_data.filter(Q(paymentmode='UPI') & (~Q(paymentmode=None)))
    netbanking = filtered_data.filter(Q(paymentmode='netbanking') & (~Q(paymentmode=None)))
    context = {
        'branch_name': BranchListDum.objects.exclude(branch_name='Test'),
        'status': status,
        'cash': cash,
        'upi': upi,
        'netbanking': netbanking,
    }
    print(context)
    return render(request, 'pending_payment.html', context)


@login_required(login_url="/")
def doctor_agent_list(request):
    context = {
        'branch': BranchListDum.objects.exclude(branch_name='Test'),
    }

    if 'transfer_id' in request.POST:
        pass

    if request.POST.get('from_empid'):
        from_empid = request.POST.get('from_empid')
        to_empid = request.POST.get('to_empid')
        data = DoctorAgentList.objects.filter(emp_id=from_empid).update(emp_id=to_empid)
        print(from_empid, to_empid)
        messages.success(request, f"Emp Id : {from_empid} Transferred to Emp Id : {to_empid}")
        return redirect('doctor_agent_list')

    if request.method == "POST":
        empid = request.POST.get('empid')
        branch = request.POST.get('branch')
        if branch == "All":
            context["doctor_agent_list"] = DoctorAgentList.objects.filter(~Q(emp_id='1234'))
        elif empid and branch:
            context["doctor_agent_list"] = DoctorAgentList.objects.filter(
                Q(unique_id=empid, branch=branch) & ~Q(emp_id='1234'))
        elif empid:
            context["doctor_agent_list"] = DoctorAgentList.objects.filter(Q(unique_id=empid) & ~Q(emp_id='1234'))
        elif branch:
            context["doctor_agent_list"] = DoctorAgentList.objects.filter(Q(branch=branch) & ~Q(emp_id='1234'))
    return render(request, 'doctor_agent_list.html', context)


@csrf_exempt
@login_required(login_url="/")
def doctor_agent_list_dt(request):
    # print(request.POST)
    draw = int(request.POST.get('draw'))
    # start = int(request.POST.get('start'))
    length = int(request.POST.get('length'))
    search = request.POST.get('search[value]')
    colindex = request.POST.get("order[0][column]")
    records_total = DoctorAgentList.objects.all().order_by('unique_id').count()
    records_filtered = records_total
    agent_data = DoctorAgentList.objects.all().order_by('unique_id').values()

    if search:
        agent_data = DoctorAgentList.objects.filter(
            Q(unique_id__icontains=search) | Q(agent_name__icontains=search) | Q(
                unique_id__icontains=search)).order_by('unique_id').values()
        records_total = agent_data.count()
        records_filtered = records_total

    paginator = Paginator(agent_data, length)

    try:
        object_list = paginator.page(draw).object_list
    except PageNotAnInteger:
        object_list = paginator.page(draw).object_list
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages).object_list

    data = [
        {
            'sno': '',
            # 'input': '<input type="checkbox" class="" name="'+str(emp['emp_id'])+'" value="">',
            'emp_id': emp['emp_id'],
            'unique_id': emp['unique_id'],
            'agent_type': emp['agent_type'],
            'category': emp['category'],
            'branch': emp['branch'],
            'mobile': emp['mobile'],
            'company': emp['company'],
            'pancard': emp['pancard'],
            'bank_ac': emp['bank_ac'],
            'ifsc': emp['ifsc'],
            'area': emp['area'],
            # 'city': emp['city'],
            'district': emp['district'],
            'state': emp['state'],
            'pincode': emp['pincode'],
            'date': emp['date'],
            'source': emp['source'],
            'type': emp['type'],
            'r_status': emp['r_status'],
            'designation': emp['designation'],
            'department': emp['department'],
            # 'employee_id': '<a href="/profile/?i=' + str(emp['employee_id']) + '">' + str(emp['employee_id']) + '</a>',
        } for emp in object_list
    ]
    return JsonResponse(
        {"draw": draw, "iTotalRecords": records_total, 'recordsFiltered': records_filtered, "data": data}, safe=False)


@login_required(login_url="/")
def call_report(request):
    context = {
        # 'report': CallReportMaster.objects.all(),
    }
    if request.method == "POST":
        f_date = request.POST.get('date_d')

        from_d, to_d = f_date.split(' - ')
        from_d = datetime.strptime(str(from_d), '%m/%d/%Y').date()
        to_d = datetime.strptime(str(to_d), '%m/%d/%Y').date()

        call = connection.cursor()
        if f_date:
            call.execute(
                """SELECT call_report_master.emp_id, logins.emp_name, call_report_master.unique_id,call_report_master.category,
                    call_report_master.ref_type,call_report_master.name, call_report_master.design,  call_report_master.contact, call_report_master.date,
                     call_report_master.location, call_report_master.branch
                FROM logins
                INNER JOIN call_report_master ON logins.emp_id = call_report_master.emp_id
                WHERE call_report_master.date BETWEEN '{fd}' AND '{td}'
                AND call_report_master.branch != 'Test'""".format(fd=from_d, td=to_d)
            )
        else:
            call.execute(
                """SELECT call_report_master.emp_id, logins.emp_name, call_report_master.unique_id,call_report_master.category,
                    call_report_master.ref_type, call_report_master.name, call_report_master.design,  call_report_master.contact, call_report_master.date,
                     call_report_master.location, call_report_master.branch
                FROM logins
                INNER JOIN call_report_master ON logins.emp_id = call_report_master.emp_id
                WHERE call_report_master.branch != 'Test'""")
        desc = call.description
        context['call_report'] = [
            dict(zip([i[0] for i in desc], row)) for row in call.fetchall()
        ]

    return render(request, 'call/call_report.html', context)

#
# @csrf_exempt
# @login_required(login_url="/")
# def call_reports(request):
#     # print(request.POST)
#     draw = int(request.POST.get('draw'))
#     length = int(request.POST.get('length'))
#     start = int(request.POST.get('start'))
#     search = request.POST.get('search[value]')
#     colindex = request.POST.get("order[0][column]")
#     records_total = CallReportMaster.objects.all().count()
#     records_filtered = records_total
#     call_data = CallReportMaster.objects.all().values()[start:length + start]
#
#     if search:
#         call_data = CallReportMaster.objects.filter(Q(name__icontains=search)
#                                                     ).values()[start:length + start]
#         records_total = call_data.count()
#         records_filtered = records_total
#
#     data = [
#         {
#             'sno': "",
#             'input': '<input type="checkbox" class="" name="' + str(emp['emp_id']) + '" value="">',
#             'emp_id': emp['emp_id'],
#             'unique_id': emp['unique_id'],
#             'name': emp['name'],
#             'category': emp['category'],
#             'ref_type': emp['ref_type'],
#             'design': emp['design'],
#             'contact': emp['contact'],
#             'date': emp['date'],
#             'time': emp['time'],
#             'location': emp['location'],
#             'area': emp['area'],
#             'city': emp['city'],
#             'state': emp['state'],
#             'pincode': emp['pincode'],
#             'station': emp['station'],
#             'branch': emp['branch'],
#             'type': emp['type'],
#
#         } for emp in call_data
#     ]
#     return JsonResponse(
#         {"draw": draw, "iTotalRecords": records_total, 'recordsFiltered': records_filtered,
#          "iTotalDisplayRecords": records_total, "aaData": data}, safe=False)


@login_required(login_url="/")
def call_search(request):
    if 'term' in request.GET:
        result = []
        term = request.GET.get('term')
        new = CallReportMaster.objects.filter(
            Q(emp_id__istartswith=term) | Q(name__istartswith=term) | Q(design__istartswith=term))
        for emp in new:
            result.append({'id': emp.emp_id, 'name': emp.name, 'design': emp.design})
        if not result:
            result.append({'name': "", 'id': '', 'design': 'No data found'})

        return JsonResponse(result, safe=False)


@login_required(login_url="/")
def save_transfer(request):
    status = False
    if request.is_ajax() and request.method == "POST" and 'from_empid' not in request.POST:
        transfer = request.POST.get('empid')
        agent = request.POST.get('agent_uids')
        agent = agent.split(',')
        print(transfer, agent)
        for i in agent:
            DoctorAgentList.objects.filter(emp_id=i).update(emp_id=transfer)
            print(i)

        status = True
        return JsonResponse({'res': status})


@login_required(login_url="/")
def call_report_csv(request):
    res = HttpResponse(content_type='text/csv')
    res['Content-Disposition'] = 'attachment; filename="myfile.csv"'
    writer = csv.writer(res)
    writer.writerow([
        'Emp_ID', 'Emp_name', 'ref_type', 'unique_id', 'name', 'camp', 'camp_details', 'date', 'time', 'location',
        'reason', 'Type', 'source', 'branch', 'agent_name', 'attendance', 'camp_details',

    ])
    # call_report = connection.cursor()
    # call_report.execute("SELECT `logins`.`Emp_ID`, `logins`.`Emp_name`, `call_report_master`.`ref_type`,"
    #                     "`call_report_master`.`unique_id`, `call_report_master`.`name`, `call_report_master`.`camp`, "
    #                     "`call_report_master`.`camp_details`, `call_report_master`.`date`, `call_report_master`.`time`, "
    #                     "`call_report_master`.`location`, `call_report_master`.`reason`, `call_report_master`.`Type`, "
    #                     "`call_report_master`.`source`,`call_report_master`.`branch`, `doctor_agent_list`.`agent_name`,"
    #                     "`call_report_master`.`attendance`,`call_report_master`.`camp_details`FROM `call_report_master` "
    #                     "INNER JOIN `logins` ON `call_report_master`.`emp_id` = `logins`.`Emp_ID` INNER JOIN "
    #                     "`doctor_agent_list` on `call_report_master`.`unique_id` = `doctor_agent_list`.`unique_id` "
    #                     " WHERE `logins`.`Page` = 'Marketing' ORDER BY `logins`.`Branch` ASC")
    #
    # # row = cursor.fetchall()
    #
    # call_data = CallReportMaster.objects.all()

    # for i in call_report:
    #     writer.writerow([
    #         i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[12], i[13], i[14], i[15],
    #         i[16]
    #     ])
    # #     print(i)

    return res


@login_required(login_url="/")
def total_referral_list(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test')),
        'agent_type': DoctorAgentList.objects.filter(~Q(agent_type='Type')).values('agent_type').distinct()
    }

    if request.method == "POST":
        branch = request.POST.get('branch')

        cursor = connection.cursor()
        if branch == 'All':
            cursor.execute(
                "SELECT `logins`.`Emp_ID` AS emp_id,`doctor_agent_list`.`unique_id`,`doctor_agent_list`.`agent_type`,"
                "`doctor_agent_list`.`agent_name`,`doctor_agent_list`.`designation`,`doctor_agent_list`.`mobile`,"
                "`doctor_agent_list`.`company`,`doctor_agent_list`.`area`,`logins`.`Branch` AS branch"
                " FROM `doctor_agent_list` INNER JOIN `logins` ON `doctor_agent_list`.`emp_id` = `logins`.`Emp_ID`"
                " WHERE `doctor_agent_list`.`branch` in ('AS Rao Nagar','LB Nagar','Jubilee Hills','Kukatpally','Gachibowli') "
                "AND `doctor_agent_list`.`r_status` = 'Visit' LIMIT 1000;")
        else:
            cursor.execute(
                "SELECT `logins`.`Emp_ID` AS emp_id,`doctor_agent_list`.`unique_id`,`doctor_agent_list`.`agent_type`,`doctor_agent_list`.`agent_name`,"
                "`doctor_agent_list`.`designation`,`doctor_agent_list`.`mobile`,`doctor_agent_list`.`company`,`doctor_agent_list`.`area`,`logins`.`Branch` ,"
                "AS branch FROM `doctor_agent_list` INNER JOIN `logins` ON`doctor_agent_list`.`emp_id` = `logins`.`Emp_ID` WHERE "
                "`doctor_agent_list`.`r_status` = 'Visit' AND `doctor_agent_list`.`branch` != 'Test' AND `doctor_agent_list`.`branch` = {bn}".format(
                    bn=branch))

        desc = cursor.description
        context['total_referral'] = [
            dict(zip([i[0] for i in desc], row)) for row in cursor.fetchall()
        ]

    if request.method == "GET" and request.is_ajax():
        unique_id = request.GET.get('unique_id')
        res = list(DoctorAgentList.objects.filter(unique_id=unique_id).values())[0]
        return JsonResponse(res)

    if 'edit' in request.GET:
        edit = request.GET.get('edit')
        context['total_referral'] = DoctorAgentList.objects.get(unique_id=edit)
        messages.success(request, 'Updated successfully....')
        return redirect('total_referral_list')

    if request.POST.get('unique_id'):
        unique_id = request.POST.get("unique_id")
        emp_id = request.POST.get("emp_id")
        agent_name = request.POST.get("agent_name")
        mobile = request.POST.get("mobile")
        company = request.POST.get("company")
        agent_type = request.POST.get("agent_type")
        DoctorAgentList.objects.filter(unique_id=unique_id, emp_id=emp_id, agent_name=agent_name).update(mobile=mobile,
                                                                                                         company=company,
                                                                                                         agent_type=agent_type)
    return render(request, 'referral/total_referral_list.html', context)


@login_required(login_url="/")
def referral_details(request):
    context = {}

    if 'edit' in request.GET:
        edit = request.GET.get('edit')
        context['search_ref'] = DoctorAgentList.objects.get(unique_id=edit)
        messages.success(request, 'Updated succesfully....')

    if request.POST.get('emp_id'):
        emp_id = request.POST.get('emp_id ')
        unique_id = request.POST.get('unique_id ')
        agent_type = request.POST.get('agent_type ')
        agent_name = request.POST.get('agent_name ')
        designation = request.POST.get('designation ')
        mobile = request.POST.get('mobile ')
        company = request.POST.get('company ')
        area = request.POST.get('area ')
        branch = request.POST.get('branch')
        DoctorAgentList.objects.filter(emp_id=emp_id, unique_id=unique_id, agent_type=agent_type, agent_name=agent_name,
                                       designation=designation).update(mobile=mobile, company=company, branch=branch,
                                                                       area=area)

    return render(request, 'referral/referral_details.html', context)


@login_required(login_url="/")
def new_referral_list(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test'))
    }

    if request.method == "POST":
        f_date = request.POST.get('date')

        from_d, to_d = f_date.split(' - ')
        from_d = datetime.strptime(str(from_d), '%m/%d/%Y').date()
        to_d = datetime.strptime(str(to_d), '%m/%d/%Y').date()

        cursor = connection.cursor()
        cursor.execute(
            "SELECT `logins`.`Emp_ID`,`logins`.`Emp_name`,`doctor_agent_list`.`agent_name`,`doctor_agent_list`.`designation`,"
            "`doctor_agent_list`.`agent_type`,`doctor_agent_list`.`unique_id`,`doctor_agent_list`.`category`,"
            "`doctor_agent_list`.`date`,`logins`.`Branch` FROM `doctor_agent_list` INNER JOIN `logins` ON `logins`.`Emp_ID` = `doctor_agent_list`.`emp_id`"
            " WHERE `doctor_agent_list`.`branch` != 'Test' AND `doctor_agent_list`.`date` BETWEEN  '{fd}' AND '{td}';".format(
                fd=from_d, td=to_d))

        desc = cursor.description
        context['referral'] = [
            dict(zip([i[0] for i in desc], row)) for row in cursor.fetchall()
        ]
    return render(request, 'referral/new_referral_list.html', context)


@login_required(login_url="/")
def search_referral(request):
    context = {
        'agent': DoctorAgentList.objects.all()
    }
    # if 'delete' in request.GET:
    #     delete = request.GET.get('delete')
    #     data = DoctorAgentList.objects.get(unique_id=delete)
    #     data.delete()
    #     messages.success(request, 'Deleted succesfully')
    #     return redirect('search_referral')

    if request.method == 'POST':
        unique = request.POST.get('unique')
        mobile = request.POST.get('mobile')
        if unique:
            context["search_ref"] = DoctorAgentList.objects.filter(unique_id=unique)
        elif mobile:
            context["search_ref"] = DoctorAgentList.objects.filter(mobile=mobile)

    if request.method == "GET" and request.is_ajax():
        emp_id = request.GET.get('emp_id')
        response = list(DoctorAgentList.objects.filter(emp_id=emp_id).values())[0]
        return JsonResponse(response)

    if 'edit' in request.GET:
        edit = request.GET.get('edit')
        context['search_ref'] = DoctorAgentList.objects.get(unique_id=edit)
        messages.success(request, 'Updated succesfully....')

    if request.POST.get('emp_id'):
        emp_id = request.POST.get('emp_id ')
        unique_id = request.POST.get('unique_id ')
        agent_type = request.POST.get('agent_type ')
        agent_name = request.POST.get('agent_name ')
        designation = request.POST.get('designation ')
        mobile = request.POST.get('mobile ')
        company = request.POST.get('company ')
        area = request.POST.get('area ')
        branch = request.POST.get('branch')
        DoctorAgentList.objects.filter(emp_id=emp_id, unique_id=unique_id, agent_type=agent_type, agent_name=agent_name,
                                       designation=designation).update(mobile=mobile, company=company, branch=branch,
                                                                       area=area)

    return render(request, 'referral/search_referral.html', context)


@login_required(login_url="/")
def search_reff(request):
    draw = int(request.POST.get('draw'))
    length = int(request.POST.get('length'))
    search = request.POST.get('search[value]')
    colindex = request.POST.get("order[0][column]")
    records_total = DoctorAgentList.objects.all().order_by('unique_id').count()
    records_filtered = records_total
    agent_data = DoctorAgentList.objects.all().order_by('unique_id').values()

    if search:
        agent_data = DoctorAgentList.objects.filter(Q(unique_id__icontains=search) | Q(
            mobile__icontains=search)).order_by('unique_id').values()
        records_total = agent_data.count()
        records_filtered = records_total

    paginator = Paginator(agent_data, length)

    try:
        object_list = paginator.page(draw).object_list
    except PageNotAnInteger:
        object_list = paginator.page(draw).object_list
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages).object_list

    data = [
        {
            'sno': '',
            'emp_id ': emp['emp_id'],
            'unique_id ': emp['unique_id'],
            'agent_type ': emp['agent_type'],
            'agent_name ': emp['agent_name'],
            'designation ': emp['branch'],
            'mobile ': emp['mobile'],
            'company ': emp['company'],
            'area ': emp['area'],
            'branch ': emp['branch'],
        } for emp in object_list
    ]
    return JsonResponse(
        {"draw": draw, "iTotalRecords": records_total, 'recordsFiltered': records_filtered, "data": data}, safe=False)


@login_required(login_url="/")
def patient_referral(request):
    context = {}
    if request.method == 'POST':
        filter_date = request.POST.get('date')

        first_date, last_date = filter_date.split(' - ')
        first_date = datetime.strptime(str(first_date), '%m/%d/%Y')
        last_date = datetime.strptime(str(last_date), '%m/%d/%Y')

        if filter_date:
            context['patient_ref'] = PatientReferrals.objects.filter(date__gte=first_date,
                                                                     date__lte=last_date).order_by('date')

    return render(request, 'referral/patient_referral.html', context)


@login_required(login_url="/")
def abc_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ABC_report_Sheet.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Emp_ID', 'Emp_name', 'ref_type', 'unique_id', 'name', 'camp', 'camp_details', 'date', 'time', 'location',
        'reason', 'Type', 'source', 'branch', 'agent_name', 'attendance', 'camp_details',

    ])
    cursor = connection.cursor()
    cursor.execute("SELECT `logins`.`Emp_ID`, `logins`.`Emp_name`, `call_report_master`.`ref_type`,"
                   "`call_report_master`.`unique_id`, `call_report_master`.`name`, `call_report_master`.`camp`, "
                   "`call_report_master`.`camp_details`, `call_report_master`.`date`, `call_report_master`.`time`, "
                   "`call_report_master`.`location`, `call_report_master`.`reason`, `call_report_master`.`Type`, "
                   "`call_report_master`.`source`,`call_report_master`.`branch`, `doctor_agent_list`.`agent_name`,"
                   "`call_report_master`.`attendance`,`call_report_master`.`camp_details`FROM `call_report_master` "
                   "INNER JOIN `logins` ON `call_report_master`.`emp_id` = `logins`.`Emp_ID` INNER JOIN "
                   "`doctor_agent_list` on `call_report_master`.`unique_id` = `doctor_agent_list`.`unique_id`   WHERE "
                   "`logins`.`Page` = 'Marketing' ORDER BY `logins`.`Branch` ASC")
    # row = cursor.fetchall()
    # print(row)

    # call_data = CallReportMaster.objects.all()

    for i in cursor:
        writer.writerow([
            i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[12], i[13], i[14], i[15],
            i[16]
        ])
    return response


@login_required(login_url="/")
def allowance_report(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test'))
    }
    # if request.method == "POST":
    #     branch = request.POST.get('branch')
    #     # date = request.POST.get('date')
    #
    #     # fdate, tdate = date.split(' - ')
    #     # fdate = datetime.strptime(str(fdate), '%m/%d/%Y').date()
    #     # tdate = datetime.strptime(str(tdate), '%m/%d/%Y').date()
    #
    #     if branch == 'All':
    #         context['allowance'] = Logins.objects.filter(page='Marketing', job_status='Active') & Logins.objects.filter(
    #             ~Q(branch='Test', designation='Center Head', type='Admin')).order_by('allow')
    #     else:
    #         context['allowance'] = Logins.objects.filter(page='Marketing', job_status='Active',
    #                                                      branch=branch) & Logins.objects.filter(
    #             ~Q(branch='Test', designation='Center Head', type='Admin')).order_by('allow')
    #
    #     # cursor = connection.cursor()
    #     # if branch == 'All':
    #     #     cursor.execute(
    #     #         "SELECT `Emp_ID`,`Emp_name`,`Branch` FROM `logins` WHERE `Page` = 'page' AND `Job_Status` = 'Job_Status' AND "
    #     #         "`Branch` = 'Branch'  AND `Designation` != '' AND `Date` BETWEEN '{fd}' AND '{td}' AND `type`!= `Original_Type` ORDER BY `allow` DESC;")
    #     #             # .format(
    #     #             # fd=fdate, td=tdate))
    #     # else:
    #     #     cursor.execute(
    #     #         "SELECT `Emp_ID`,`Emp_name`,`Branch` FROM `logins` WHERE `Page` = 'Page' AND `Job_Status` = 'Job_Status' AND "
    #     #         "`Branch` != ''  AND `Designation` != '' AND `Date` BETWEEN '{fd}' AND '{td}' AND `Branch` = '{bn}' AND `type`!= `Original_Type` ORDER BY `allow` DESC;")
    #     #             # .format(
    #     #             # fd=fdate, td=tdate, bn=branch))

    if request.method == "POST":
        branch = request.POST.get('branch')
        filter_date = request.POST.get('date')

        from_d, to_d = filter_date.split(' - ')
        from_d = datetime.strptime(str(from_d), '%m/%d/%Y').date()
        to_d = datetime.strptime(str(to_d), '%m/%d/%Y').date()

        cursor = connection.cursor()
        if branch == 'All':
            cursor.execute(f"""SELECT `call_report_master`.`emp_id` AS Emp_ID,`logins`.`Emp_name` AS Emp_name,
                `logins`.`Branch` AS Branch, `logins`.`allow` AS Allowance,
                 COUNT(DISTINCT `call_report_master`.`date`) AS Total_Days,
                 COUNT(`call_report_master`.`emp_id`) AS Total_Calls, CASE WHEN `logins`.`allow` = 300 THEN 25.00
                 WHEN `logins`.`allow` = 250 THEN 21 ELSE 0.00 END AS Per_Day_Allowance,
                 COUNT(`call_report_master`.`emp_id`) * CASE  WHEN `logins`.`allow` = 300 THEN 25.00
                  WHEN `logins`.`allow` = 250 THEN 21  ELSE 0.00  END As TOTAL FROM `call_report_master`
                 INNER JOIN `logins` ON `call_report_master`.`emp_id` = `logins`.`Emp_ID` WHERE
                `call_report_master`.`date` BETWEEN '{from_d}' AND '{to_d}'  and `logins`.`Branch` != 'Test'
                 AND `logins`.`Job_Status` = 'Active' AND `logins`.`Designation` != 'Center Head'
                 AND `logins`.`Page` = 'Marketing' AND `logins`.`type` != 'Admin' GROUP BY
                `call_report_master`.`emp_id` ORDER BY`logins`.`allow` DESC;""".format(fd=from_d, td=to_d))
        else:
            cursor.execute(
                "SELECT `call_report_master`.`emp_id` AS Emp_ID,`logins`.`Emp_name` AS Emp_name,"
                "`logins`.`Branch` AS Branch, `logins`.`allow` AS Allowance,"
                " COUNT(DISTINCT `call_report_master`.`date`) AS Total_Days,"
                " COUNT(`call_report_master`.`emp_id`) AS Total_Calls, CASE WHEN `logins`.`allow` = 300 THEN 25.00"
                " WHEN `logins`.`allow` = 250 THEN 21 ELSE 0.00 END AS Per_Day_Allowance,"
                " COUNT(`call_report_master`.`emp_id`) * CASE  WHEN `logins`.`allow` = 300 THEN 25.00"
                "  WHEN `logins`.`allow` = 250 THEN 21 ELSE 0.00  END As TOTAL FROM `call_report_master`"
                " INNER JOIN `logins` ON `call_report_master`.`emp_id` = `logins`.`Emp_ID` WHERE"
                "`call_report_master`.`date` BETWEEN '{fd}' AND '{td}' and `logins`.`Branch` = '{bn}'  and `logins`.`Branch` != 'Test'"
                " AND `logins`.`Job_Status` = 'Active' AND `logins`.`Designation` != 'Center Head'"
                " AND `logins`.`Page` = 'Marketing' AND `logins`.`type` != 'Admin' GROUP BY"
                "`call_report_master`.`emp_id` ORDER BY`logins`.`allow` DESC;".format(fd=from_d, td=to_d, bn=branch))
        ina = cursor.description
        context['allowance'] = [
            dict(zip([i[0] for i in ina], list)) for list in cursor.fetchall()
        ]

    return render(request, 'referral/allowance_report.html', context)


# SELECT (SELECT `emp_id`) AS empid,(SELECT `name`) AS empname,IFNULL((SELECT COUNT(DISTINCT `date`) FROM `call_report_master` WHERE (`emp_id` =  `Emp_ID` AND `date` BETWEEN '2021-01-01' AND '2022-04-08' AND `camp` != 'Hospital Visit') AND (`emp_id` = `Emp_ID` AND `date` BETWEEN  '2020-01-01' AND '2022-04-08' AND `camp` != 'Office Work') AND (`emp_id` =  `emp_id` AND `date` BETWEEN  '2019-01-01' AND '2022-04-08' AND `camp` != 'Meeting') GROUP BY `emp_id`),0) AS TOTALDAYS,IFNULL((SELECT COUNT(`date`) FROM `call_report_master` WHERE (`emp_id` = `Emp_ID` AND `date` BETWEEN  '2021-01-01' AND '2022-04-08' AND `camp` != 'Hospital Visit' ) AND (`emp_id` =  `emp_id` AND `date` BETWEEN  '2021-01-01' AND '2022-04-08' AND `camp` != 'Office Work') AND (`emp_id` =  `emp_id` AND `date` BETWEEN  '2021-01-01' AND '2022-04-08' AND `camp` != 'Meeting') GROUP BY `emp_id`),0) AS TOTALCALLS,(SELECT (`logins`.`allow`) FROM `call_report_master` INNER JOIN `logins` ON `call_report_master`.`emp_id` = `logins`.`Emp_ID` WHERE `logins`.`Emp_ID` = `Emp_ID` LIMIT 1) AS ALLOWANCE,(SELECT ROUND((`logins`.`allow`/12),2) FROM `call_report_master` INNER JOIN `logins` ON `call_report_master`.`emp_id` = `logins`.`Emp_ID` WHERE `logins`.`Emp_ID` = `Emp_ID` LIMIT 1) AS PERDAYALLOWNACE,(SELECT IF(TOTALCALLS != '',ROUND(PERDAYALLOWNACE*TOTALCALLS,2),0)) AS TOTALALLOWANCE;

@login_required(login_url="/")
def inactive_allowance_report(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test'))
    }
    if request.method == "POST":
        branch = request.POST.get('branch')
        filter_date = request.POST.get('date')

        from_d, to_d = filter_date.split(' - ')
        from_d = datetime.strptime(str(from_d), '%m/%d/%Y').date()
        to_d = datetime.strptime(str(to_d), '%m/%d/%Y').date()

        cursor = connection.cursor()
        if branch == 'All':
            cursor.execute(f"""SELECT `call_report_master`.`emp_id` AS Emp_ID,`logins`.`Emp_name` AS Emp_name,
                `logins`.`Branch` AS Branch, `logins`.`allow` AS Allowance,
                 COUNT(DISTINCT `call_report_master`.`date`) AS Total_Days,
                 COUNT(`call_report_master`.`emp_id`) AS Total_Calls, CASE WHEN `logins`.`allow` = 300 THEN 25.00
                 WHEN `logins`.`allow` = 250 THEN 21 ELSE 0.00 END AS Per_Day_Allowance,
                 COUNT(`call_report_master`.`emp_id`) * CASE  WHEN `logins`.`allow` = 300 THEN 25.00
                  WHEN `logins`.`allow` = 250 THEN 21 ELSE 0.00  END As TOTAL FROM `call_report_master`
                 INNER JOIN `logins` ON `call_report_master`.`emp_id` = `logins`.`Emp_ID` WHERE
                `call_report_master`.`date` BETWEEN '{from_d}' AND '{to_d}'
                 AND `logins`.`Job_Status` = 'Inactive' AND `logins`.`Designation` != 'Center Head'
                 AND `logins`.`Page` = 'Marketing' AND `logins`.`type` != 'Admin' GROUP BY
                `call_report_master`.`emp_id` ORDER BY`logins`.`allow` DESC;""".format(fd=from_d, td=to_d))
        else:
            cursor.execute(
                "SELECT `call_report_master`.`emp_id` AS Emp_ID,`logins`.`Emp_name` AS Emp_name,"
                "`logins`.`Branch` AS Branch, `logins`.`allow` AS Allowance,"
                " COUNT(DISTINCT `call_report_master`.`date`) AS Total_Days,"
                " COUNT(`call_report_master`.`emp_id`) AS Total_Calls, CASE WHEN `logins`.`allow` = 300 THEN 25.00"
                " WHEN `logins`.`allow` = 250 THEN 21 ELSE 0.00 END AS Per_Day_Allowance,"
                " COUNT(`call_report_master`.`emp_id`) * CASE  WHEN `logins`.`allow` = 300 THEN 25.00"
                "  WHEN `logins`.`allow` = 250 THEN 21  ELSE 0.00  END As TOTAL FROM `call_report_master`"
                " INNER JOIN `logins` ON `call_report_master`.`emp_id` = `logins`.`Emp_ID` WHERE"
                "`call_report_master`.`date` BETWEEN '{fd}' AND '{td}' and `logins`.`Branch` = '{bn}'"
                " AND `logins`.`Job_Status` = 'Inactive' AND `logins`.`Designation` != 'Center Head'"
                " AND `logins`.`Page` = 'Marketing' AND `logins`.`type` != 'Admin' GROUP BY"
                "`call_report_master`.`emp_id` ORDER BY`logins`.`allow` DESC;".format(fd=from_d, td=to_d, bn=branch))
        ina = cursor.description
        context['inactive'] = [
            dict(zip([i[0] for i in ina], list)) for list in cursor.fetchall()
        ]
    return render(request, 'referral/inactive_allowance_report.html', context)


@login_required(login_url="/")
def bill_list(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test')),
    }

    if request.method == "POST":
        sno = request.POST.get('modal_sno')
        unique_id = request.POST.get('unique_id')
        patient_name = request.POST.get('patient_name')
        agent_name = request.POST.get('agent_name')
        calculationtype = request.POST.get('referralpercentagename')
        referralpercentage = request.POST.get('referralpercentage')
        referralamount = request.POST.get('referralamount')
        paymentmode = request.POST.get('paymentmode')
        ref_type = request.POST.get('referral_type')
        # print(sno)
        if paymentmode == "NetBanking":
            accnumber = request.POST.get("accnumber")
            ifsccode = request.POST.get("ifsccode")
            pancard = request.POST.get("pancard")
            upinumber = None
        elif paymentmode == "UPI":
            accnumber = None
            ifsccode = None
            pancard = None
            upinumber = request.POST.get("upinumber")
        elif paymentmode == "Cash":
            accnumber = None
            ifsccode = None
            pancard = None
            upinumber = None
        else:
            accnumber = None
            ifsccode = None
            pancard = None
            upinumber = None
        doctor_agent = DoctorAgentList.objects.get(unique_id=unique_id)
        if doctor_agent.bank_ac == "No Update" or doctor_agent.bank_ac == "":
            if paymentmode == "NetBanking":
                doctor_agent.bank_ac = accnumber
                doctor_agent.ifsc = ifsccode
                doctor_agent.pancard = pancard
                doctor_agent.save()
            # print(sno)
            PatientData.objects.filter(sno=sno).update(ucid=unique_id,
                                                       referral_cal_by=request.user.emp_id,
                                                       referralcreatedby=request.user.emp_id,
                                                       ucidcreatedon=timezone.now(),
                                                       referralcreatedon=timezone.now(),
                                                       patient_name=patient_name,
                                                       referralname=agent_name,
                                                       referralpercentagename=calculationtype,
                                                       referralpercentage=referralpercentage,
                                                       referralamount=referralamount,
                                                       referral_type=ref_type,
                                                       paymentmode=paymentmode,
                                                       accnumber=accnumber,
                                                       ifsccode=ifsccode,
                                                       pancard=pancard, upinumber=upinumber,
                                                       referralstatus='Yes')
            messages.success(request, "Updated successfully")

        else:
            # print(doctor_agent.unique_id)
            PatientData.objects.filter(sno=sno).update(ucid=unique_id,
                                                       referral_cal_by=request.user.emp_id,
                                                       referralcreatedby=request.user.emp_id,
                                                       ucidcreatedon=timezone.now(),
                                                       referralcreatedon=timezone.now(),
                                                       patient_name=patient_name,
                                                       referralname=agent_name,
                                                       referralpercentagename=calculationtype,
                                                       referralpercentage=referralpercentage,
                                                       referralamount=referralamount,
                                                       referral_type=ref_type,
                                                       paymentmode=paymentmode,
                                                       accnumber=doctor_agent.bank_ac,
                                                       ifsccode=doctor_agent.ifsc,
                                                       pancard=doctor_agent.pancard, upinumber=upinumber,
                                                       referralstatus='Yes')

            messages.success(request, "Updated successfully")
        return redirect('bill_list')

    if request.method == "GET" and request.is_ajax():
        sno = int(request.GET.get('sno'))
        res = list(PatientData.objects.filter(sno=sno).values())[0]
        return JsonResponse(res)

    if 'delete_sno' in request.GET and request.is_ajax():
        delete_sno = request.GET.get('delete_sno')
        PatientData.objects.get(sno=delete_sno)
        messages.success(request, 'Deleted succesfully')
        return JsonResponse({"success": True})

    return render(request, 'bills_list.html', context)


@login_required(login_url="/")
def bill(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test')),
    }
    if 'date' in request.POST:
        date_range_str = request.POST.get('date')
        if date_range_str:
            start_date_str, end_date_str = date_range_str.split(' - ')

            # Convert the start and end dates to datetime objects
            start_date_obj = datetime.strptime(start_date_str, '%m/%d/%Y')
            end_date_obj = datetime.strptime(end_date_str, '%m/%d/%Y')

            # Convert the datetime objects to strings in the desired format
            start_date_formatted = start_date_obj.strftime('%Y-%m-%d')
            end_date_formatted = end_date_obj.strftime('%Y-%m-%d')

            # Use the formatted dates to filter the CallReportMaster objects
            context["admission"] = PatientData.objects.filter(
                invoice_date__range=[start_date_formatted, end_date_formatted])

            context["date_range"] = date_range_str

    return render(request, 'bill_list.html', context)


@login_required(login_url="/")
def admission_list_filter(request):
    date = request.GET.get('date')
    draw = int(request.GET.get('draw'))
    start = int(request.GET.get('start'))
    length = int(request.GET.get('length'))
    search = request.GET.get('search[value]')
    colindex = request.GET.get("order[0][column]")

    if date is not None:
        records_total = PatientData.objects.filter(invoice_date__lte=date, invoice_date__gte=date,
                                                   referralstatus='').order_by('sno').count()
        records_filtered = records_total
        agent_data = PatientData.objects.filter(invoice_date__lte=date, invoice_date__gte=date,
                                                referralstatus='').order_by('sno').values()[
                     start:length + start]
        if search:
            agent_data = PatientData.objects.filter(Q(invoice_date__lte=search, invoice_date__gte=search)).order_by(
                'sno').values()
            records_total = agent_data.count()
            records_filtered = records_total

    else:
        records_total = PatientData.objects.filter(referralstatus='').order_by('sno').count()
        records_filtered = records_total
        agent_data = PatientData.objects.filter(referralstatus='').order_by('sno').values()
        if search:
            agent_data = PatientData.objects.filter(Q(invoice_date__lte=search, invoice_date__gte=search)).order_by(
                'sno').values()

            records_total = agent_data.count()
            records_filtered = records_total
    paginator = Paginator(agent_data, length)
    try:
        object_list = paginator.page(draw).object_list
    except PageNotAnInteger:
        object_list = paginator.page(draw).object_list
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages).object_list

    data = [
        {
            'sno': emp['sno'],
            'edit': '',
            'invoice_no': emp['invoice_no'],
            'invoice_date': emp['invoice_date'],
            'branch': emp['branch'],
            'patient_name': emp['patient_name'],
            'service_name': emp['service_name'],
            'department_name': emp['department_name'],
            'grossamount': emp['grossamount'],
            'discount': emp['discount'],
            'netamount': emp['netamount'],

        } for emp in object_list
    ]
    return JsonResponse(
        {"draw": draw, "iTotalRecords": records_total, 'recordsFiltered': records_filtered, "data": data},
        safe=False)


@login_required(login_url="/")
@csrf_exempt
def admission(request):
    draw = int(request.POST.get('draw'))
    start = int(request.POST.get('start'))
    length = int(request.POST.get('length'))
    search = request.POST.get('search[value]')
    colindex = request.POST.get("order[0][column]")
    records_total = PatientData.objects.filter(referralstatus='').order_by('sno').count()
    records_filtered = records_total
    agent_data = PatientData.objects.filter(referralstatus='').order_by('sno').values()[start:length + start]
    if search:
        agent_data = PatientData.objects.filter(Q(sno=search) & Q(referralstatus='')).order_by('sno').values()[
                     start:length + start]
        records_total = agent_data.count()
        records_filtered = records_total

    # paginator = Paginator(agent_data, length)
    #
    # try:
    #     object_list = paginator.page(draw).object_list
    # except PageNotAnInteger:
    #     object_list = paginator.page(draw).object_list
    # except EmptyPage:
    #     object_list = paginator.page(paginator.num_pages).object_list

    data = [
        {
            'sno': emp['sno'],
            # 'edit': '',
            'edit': '<a href="#"  onclick="editAdmission(' + str(emp[
                                                                     'sno']) + ')" class="icon-pencil mr-2 text-info" data-toggle="modal" data-target="#admissionModal" ></a><a href="/admission_list/?delete=' + str(
                emp['sno']) + '" class="btn btn-sm btn-danger"><i class="icon-trash" aria-hidden="true"></i></a>',
            'invoice_no': emp['invoice_no'],
            'invoice_date': emp['invoice_date'],
            'branch': emp['branch'],
            'patient_name': emp['patient_name'],
            'marketing_executive': emp['marketing_executive'],
            'referral_type': emp['referral_type'],
            'referralpercentage': emp['referralpercentage'],
            'referralpercentagename': emp['referralpercentagename'],
            'grossamount': emp['grossamount'],
            'discount': emp['discount'],
            'netamount': emp['netamount'],
            'referralamount': emp['referralamount'],
            'ucidcreatedon': emp['ucidcreatedon'],
            'paymentmode': emp['paymentmode'],
            'department_name': emp['department_name'],
            'service_name': emp['service_name'],
        } for emp in agent_data

    ]
    return JsonResponse(
        {"draw": draw, "iTotalRecords": records_total, 'recordsFiltered': records_filtered,
         "iTotalDisplayRecords": records_total, "data": data}, safe=False)


@login_required(login_url="/")
def recent_updates(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test')),
        'agent_type': DoctorAgentList.objects.filter(~Q(agent_type='Type')).values('agent_type').distinct()
    }
    if 'delete' in request.GET:
        delete = request.GET.get('delete')
        data = DoctorAgentList.objects.get(unique_id=delete)
        data.delete()
        messages.success(request, 'Deleted succesfully')
        return redirect('recent_updates')

    if request.method == "POST":
        branch = request.POST.get('branch')

        if branch == 'All':
            context['update'] = DoctorAgentList.objects.filter(~Q(url='', emp_id='1234', branch='Test')).order_by(
                'emp_id', 'branch')
        else:
            context['update'] = DoctorAgentList.objects.filter(
                ~Q(url='', emp_id='1234', branch='Test')) & DoctorAgentList.objects.filter(branch=branch).order_by(
                'emp_id', 'branch')

    if request.method == "GET" and request.is_ajax():
        unique_id = request.GET.get('unique_id')
        response = list(DoctorAgentList.objects.filter(unique_id=unique_id).values())[0]
        return JsonResponse(response)

    if 'edit' in request.GET:
        edit = request.GET.get('edit')
        context['re'] = DoctorAgentList.objects.get(unique_id=edit)
        messages.success(request, 'Updated succesfully....')

    if request.POST.get('unique_id'):
        unique_id = request.POST.get("unique_id")
        emp_id = request.POST.get("emp_id")
        agent_name = request.POST.get("agent_name")
        mobile = request.POST.get("mobile")
        company = request.POST.get("company")
        agent_type = request.POST.get("agent_type")
        area = request.POST.get("area")
        DoctorAgentList.objects.filter(unique_id=unique_id, emp_id=emp_id, agent_name=agent_name).update(mobile=mobile,
                                                                                                         company=company,
                                                                                                         agent_type=agent_type,
                                                                                                         area=area)

    return render(request, 'referral/recent_updates.html', context)


@login_required(login_url="/")
def bifurcation_list(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test')),
        'agent_type': DoctorAgentList.objects.filter(~Q(agent_type='Type')).values('agent_type').distinct()
    }

    cursor = connection.cursor()
    if request.method == "POST":
        branch = request.POST.get('branch')

        if branch == 'All':
            cursor.execute(
                "SELECT `logins`.`Branch`, COUNT(DISTINCT `logins`.`Emp_ID`) AS ce, COUNT(`doctor_agent_list`.`unique_id`) "
                "AS CDU FROM `logins` LEFT JOIN `doctor_agent_list` ON `logins`.`Emp_ID` = `doctor_agent_list`.`emp_id` "
                "WHERE `logins`.`Job_Status` = 'Active' AND `logins`.`Page` = 'Marketing' GROUP BY `logins`.`Branch` ORDER BY `logins`.`Branch` ASC;")
            # else:
            #     cursor.execute("SELECT `unique_id`,if(COUNT(`unique_id`)=1,1,0) AS V1,if(COUNT(`unique_id`)=2,1,0) AS V2,"
            #                    "if(COUNT(`unique_id`)>2,1,0) AS V3 FROM `call_report_master` WHERE `branch` = 'kukatpally' AND "
            #                    "MONTH(`date`) = MONTH(CURRENT_DATE()) AND YEAR(`date`) = YEAR(CURRENT_DATE()) GROUP BY `unique_id` ORDER BY `emp_id` ASC;".format(bn=branch))

            bifu = cursor.description
            # print(cursor)
            context['bifurcation'] = [
                dict(zip([i[0] for i in bifu], list)) for list in cursor.fetchall()
            ]

    return render(request, 'referral/bifurcation_list.html', context)


@login_required(login_url="/")
def attendance_list(request):
    context = {
    }
    if request.method == 'POST':
        date_d = request.POST.get('date_d')

        from_d, to_d = date_d.split(' - ')
        from_d = datetime.strptime(str(from_d), '%m/%d/%Y')
        to_d = datetime.strptime(str(to_d), '%m/%d/%Y')

        cursor = connection.cursor()
        cursor.execute("""SELECT l.`emp_id`, l.`emp_name`,  crm.`date`, MIN(crm.`time`) AS `first_time`,
                         MAX(crm.`time`) AS `last_time`,crm.`attendance`, crm.`branch`
                        FROM `call_report_master` crm JOIN `logins` l ON crm.`emp_id` = l.`emp_id` 
                         WHERE l.`Job_Status` = 'Active' AND l.`Page` = 'Marketing' AND l.`type` != 'Center Head' 
                        AND crm.`emp_id` IS NOT NULL AND crm.`date` between '{fd}' AND '{td}' and 
                       l.branch IN ('Kukatpally', 'As Rao Nagar', 'Gachibowli', 'LB Nagar', 'Jubilee Hills', 'Corporate')
                        GROUP BY crm.`date`, crm.`emp_id` ORDER BY l.branch ASC;""".format(fd=from_d, td=to_d))
        call = cursor.description
        context['attendance'] = [
            dict(zip([i[0] for i in call], report)) for report in cursor.fetchall()
        ]

    return render(request, 'Employee/attendance_list.html', context)


@login_required(login_url="/")
def employee_leave_list(request):
    url = f'http://3.6.104.94/api/employee-leaves/?from_date={timezone.now().date()}&to_date={timezone.now().date()}'
    response = requests.get(url)
    response = json.loads(response.text)

    if request.method == 'POST':
        filter_date = request.POST.get('date')

        fdate, tdate = filter_date.split(' - ')
        fdate = datetime.strptime(str(fdate), '%m/%d/%Y').date()
        tdate = datetime.strptime(str(tdate), '%m/%d/%Y').date()

        url = f'http://3.6.104.94/api/employee-leaves/?from_date={fdate}&to_date={tdate}'
        response = requests.get(url)
        response = json.loads(response.text)

    context = {
        'data': response,
    }
    return render(request, 'Employee/employee_leave_list.html', context)


@login_required(login_url="/")
def daily_call_report(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test')),
        # 'ref_type': CallReportMaster.objects.filter(Q(ref_type='ref_type'))
    }
    cursor = connection.cursor()
    if 'date' in request.POST:
        date = request.POST.get('date')

        cursor.execute(
            "SELECT `logins`.`emp_id`, `logins`.`Emp_name`, `call_report_master`.`ref_type`,"
            " `call_report_master`.`unique_id`, `call_report_master`.`name`, `call_report_master`.`camp`,"
            "`call_report_master`.`date`, `call_report_master`.`time`, `call_report_master`.`location`, "
            "`call_report_master`.`reason`, `call_report_master`.`Type`, `call_report_master`.`source`,`call_report_master`.`branch` "
            "FROM `call_report_master` INNER JOIN `logins` ON `call_report_master`.`emp_id` = `logins`.`emp_id`"
            " WHERE `call_report_master`.`date` = '{d}' AND `call_report_master`.`branch` != 'Test' AND `logins`.`Page` = 'Marketing'"
            " ORDER BY `logins`.`Branch` ASC;".format(d=date))

        call = cursor.description
        context['daily'] = [
            dict(zip([i[0] for i in call], report)) for report in cursor.fetchall()
        ]

    elif 'unique_id' in request.POST:
        unique_id = request.POST.get("unique_id")
        emp_id = request.POST.get("emp_id")
        name = request.POST.get("name")
        types = request.POST.get("type")
        ref_type = request.POST.get("ref_type")
        CallReportMaster.objects.filter(unique_id=unique_id).update(emp_id=emp_id, name=name, type=types,
                                                                    ref_type=ref_type)
        messages.success(request, "Updated successfully....")

    if request.method == "GET" and request.is_ajax():
        unique_id = request.GET.get('unique_id')
        res = list(CallReportMaster.objects.filter(unique_id=unique_id).values())[0]
        return JsonResponse(res)

    return render(request, 'call/daily_call_report.html', context)


@login_required(login_url="/")
def day_report(request):
    context = {
        # 'report': Logins.objects.all()
    }
    if request.method == 'POST':
        date = request.POST.get('date')

        from_d, to_d = date.split(' - ')
        from_d = datetime.strptime(str(from_d), '%m/%d/%Y')
        to_d = datetime.strptime(str(to_d), '%m/%d/%Y')
        #
        # context['report'] = Logins.objects.filter(page='Marketing', job_status='Active', date=date
        #                                           ) & Logins.objects.filter(~Q(type='Center Head', new_type__contains='Neighbourhood')) \
        #                     & Logins.objects.filter(~Q(type='Admin')).order_by('branch', 'emp_id')

        # cursor = connection.cursor()
        # cursor.execute(
        #     "SELECT `logins`.`type`, `logins`.`Emp_ID`, `logins`.`Emp_name`, c.`first_time`, c.`last_time`,c.`date`,"
        #     " `logins`.`ref_count`, c.`attendance`, `logins`.`Branch`, cc.`call_count`FROM `logins`"
        #     "INNER JOIN (SELECT `date`, `attendance`, `branch`, MIN(`time`) AS `first_time`, "
        #     "MAX(`time`) AS `last_time` FROM `call_report_master`WHERE `emp_id` IS NOT NULL"
        #     " GROUP BY `date`) AS c ON `logins`.`Branch` = c.`branch` LEFT JOIN (SELECT `emp_id`,"
        #     " `date`, COUNT(*) AS `call_count` FROM `call_report_master` WHERE `emp_id`"
        #     " IS NOT NULL) AS cc ON `logins`.`Emp_ID` = cc.`emp_id`"
        #     "WHERE `logins`.`Page` = 'Marketing' AND `logins`.`Job_Status` = 'Active' AND `logins`.`type` != 'Center Head'"
        #     " AND NOT `logins`.`type` LIKE 'Neighbourhood' AND `logins`.`type` != `logins`.`Page`AND c.`date` = '{d}'"
        #     "ORDER BY `logins`.`Branch`, `logins`.`levels` ASC;".format(d=date))
        # day = cursor.description
        # context['report'] = [
        #     dict(zip([i[0] for i in day], rep)) for rep in cursor.fetchall()
        # ]
        cursor = connection.cursor()
        cursor.execute("SELECT l.`emp_id`, l.`emp_name`,l.`Orginal_Design`, crm.`attendance`, crm.`branch`,crm.`date`, "
                       "MIN(crm.`time`) AS `first_time`, MAX(crm.`time`) AS `last_time`, "
                       "COUNT(*) AS `call_count`, l.`ref_count`, l.`type` FROM `call_report_master` crm "
                       "INNER JOIN `logins` l ON crm.`emp_id` = l.`emp_id` WHERE l.`Job_Status` = 'Active' and "
                       # "l.`Page` = 'Marketing' AND l.`Job_Status` = 'Active' AND "
                       # "(l.`Designation` != 'Center Head') AND 
                       "crm.`date` "
                       "BETWEEN '{fd}' AND '{td}' "
                       # "l.branch != 'Test' AND NOT l.`type` LIKE 'Neighbourhood' and crm.`emp_id` IS NOT NULL "
                        " GROUP BY crm.`date`, crm.`emp_id` ORDER BY crm.`date` "
                       "ASC;".format(fd=from_d, td=to_d))
        day = cursor.description
        context['report'] = [
            dict(zip([i[0] for i in day], rep)) for rep in cursor.fetchall()
        ]

    return render(request, 'call/day_report.html', context)


@login_required(login_url="/")
def n_day_report(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        cur = connection.cursor()
        cur.execute(
            "SELECT `Emp_name`,`Emp_ID`,`new_type`,`Branch`,`ref_count` FROM `logins` WHERE `Page` = page"
            " AND `Job_Status` = Job_Status  AND `type` != new_type AND `new_type` LIKE new_type ORDER BY `Branch`,`levels` ASC;")
        cur.fetchall()
    return render(request, 'call/ndy.html')


@login_required(login_url="/")
def camp_report(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test'))
    }

    if request.method == "POST":
        filter_date = request.POST.get('date')

        fdate, tdate = filter_date.split(' - ')
        fdate = datetime.strptime(str(fdate), '%m/%d/%Y').date()
        tdate = datetime.strptime(str(tdate), '%m/%d/%Y').date()

        data = connection.cursor()
        if filter_date:
            data.execute(
                "SELECT `camp_create`.`sno`,`camp_create`.`empid`,`camp_create`.`empname`,`camp_create`.`state`,"
                "`camp_create`.`zone`,`camp_create`.`area`,`camp_create`.`colonyname`,`camp_create`.`camptype`,"
                "`camp_create`.`transid`,`camp_create`.`branch`,DATE_FORMAT(`camp_create`.`date_time`,'%d-%m-%Y') "
                "AS date_time,`camp_create`.`status`,COUNT(`camp_reg`.`transid`) AS registration FROM `camp_create` "
                "INNER JOIN `camp_reg` ON `camp_create`.`transid` = `camp_reg`.`transid` WHERE"
                " DATE_FORMAT(`camp_create`.`date_time`,'%Y-%m-%d') BETWEEN '{fd}' AND '{td}' and `camp_create`.`branch` !='Test' GROUP BY "
                "`camp_reg`.`transid` ORDER BY `camp_create`.`date_time` ASC;".format(
                    fd=fdate, td=tdate))
        desc = data.description
        context['camp'] = [
            dict(zip([i[0] for i in desc], row)) for row in data.fetchall()
        ]
    else:
        data = connection.cursor()
        data.execute("SELECT `camp_create`.`sno`,`camp_create`.`empid`,`camp_create`.`empname`,`camp_create`.`state`,"
                     "`camp_create`.`zone`,`camp_create`.`area`,`camp_create`.`colonyname`,`camp_create`.`camptype`,"
                     "`camp_create`.`transid`,`camp_create`.`branch`,DATE_FORMAT(`camp_create`.`date_time`,'%d-%m-%Y') "
                     "AS date_time,`camp_create`.`status`,COUNT(`camp_reg`.`transid`) AS registration FROM `camp_create` "
                     "INNER JOIN `camp_reg` ON `camp_create`.`transid` = `camp_reg`.`transid` where `camp_create`.`branch` !='Test' GROUP BY "
                     "`camp_reg`.`transid` ORDER BY `camp_create`.`date_time` ASC;")
        desc = data.description
        context['camp'] = [
            dict(zip([i[0] for i in desc], row)) for row in data.fetchall()
        ]

    return render(request, 'call/camp_report.html', context)


@login_required(login_url="/")
def processed_ref(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test'))
    }
    if request.method == "POST":
        branch_name = request.POST.get('branch')
        first_date = request.POST.get('date')

        fr_date, tm_date = first_date.split(' - ')
        fr_date = datetime.strptime(str(fr_date), '%m/%d/%Y').date()
        tm_date = datetime.strptime(str(tm_date), '%m/%d/%Y').date()

        cursor = connection.cursor()
        if branch_name == 'All':
            cursor.execute(
                """SELECT `invoice_no`, `patient_name`, DATE_FORMAT(`visit_data`,'%d-%b-%Y') AS adate,DATE_FORMAT(`invoice_date`,'%d-%b-%Y') AS ddate, `isbilldone` 
                AS admissionstatus, `patient_data`.`referralmobile` as referralmobile, `patient_data`.`branch` as branch,`patient_data`.`referraldepartment` as department,
                 `patient_data`.`organization` organization, `referralstatus`, `Admissiontype`, UPPER(`doctor_agent_list`.`agent_name`) AS referralname, 
                `referraldepartment`, `doctor_agent_list`.`mobile` as referralmobile, `referralremarks`, `paymentmode`, CONCAT('''',`doctor_agent_list`.`bank_ac`) 
                as accnumber,`doctor_agent_list`.`ifsc` as ifsccode, `doctor_agent_list`.`pancard` as pancard, `clashstatus`,DATE_FORMAT(`referralcreatedon`,'%d-%b-%Y %H:%i:%s') 
                AS referralcreatedon, `referralcreatedby`, `cluster_approval`,`cluster_approved_on`,(`phar_consum_billamount`) AS billamount, UPPER(`UCID`) AS referralcode,`referralamount`,`utr_no`,
                DATE(`utr_on`) FROM `patient_data` INNER JOIN `doctor_agent_list` ON `patient_data`.`UCID`=`doctor_agent_list`.`unique_id` WHERE `patient_data`.`branch` != 'Test' 
                AND `cluster_approval` = 'Approved' AND `doctor_agent_list`.`bank_ac`!='' AND `doctor_agent_list`.`bank_ac`!='null' AND `utr_no`!='NEFT Return'
                 AND `utr_no`!='Wrong Bank Details' AND DATE(`cluster_approved_on`) BETWEEN  '{fd}' AND '{td}' GROUP BY `invoice_no` ORDER BY `patient_data`.`branch`,
                `patient_data`.`utr_on`,`patient_data`.`discharge_datetime` ASC""".format(fd=fr_date, td=tm_date))
        else:
            cursor.execute(
                """SELECT `invoice_no`, `patient_name`, DATE_FORMAT(`visit_data`,'%d-%b-%Y') AS adate,DATE_FORMAT(`invoice_date`,'%d-%b-%Y') AS ddate, `isbilldone` 
                AS admissionstatus, `patient_data`.`referralmobile` as referralmobile, `patient_data`.`branch` as branch,`patient_data`.`referraldepartment` 
                as department,`patient_data`.`organization` organization, `referralstatus`, `Admissiontype`, UPPER(`doctor_agent_list`.`agent_name`) AS referralname,
                 `referraldepartment`, `doctor_agent_list`.`mobile` as referralmobile, `referralremarks`, `paymentmode`, CONCAT('''',`doctor_agent_list`.`bank_ac`) 
                as accnumber,`doctor_agent_list`.`ifsc` as ifsccode, `doctor_agent_list`.`pancard` as pancard, `clashstatus`,
                DATE_FORMAT(`referralcreatedon`,'%d-%b-%Y %H:%i:%s') AS referralcreatedon, `referralcreatedby`, `cluster_approval`, `cluster_approved_on`,(`phar_consum_billamount`) 
                AS billamount, UPPER(`UCID`) AS referralcode,`referralamount`,`utr_no`, DATE(`utr_on`) FROM `patient_data` INNER JOIN `doctor_agent_list` ON
                 `patient_data`.`UCID`=`doctor_agent_list`.`unique_id` WHERE `patient_data`.`branch` != 'Test' AND `cluster_approval` = 'Approved' AND
                 `doctor_agent_list`.`bank_ac`!='' AND `doctor_agent_list`.`bank_ac`!='null'  AND `utr_no`!='NEFT Return' AND `utr_no`!='Wrong Bank Details' AND
                 DATE(`cluster_approved_on`) BETWEEN  '{fd}' AND '{td}'   AND `patient_data`.`branch` = '{bn}' GROUP BY `invoice_no` ORDER BY `patient_data`.`branch`, `patient_data`.`utr_on`,
                `patient_data`.`discharge_datetime` ASC""".format(fd=fr_date, td=tm_date, bn=branch_name))
        print(cursor)
        payment = cursor.description
        context['process_ref'] = [
            dict(zip([i[0] for i in payment], pay)) for pay in cursor.fetchall()
        ]

    return render(request, 'processed_ref.html', context)


@login_required(login_url="/")
def wrong_bank_details(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test'))
    }

    if request.method == "POST":
        branch_n = request.POST.get('branch')
        f_date = request.POST.get('date')

        from_date, to_date = f_date.split(' - ')
        from_date = datetime.strptime(str(from_date), '%m/%d/%Y').date()
        to_date = datetime.strptime(str(to_date), '%m/%d/%Y').date()

        cursor = connection.cursor()
        if branch_n == 'All':
            cursor.execute(
                "SELECT `invoice_no`, `patient_name`, DATE_FORMAT(`visit_data`,'%d-%b-%Y') AS adate,DATE_FORMAT(`discharge_datetime`,'%d-%b-%Y') AS ddate,`isbilldone` AS admissionstatus, `patient_data`.`referralmobile` as mobile, `patient_data`.`branch` "
                "as branch,`patient_data`.`consultantentry` as consultantentry,`consultantremarks`,`patient_data`.`referraldepartment` as department, "
                "`patient_data`.`organization` organization, `referralstatus`, `Admissiontype`, UPPER(`doctor_agent_list`.`agent_name`) AS referralname, `referraldepartment`,"
                " `doctor_agent_list`.`mobile` as referralmobile, `referralremarks`, `paymentmode`, `doctor_agent_list`.`bank_ac` as accnumber,`doctor_agent_list`.`ifsc` as ifsccode, "
                "`doctor_agent_list`.`pancard` as pancard, `clashstatus`, DATE_FORMAT(`referralcreatedon`,'%d-%b-%Y %H:%i:%s') AS referralcreatedon, `referralcreatedby`,"
                " `chapproval`, (`phar_consum_billamount`) AS billamount,`referralpercentage`, ROUND(if(`referralmode` = 'Fixed Amount',`referralamount`,"
                "(`referralpercentage`/100)*(`phar_consum_billamount`-`phar_consum_billamount`)),2) AS referralamount2,`chapproval`,UPPER(`UCID`) AS referralcode,`referralamount` "
                "FROM `patient_data` INNER JOIN `doctor_agent_list` ON `patient_data`.`UCID`=`doctor_agent_list`.`unique_id`  WHERE `patient_data`.`branch` != 'Test' AND "
                "`cluster_approval` = 'Approved'  AND `doctor_agent_list`.`bank_ac`!='' AND `doctor_agent_list`.`bank_ac`!='null' AND `utr_no`='Wrong Bank Details' AND"
                " DATE(`cluster_approved_on`) BETWEEN '{fd}' AND '{td}' GROUP BY `invoice_no` ORDER BY `patient_data`.`branch`,`patient_data`.`visit_data`,`patient_data`.`discharge_datetime`"
                " ASC".format(fd=from_date, td=to_date))
        else:
            cursor.execute(
                "SELECT `invoice_no`, `patient_name`, DATE_FORMAT(`visit_data`,'%d-%b-%Y') AS adate,DATE_FORMAT(`discharge_datetime`,'%d-%b-%Y') AS ddate, `isbilldone` AS"
                " admissionstatus, `patient_data`.`referralmobile` as mobile, `patient_data`.`branch` as branch,`patient_data`.`consultantentry` as consultantentry,`consultantremarks`,"
                "`patient_data`.`referraldepartment` as department, `patient_data`.`organization` organization, `referralstatus`, `Admissiontype`, UPPER(`doctor_agent_list`.`agent_name`)"
                " AS referralname, `referraldepartment`, `doctor_agent_list`.`mobile` as referralmobile, `referralremarks`, `paymentmode`, `doctor_agent_list`.`bank_ac` "
                "as accnumber,`doctor_agent_list`.`ifsc` as ifsccode, `doctor_agent_list`.`pancard` as pancard, `clashstatus`, DATE_FORMAT(`referralcreatedon`,'%d-%b-%Y %H:%i:%s')"
                " AS referralcreatedon, `referralcreatedby`, `chapproval`, (`phar_consum_billamount`) AS billamount,`referralpercentage`, ROUND(if(`referralmode` = 'Fixed Amount',"
                "`referralamount`,(`referralpercentage`/100)*(`phar_consum_billamount`-`phar_consum_billamount`)),2) AS referralamount2, `chapproval`,UPPER(`UCID`)"
                " AS referralcode,`referralamount` FROM `patient_data` INNER JOIN `doctor_agent_list` ON `patient_data`.`UCID`=`doctor_agent_list`.`unique_id` "
                "WHERE `patient_data`.`branch` != 'Test' AND `cluster_approval` = 'Approved'  AND `doctor_agent_list`.`bank_ac`!='' AND `doctor_agent_list`.`bank_ac`!='null' "
                " AND DATE(`cluster_approved_on`) BETWEEN '{fd}' AND '{td}' AND `patient_data`.`branch` = '{bn}' GROUP BY `invoice_no` ORDER BY "
                "`patient_data`.`branch`,`patient_data`.`visit_data`,`patient_data`.`discharge_datetime` ASC".format(
                    fd=from_date, td=to_date, bn=branch_n))

        wrong_details = cursor.description
        context['wrong_bank_d'] = [
            dict(zip([i[0] for i in wrong_details], wrong)) for wrong in cursor.fetchall()
        ]

    return render(request, 'wrong_bank_details.html', context)


@login_required(login_url="/")
def bank_details(request):
    context = {}
    if 'search' in request.POST:
        search = request.POST.get('search')
        context["b_details"] = DoctorAgentList.objects.get(unique_id=search)

    elif request.method == "POST":
        unique_id = request.POST.get('unique_id')
        agent_name = request.POST.get('agent_name')
        mobile = request.POST.get('mobile')
        pancard = request.POST.get('pancard')
        bank_branch_name = request.POST.get('bank_branch_name')
        bank_ac = request.POST.get('bank_ac')
        ifsc = request.POST.get('ifsc')

        # try:
        doctor_agent = DoctorAgentList.objects.get(unique_id=unique_id)
        if doctor_agent.bank_ac == "No Update" or doctor_agent.bank_ac == "":
            doctor_agent.bank_branch_name = bank_branch_name
            doctor_agent.bank_ac = bank_ac
            doctor_agent.ifsc = ifsc
            doctor_agent.pancard = pancard
            doctor_agent.save()
            messages.success(request, "Updated Successfully!")
        else:
            messages.error(request, "Bank Details already Updated!")

        # except DoctorAgentList.DoesNotExist:
        #     messages.error(request, "Unique Id is Mandatory!")

        # if unique_id:
        #     doctor_agent = DoctorAgentList.objects.filter(unique_id=unique_id).update(
        #                                                bank_branch_name=bank_branch_name, bank_ac=bank_ac, ifsc=ifsc, pancard=pancard)
        #     if doctor_agent:
        #         messages.success(request, "Updated Successfully!")
        #     else:
        #         messages.error(request, "Please check details!")
        # else:
        #     messages.error(request, "Unique Id is Mandatory!")
        return redirect('bank_details')

    return render(request, 'bank_details.html', context)


@login_required(login_url="/")
def search_id(request):
    if 'term' in request.GET:
        result = []
        term = request.GET.get('term')
        new = DoctorAgentList.objects.filter(
            Q(unique_id__istartswith=term) | Q(agent_name__istartswith=term) | Q(
                mobile__istartswith=term))
        for emp in new:
            result.append(
                {'id': emp.unique_id, 'mobile': emp.mobile, 'agent_name': emp.agent_name})

        if not result:
            result.append({'mobile': '', 'id': '', 'agent_name': 'Search not found!'})

        return JsonResponse(result, safe=False)


@login_required(login_url="/")
def search_uid(request):
    if 'term' in request.GET:
        result = []
        term = request.GET.get('term')
        accnumber = request.GET.get('accnumber ')
        ifsccode = request.GET.get('ifsccode ')
        pancard = request.GET.get('pancard ')
        upinumber = request.GET.get('upinumber')
        new = DoctorAgentList.objects.filter(
            Q(unique_id__istartswith=term) | Q(agent_name__istartswith=term) | Q(
                mobile__istartswith=term)) & DoctorAgentList.objects.filter(
            ~Q(bank_ac=accnumber, ifsc=ifsccode, pancard=pancard))
        for emp in new:
            result.append(
                {'id': emp.unique_id, 'mobile': emp.mobile, 'agent_name': emp.agent_name, 'accnumber': emp.bank_ac,
                 'ifsccode': emp.ifsc, 'pancard': emp.pancard})

        if not result:
            result.append({'mobile': '', 'id': '', 'agent_name': 'Search not found!'})

        return JsonResponse(result, safe=False)


@login_required(login_url="/")
def utr_update(request):
    if request.method == "POST" or request.method == "FILES ":
        # file = request.FILES['upload_csv_file']
        # filename = file.save()
        reader = csv.DictReader(decode_utf8(request.FILES.get("upload_csv_file")))

        # cursor.execute(f"UPDATE `patient_data` INNER JOIN `utrupdate` ON `patient_data`.`sno`=`utrupdate`.`sno` SET `utr_no`=`utrupdate`.`sno`,`utr_created_by`='01238',`utr_on`=`utrupdate`.`utr_date`")

        for row in reader:
            if row["Sno"]:
                UtrUpdate(sno=int(row["Sno"]), invoice_no=row["Invoice_No"], patient_name=row["Patient_Name"],
                          branch=row["Branch"], service_name=row["Service_Name"], grossamount=row["Gross Bill Amount"],
                          discount=row["Discount Amount"], netamount=row["Net Bill Amount"],
                          referralamount=row["Referral Amount"],
                          utr_no=row["UTR_No"], utr_date=row["UTR_Date"], utr_created_by=request.user.emp_id).save()

                PatientData.objects.filter(sno=int(row["Sno"])).update(utr_on=row["UTR_Date"], utr_no=row["UTR_No"])
        messages.success(request, "upload successfully....")
        return redirect('utr_update')
    return render(request, 'utr.html')


@login_required(login_url="/")
def utr_csv(request):
    res = HttpResponse(content_type='text/csv')
    res['Content-Disposition'] = 'attachment; filename="Utr_Updated_file.csv"'
    writer = csv.writer(res)
    writer.writerow([
        'Sno', 'Invoice_No', 'Patient_Name', 'Branch',
        'Service_Name', 'Gross Bill Amount',
        'Discount Amount', 'Net Bill Amount', 'Referral Amount',
        'UTR_No', 'UTR_Date'
    ])
    # utr = PatientData.objects.all()
    # for i in utr:
    #     writer.writerow([
    #         i.sno, i.invoice_no, i.patient_name, i.branch, i.service_name, i.grossamount
    #     ])

    return res


def upload_utr_csv(request):
    res = HttpResponse(content_type='text/csv')
    res['Content-Disposition'] = 'attachment; filename="Utr_Updated_file.csv"'
    writer = csv.writer(res)
    writer.writerow([
        'Sno', 'Invoice_No', 'Patient_Name', 'Branch',
        'Service_Name', 'Gross Bill Amount',
        'Discount Amount', 'Net Bill Amount', 'Referral Amount',
        'UTR No', 'UTR Date'
    ])

    return res


@login_required(login_url="/")
def day_reports(request):
    context = {}

    if 'edit' in request.GET:
        edit = request.GET.get('edit')
        context['emp_list'] = Logins.objects.filter(emp_id=edit)

    return render(request, 'call/report.html', context)


@login_required(login_url="/")
def incomplete_referral(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test'))
    }
    if request.method == "POST":
        branch = request.POST.get('branch')

        cur = connection.cursor()
        if branch == 'All':
            cur.execute(
                "SELECT `invoice_no`, `patient_name`, DATE_FORMAT(`visit_data`,'%d-%b-%Y') AS"
                " adate,DATE_FORMAT(`discharge_datetime`,'%d-%b-%Y') AS ddate, `isbilldone` AS "
                "admissionstatus, `patient_data`.`referralmobile` as mobile, `patient_data`.`branch` "
                "as branch,`patient_data`.`referraldepartment` as department, `patient_data`.`organization`"
                " organization, `referralstatus`, `Admissiontype`, UPPER(`doctor_agent_list`.`agent_name`) AS"
                " referralname, `referraldepartment`, `doctor_agent_list`.`mobile` as referralmobile,"
                " `referralremarks`, `paymentmode`, `doctor_agent_list`.`bank_ac` as accnumber,`doctor_agent_list`.`ifsc` "
                "as ifsccode, `doctor_agent_list`.`pancard` as pancard, `clashstatus`,"
                " DATE_FORMAT(`referralcreatedon`,'%d-%b-%Y %H:%i:%s') AS referralcreatedon, "
                "`referralcreatedby`, (`phar_consum_billamount`) AS billamount,UPPER(`UCID`) AS "
                "referralcode,`referralamount` FROM `patient_data` INNER JOIN `doctor_agent_list` ON "
                "`patient_data`.`UCID`=`doctor_agent_list`.`unique_id` WHERE `patient_data`.`referralamount`!='0' "
                "AND `patient_data`.`cluster_approval`='Approved' AND `patient_data`.`paymentmode`!='Cash' AND DATE(`cluster_approved_on`) BETWEEN '2019-01-01' AND '2023-01-01' AND (`doctor_agent_list`.`bank_ac`='' OR `doctor_agent_list`.`bank_ac`='null' OR `doctor_agent_list`.`bank_ac`='No Update')GROUP BY "
                "`invoice_no` ORDER BY `patient_data`.`branch`,`patient_data`.`utr_on`,`patient_data`.`discharge_datetime` ASC;")

        else:
            cur.execute(
                "SELECT `invoice_no`, `patient_name`, DATE_FORMAT(`visit_data`,'%d-%b-%Y') AS adate,DATE_FORMAT(`discharge_datetime`,'%d-%b-%Y') AS ddate,"
                "`isbilldone` AS  admissionstatus, `patient_data`.`referralmobile` as mobile, `patient_data`.`branch`"
                " as branch,`patient_data`.`referraldepartment` as department, `patient_data`.`organization`"
                " organization, `referralstatus`, `Admissiontype`, UPPER(`doctor_agent_list`.`agent_name`) AS"
                " referralname, `referraldepartment`, `doctor_agent_list`.`mobile` as referralmobile,"
                " `referralremarks`, `paymentmode`, `doctor_agent_list`.`bank_ac` as accnumber,`doctor_agent_list`.`ifsc` "
                " as ifsccode, `doctor_agent_list`.`pancard` as pancard, `clashstatus`,"
                "DATE_FORMAT(`referralcreatedon`,'%d-%b-%Y %H:%i:%s') AS referralcreatedon, "
                "`referralcreatedby`, (`phar_consum_billamount`) AS billamount,UPPER(`UCID`) AS "
                " referralcode,`referralamount` FROM `patient_data` INNER JOIN `doctor_agent_list` ON "
                " `patient_data`.`UCID`=`doctor_agent_list`.`unique_id` WHERE  `patient_data`.`referralamount`!='0' "
                "AND `patient_data`.`cluster_approval`='Approved'  AND DATE(`cluster_approved_on`)"
                " BETWEEN '2019-01-01' AND '2023-01-01' AND (`doctor_agent_list`.`bank_ac`='' OR `doctor_agent_list`.`bank_ac`='null' OR "
                "`doctor_agent_list`.`bank_ac`='No Update')  GROUP BY `invoice_no` ORDER BY `patient_data`.`branch`,"
                "`patient_data`.`utr_on`,`patient_data`.`discharge_datetime` ASC;")
            emp = cur.description
            context['emp_list'] = [
                dict(zip([i[0] for i in emp], report)) for report in cur.fetchall()
            ]
    return render(request, 'referral/incomplete_referral.html', context)


@login_required(login_url="/")
def abc_report(request):
    context = {'branch': BranchListDum.objects.filter(~Q(branch_name='Test')), }
    if request.method == "POST":
        branch = request.POST.get('branch')
        filter_date = request.POST.get('date')

        fdate, tdate = filter_date.split(' - ')
        fdate = datetime.strptime(str(fdate), '%m/%d/%Y').date()
        tdate = datetime.strptime(str(tdate), '%m/%d/%Y').date()
        cur = connection.cursor()
        cur.execute("""SELECT `Emp_name`,`Emp_ID`,`Branch`,(SELECT COUNT(`unique_id`) FROM `doctor_agent_list` WHERE `emp_id` = `logins`.`Emp_ID`
                     AND `category` = 'A') AS aTotalcount, (SELECT COUNT(`unique_id`)
                     FROM `doctor_agent_list` WHERE `emp_id` = `logins`.`Emp_ID` AND `category` = 'B') AS bTotalcount,
                     (SELECT COUNT(`unique_id`) FROM `doctor_agent_list` WHERE `emp_id` = `logins`.`Emp_ID` AND `category` = 'C') 
                    AS cTotalcount, (SELECT COALESCE(SUM(av1),0) FROM (SELECT IF(COUNT(`call_report_master`.`unique_id`) = 1, 1, 0) 
                    AS av1 FROM `call_report_master` INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id`
                     WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'A'
                     AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `call_report_master`.`unique_id` != ''
                      GROUP BY `call_report_master`.`unique_id`
                      ORDER BY `call_report_master`.`emp_id` ASC
                    ) AS av1) AS AV1,
                    (SELECT COALESCE(SUM(bv1),0) FROM (
                      SELECT IF(COUNT(`call_report_master`.`unique_id`) = 1, 1, 0) AS bv1
                      FROM `call_report_master`
                      INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id`
                     WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'B'
                     AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `call_report_master`.`unique_id` != ''
                      GROUP BY `call_report_master`.`unique_id`
                      ORDER BY `call_report_master`.`emp_id` ASC
                    ) AS av1) AS BV1,
                    (SELECT COALESCE(SUM(cv1),0) FROM (
                      SELECT IF(COUNT(`call_report_master`.`unique_id`) = 1, 1, 0) AS cv1
                      FROM `call_report_master`
                      INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id`
                     WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'C'
                     AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `call_report_master`.`unique_id` != ''
                      GROUP BY `call_report_master`.`unique_id`
                      ORDER BY `call_report_master`.`emp_id` ASC
                    ) AS av1) AS CV1,
                     (SELECT COALESCE(SUM(av2),0) FROM (
                       SELECT IF(COUNT(`call_report_master`.`unique_id`) = 2, 1, 0) AS av2
                       FROM `call_report_master`
                       INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id`
                      WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'A'
                      AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' 
                      AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `call_report_master`.`unique_id` != ''
                      GROUP BY `call_report_master`.`unique_id`
                      ORDER BY `call_report_master`.`emp_id` ASC
                    ) AS av2) AS AV2,
                    (SELECT COALESCE(SUM(bv2),0) FROM (
                      SELECT IF(COUNT(`call_report_master`.`unique_id`) = 2, 1, 0) AS bv2
                      FROM `call_report_master`
                      INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id`
                     WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'B'
                     AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `call_report_master`.`unique_id` != ''
                      GROUP BY `call_report_master`.`unique_id`
                      ORDER BY `call_report_master`.`emp_id` ASC
                    ) AS bv2) AS BV2,
                    (SELECT COALESCE(SUM(cv2),0) FROM (
                      SELECT IF(COUNT(`call_report_master`.`unique_id`) = 2, 1, 0) AS cv2
                      FROM `call_report_master`
                      INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id`
                     WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'C'
                     AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `call_report_master`.`unique_id` != ''
                      GROUP BY `call_report_master`.`unique_id`
                      ORDER BY `call_report_master`.`emp_id` ASC
                    ) AS cv2) AS CV2,
                    (SELECT COALESCE(SUM(av3),0) FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)>2,1,0) AS av3 FROM `call_report_master`
                      INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id`
                     WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'A'
                     AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `call_report_master`.`unique_id` != ''
                      GROUP BY `call_report_master`.`unique_id`
                      ORDER BY `call_report_master`.`emp_id` ASC
                    ) AS av3) AS AV3,
                     (SELECT COALESCE(SUM(bv3),0) FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)>2,1,0) AS bv3 FROM `call_report_master`
                      INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id`
                     WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'B'
                     AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `call_report_master`.`unique_id` != ''
                     GROUP BY `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) AS bv3) AS BV3,
                     (SELECT COALESCE(SUM(cv3),0) FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)>2,1,0) AS cv3 FROM `call_report_master`
                      INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id`
                     WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'C'
                     AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' 
                     AND `call_report_master`.`unique_id` != ''
                      GROUP BY `call_report_master`.`unique_id`
                      ORDER BY `call_report_master`.`emp_id` ASC
                    ) AS cv3) AS CV3,
                      (SELECT COALESCE(SUM(eav1), 0)FROM (SELECT IF(COUNT(`unique_id`) = 1, 1, 0) AS eav1 FROM `call_report_master`
                     WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'A'
                          AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}'  AND `unique_id` != '' GROUP BY `call_report_master`.`unique_id` ORDER BY  `call_report_master`.`emp_id` ASC) AS eav1 ) AS EAV1,
                          (SELECT COALESCE(SUM(ebv1), 0)FROM (SELECT IF(COUNT(`unique_id`) = 1, 1, 0) AS ebv1 FROM `call_report_master`
                     WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'B'
                          AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}'  AND `unique_id` != '' GROUP BY `call_report_master`.`unique_id` ORDER BY  `call_report_master`.`emp_id` ASC) AS ebv1 ) AS EBV1,
                          (SELECT COALESCE(SUM(ecv1), 0)FROM (SELECT IF(COUNT(`unique_id`) = 1, 1, 0) AS ecv1 FROM `call_report_master`
                     WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'C'
                           AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}'  AND `unique_id` != '' GROUP BY `call_report_master`.`unique_id` ORDER BY  `call_report_master`.`emp_id` ASC) AS ecv1 ) AS ECV1,
                            (SELECT COALESCE(SUM(eav2), 0)FROM (SELECT IF(COUNT(`unique_id`) = 2, 1, 0) AS eav2 FROM `call_report_master`
                      WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'A'
                           AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}'  AND `unique_id` != '' GROUP BY `call_report_master`.`unique_id` ORDER BY  `call_report_master`.`emp_id` ASC) AS eav2 ) AS EAV2,
                       (SELECT COALESCE(SUM(ebv2), 0)FROM (SELECT IF(COUNT(`unique_id`) = 2, 1, 0) AS ebv2 FROM `call_report_master`
                      WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'B'
                           AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}'  AND `unique_id` != '' GROUP BY `call_report_master`.`unique_id` ORDER BY  `call_report_master`.`emp_id` ASC) AS ebv2 ) AS EBV2,
                    (SELECT COALESCE(SUM(ecv2), 0)FROM (SELECT IF(COUNT(`unique_id`) = 2, 1, 0) AS ecv2 FROM 
                    `call_report_master` 
                    WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'C'
                         AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}'  AND `unique_id` != '' GROUP BY `call_report_master`.`unique_id` ORDER BY  `call_report_master`.`emp_id` ASC) AS ecv2 ) AS ECV2,
                         (SELECT COALESCE(SUM(eav3),0) FROM (SELECT if(COUNT(`unique_id`)>2,1,0) AS eav3 FROM call_report_master
                    WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'A'
                         AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}'  AND `unique_id` != '' GROUP BY `call_report_master`.`unique_id` ORDER BY  `call_report_master`.`emp_id` ASC) AS eav3 ) AS EAV3,
                         (SELECT COALESCE(SUM(ebv3),0) FROM (SELECT if(COUNT(`unique_id`)>2,1,0) AS ebv3 FROM call_report_master
                    WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'B'
                         AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}'  AND `unique_id` != '' GROUP BY `call_report_master`.`unique_id` ORDER BY  `call_report_master`.`emp_id` ASC) AS ebv3 ) AS EBV3,
                         (SELECT COALESCE(SUM(ecv3),0) FROM (SELECT if(COUNT(`unique_id`)>2,1,0) AS ecv3 FROM call_report_master
                    WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID` AND `call_report_master`.`category` = 'C'
                         AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}'  AND `unique_id` != '' GROUP BY `call_report_master`.`unique_id` ORDER BY  `call_report_master`.`emp_id` ASC) AS ecv3 ) AS ECV3,
                             (SELECT COALESCE(SUM(aothers1), 0) FROM (SELECT IF(doctor_agent_list.emp_id != call_report_master.emp_id, 1, 0) AS aothers1 FROM  `call_report_master`
                       INNER JOIN doctor_agent_list ON  `call_report_master`.unique_id = doctor_agent_list.unique_id WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID`
                        AND  `call_report_master`.category = 'A'
                        AND  `call_report_master`.date BETWEEN '{fd}' AND '{td}' 
                        AND  `call_report_master`.unique_id != ''
                       GROUP BY  `call_report_master`.unique_id
                       ORDER BY  `call_report_master`.emp_id ASC
                     ) AS aothers1) AS aothers1,
                     (SELECT COALESCE(SUM(bothers1), 0) FROM (SELECT IF(doctor_agent_list.emp_id != call_report_master.emp_id, 1, 0) AS bothers1 FROM  `call_report_master` INNER JOIN doctor_agent_list ON  `call_report_master`.unique_id = doctor_agent_list.unique_id WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID`
                          AND  `call_report_master`.category = 'B'
                          AND  `call_report_master`.date BETWEEN '{fd}' AND '{td}' 
                          AND  `call_report_master`.unique_id != ''
                         GROUP BY  `call_report_master`.unique_id
                         ORDER BY  `call_report_master`.emp_id ASC
                       ) AS bothers1
                     ) AS bothers1,
                    (SELECT COALESCE(SUM(cothers1), 0) FROM (SELECT IF(doctor_agent_list.emp_id != call_report_master.emp_id, 1, 0) AS cothers1 FROM  `call_report_master`
                     INNER JOIN doctor_agent_list ON  `call_report_master`.unique_id = doctor_agent_list.unique_id WHERE `call_report_master`.`emp_id` = `logins`.`Emp_ID`
                          AND  `call_report_master`.category = 'C'
                          AND  `call_report_master`.date BETWEEN '{fd}' AND '{td}' 
                          AND  `call_report_master`.unique_id != ''
                         GROUP BY  `call_report_master`.unique_id
                         ORDER BY  `call_report_master`.emp_id ASC) AS cothers1) AS cothers1 FROM `logins` WHERE `Page` = 'Marketing'
                    AND `Job_Status` = 'Active'
                    AND `branch` = '{b}';""".format(fd=fdate, td=tdate, b=branch))

        desc = cur.description
        context['abc'] = [
            dict(zip([i[0] for i in desc], row)) for row in cur.fetchall()
        ]
        for i in context['abc']:
            i['atotal'] = i['aTotalcount'] + i['aothers1']
            i['btotal'] = i['bTotalcount'] + i['bothers1']
            i['ctotal'] = i['cTotalcount'] + i['cothers1']

            i['nvav1'] = (i['atotal']) - (i['EAV2'] + i['EAV3']) - i['EAV1']
            i['nvbv1'] = (i['btotal']) - (i['EBV2'] + i['EBV3']) - i['EBV1']
            i['nvcv1'] = (i['ctotal']) - (i['ECV2'] + i['ECV3']) - i['ECV1']

            i['nvav2'] = (i['atotal']) - (i['ECV3'] + i['ECV1']) - i['EAV3']
            i['nvbv2'] = (i['btotal']) - (i['ECV3'] + i['ECV1']) - i['EBV3']
            i['nvcv2'] = (i['ctotal']) - (i['ECV3'] + i['ECV1']) - i['ECV3']

            i['nvav3'] = (i['atotal']) - (i['ECV1'] + i['ECV2']) - i['EAV3']
            i['nvbv3'] = (i['btotal']) - (i['ECV1'] + i['ECV2']) - i['EBV3']
            i['nvcv3'] = (i['ctotal']) - (i['ECV1'] + i['ECV2']) - i['ECV3']

    return render(request, 'abc_report.html', context)


# @login_required(login_url="/")
# def abc_report(request):
#     context = { 'branch': BranchListDum.objects.filter(~Q(branch_name='Test')),}
#     if request.method == "POST":
#         branch = request.POST.get('branch')
#         filter_date = request.POST.get('date')
#
#         fdate, tdate = filter_date.split(' - ')
#         fd = datetime.strptime(str(fdate), '%m/%d/%Y').date()
#         td = datetime.strptime(str(tdate), '%m/%d/%Y').date()
#         employee_ids = tuple(Logins.objects.filter(branch=branch, page='Marketing', job_status='Active').values_list('emp_id', flat=True))
#         data = connection.cursor()
#         data.execute(f"""SELECT (SELECT count(`unique_id`) FROM `doctor_agent_list` WHERE `emp_id` IN {employee_ids} AND `category`='A' )
#                         AS aTotalcount,(SELECT count(`unique_id`) FROM `doctor_agent_list` WHERE `emp_id` IN {employee_ids} AND `category`='B' )
#                         AS bTotalcount,(SELECT count(`unique_id`) FROM `doctor_agent_list` WHERE `emp_id` IN {employee_ids} AND `category`='C' ) AS cTotalcount,
#                         (SELECT COALESCE(SUM(av1),0) FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)=1,1,0) AS av1 FROM `call_report_master` INNER JOIN
#                          `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id` WHERE
#                           `call_report_master`.`emp_id` IN {employee_ids} AND `call_report_master`.`category`='A' AND `call_report_master`.`date`
#                           BETWEEN '{fd}' AND '{td}' AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' AND`call_report_master`.`unique_id`!=''
#                            GROUP BY `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) AS av1) AS AV1, (SELECT COALESCE(SUM(bv1),0) FROM
#                            (SELECT if(COUNT(`call_report_master`.`unique_id`)=1,1,0) AS bv1 FROM `call_report_master` INNER JOIN `doctor_agent_list` ON
#                            `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id` WHERE `call_report_master`.`emp_id` IN {employee_ids} AND
#                            `call_report_master`.`category`='B' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `doctor_agent_list`.`date`
#                            BETWEEN '{fd}' AND '{td}' AND`call_report_master`.`unique_id`!='' GROUP BY `call_report_master`.`unique_id` ORDER BY
#                            `call_report_master`.`emp_id` ASC) AS bv1) AS BV1, (SELECT COALESCE(SUM(cv1),0) FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)=1,1,0)
#                            AS cv1 FROM `call_report_master` INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id`
#                            WHERE `call_report_master`.`emp_id` IN {employee_ids} AND `call_report_master`.`category`='C' AND `call_report_master`.`date`
#                            BETWEEN '{fd}' AND '{td}' AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' AND`call_report_master`.`unique_id`!=''
#                            GROUP BY `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) AS cv1) AS CV1,(SELECT COALESCE(SUM(av2),0)
#                             FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)=2,1,0) AS av2 FROM `call_report_master` INNER JOIN `doctor_agent_list` ON
#                             `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id` WHERE `call_report_master`.`emp_id` IN {employee_ids} AND
#                              `call_report_master`.`category`='A' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `doctor_agent_list`.`date`
#                              BETWEEN '{fd}' AND '{td}' AND`call_report_master`.`unique_id`!='' GROUP BY `call_report_master`.`unique_id` ORDER BY
#                              `call_report_master`.`emp_id` ASC) AS av2) AS AV2, (SELECT COALESCE(SUM(bv2),0) FROM
#                              (SELECT if(COUNT(`call_report_master`.`unique_id`)=2,1,0) AS bv2 FROM `call_report_master` INNER JOIN `doctor_agent_list` ON
#                              `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id` WHERE `call_report_master`.`emp_id` IN {employee_ids} AND
#                               `call_report_master`.`category`='B' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `doctor_agent_list`.`date`
#                                BETWEEN '{fd}' AND '{td}' AND`call_report_master`.`unique_id`!='' GROUP BY `call_report_master`.`unique_id` ORDER BY
#                                 `call_report_master`.`emp_id` ASC) AS bv2) AS BV2, (SELECT COALESCE(SUM(cv2),0)
#                                 FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)=2,1,0) AS cv2 FROM `call_report_master` INNER JOIN `doctor_agent_list` ON
#                                  `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id` WHERE `call_report_master`.`emp_id` IN {employee_ids} AND
#                                   `call_report_master`.`category`='C' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `doctor_agent_list`.`date`
#                                    BETWEEN '{fd}' AND '{td}' AND`call_report_master`.`unique_id`!='' GROUP BY `call_report_master`.`unique_id` ORDER BY
#                                     `call_report_master`.`emp_id` ASC) AS cv2) AS CV2,(SELECT COALESCE(SUM(av3),0)
#                                     FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)>2,1,0) AS av3 FROM `call_report_master` INNER JOIN `doctor_agent_list`
#                                      ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id` WHERE `call_report_master`.`emp_id` IN {employee_ids}
#                                      AND `call_report_master`.`category`='A' AND `call_report_master`.`date` BETWEEN'{fd}' AND '{td}'
#                                      AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' AND`call_report_master`.`unique_id`!='' GROUP BY
#                                      `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) AS av3) AS AV3, (SELECT COALESCE(SUM(bv3),0) FROM
#                                      (SELECT if(COUNT(`call_report_master`.`unique_id`)>2,1,0) AS bv3 FROM `call_report_master` INNER JOIN `doctor_agent_list` ON
#                                      `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id` WHERE `call_report_master`.`emp_id` IN {employee_ids}
#                                       AND `call_report_master`.`category`='B' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND
#                                       `doctor_agent_list`.`date` BETWEEN'{fd}' AND '{td}' AND`call_report_master`.`unique_id`!=''
#                                       GROUP BY `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) AS bv3) AS BV3,
#                                 (SELECT COALESCE(SUM(cv3),0) FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)>2,1,0) AS cv3 FROM
#                                 `call_report_master` INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id`
#                                  WHERE `call_report_master`.`emp_id` IN {employee_ids} AND `call_report_master`.`category`='C' AND `call_report_master`.`date`
#                                   BETWEEN '{fd}' AND '{td}' AND `doctor_agent_list`.`date` BETWEEN'{fd}' AND '{td}'
#                                     AND`call_report_master`.`unique_id`!='' GROUP BY `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC)
#                                      AS cv3) AS CV3,(SELECT COALESCE(SUM(eav1),0) FROM (SELECT if(COUNT(`unique_id`)=1,1,0) AS eav1 FROM call_report_master WHERE
#                                      `emp_id` IN {employee_ids} AND `category`='A' AND `call_report_master`.`date` BETWEEN'{fd}' AND '{td}' AND
#                                       `unique_id`!='' GROUP BY `unique_id` ORDER BY `emp_id` ASC) AS eav1) AS EAV1,(SELECT COALESCE(SUM(ebv1),0) FROM
#                                       (SELECT if(COUNT(`unique_id`)=1,1,0) AS ebv1 FROM call_report_master WHERE `emp_id` IN {employee_ids} AND
#                                        `category`='B' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `unique_id`!='' GROUP BY
#                                        `unique_id` ORDER BY `emp_id` ASC) AS ebv1) AS EBV1,(SELECT COALESCE(SUM(ecv1),0) FROM (SELECT if(COUNT(`unique_id`)=1,1,0)
#                                        AS ecv1 FROM call_report_master WHERE `emp_id` IN {employee_ids} AND `category`='C' AND `call_report_master`.`date`
#                                        BETWEEN '{fd}' AND '{td}' AND `unique_id`!='' GROUP BY `unique_id` ORDER BY `emp_id` ASC) AS ecv1) AS ECV1,
#                                        (SELECT COALESCE(SUM(eav2),0) FROM (SELECT if(COUNT(`unique_id`)=2,1,0) AS eav2 FROM call_report_master WHERE
#                                        `emp_id` IN {employee_ids} AND `category`='A' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND
#                                         `unique_id`!='' GROUP BY `unique_id` ORDER BY `emp_id` ASC) AS eav2) AS EAV2,(SELECT COALESCE(SUM(ebv2),0) FROM
#                                         (SELECT if(COUNT(`unique_id`)=2,1,0) AS ebv2 FROM call_report_master WHERE `emp_id` IN {employee_ids} AND
#                                         `category`='B' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `unique_id`!='' GROUP BY
#                                         `unique_id` ORDER BY `emp_id` ASC) AS ebv2) AS EBV2,(SELECT COALESCE(SUM(ecv2),0) FROM (SELECT if(COUNT(`unique_id`)=2,1,0)
#                                         AS ecv2 FROM call_report_master WHERE `emp_id` IN {employee_ids} AND `category`='C' AND `call_report_master`.`date`
#                                          BETWEEN '{fd}' AND '{td}' AND `unique_id`!='' GROUP BY `unique_id` ORDER BY `emp_id` ASC) AS ecv2)
#                                          AS ECV2,(SELECT COALESCE(SUM(eav3),0) FROM (SELECT if(COUNT(`unique_id`)>2,1,0) AS eav3 FROM call_report_master
#                                           WHERE `emp_id` IN {employee_ids} AND `category`='A' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `unique_id`!='' GROUP BY `unique_id` ORDER BY `emp_id` ASC) AS eav3) AS EAV3,(SELECT COALESCE(SUM(ebv3),0)
#                                            FROM (SELECT if(COUNT(`unique_id`)>2,1,0) AS ebv3 FROM call_report_master WHERE `emp_id` IN {employee_ids}
#                  AND `category`='B' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `unique_id`!='' GROUP BY
#                  `unique_id` ORDER BY `emp_id` ASC) AS ebv3) AS EBV3,(SELECT COALESCE(SUM(ecv3),0) FROM (SELECT if(COUNT(`unique_id`)>2,1,0)
#                  AS ecv3 FROM call_report_master WHERE `emp_id` IN {employee_ids} AND `category`='C' AND `call_report_master`.`date`
#                   BETWEEN '{fd}' AND '{td}' AND `unique_id`!='' GROUP BY `unique_id` ORDER BY `emp_id` ASC) AS ecv3) AS ECV3,
#                     (SELECT COALESCE(SUM(aothers1),0) FROM (SELECT if((`doctor_agent_list`.`emp_id`!=`call_report_master`.`emp_id`),1,0)
#                     AS aothers1 FROM `call_report_master` INNER JOIN `doctor_agent_list`
#                     on `call_report_master`.`unique_id`= `doctor_agent_list`.`unique_id` WHERE
#                     `call_report_master`.`emp_id` IN {employee_ids} AND `call_report_master`.`category`='A' AND
#                     `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `call_report_master`.`unique_id`!='' GROUP BY
#                     `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) as aothers1) AS aothers1,
#                     (SELECT COALESCE(SUM(bothers1),0) FROM (SELECT if((`doctor_agent_list`.`emp_id`!=`call_report_master`.`emp_id`),1,0)
#                      AS bothers1 FROM `call_report_master` INNER JOIN `doctor_agent_list` on
#                      `call_report_master`.`unique_id`= `doctor_agent_list`.`unique_id` WHERE `call_report_master`.
#                      `emp_id` IN {employee_ids} AND `call_report_master`.`category`='B' AND `call_report_master`.`date` BETWEEN
#                      '{fd}' AND '{td}' AND `call_report_master`.`unique_id`!='' GROUP BY `call_report_master`.`unique_id` ORDER BY
#                        `call_report_master`.`emp_id` ASC) as bothers1) AS bothers1,(SELECT COALESCE(SUM(cothers1),0)
#                        FROM (SELECT if((`doctor_agent_list`.`emp_id`!=`call_report_master`.`emp_id`),1,0) AS cothers1 FROM
#                        `call_report_master` INNER JOIN `doctor_agent_list` on
#                         `call_report_master`.`unique_id`= `doctor_agent_list`.`unique_id` WHERE `call_report_master`.
#                         `emp_id` IN {employee_ids} AND `call_report_master`.`category`='C' AND `call_report_master`.`date` BETWEEN
#                         '{fd}' AND '{td}' AND `call_report_master`.`unique_id`!='' GROUP BY `call_report_master`.`unique_id` ORDER BY
#                          `call_report_master`.`emp_id` ASC) as cothers1) AS cothers1;""")
#         result = data.fetchone()
#         context['abc'] = result
#         print(context['abc'])
#
#     return render(request, 'abc_report.html', context)
#
#
# # data.execute("""SELECT (SELECT count(`unique_id`) FROM `doctor_agent_list` WHERE `emp_id` IN {employee_ids} AND
# #             `category`='A' ) AS aTotalcount,(SELECT count(`unique_id`) FROM `doctor_agent_list`
# #                WHERE `emp_id` IN {employee_ids} AND `category`='B' ) AS bTotalcount,(SELECT count(`unique_id`)
# #              (SELECT COALESCE(SUM(av1),0) FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)=1,1,0) AS av1 FROM"
# #               `call_report_master` INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id`
# #             WHERE `call_report_master`.`emp_id` IN {employee_ids} AND `call_report_master`.`category`='A' AND
# #                `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}'
# #           AND`call_report_master`.`unique_id`!='' GROUP BY `call_report_master`.`unique_id` ORDER BY
# #           `call_report_master`.`emp_id` ASC) AS av1) AS AV1, (SELECT COALESCE(SUM(bv1),0) FROM
# #            (SELECT if(COUNT(`call_report_master`.`unique_id`)=1,1,0) AS bv1 FROM `call_report_master` INNER JOIN
# #           `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id`
# #              WHERE `call_report_master`.`emp_id` IN {employee_ids} AND `call_report_master`.`category`='B' AND
# #              `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `doctor_agent_list`.`date` BETWEEN
# #         '{fd}' AND '{td}' AND`call_report_master`.`unique_id`!='' GROUP BY `call_report_master`.`unique_id`
# #               ORDER BY `call_report_master`.`emp_id` ASC) AS bv1) AS BV1, (SELECT COALESCE(SUM(cv1),0)
# #             FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)=1,1,0) AS cv1 FROM `call_report_master`
# #            INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id`
# #           WHERE `call_report_master`.`emp_id` IN {employee_ids} AND `call_report_master`.`category`='C' AND
# #      `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `doctor_agent_list`.`date`
# #         BETWEEN '{fd}' AND '{td}' AND`call_report_master`.`unique_id`!='' GROUP BY
# #        `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) AS cv1) AS CV1,
# #       (SELECT COALESCE(SUM(av2),0) FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)=2,1,0) AS av2 FROM
# #        `call_report_master` INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id`
# #      WHERE `call_report_master`.`emp_id` IN {employee_ids} AND
# #        `call_report_master`.`category`='A' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND
# #       `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' AND`call_report_master`.`unique_id`!=''
# #        GROUP BY `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) AS av2) AS AV2,
# #        (SELECT COALESCE(SUM(bv2),0) FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)=2,1,0)
# #        AS bv2 FROM `call_report_master` INNER JOIN `doctor_agent_list` ON
# #        `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id` WHERE `call_report_master`.`emp_id` IN {employee_ids}
# #      AND `call_report_master`.`category`='B' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND
# #         `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' AND`call_report_master`.`unique_id`!='' GROUP BY
# #           `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) AS bv2) AS BV2, (SELECT COALESCE(SUM(cv2),0)
# #         FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)=2,1,0) AS cv2 FROM `call_report_master` INNER JOIN `doctor_agent_list`
# #      ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id` WHERE `call_report_master`.`emp_id` IN {employee_ids}
# #      AND `call_report_master`.`category`='C' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}'
# #      AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' AND`call_report_master`.`unique_id`!=''
# #       GROUP BY `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) AS cv2) AS CV2,
# #        (SELECT COALESCE(SUM(av3),0) FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)>2,1,0) AS av3 FROM `call_report_master`
# #          INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id` WHERE
# #             `call_report_master`.`emp_id` IN {employee_ids} AND `call_report_master`.`category`='A' AND `call_report_master`.`date`
# #         BETWEEN '{fd}' AND '{td}' AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' AND
# #         `call_report_master`.`unique_id`!='' GROUP BY `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) AS av3)
# #          AS AV3, (SELECT COALESCE(SUM(bv3),0) FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)>2,1,0) AS bv3 FROM `call_report_master`
# #         INNER JOIN `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id` WHERE
# #          `call_report_master`.`emp_id` IN {employee_ids} AND `call_report_master`.`category`='B' AND `call_report_master`.`date`
# #        BETWEEN '{fd}' AND '{td}' AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' AND`call_report_master`.`unique_id`!=''
# #          GROUP BY `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) AS bv3) AS BV3, (SELECT COALESCE(SUM(cv3),0)
# #          FROM (SELECT if(COUNT(`call_report_master`.`unique_id`)>2,1,0) AS cv3 FROM `call_report_master` INNER JOIN
# #        `doctor_agent_list` ON `doctor_agent_list`.`unique_id` = `call_report_master`.`unique_id` WHERE
# #         `call_report_master`.`emp_id` IN {employee_ids} AND `call_report_master`.`category`='C' AND `call_report_master`.`date`
# #           "BETWEEN '{fd}' AND '{td}' AND `doctor_agent_list`.`date` BETWEEN '{fd}' AND '{td}' AND
# #        `call_report_master`.`unique_id`!='' GROUP BY `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) AS cv3) AS CV3,
# #         (SELECT COALESCE(SUM(eav1),0) FROM (SELECT if(COUNT(`unique_id`)=1,1,0) AS eav1 FROM call_report_master WHERE
# #        `emp_id` IN {employee_ids} AND `category`='A' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND
# #        `unique_id`!='' GROUP BY `unique_id` ORDER BY `emp_id` ASC) AS eav1) AS EAV1,(SELECT COALESCE(SUM(ebv1),0) FROM
# #       (SELECT if(COUNT(`unique_id`)=1,1,0) AS ebv1 FROM call_report_master WHERE `emp_id` IN {employee_ids} AND
# #       `category`='B' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `unique_id`!='' GROUP BY
# #        `unique_id` ORDER BY `emp_id` ASC) AS ebv1) AS EBV1,(SELECT COALESCE(SUM(ecv1),0) FROM (SELECT if(COUNT(`unique_id`)=1,1,0)
# #         AS ecv1 FROM call_report_master WHERE `emp_id` IN {employee_ids} AND `category`='C' AND `call_report_master`.`date`
# #        BETWEEN '{fd}' AND '{td}' AND `unique_id`!='' GROUP BY `unique_id` ORDER BY `emp_id` ASC) AS ecv1) AS ECV1,
# #       (SELECT COALESCE(SUM(eav2),0) FROM (SELECT if(COUNT(`unique_id`)=2,1,0) AS eav2 FROM call_report_master WHERE
# #      `emp_id` IN {employee_ids} AND `category`='A' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}'
# #       AND `unique_id`!='' GROUP BY `unique_id` ORDER BY `emp_id` ASC) AS eav2) AS EAV2,(SELECT COALESCE(SUM(ebv2),0)
# #       FROM (SELECT if(COUNT(`unique_id`)=2,1,0) AS ebv2 FROM call_report_master WHERE `emp_id` IN {employee_ids}
# #       AND `category`='B' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `unique_id`!='' GROUP BY
# #          `unique_id` ORDER BY `emp_id` ASC) AS ebv2) AS EBV2,(SELECT COALESCE(SUM(ecv2),0) FROM (SELECT if(COUNT(`unique_id`)=2,1,0)
# #         AS ecv2 FROM call_report_master WHERE `emp_id` IN {employee_ids} AND `category`='C' AND `call_report_master`.`date`
# #        BETWEEN '{fd}' AND '{td}' AND `unique_id`!='' GROUP BY `unique_id` ORDER BY `emp_id` ASC) AS ecv2) AS ECV2,
# #     (SELECT COALESCE(SUM(eav3),0) FROM (SELECT if(COUNT(`unique_id`)>2,1,0) AS eav3 FROM call_report_master WHERE
# #        `emp_id` IN {employee_ids} AND `category`='A' AND `call_report_master`.`date` BETWEEN '{fd}' AND
# #       '{td}' AND `unique_id`!='' GROUP BY `unique_id` ORDER BY `emp_id` ASC) AS eav3) AS EAV3,(SELECT COALESCE(SUM(ebv3),0)
# #      FROM (SELECT if(COUNT(`unique_id`)>2,1,0) AS ebv3 FROM call_report_master WHERE `emp_id` IN {employee_ids} AND
# #         `category`='B' AND `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `unique_id`!='' GROUP BY `unique_id`
# #        ORDER BY `emp_id` ASC) AS ebv3) AS EBV3,(SELECT COALESCE(SUM(ecv3),0) FROM (SELECT if(COUNT(`unique_id`)>2,1,0) AS ecv3 FROM
# #      call_report_master WHERE `emp_id` IN {employee_ids} AND `category`='C' AND `call_report_master`.`date` BETWEEN '{fd}'
# #       AND '{td}' AND `unique_id`!='' GROUP BY `unique_id` ORDER BY `emp_id` ASC) AS ecv3) AS ECV3,(SELECT COALESCE(SUM(aothers1),0)
# #        FROM (SELECT if((`doctor_agent_list`.`emp_id`!=`call_report_master`.`emp_id`),1,0) AS aothers1 FROM `call_report_master`
# #       INNER JOIN `doctor_agent_list` on `call_report_master`.`unique_id`= `doctor_agent_list`.`unique_id` WHERE
# #       `call_report_master`.`emp_id` IN {employee_ids} AND `call_report_master`.`category`='A' AND
# #        `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `call_report_master`.`unique_id`!='' GROUP BY
# #      `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) as aothers1) AS aothers1,
# #     (SELECT COALESCE(SUM(bothers1),0) FROM (SELECT if((`doctor_agent_list`.`emp_id`!=`call_report_master`.`emp_id`),1,0) AS bothers1
# #        FROM `call_report_master` INNER JOIN `doctor_agent_list` on `call_report_master`.`unique_id`= `doctor_agent_list`.`unique_id`
# #       WHERE `call_report_master`.`emp_id` IN {employee_ids} AND `call_report_master`.`category`='B' AND
# #     `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `call_report_master`.`unique_id`!='' GROUP BY
# #      `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) as bothers1) AS bothers1,
# #      (SELECT COALESCE(SUM(cothers1),0) FROM (SELECT if((`doctor_agent_list`.`emp_id`!=`call_report_master`.`emp_id`),1,0) AS
# #        cothers1 FROM `call_report_master` INNER JOIN `doctor_agent_list` on `call_report_master`.`unique_id`= `doctor_agent_list`.`unique_id`
# #        WHERE `call_report_master`.`emp_id` IN {employee_ids} AND `call_report_master`.`category`='C' AND
# #      `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `call_report_master`.`unique_id`!='' GROUP BY
# #      `call_report_master`.`unique_id` ORDER BY `call_report_master`.`emp_id` ASC) as cothers1) AS
# #       cothers1);""".format(fd=fdate, td=tdate, emp=emp_id))


@login_required(login_url="/")
def reject(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test')),

    }

    if request.method == "POST":
        branch = request.POST.get('branch')
        if branch == 'All':
            context['rejected_list'] = PatientData.objects.filter(referralstatus='Yes', chapproval="No")
        else:
            context['rejected_list'] = PatientData.objects.filter(referralstatus='Yes', chapproval="No", branch=branch)

    return render(request, 'reject.html', context)


@login_required(login_url="/")
def neft_return_list(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test'))
    }

    if request.method == "POST":
        branch = request.POST.get('branch')
        filter_date = request.POST.get('date')

        fdate, tdate = filter_date.split(' - ')
        fdate = datetime.strptime(str(fdate), '%m/%d/%Y').date()
        tdate = datetime.strptime(str(tdate), '%m/%d/%Y').date()

        cursor = connection.cursor()
        if branch == 'All':
            cursor.execute(
                "SELECT `invoice_no`, `patient_name`, DATE_FORMAT(`visit_data`,'%d-%b-%Y') AS adate,"
                "DATE_FORMAT(`discharge_datetime`,'%d-%b-%Y') AS ddate,`isbilldone` AS admissionstatus, `patient_data`.`referralmobile` "
                "as mobile, `patient_data`.`branch` as branch,`patient_data`.`consultantentry` as consultantentry,`consultantremarks`,"
                "`patient_data`.`referraldepartment` as department, `patient_data`.`organization` organization, `referralstatus`, `Admissiontype`, "
                "UPPER(`doctor_agent_list`.`agent_name`) AS referralname, `referraldepartment`, `doctor_agent_list`.`mobile` as referralmobile, `referralremarks`, `paymentmode`, `doctor_agent_list`.`bank_ac` as accnumber,"
                "`doctor_agent_list`.`ifsc` as ifsccode, `doctor_agent_list`.`pancard` as pancard, `clashstatus`,DATE_FORMAT(`referralcreatedon`,'%d-%b-%Y %H:%i:%s') AS referralcreatedon, `referralcreatedby`,  `chapproval`, "
                "(`phar_consum_billamount`) AS billamount,`referralpercentage`, ROUND(if(`referralmode` = 'Fixed Amount',`referralamount`,(`referralpercentage`/100)*(`phar_consum_billamount`-`phar_consum_billamount`)),2) AS referralamount2,`chapproval`,UPPER(`UCID`) AS referralcode,"
                "`referralamount` FROM `patient_data` INNER JOIN `doctor_agent_list` ON `patient_data`.`UCID`=`doctor_agent_list`.`unique_id` WHERE `patient_data`.`branch` != 'Test' AND `cluster_approval` = 'Approved'  AND `doctor_agent_list`.`bank_ac`!='null'  "
                "AND DATE(`cluster_approved_on`) BETWEEN '2019-01-01' AND '2023-01-01' GROUP BY `invoice_no` ORDER BY `patient_data`.`branch`,`patient_data`.`visit_data`,`patient_data`.`discharge_datetime` ASC;")

        else:
            cursor.execute(
                """SELECT `invoice_no`,`patient_name`, DATE_FORMAT(`visit_data`,'%d-%b-%Y') AS adate,DATE_FORMAT(`discharge_datetime`,'%d-%b-%Y') AS ddate,  `isbilldone` AS admissionstatus, `patient_data`.`referralmobile` as mobile, `patient_data`.`branch` as branch,`patient_data`.`consultantentry` as consultantentry,`consultantremarks`, `patient_data`.`referraldepartment` as department, `patient_data`.`organization` as organization, `referralstatus`, 
                `Admissiontype`, UPPER(`doctor_agent_list`.`agent_name`) AS referralname, `referraldepartment`, `doctor_agent_list`.`mobile` as referralmobile, `referralremarks`, `paymentmode`, `doctor_agent_list`.`bank_ac` as accnumber,`doctor_agent_list`.`ifsc` as ifsccode, `doctor_agent_list`.`pancard` as pancard, `clashstatus`, DATE_FORMAT(`referralcreatedon`,'%d-%b-%Y %H:%i:%s') AS referralcreatedon, `referralcreatedby`,  `chapproval`, (`phar_consum_billamount`) AS billamount,`referralpercentage`, ROUND(if(`referralmode` = 'Fixed Amount',`referralamount`,(`referralpercentage`/100)*(`phar_consum_billamount`-`phar_consum_billamount`)),2) AS referralamount2,`chapproval`,UPPER(`UCID`) AS referralcode,`referralamount` FROM `patient_data` INNER JOIN `doctor_agent_list` ON `patient_data`.`UCID`=`doctor_agent_list`.`unique_id`
                 WHERE `patient_data`.`branch` != 'Test' AND `cluster_approval` = 'Approved' AND `doctor_agent_list`.`bank_ac`!='' AND `doctor_agent_list`.`bank_ac`!='null' AND `utr_no`='NEFT Return' AND 
                  `patient_data`.`branch` = 'branch'  GROUP BY `invoice_no` ORDER BY `patient_data`.`branch`,`patient_data`.`visit_data`,`patient_data`.`discharge_datetime` ASC""".format(
                    b=branch))
        desc = cursor.description
        context['neft'] = [
            dict(zip([i[0] for i in desc], row)) for row in cursor.fetchall()
        ]

    return render(request, 'neft.html', context)


@login_required(login_url="/")
def cash_payment(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test'))

    }
    if request.method == "POST":
        branch = request.POST.get('branch')

        if branch == 'All':
            context['cash'] = PatientData.objects.filter(paymentmode='Cash', referralstatus='Yes')
        else:
            context['cash'] = PatientData.objects.filter(paymentmode='Cash', branch=branch, referralstatus='Yes')

    return render(request, 'cash_payment.html', context)


@login_required(login_url="/")
@csrf_exempt
def functional_approval_list(request):
    context = {
        'branch_name': BranchListDum.objects.filter(~Q(branch_name='Test')),
        'cluster': PatientData.objects.filter(referralstatus='Yes', chapproval="")
    }
    if 'approval_value' in request.POST:
        data_list = request.POST.get('approval_value')
        try:
            for sno in ast.literal_eval(data_list):
                print(sno)
                PatientData.objects.filter(sno=sno).update(chapproval="approved", chapproval_by=request.user.emp_id,
                                                           ch_approved_on=timezone.now())
            messages.success(request, 'Approved successfully')

        except TypeError:
            PatientData.objects.filter(sno=data_list).update(chapproval="approved", chapproval_by=request.user.emp_id,
                                                             ch_approved_on=timezone.now())
            messages.success(request, 'Approved successfully')
        return redirect('functional_approval_list')

    elif 'reject_value' in request.POST:
        data_list = request.POST.get('reject_value')
        try:
            for sno in ast.literal_eval(data_list):
                PatientData.objects.filter(sno=sno).update(chapproval="No", chapproval_by=request.user.emp_id,
                                                           ch_approved_on=timezone.now())
            messages.success(request, 'Rejected successfully')
        except TypeError:
            PatientData.objects.filter(sno=data_list).update(chapproval="No", chapproval_by=request.user.emp_id,
                                                             ch_approved_on=timezone.now())
            messages.success(request, 'Rejected successfully')
        return redirect('functional_approval_list')

    elif request.method == "POST":
        branch_name = request.POST.get('branch')

        if branch_name == 'All':
            context['cluster'] = PatientData.objects.filter(referralstatus='Yes', chapproval="")
        else:
            context['cluster'] = PatientData.objects.filter(referralstatus='Yes', branch=branch_name, chapproval="")

    return render(request, 'fucntional_aprroval_list.html', context)


@login_required(login_url="/")
def s_id(request):
    if 'term' in request.GET:
        result = []
        term = request.GET.get('term')
        new = PatientData.objects.filter(Q(registration_number__istartswith=term) | Q(patient_name__istartswith=term))
        for emp in new:
            result.append({'registration_number': emp.registration_number, 'patient_name': emp.patient_name,
                           'invoice_no': emp.invoice_no})
        if not result:
            result.append({'registration_number': '', 'patient_name': '', 'invoice_no': ''})

        return JsonResponse(result, safe=False)


@login_required(login_url="/")
@csrf_exempt
def daily_call(request):
    draw = int(request.POST.get('draw'))
    # start = int(request.POST.get('start'))
    length = int(request.POST.get('length'))
    search = request.POST.get('search[value]')
    colindex = request.POST.get("order[0][column]")
    records_total = CallReportMaster.objects.all().order_by('unique_id').count()
    records_filtered = records_total
    call_data = CallReportMaster.objects.all().order_by('unique_id').values()

    if search:
        call_data = CallReportMaster.objects.filter(date__lte=search, date__gte=search
                                                    ).order_by('unique_id').values()
        records_total = call_data.count()
        records_filtered = records_total

    paginator = Paginator(call_data, length)
    try:
        object_list = paginator.page(draw).object_list
    except PageNotAnInteger:
        object_list = paginator.page(draw).object_list
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages).object_list

    data = [
        {
            'sno': emp['sno'],
            'edit': '',
            'emp_id ': emp['emp_id '],
            'Emp_name ': emp['Emp_name '],
            'ref_type ': emp['ref_type '],
            'unique_id ': emp['unique_id '],
            'name ': emp['name '],
            'camp ': emp['camp '],
            'date ': emp['date '],
            'time': emp['time'],
            'location ': emp['location '],
            'Type ': emp['Type '],
            'source ': emp['source '],
            'branch ': emp['branch '],
        } for emp in object_list
    ]
    return JsonResponse(
        {"draw": draw, "iTotalRecords": records_total, 'recordsFiltered': records_filtered, "data": data}, safe=False)


@login_required(login_url="/")
def edit_list(request):
    if request.method == "POST":
        data_list = request.POST.get('transfer_id')
        print(request.POST)
    return redirect('functional_approval_list')


@login_required(login_url="/")
def payment_list(request):
    context = {
        'branch_name': BranchListDum.objects.filter(~Q(branch_name='Test')),

    }
    if request.method == "POST":
        branch_name = request.POST.get('branch')

        if branch_name == 'All':
            context['status'] = PatientData.objects.filter(referralstatus='Yes', chapproval="approved")

        else:
            context['status'] = PatientData.objects.filter(referralstatus='Yes', branch=branch_name,
                                                           chapproval="approved")

    return render(request, 'payment_list.html', context)


@login_required(login_url="/")
def pending_payment_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pending_payment.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Sno',
        'BILL NO',
        'Bill Date',
        'Mobile _Number',
        'Department_Name',
        'Service_Name', ' Bill_type', 'Payment_Mode', 'Branch', 'Patient_Name',
        'Referral_Name', 'Referral_Type', 'Referral_Percentage', 'Referral_Percentage_Name',
        'Gross Bill Amount', 'Discount Amount', 'Net Bill Amount', 'Referral Amount', 'Referral updated on',
        'Referral created_by',
        'Functional_Approval', 'Functional approved on', 'UCID', 'Agent / doctor name', 'bank account',
        'IFSC', 'PANCARD', 'UTR No', 'UTR Date'
    ])
    data = PatientData.objects.all().values_list('sno', 'invoice_no', 'invoice_date', 'referralmobile',
                                                 'department_name', 'service_name', 'admissiontype', 'paymentmode',
                                                 'branch', 'patient_name', 'referralname', 'referral_type',
                                                 'referralpercentage', 'referralpercentagename',
                                                 'grossamount', 'discount', 'netamount', 'referralamount',
                                                 'referralcreatedon', 'referralcreatedby', 'chapproval',
                                                 'ch_approved_on', 'ucid', 'marketing_executive', 'accnumber',
                                                 'ifsccode', 'pancard', 'utr_no')
    for i in data:
        writer.writerow(i)
    return response


def coverage_report(request):
    context = {}
    if request.method == 'POST':
        branch = request.POST.get('branch')
        date = request.POST.get('date')
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        query = Logins.objects.filter(
            Q(page='Marketing') &
            ~Q(branch='Test') &
            Q(job_status='Active') &
            ~Q(emp_id__in=[15217, 15030, 15179, 15376, 15251])
        ).distinct()

        results = query.extra(
            tables=['call_report_master'],
            where=[
                '`call_report_master`.`emp_id` = `logins`.`Emp_ID`',
            ],
            select={
                'Emp_ID': '`logins`.`Emp_ID`',
                'Emp_name': '`logins`.`Emp_name`',
                'Branch': '`logins`.`Branch`',
            }
        )
        if branch == 'All':
            results = results.order_by('branch')
        else:
            results = results.filter(branch=branch)

        result = []
        for emp in results:
            emp_id = emp.emp_id
            call_report_qs = CallReportMaster.objects.filter(emp_id=emp_id, date=date).values('area', 'city', 'state',
                                                                                              'pincode')
            total = call_report_qs.aggregate(TOTAL=Count('unique_id'))
            qua = call_report_qs.filter(ref_type__contains='QUALIFIED').aggregate(QUA=Count('unique_id'))
            reg = call_report_qs.filter(ref_type__contains='REGISTERED PRACTIONER').aggregate(REG=Count('unique_id'))
            spc = call_report_qs.filter(ref_type__contains='SPECIAL CATEGORY').aggregate(SPC=Count('unique_id'))
            karnataka = call_report_qs.filter(ref_type__contains='KARNATAKA').aggregate(KARNATAKA=Count('unique_id'))
            mintime = call_report_qs.aggregate(MINTIME=Min('time'))
            logins_location = Logins.objects.filter(emp_id=emp_id, last_loc_datetime__date=date).values('last_location')

            values = {
                'empid': emp_id,
                'name': emp.emp_name,
                'branch': emp.branch,
                'TOTAL': total['TOTAL'] if total['TOTAL'] else 0,
                'QUA': qua['QUA'] if qua['QUA'] else 0,
                'REG': reg['REG'] if reg['REG'] else 0,
                'SPC': spc['SPC'] if spc['SPC'] else 0,
                'KARNATAKA': karnataka['KARNATAKA'] if karnataka['KARNATAKA'] else 0,
                'MINTIME': mintime['MINTIME'] if mintime['MINTIME'] else '-',
                'location': logins_location[0]['last_location'] if logins_location else None,
                'area': call_report_qs[0]['area'] if call_report_qs else None,
                'city': call_report_qs[0]['city'] if call_report_qs else None,
                'state': call_report_qs[0]['state'] if call_report_qs else None,
                'pincode': call_report_qs[0]['pincode'] if call_report_qs else None,
            }
            result.append(values)
        context = {
            'result': result,
            'date': date_obj,
        }
    context['branch'] = BranchListDum.objects.filter(~Q(branch_name='Test'))

    # if request.method == 'POST':
    #     branch = request.POST.get('branch', '')
    #     date = request.POST.get('date', '')
    #     cursor = connection.cursor()
    #     if branch == 'All':
    #         cursor.execute("""SELECT DISTINCT  logins.Emp_ID,  logins.Emp_name,  logins.Branch,  logins.type, (SELECT COUNT(`unique_id`) FROM `call_report_master`
    #         WHERE `emp_id` = logins.Emp_ID AND `date` = '{d}') AS TOTAL,
    #          SUM(CASE WHEN call_report_master.ref_type
    #          LIKE '%QUALIFIED%' THEN 1 ELSE 0 END) AS QUA, SUM(CASE WHEN call_report_master.ref_type LIKE '%REGISTERED PRACTIONER%' THEN 1 ELSE 0 END) AS REG,
    #            SUM(CASE WHEN call_report_master.ref_type LIKE '%SPECIAL CATEGORY%' THEN 1 ELSE 0 END) AS SPC,
    #                SUM(CASE WHEN call_report_master.ref_type LIKE '%KARNATAKA%' THEN 1 ELSE 0 END) AS KARNATAKA,
    #                    IFNULL(MIN(CASE WHEN call_report_master.time != '' THEN call_report_master.time ELSE NULL END),'-') AS MINTIME,
    #                        logins.Last_Location AS location, logins.last_loc_datetime AS lastupdate FROM logins INNER JOIN
    #                        call_report_master ON call_report_master.emp_id = logins.Emp_ID WHERE   logins.Page = 'Marketing' AND logins.Job_Status = 'Active'
    #                         AND call_report_master.date = '{d}' GROUP BY logins.Emp_ID, logins.Emp_name,  logins.Branch,  logins.type,
    #                         logins.Last_Location, logins.last_loc_datetime;""".format(d=date))
    #     else:
    #         cursor.execute("""SELECT DISTINCT  logins.Emp_ID,  logins.Emp_name,  logins.Branch,  logins.type, (SELECT COUNT(`unique_id`) FROM `call_report_master`
    #          WHERE `emp_id` = logins.Emp_ID AND `date` = '{d}') AS TOTAL, SUM(CASE WHEN call_report_master.ref_type
    #          LIKE '%QUALIFIED%' THEN 1 ELSE 0 END) AS QUA, SUM(CASE WHEN call_report_master.ref_type LIKE '%REGISTERED PRACTIONER%' THEN 1 ELSE 0 END) AS REG,
    #            SUM(CASE WHEN call_report_master.ref_type LIKE '%SPECIAL CATEGORY%' THEN 1 ELSE 0 END) AS SPC,
    #                SUM(CASE WHEN call_report_master.ref_type LIKE '%KARNATAKA%' THEN 1 ELSE 0 END) AS KARNATAKA,
    #                    IFNULL(MIN(CASE WHEN call_report_master.time != '' THEN call_report_master.time ELSE NULL END),'-') AS MINTIME,
    #                        logins.Last_Location AS location, logins.last_loc_datetime AS lastupdate FROM logins INNER JOIN
    #                        call_report_master ON call_report_master.emp_id = logins.Emp_ID WHERE   logins.Page = 'Marketing' AND logins.Job_Status = 'Active'
    #                         AND logins.Branch = '{b}'  AND call_report_master.date = '{d}' GROUP BY logins.Emp_ID, logins.Emp_name,  logins.Branch,  logins.type,
    #                         logins.Last_Location, logins.last_loc_datetime;""".format(d=date, b=branch))
    #     desc = cursor.description
    #     context['new'] = [
    #         dict(zip([i[0] for i in desc], row)) for row in cursor.fetchall()
    #     ]
    return render(request, 'coverage_report.html', context)


def map_data(request):
    context = {}

    if request.method == 'POST':
        branch = request.POST.get('branch')
        date = request.POST.get('date')
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        query = Logins.objects.filter(
            # Q(page='Marketing') &
            # ~Q(branch='Test') &
            # Q(job_status='Active') &
            ~Q(emp_id__in=[15217, 15030, 15179, 15376, 15251])
        ).distinct()
        results = query.extra(
            tables=['call_report_master'],
            where=[
                '`call_report_master`.`emp_id` = `logins`.`Emp_ID`',
            ],
            select={
                'Emp_ID': '`logins`.`Emp_ID`',
                'Emp_name': '`logins`.`Emp_name`',
                'Branch': '`logins`.`Branch`',
                'type': '`logins`.`type`',
            }
        )
        if branch != 'All':
            results = results.filter(branch=branch)
        result = []
        for emp in results:
            emp_id = emp.emp_id
            total = CallReportMaster.objects.filter(emp_id=emp_id, date=date).count()
            rmp = CallReportMaster.objects.filter(emp_id=emp_id, date=date, ref_type='RMP').count()
            doctor = CallReportMaster.objects.filter(emp_id=emp_id, date=date, ref_type='DOCTOR').count()
            mintime = CallReportMaster.objects.filter(emp_id=emp_id, date=date).aggregate(MINTIME=Min('time'))

            value = {
                'empid': emp_id,
                'name': emp.emp_name,
                'branch': emp.branch,
                'date': date,
                'type': emp.type,
                'TOTAL': total,
                'RMP': rmp,
                'doctor': doctor,
                'others': total - doctor + rmp,
                'MINTIME': mintime['MINTIME'] if mintime['MINTIME'] else '---',
            }

            result.append(value)
        context = {
            'result': result,
            'date': date_obj,
        }
    context['branch'] = BranchListDum.objects.filter(~Q(branch_name='Test'))

    return render(request, 'report.html', context)


def map_maker(request):
    empid = request.GET.get('empid')
    date = request.GET.get('date')

    queryset = CallReportMaster.objects.filter(emp_id=empid, date=date).values('latitude', 'longitude')
    center = queryset.first()
    if center:
        last_location = f'{center["latitude"]}, {center["longitude"]}'
        context = {
            'last_location': last_location,
            'center': center,
            'no_data_found': False
        }
        return render(request, 'map_maker.html', context)
    else:
        messages.error(request, "No Data Found!")
        context = {
            'no_data_found': True
        }
        return render(request, 'map_maker.html', context)


def live_location(request):
    empid = request.GET.get('empid')
    date = request.GET.get('date')
    cursor = connection.cursor()
    cursor.execute("""SELECT `Last_Location`,
                       SUBSTRING_INDEX(`Last_Location`, ',', 1) AS latitude,
                       SUBSTRING_INDEX(`Last_Location`, ',', -1) AS longitude
                FROM `logins`
                WHERE DATE(`last_loc_datetime`) = '{d}' and `Emp_ID` ='{empid}';""".format(d=date, empid=empid))
    query = cursor.fetchall()

    if query:
        center = query[0]
        if center[0] == ",":
            messages.warning(request, "No Data Found!")
            return redirect('emp_map_data')
        else:
            last_location = center[0]
            context = {
                'last_location': last_location,
            }
            return render(request, 'live_status.html', context)
    else:
        messages.warning(request, "No Data Found!")
        return HttpResponse("No data found")


def ucid_creation(request):
    # url = f'http://127.0.0.1:8000/api/category/'
    # response = requests.get(url)
    # response = json.loads(response.text)

    # context = {
    #     'data': response,
    # }
    # #
    health_data = CampCreate.objects.values()
    df = pd.DataFrame.from_records(health_data)

    df.info()
    return render(request, 'ucid_creation.html')


class HomeSampleVisitsListAPIView(generics.ListAPIView):
    queryset = HomeSampleVisits.objects.all()
    serializer_class = HomeSampleVisitsSerializer


@login_required(login_url="/")
def master_list(request):
    context = {
        'branch': BranchListDum.objects.exclude(branch_name='Test')
    }

    if request.method == "POST":
        branch = request.POST.get('branch')
        cur = connection.cursor()
        if branch == "All":
            cur.execute("SELECT CONCAT(sprint_mis.doctor_agent_list.emp_id) As emp_id, logins.Emp_name, unique_id,"
                        " agent_name, doctor_agent_list.mobile, agent_type, logins.branch, "
                        "category FROM sprint_mis.doctor_agent_list INNER JOIN sprint_mis.`logins` "
                        "ON doctor_agent_list.emp_id = logins.Emp_ID WHERE Job_Status = 'Active' AND "
                        "logins.emp_id NOT IN ('100','200','300','400','500') and doctor_agent_list.branch != 'Test';")
        else:
            cur.execute("SELECT CONCAT(sprint_mis.doctor_agent_list.emp_id) As emp_id, logins.Emp_name, "
                        "unique_id, agent_name, doctor_agent_list.mobile, agent_type, logins.branch,"
                        " category FROM sprint_mis.doctor_agent_list INNER JOIN sprint_mis.`logins` ON"
                        " doctor_agent_list.emp_id = logins.Emp_ID WHERE Job_Status = 'Active' AND logins.emp_id "
                        "NOT IN ('100','200','300','400','500') and doctor_agent_list.branch != 'Test' and doctor_agent_list.branch = '{b}';".format(
                b=branch))

        desc = cur.description
        context['doctor_agent_list'] = [
            dict(zip([i[0] for i in desc], row)) for row in cur.fetchall()
        ]

    return render(request, 'master_list.html', context)

