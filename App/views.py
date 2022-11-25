import ast
import csv
import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import connection
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse, FileResponse, HttpResponseRedirect, response
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from fpdf import FPDF

from App.forms import Update, Upload
from .models import *


# Create your views here.


def loginuser(request):
    for logins in WebLogins.objects.all():
        # if logins.join_date == "0000-00-00":
        WebLogins.objects.filter(emp_id=logins.emp_id).update(is_staff=True, is_active=True)
    #     # login_data = WebLogins.objects.get(emp_id=logins.emp_id)
    #     # login_data.mpassword = login_data.password
    #     # login_data.password = make_password(login_data.password)
    #     # login_data.save()
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        password = request.POST.get('password')
        # emp_id = request.POST['emp_id']
        # password = request.POST['password']
        user = authenticate(username=emp_id, password=password)
        # print(user)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'invalid emp_id and password')
            return redirect('loginuser')
    if request.user.is_authenticated:
        return redirect('dashboard')
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

    # cur = connection.cursor()
    # cur.execute(
    #     '''SELECT `emp_id`,`unique_id`,`name`,`category`,`design`,`contact`,`date`,`time` FROM `call_report_master` WHERE `date` = CURRENT_DATE     GROUP  BY `emp_id`;''')
    # desc = cur.description
    # context['preset_data'] = [
    #     dict(zip([i[0] for i in desc], row)) for row in cur.fetchall()
    # ]
    return render(request, 'dashboard.html', context)


def logout_user(request):
    logout(request)
    return redirect('loginuser')


@login_required(login_url="/")
def register(request):
    result = []
    for branch in list(CallReportMaster.objects.values('branch').distinct()):
        # for branch in list(CallReportMaster.objects.values('branch').filter(date=datetime.today().date()).distinct()):
        if branch['branch']:
            result.append(
                {'branch': branch['branch'], 'count': CallReportMaster.objects.filter(branch=branch['branch']).count()})

    if 'empname' in request.POST:
        empname = request.POST.get('empname')
        empid = request.POST.get('empid')
        mobile = request.POST.get('mobile')
        designation = request.POST.get('designation')
        branch = request.POST.get('branch')
        department = request.POST.get('department')
        catogery = request.POST.get('catogery')
        reporting_to = request.POST.get('reporting_to')
        old_branch = Logins.objects.filter(branch=branch).exclude(branch='').first()

        if designation == 'Executive' or designation == 'Senior Executive':
            Logins.objects.create(emp_name=empname, emp_id=empid, password=make_password(mobile), mpassword=mobile,
                                  personal_number=mobile, office_number=mobile, branch=branch,
                                  old_branch=old_branch.old_branch,
                                  page='Executive', designation=designation, original_type=department,
                                  head=reporting_to, type=department, branch_access=branch, new_type=catogery).save()
            # Executive
        elif designation == 'Manager':
            Logins.objects.create(emp_name=empname, emp_id=empid, password=make_password(mobile), mpassword=mobile,
                                  personal_number=mobile, office_number=mobile, branch=branch,
                                  old_branch=old_branch.old_branch,
                                  page='Manager', designation=designation, original_type=department, head=reporting_to,
                                  type=department, branch_access=branch, new_type=catogery).save()
            # Manager
        else:
            Logins.objects.create(emp_name=empname, emp_id=empid, password=make_password(mobile), mpassword=mobile,
                                  personal_number=mobile, office_number=mobile, branch=branch,
                                  old_branch=old_branch.old_branch,
                                  page='Team Lead', designation=designation, original_type=department,
                                  head=reporting_to, type=department, branch_access=branch, new_type=catogery).save()
            # Team Lead
        messages.success(request, 'Employee Account has been created')
        return redirect('register')

    if 'branch_name' in request.POST:
        branch = request.POST.get('branch_name')
        BranchListDum.objects.create(branch_name=branch).save()
        messages.success(request, "branch added")
        return redirect('register')

    # active and inactive user
    if 'emp_search' in request.POST:
        emp_search = request.POST.get('emp_search')
        status = request.POST.get('status')
        try:
            user = Logins.objects.get(emp_id=emp_search)
            user.job_status = status
            user.inactive_dt = datetime.today().date()
            user.save()
            messages.success(request, "updated successfully..")
        except Logins.DoesNotExist:
            messages.error(request, "You have entered incorrect Emp_ID")

        return redirect('register')

    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test')),
        'branch_wise_count': result,
        'total_count': CallReportMaster.objects.count(),
    }
    return render(request, 'Employee/register.html', context)


@login_required(login_url="/")
def search_emp(request):
    # print(request.GET, request.POST)
    if 'term' in request.GET:
        result = []
        term = request.GET.get('term')
        new = Logins.objects.filter(Q(emp_id__istartswith=term) | Q(emp_name__istartswith=term))
        for emp in new:
            result.append({'id': emp.emp_id, 'name': emp.emp_name, 'desg': emp.designation})
        if not result:
            result.append({'name': "No data found", 'id': '', 'desg': ''})

        return JsonResponse(result, safe=False)


@login_required(login_url="/")
def emp_list(request):
    return render(request, 'emp_list.html')


@login_required(login_url="/")
def update_activity(request):
    return render(request, 'update_act.html')


@login_required(login_url="/")
def ref_dashboard(request):
    return render(request, 'ref_dashboard.html')
    #     # print(PatientData.objects.filter(~Q(branch='Test') & Q(cluster_approval='Approved') & ~Q(utr_no='') & ~Q(utr_no='NEFT Return') & ~Q(utr_no='Wrong Bank Details')).select_related('invoice_no'))


@login_required(login_url="/")
def pending_payment(request):
    status = PatientData.objects.filter(referralstatus='Yes', chapproval="approved")
    cash = PatientData.objects.filter(referralstatus='Yes', chapproval="approved", paymentmode='cash')
    upi = PatientData.objects.filter(referralstatus='Yes', chapproval="approved", paymentmode='upi')
    netbanking = PatientData.objects.filter(referralstatus='Yes', chapproval="approved", paymentmode='netbanking')

    if request.method == "POST":
        branch_name = request.POST.get('branch')

        if branch_name == 'All':
            status = PatientData.objects.filter(referralstatus='Yes', chapproval="approved")
            cash = PatientData.objects.filter(referralstatus='Yes', chapproval="approved", paymentmode='cash'
                                              ),
            upi = PatientData.objects.filter(referralstatus='Yes', chapproval="approved", paymentmode='upi'
                                             ),
            netbanking = PatientData.objects.filter(referralstatus='Yes', chapproval="approved",
                                                    paymentmode='netbanking')
        else:
            status = PatientData.objects.filter(referralstatus='Yes',
                                                      chapproval="approved", branch=branch_name)
            cash = PatientData.objects.filter(referralstatus='Yes', chapproval="approved",
                                              paymentmode='cash', branch=branch_name)
            upi = PatientData.objects.filter(referralstatus='Yes', chapproval="approved", paymentmode='upi',
                                             branch=branch_name),
            netbanking = PatientData.objects.filter(referralstatus='Yes', chapproval="approved",
                                                    paymentmode='netbanking', branch=branch_name)

    context = {
        'branch_name': BranchListDum.objects.filter(~Q(branch_name='Test')),
        'status': status,
        'cash': cash,
        'upi': upi,
        'netbanking': netbanking,
    }
    return render(request, 'pending_payment.html', context)


@login_required(login_url="/")
def doctor_agent_list(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test')),
        # 'doctor_agent_list': DoctorAgentList.objects.all(),
    }
    if 'transfer_id' in request.POST:
        pass

    if request.POST.get('from_empid'):
        from_empid = request.POST.get('from_empid')
        to_empid = request.POST.get('to_empid')
        DoctorAgentList.objects.filter(emp_id=from_empid).update(emp_id=to_empid)
        # print(from_empid, to_empid)
        messages.success(request, f"Emp Id : {from_empid} Transferred to Emp Id : {to_empid}")
        return redirect('doctor_agent_list')

    if request.method == "POST":
        empid = request.POST.get('empid')
        branch = request.POST.get('branch')
        if branch == "All":
            context["doctor_agent_list"] = DoctorAgentList.objects.filter()
        elif empid and branch:
            context["doctor_agent_list"] = DoctorAgentList.objects.filter(emp_id=empid, branch=branch)
        elif empid:
            context["doctor_agent_list"] = DoctorAgentList.objects.filter(emp_id=empid)
        elif branch:
            context["doctor_agent_list"] = DoctorAgentList.objects.filter(branch=branch)
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
    records_total = DoctorAgentList.objects.all().order_by('emp_id').count()
    records_filtered = records_total
    agent_data = DoctorAgentList.objects.all().order_by('emp_id').values()

    if search:
        agent_data = DoctorAgentList.objects.filter(Q(emp_id__icontains=search) | Q(agent_name__icontains=search) | Q(
            unique_id__icontains=search)).order_by('emp_id').values()
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
        'report': CallReportMaster.objects.all(),
    }
    if request.method == "POST":
        empid = request.POST.get('empid')
        if empid:
            context["call_report"] = CallReportMaster.objects.filter(emp_id=empid)
            context["emp_id"] = empid

    return render(request, 'call/call_report.html', context)


@csrf_exempt
@login_required(login_url="/")
def call_reports(request):
    # print(request.POST)
    draw = int(request.POST.get('draw'))
    length = int(request.POST.get('length'))
    start = int(request.POST.get('start'))
    search = request.POST.get('search[value]')
    colindex = request.POST.get("order[0][column]")
    # print(draw, length, search, colindex, )
    records_total = CallReportMaster.objects.all().order_by('emp_id').count()
    records_filtered = records_total
    call_data = CallReportMaster.objects.all().order_by('emp_id').values()[start:length + start]

    if search:
        call_data = CallReportMaster.objects.filter(Q(emp_id__icontains=search) | Q(name__icontains=search)
                                                    ).order_by('emp_id').values()[start:length + start]
        records_total = call_data.count()
        records_filtered = records_total

    # paginator = Paginator(call_data, length)
    #
    # try:
    #     object_list = paginator.page(draw).object_list
    # except PageNotAnInteger:
    #     object_list = paginator.page(draw).object_list
    # except EmptyPage:
    #     object_list = paginator.page(paginator.num_pages).object_list

    data = [
        {
            'sno': "",
            # 'input': '<input type="checkbox" class="" name="' + str(emp['emp_id']) + '" value="">',
            'emp_id': emp['emp_id'],
            'unique_id': emp['unique_id'],
            'name': emp['name'],
            'category': emp['category'],
            'design': emp['design'],
            'contact': emp['contact'],
            'date': emp['date'],
            'time': emp['time'],
            'area': emp['area'],
            'city': emp['city'],
            'state': emp['state'],
            'pincode': emp['pincode'],
            'station': emp['station'],
            'branch': emp['branch'],
            'source': emp['source'],
            'attendance': emp['attendance'],
            'type': emp['type'],

            # 'employee_id': '<a href="/profile/?i=' + str(emp['employee_id']) + '">' + str(emp['employee_id']) + '</a>',
        } for emp in call_data
    ]
    return JsonResponse(
        {"draw": draw, "iTotalRecords": records_total, 'recordsFiltered': records_filtered,
         "iTotalDisplayRecords": records_total, "aaData": data}, safe=False)


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
            DoctorAgentList.objects.filter(unique_id=i).update(emp_id=transfer)
            print(i)

        status = True
        return JsonResponse({'res': status})

@login_required(login_url="/")
def call_report_csv(request):
    # empid = request.GET.get('i')
    # print(empid)

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
            " WHERE `doctor_agent_list`.`branch` != 'Test' AND `doctor_agent_list`.`date` BETWEEN  '2019-01-01' AND '2023-12-12';".format(
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
def abc_report(request):
    context = {
        'abcreport': AbcReport.objects.all(),
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test'))
    }
    if request.method == 'POST':
        branch = request.POST.get('branch')
        # first_date = request.POST.get('date')
        #
        # fr_date, tm_date = first_date.split(' - ')
        # fr_date = datetime.strptime(str(fr_date), '%m/%d/%Y').date()
        # tm_date = datetime.strptime(str(tm_date), '%m/%d/%Y').date()
        #
        # if branch and first_date:
        #     context['abcreport'] =

    return render(request, 'referral/abc_report.html', context)


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
    if request.method == "POST":
        branch = request.POST.get('branch')
        filter_date = request.POST.get('date')

        fdate, tdate = filter_date.split(' - ')
        fdate = datetime.strptime(str(fdate), '%m/%d/%Y').date()
        tdate = datetime.strptime(str(tdate), '%m/%d/%Y').date()

        if branch == 'All':
            context['allowance'] = Logins.objects.filter(page='Marketing', job_status='Active') & Logins.objects.filter(
                ~Q(branch='Test', designation='Center Head', type='Admin')).order_by('allow')
        else:
            context['allowance'] = Logins.objects.filter(page='Marketing', job_status='Active',
                                                         branch=branch) & Logins.objects.filter(
                ~Q(branch='Test', designation='Center Head', type='Admin')).order_by('allow')
        #     cursor.execute(
        #         "SELECT `Emp_ID`,`Emp_name`,`Branch` FROM `logins` WHERE `Page` = page AND `Job_Status` = Job_Status AND "
        #         "`Branch` = Branch  AND `Designation` != '' AND `Branch` = branch AND `type`!= Original_Type ORDER BY `allow` DESC;")
        # else:
        #     cursor.execute(
        #         "SELECT `Emp_ID`,`Emp_name`,`Branch` FROM `logins` WHERE `Page` = Page AND `Job_Status` = Job_Status AND "
        #         "`Branch` != ''  AND `Designation` != ''AND `Branch` = Branch AND `type`!= Original_Type ORDER BY `allow` DESC;")
    return render(request, 'referral/allowance_report.html', context)


# SELECT (SELECT `emp_id`) AS empid,(SELECT `name`) AS empname,IFNULL((SELECT COUNT(DISTINCT `date`) FROM `call_report_master` WHERE (`emp_id` =  `Emp_ID` AND `date` BETWEEN '2021-01-01' AND '2022-04-08' AND `camp` != 'Hospital Visit') AND (`emp_id` = `Emp_ID` AND `date` BETWEEN  '2020-01-01' AND '2022-04-08' AND `camp` != 'Office Work') AND (`emp_id` =  `emp_id` AND `date` BETWEEN  '2019-01-01' AND '2022-04-08' AND `camp` != 'Meeting') GROUP BY `emp_id`),0) AS TOTALDAYS,IFNULL((SELECT COUNT(`date`) FROM `call_report_master` WHERE (`emp_id` = `Emp_ID` AND `date` BETWEEN  '2021-01-01' AND '2022-04-08' AND `camp` != 'Hospital Visit' ) AND (`emp_id` =  `emp_id` AND `date` BETWEEN  '2021-01-01' AND '2022-04-08' AND `camp` != 'Office Work') AND (`emp_id` =  `emp_id` AND `date` BETWEEN  '2021-01-01' AND '2022-04-08' AND `camp` != 'Meeting') GROUP BY `emp_id`),0) AS TOTALCALLS,(SELECT (`logins`.`allow`) FROM `call_report_master` INNER JOIN `logins` ON `call_report_master`.`emp_id` = `logins`.`Emp_ID` WHERE `logins`.`Emp_ID` = `Emp_ID` LIMIT 1) AS ALLOWANCE,(SELECT ROUND((`logins`.`allow`/12),2) FROM `call_report_master` INNER JOIN `logins` ON `call_report_master`.`emp_id` = `logins`.`Emp_ID` WHERE `logins`.`Emp_ID` = `Emp_ID` LIMIT 1) AS PERDAYALLOWNACE,(SELECT IF(TOTALCALLS != '',ROUND(PERDAYALLOWNACE*TOTALCALLS,2),0)) AS TOTALALLOWANCE;


@login_required(login_url="/")
def inactive_allowance_report(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test'))
    }
    if request.method == "POST":
        branch = request.POST.get('branch')
        # filter_date = request.POST.get('date')
        #
        # from_d, to_d = filter_date.split(' - ')
        # from_d = datetime.strptime(str(from_d), '%m/%d/%Y').date()
        # to_d = datetime.strptime(str(to_d), '%m/%d/%Y').date()

        cursor = connection.cursor()
        if branch == 'All':

            cursor.execute(
                "SELECT `call_report_master`.`emp_id` AS Emp_ID,`logins`.`Emp_name` As Emp_name,`logins`.`Branch` As"
                " Branch FROM `call_report_master` INNER JOIN `logins` ON `call_report_master`.`emp_id`=`logins`.`Emp_ID`"
                " WHERE `call_report_master`.`date`  BETWEEN  '2021-01-01' AND '2022-08-04' AND `logins`.`Job_Status`= 'Inactive'"
                " AND `logins`.`Branch`!= 'Test' AND `logins`.`Designation`!= 'Center Head' AND `logins`.`Page`= 'Marketing' AND"
                " `logins`.`type`!= 'Admin' GROUP by emp_id ORDER BY `logins`.`allow` DESC;")
        else:
            cursor.execute(
                "SELECT `call_report_master`.`emp_id` AS Emp_ID,`logins`.`Emp_name` As Emp_name,`logins`.`Branch` As "
                "Branch FROM `call_report_master` INNER JOIN `logins` ON `call_report_master`.`emp_id`=`logins`.`Emp_ID`"
                " WHERE `call_report_master`.`date` BETWEEN '2021-01-01' AND '2022-08-04'  AND "
                "`logins`.`Job_Status`= 'Inactive' AND `logins`.`Designation`!= 'Center Head' AND `logins`.`Page`=  'Marketing' "
                "AND `logins`.`type`!= 'Admin' GROUP by emp_id ORDER BY `logins`.`allow` DESC;")
            ina = cursor.description
            context['inactive'] = [
                dict(zip([i[0] for i in ina], list)) for list in cursor.fetchall()
            ]
    return render(request, 'referral/inactive_allowance_report.html', context)


@login_required(login_url="/")
# def bill_list(request):
#     context = {
#         'branch': BranchListDum.objects.filter(~Q(branch_name='Test')),
#     }
#
#     if request.POST.get('invoice_no'):
#         invoice_no = request.POST.get("unique_id")
#         unique_id = request.POST.get("invoice_no")
#         marketing_executive marketing_executive request.POST.get("marketing_executive ")
#         calculationtype = request.POST.get("referralpercentagename")
#         referralpercentage = request.POST.get("referralpercentage")
#         referralamount = request.POST.get("referralamount")
#         ref_type = request.POST.get("referral_type")
#         paymentmode = request.POST.get("paymentmode")
#         if paymentmode == "NetBanking":
#             accnumber = request.POST.get("accnumber")
#             ifsccode = request.POST.get("ifsccode")
#             pancard = request.POST.get("pancard")
#             upinumber = None
#         elif paymentmode == "UPI":
#             accnumber = None
#             ifsccode = None
#             pancard = None
#             upinumber = request.POST.get("upinumber")
#         else:
#             accnumber = None
#             ifsccode = None
#             pancard = None
#             upinumber = None
#
#         doctor_agent = DoctorAgentList.objects.get(unique_id=invoice_no)
#         if doctor_agent.bank_ac == "No Update" or doctor_agent.bank_ac == "":
#             if paymentmode == "NetBanking":
#                 doctor_agent.bank_ac = accnumber
#                 doctor_agent.ifsc = ifsccode
#                 doctor_agent.pancard = pancard
#                 doctor_agent.save()
#             PatientData.objects.filter(sno=invoice_no).update(ucid=unique_id,
#                                                               referral_cal_by=request.user.emp_id,
#                                                               referralcreatedby=request.user.emp_id,
#                                                               ucidcreatedon=timezone.now(),
#                                                               referralcreatedon=timezone.now(),
#                                                               referralname=marketing_executive,
#                                                               referralpercentagename=calculationtype,
#                                                               referralpercentage=referralpercentage,
#                                                               referralamount=referralamount,
#                                                               referral_type=ref_type,
#                                                               paymentmode=paymentmode,
#                                                               accnumber=accnumber,
#                                                               ifsccode=ifsccode,
#                                                               pancard=pancard, upinumber=upinumber,
#                                                               referralstatus='Yes')
#             messages.success(request, "Updated successfully")
#         else:
#             PatientData.objects.filter(sno=invoice_no).update(ucid=unique_id,
#                                                               referral_cal_by=request.user.emp_id,
#                                                               referralcreatedby=request.user.emp_id,
#                                                               ucidcreatedon=timezone.now(),
#                                                               referralcreatedon=timezone.now(),
#                                                               referralname=marketing_executive,
#                                                               referralpercentagename=calculationtype,
#                                                               referralpercentage=referralpercentage,
#                                                               referralamount=referralamount,
#                                                               referral_type=ref_type,
#                                                               paymentmode=paymentmode,
#                                                               accnumber=doctor_agent.bank_ac,
#                                                               ifsccode=doctor_agent.ifsc,
#                                                               pancard=doctor_agent.pancard, upinumber=upinumber,
#                                                               referralstatus='Yes')
#
#     # if 'referralstatus' in request.POST:
#     #     referralstatus = request.POST.get('referralstatus')
#     #     PatientData.objects.filter(referralstatus=referralstatus).update(referralstatus='Yes')
#     #     print(referralstatus)
#     #     return redirect('cluster_approved_list')
#
#     if request.method == "GET" and request.is_ajax():
#         sno = int(request.GET.get('sno'))
#         res = list(PatientData.objects.filter(sno=sno).values())[0]
#         return JsonResponse(res)
#
#     if 'delete_sno' in request.GET and request.is_ajax():
#         delete_sno = request.GET.get('delete_sno')
#         PatientData.objects.get(sno=delete_sno)
#         messages.success(request, 'Deleted succesfully')
#         return JsonResponse({"success": True})
#
#     return render(request, 'bills_list.html', context)

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

    # if 'delete_sno' in request.GET and request.is_ajax():
    #     delete_sno = request.GET.get('delete_sno')
    #     PatientData.objects.get(sno=delete_sno)
    #     messages.success(request, 'Deleted succesfully')
    #     return JsonResponse({"success": True})

    return render(request, 'bills_list.html', context)

@login_required(login_url="/")
def admission_list_filter(request):
    branch = request.GET.get('branch')
    # first_date = request.POST.get('date_input')
    #
    # fr_date, tm_date = first_date.split(' - ')
    # fr_date = datetime.strptime(str(fr_date), '%m/%d/%Y').date()
    # tm_date = datetime.strptime(str(tm_date), '%m/%d/%Y').date()
    draw = int(request.GET.get('draw'))
    start = int(request.GET.get('start'))
    length = int(request.GET.get('length'))
    search = request.GET.get('search[value]')
    colindex = request.GET.get("order[0][column]")

    if branch != "All":
        records_total = PatientData.objects.filter(branch=branch, referralstatus='').order_by('sno').count()
        records_filtered = records_total
        agent_data = PatientData.objects.filter(branch=branch, referralstatus='').order_by('sno').values()[
                     start:length + start]
        if search:
            agent_data = PatientData.objects.filter(Q(branch__istartswith=search)).order_by('sno').values()[
                         start:length + start]
            records_total = agent_data.count()
            records_filtered = records_total

    else:
        records_total = PatientData.objects.filter(referralstatus='').order_by('sno').count()
        records_filtered = records_total
        agent_data = PatientData.objects.filter(referralstatus='').order_by('sno').values()[start:length + start]
        if search:
            agent_data = PatientData.objects.filter(Q(branch__istartswith=search)).order_by('sno').values()[
                         start:length + start]
            records_total = agent_data.count()
            records_filtered = records_total

    data = [
        {
            'sno': emp['sno'],
            'edit': '',
            'invoice_no': emp['invoice_no'],
            'branch': emp['branch'],
            'patient_name': emp['patient_name'],

            'service_name': emp['service_name'],
            'department_name': emp['department_name'],
            # 'marketing_executive': emp['marketing_executive'],
            # 'referral_type': emp['referral_type'],
            # 'referralpercentage': emp['referralpercentage'],
            # 'referralpercentagename': emp['referralpercentagename'],
            'grossamount': emp['grossamount'],
            'discount': emp['discount'],
            'netamount': emp['netamount'],
            # 'referralamount': emp['referralamount'],
            # 'ucidcreatedon': emp['ucidcreatedon'],
            # 'paymentmode': emp['paymentmode'],

        } for emp in agent_data
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
        agent_data = PatientData.objects.filter(Q(branch=search) & Q(referralstatus='')).order_by('sno').values()[
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
            'edit': '',
            # 'edit': '<a href="#"  onclick="editAdmission('+str(emp['sno'])+')" class="icon-pencil mr-2 text-info" data-toggle="modal" data-target="#admissionModal" ></a><a href="/admission_list/?delete='+str(emp['sno'])+'" class="btn btn-sm btn-danger"><i class="icon-trash" aria-hidden="true"></i></a>',
            'invoice_no': emp['invoice_no'],
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
        {"draw": draw, "iTotalRecords": records_total, 'recordsFiltered': records_filtered, "data": data}, safe=False)


# def search_upi(request):
#     if 'term' in request.GET:
#         result = []
#         term = request.GET.get('term')
#         cursor = connection.cursor()
#         cursor.execute(
#             "SELECT `unique_id`,`agent_name`,`mobile`,`logins`.`Emp_name` As empname FROM `doctor_agent_list` INNER JOIN `logins` "
#             "ON `doctor_agent_list`.`emp_id`=`logins`.`Emp_ID` WHERE `unique_id` LIKE '%{term}%' OR `agent_name` LIKE '%{term}%' OR `mobile` LIKE '{term}' LIMIT 15;".format(
#                 term=term))
#         desc = cursor.description
#         data = [
#             dict(zip([i[0] for i in desc], emp)) for emp in cursor.fetchall()
#         ]
#         for emp in data:
#             result.append(
#                 {'id': emp['unique_id'], 'name': emp['agent_name'], 'empname': emp['empname'], 'mobile': emp['mobile']})
#         if not result:
#             result.append({'name': '', 'id': '', 'mobile': '', 'empname': 'No search found'})
#
#         return JsonResponse(result, safe=False)


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
def employee_list(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test')),
        'agent_type': DoctorAgentList.objects.filter(~Q(agent_type='Type')).values('agent_type').distinct()
    }

    if request.method == 'POST':
        branch = request.POST.get('branch')

        if branch == 'All':
            context['emp_list'] = Logins.objects.filter(job_status='Active', page='Marketing') & Logins.objects.filter(
                ~Q(type='Admin')).order_by(
                'branch', 'emp_id')

        else:
            context['emp_list'] = Logins.objects.filter(job_status='Active', page='Marketing',
                                                        branch=branch) & Logins.objects.filter(
                ~Q(type='Admin')).order_by('branch', 'emp_id')
    if 'delete' in request.GET:
        delete = request.GET.get('delete')
        data = Logins.objects.get(emp_id=delete)
        data.delete()
        messages.success(request, 'Deleted succesfully')
        return redirect('employee_list')

    if 'edit' in request.GET:
        edit = request.GET.get('edit')
        context['emp_list'] = Logins.objects.get(emp_name=edit)
        messages.success(request, 'Updated succesfully....')
        return redirect('employee_list')

    if request.POST.get('emp_name'):
        emp_id = request.POST.get("emp_id")
        emp_name = request.POST.get("emp_name")
        orginal_design = request.POST.get("orginal_design")
        original_type = request.POST.get("original_type")
        office_number = request.POST.get("office_number")
        branch = request.POST.get("branch")
        Logins.objects.filter(emp_id=emp_id, emp_name=emp_name, orginal_design=orginal_design).update(
            original_type=original_type, office_number=office_number,
            branch=branch)

    return render(request, 'Employee/employee_list.html', context)


@login_required(login_url="/")
def attendance_list(request):
    context = {
        'attendance': CallReportMaster.objects.all()
    }
    if request.method == 'POST':
        date = request.POST.get('date')
    return render(request, 'Employee/attendance_list.html')


@login_required(login_url="/")
def employee_leave_list(request):
    context = {
        'daily_call': CallReportMaster.objects.all()
    }
    if request.method == 'POST':
        filter_date = request.POST.get('date')

        fdate, tdate = filter_date.split(' - ')
        fdate = datetime.strptime(str(fdate), '%m/%d/%Y').date()
        tdate = datetime.strptime(str(tdate), '%m/%d/%Y').date()

    return render(request, 'Employee/employee_leave_list.html')


@login_required(login_url="/")
def daily_call_report(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test')),
        # 'ref_type': CallReportMaster.objects.filter(Q(ref_type='ref_type'))
    }
    if 'date_d' in request.POST:
        date_d = request.POST.get('date_d')

        from_d, to_d = date_d.split(' - ')
        from_d = datetime.strptime(str(from_d), '%m/%d/%Y')
        to_d = datetime.strptime(str(to_d), '%m/%d/%Y')

        cursor = connection.cursor()

        cursor.execute(
            "SELECT `logins`.`emp_id`, `logins`.`Emp_name`, `call_report_master`.`ref_type`,"
            " `call_report_master`.`unique_id`, `call_report_master`.`name`, `call_report_master`.`camp`,"
            " `call_report_master`.`date`, `call_report_master`.`time`, `call_report_master`.`location`, "
            "`call_report_master`.`reason`, `call_report_master`.`Type`, `call_report_master`.`source`,`call_report_master`.`branch` "
            "FROM `call_report_master` INNER JOIN `logins` ON `call_report_master`.`emp_id` = `logins`.`emp_id`"
            " WHERE `call_report_master`.`date` BETWEEN '{fd}' AND '{td}' AND `call_report_master`.`branch` != 'Test' AND `logins`.`Page` = 'Marketing'"
            " ORDER BY `logins`.`Branch` ASC;".format(fd=from_d, td=to_d))

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
        'report': Logins.objects.all()
    }
    if request.method == 'POST':
        date = request.POST.get('date')

        from_d, to_d = date.split(' - ')
        from_d = datetime.strptime(str(from_d), '%m/%d/%Y')
        to_d = datetime.strptime(str(to_d), '%m/%d/%Y')

        # context['report'] = Logins.objects.filter(page='Marketing', job_status='Active', date__gte=from_d, date__lte=to_d) & Logins.objects.filter(~Q(type='Center Head', new_type__contains='Neighbourhood')) \
        #                       & Logins.objects.filter(~Q(type='Admin')).order_by('branch', 'emp_id')

        cursor = connection.cursor()
        cursor.execute(
            "SELECT `Emp_name`,`Emp_ID`,`new_type`,`Branch`,`ref_count` FROM `logins` WHERE `Page` = 'Marketing' AND"
            " `Job_Status` = 'Active'  AND `type` != 'Center Head' AND NOT `new_type`LIKE 'Neighbourhood' AND "
            "`type`!= Page ORDER BY `Branch`,`levels` ASC;;")
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
def champion(request):
    return render(request, 'call/champion.html')


@login_required(login_url="/")
def admission_breakup(request):
    if request.method == 'POST':
        date = request.POST.get('date')

    return render(request, 'call/admission_breakup.html')


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
        data.execute("SELECT `camp_create`.`sno`,`camp_create`.`empid`,`camp_create`.`empname`,`camp_create`.`state`,"
                     "`camp_create`.`zone`,`camp_create`.`area`,`camp_create`.`colonyname`,`camp_create`.`camptype`,"
                     "`camp_create`.`transid`,`camp_create`.`branch`,DATE_FORMAT(`camp_create`.`date_time`,'%d-%m-%Y') "
                     "AS date_time,`camp_create`.`status`,COUNT(`camp_reg`.`transid`) AS registration FROM `camp_create` "
                     "INNER JOIN `camp_reg` ON `camp_create`.`transid` = `camp_reg`.`transid` WHERE"
                     " DATE_FORMAT(`camp_create`.`date_time`,'%Y-%m-%d') BETWEEN '2019-01-01' AND '2023-01-01' GROUP BY "
                     "`camp_reg`.`transid` ORDER BY `camp_create`.`date_time` ASC;".format(
            fd=fdate, td=tdate))

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
                "SELECT `invoice_no`, `patient_name`, DATE_FORMAT(`visit_data`,'%d-%b-%Y') AS adate,DATE_FORMAT(`invoice_date`,'%d-%b-%Y') AS ddate, `isbilldone` "
                "AS admissionstatus, `patient_data`.`referralmobile` as referralmobile, `patient_data`.`branch` as branch,`patient_data`.`referraldepartment` as department,"
                " `patient_data`.`organization` organization, `referralstatus`, `Admissiontype`, UPPER(`doctor_agent_list`.`agent_name`) AS referralname, "
                "`referraldepartment`, `doctor_agent_list`.`mobile` as referralmobile, `referralremarks`, `paymentmode`, CONCAT('''',`doctor_agent_list`.`bank_ac`) "
                "as accnumber,`doctor_agent_list`.`ifsc` as ifsccode, `doctor_agent_list`.`pancard` as pancard, `clashstatus`,DATE_FORMAT(`referralcreatedon`,'%d-%b-%Y %H:%i:%s') "
                "AS referralcreatedon, `referralcreatedby`, `cluster_approval`,`cluster_approved_on`,(`phar_consum_billamount`) AS billamount, UPPER(`UCID`) AS referralcode,`referralamount`,`utr_no`,"
                "DATE(`utr_on`) FROM `patient_data` INNER JOIN `doctor_agent_list` ON `patient_data`.`UCID`=`doctor_agent_list`.`unique_id` WHERE `patient_data`.`branch` != 'Test' "
                "AND `cluster_approval` = 'Approved' AND `doctor_agent_list`.`bank_ac`!='' AND `doctor_agent_list`.`bank_ac`!='null' AND `utr_no`!='NEFT Return'"
                " AND `utr_no`!='Wrong Bank Details' AND DATE(`cluster_approved_on`) BETWEEN  '{fd}' AND '{td}' GROUP BY `invoice_no` ORDER BY `patient_data`.`branch`,"
                "`patient_data`.`utr_on`,`patient_data`.`discharge_datetime` ASC".format(fd=fr_date, td=tm_date))
        else:
            cursor.execute(
                "SELECT `invoice_no`, `patient_name`, DATE_FORMAT(`visit_data`,'%d-%b-%Y') AS adate,DATE_FORMAT(`invoice_date`,'%d-%b-%Y') AS ddate, `isbilldone` "
                "AS admissionstatus, `patient_data`.`referralmobile` as referralmobile, `patient_data`.`branch` as branch,`patient_data`.`referraldepartment` "
                "as department,`patient_data`.`organization` organization, `referralstatus`, `Admissiontype`, UPPER(`doctor_agent_list`.`agent_name`) AS referralname,"
                " `referraldepartment`, `doctor_agent_list`.`mobile` as referralmobile, `referralremarks`, `paymentmode`, CONCAT('''',`doctor_agent_list`.`bank_ac`) "
                "as accnumber,`doctor_agent_list`.`ifsc` as ifsccode, `doctor_agent_list`.`pancard` as pancard, `clashstatus`,"
                "DATE_FORMAT(`referralcreatedon`,'%d-%b-%Y %H:%i:%s') AS referralcreatedon, `referralcreatedby`, `cluster_approval`, `cluster_approved_on`,(`phar_consum_billamount`) "
                "AS billamount, UPPER(`UCID`) AS referralcode,`referralamount`,`utr_no`, DATE(`utr_on`) FROM `patient_data` INNER JOIN `doctor_agent_list` ON"
                " `patient_data`.`UCID`=`doctor_agent_list`.`unique_id` WHERE `patient_data`.`branch` != 'Test' AND `cluster_approval` = 'Approved' AND"
                " `doctor_agent_list`.`bank_ac`!='' AND `doctor_agent_list`.`bank_ac`!='null'  AND `utr_no`!='NEFT Return' AND `utr_no`!='Wrong Bank Details' AND"
                " DATE(`cluster_approved_on`) BETWEEN  '{fd}' AND '{td}' GROUP BY `invoice_no` ORDER BY `patient_data`.`branch`, `patient_data`.`utr_on`,"
                "`patient_data`.`discharge_datetime` ASC".format(fd=fr_date, td=tm_date, bn=branch_name))
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
    if request.method == 'POST':
        form = Upload(request.POST, request.FILES)
        if form.is_valid():
            newdoc = UtrUpdate(upload_csv_file=request.FILES.get('upload_csv_file'))
            newdoc.save()
            messages.success(request, "upload successfully....")
        else:
            messages.error(request, "failed to update")
            return redirect('utr_update')
    return render(request, 'utr.html')


@login_required(login_url="/")
def utr_csv(request):
    res = HttpResponse(content_type='text/csv')
    res['Content-Disposition'] = 'attachment; filename="Utr_Updated_file.csv"'
    writer = csv.writer(res)
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


class PDFS(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 10)

        self.ln(15)

    def footer(self):
        self.set_y(-37)
        self.line(10, 300, 220, 300)
        self.cell(1, 7, f"Page No. {self.page_no()}", align="c")


def pdf(request):
    # emp = DoctorAgentList.objects.all()

    pdf = PDFS()
    pdf.add_page()
    pdf.set_fill_color(240, 200, 185)
    pdf.title = "Payslip"
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(1, 7, "", 0, 0)
    pdf.cell(100, 8, "", 1, 0)
    pdf.cell(50, 8, "", 1, 0)
    pdf.cell(40, 8, "Growth%", 1, 1, 'C')
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(1, 6, "", 0, 0)
    pdf.set_fill_color(240, 200, 185)
    pdf.cell(10, 7, "S.NO", 1, 0, 'C', fill=True)
    pdf.cell(20, 7, "Unit", 1, 0, 'C', fill=True)
    pdf.cell(20, 7, "Target", 1, 0, 'C', fill=True)
    pdf.cell(25, 7, "Admissions", 1, 0, 'C', fill=True)
    pdf.cell(25, 7, "Percentage ", 1, 0, 'C', fill=True)
    pdf.cell(25, 7, "Admissions", 1, 0, 'C', fill=True)
    pdf.cell(25, 7, "Percentage", 1, 0, 'C', fill=True)
    pdf.cell(40, 7, "From", 1, 1)
    pdf.cell(1, 6, "", 0, 0)

    pdf.set_fill_color(210, 100, 135)
    pdf.cell(10, 6, "", 1, 0)
    pdf.cell(20, 6, "", 1, 0)
    pdf.set_fill_color(240, 245, 200)
    pdf.cell(20, 6, "", 1, 0, fill=True)
    pdf.cell(25, 6, "", 1, 0, fill=True)
    pdf.cell(25, 6, "", 1, 0, fill=True)
    pdf.set_fill_color(250, 195, 230)
    pdf.cell(25, 6, "", 1, 0, fill=True)
    pdf.cell(25, 6, "", 1, 0, fill=True)
    pdf.cell(40, 6, "", 1, 1)
    pdf.cell(1, 6, "", 0, 0)

    pdf.cell(30, 6, "Grand Total", 1, 0)
    pdf.set_fill_color(240, 245, 200)
    pdf.cell(20, 6, "", 1, 0, fill=True)
    pdf.cell(25, 6, "", 1, 0, fill=True)
    pdf.cell(25, 6, "", 1, 0, fill=True)
    pdf.set_fill_color(250, 195, 230)
    pdf.cell(25, 6, "", 1, 0, fill=True)
    pdf.cell(25, 6, "", 1, 0, fill=True)
    pdf.cell(40, 6, "", 1, 1)
    pdf.cell(1, 6, "", 0, 0)
    pdf.output("svs.pdf")
    filepath = os.path.join('svs.pdf')
    return FileResponse(open(filepath, 'rb'))

@login_required(login_url="/")
def cash_payment(request):
    context = {
        'branch': BranchListDum.objects.filter(~Q(branch_name='Test'))

    }
    if request.method == "POST":
        branch = request.POST.get('branch')

        if branch == 'All':
            context['cash'] = PatientData.objects.filter(paymentmode='Cash')
        else:
            context['cash'] = PatientData.objects.filter(paymentmode='Cash', branch=branch)

    return render(request, 'cash_payment.html', context)


@csrf_exempt
def functional_approval_list(request):
    context = {
        'branch_name': BranchListDum.objects.filter(~Q(branch_name='Test')),
        'cluster': PatientData.objects.filter(chapproval="Yes")
    }
    if 'approval_value' in request.POST:
        data_list = request.POST.get('approval_value')
        print(data_list)
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
        return redirect('pending_payment')

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
        return redirect('reject')

    elif request.method == "POST":
        branch_name = request.POST.get('branch')
        # f_date = request.POST.get('date')
        #
        # from_date, to_date = f_date.split(' - ')
        # from_date = datetime.strptime(str(from_date), '%m/%d/%Y').date()
        # to_date = datetime.strptime(str(to_date), '%m/%d/%Y').date()

        if branch_name == 'All':
            context['cluster'] = PatientData.objects.filter(referralstatus='Yes', chapproval="")
        else:
            context['cluster'] = PatientData.objects.filter(referralstatus='Yes', branch=branch_name, chapproval="")

    #     approve = request.GET.get('approve')
    #     # data = PatientData.objects.get(sno=approve)
    #     # data.chapproval = "Yes"
    #     # data.chapproval_by = request.user.emp_id
    #     # data.ch_approved_on = timezone.now()
    #     # data.save()

    # if 'approve' in request.GET:
    #     approve = request.GET.get('approve')
    #     # data = PatientData.objects.get(sno=approve)
    #     # data.chapproval = "Yes"
    #     # data.chapproval_by = request.user.emp_id
    #     # data.ch_approved_on = timezone.now()
    #     # data.save()
    #
    #     PatientData.objects.filter(sno=approve).update(chapproval="approved", chapproval_by=request.user.emp_id,
    #                                                    ch_approved_on=timezone.now())
    #     messages.success(request, 'Approved successfully')
    #     return redirect('pending_payment')
    #
    # if 'reject_id' in request.GET and request.is_ajax():
    #     reject = request.GET.get('reject_id')
    #     # data = PatientData.objects.get(sno=approve)
    #     # data.chapproval = "Yes"
    #     # data.chapproval_by = request.user.emp_id
    #     # data.ch_approved_on = timezone.now()
    #     # data.save()
    #
    #     PatientData.objects.filter(sno=reject).update(chapproval="No", chapproval_by=request.user.emp_id,
    #                                                   ch_approved_on=timezone.now())
    #     # messages.success(request, 'Approved successfully')
    #     return JsonResponse({"success": True})

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


def delete_data(request):
    return None

@login_required(login_url="/")
def edit_list(request):
    if request.method == "POST":
        data_list = request.POST.get('transfer_id')
        print(request.POST)
        print(data_list)
        # for i in data_list:
        #     data = PatientData.objects.filter(sno=i)
        #     data.delete()
        #     print(i)
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
