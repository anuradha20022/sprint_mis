# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AbcReport(models.Model):
    sno = models.IntegerField(primary_key=True)
    emp_id = models.TextField()
    emp_name = models.TextField()
    totalrefer_count = models.TextField()
    atotal = models.TextField()
    btotal = models.TextField()
    ctotal = models.TextField()
    av1 = models.TextField()
    av2 = models.TextField()
    av3 = models.TextField()
    bv1 = models.TextField()
    bv2 = models.TextField()
    bv3 = models.IntegerField()
    cv1 = models.TextField()
    cv2 = models.TextField()
    cv3 = models.TextField()
    anv = models.TextField()
    bnv = models.TextField()
    cnv = models.TextField()
    date = models.CharField(max_length=50)
    date_time = models.DateTimeField()
    branch = models.TextField()

    class Meta:
        managed = False
        db_table = 'abc_report'


class AdmissionDummyTable(models.Model):
    sno = models.AutoField(primary_key=True)
    branch = models.CharField(max_length=50)
    plan = models.IntegerField()
    adm = models.IntegerField()
    ach = models.IntegerField()
    gap = models.IntegerField()
    mtd = models.IntegerField()
    clustername = models.TextField()
    clustername2 = models.CharField(max_length=50)
    cluster_empid = models.CharField(max_length=50)
    cname = models.CharField(max_length=50)
    view_branch = models.CharField(max_length=30)
    status = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'admission_dummy_table'


class AdmissionType(models.Model):
    sno = models.AutoField(primary_key=True)
    type = models.TextField()
    catogery = models.TextField()
    status = models.TextField()

    class Meta:
        managed = False
        db_table = 'admission_type'


class AndroidPermissions(models.Model):
    sno = models.AutoField(primary_key=True)
    menu = models.CharField(max_length=50)
    submenu = models.CharField(max_length=100)
    titlename = models.CharField(max_length=50)
    dashboardtitle = models.CharField(max_length=60)
    ioscontrollers = models.CharField(max_length=90)
    packagename = models.CharField(max_length=100)
    classname = models.CharField(max_length=60)
    classtype = models.CharField(max_length=50)
    substatus = models.CharField(max_length=10)
    d_icons = models.CharField(db_column='d-icons', max_length=50)  # Field renamed to remove unsuitable characters.
    side_icons = models.CharField(db_column='side-icons', max_length=50)  # Field renamed to remove unsuitable characters.
    status = models.TextField()

    class Meta:
        managed = False
        db_table = 'android_permissions'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group_id', 'permission_id'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type_id = models.IntegerField()
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type_id', 'codename'),)


class BankDetails(models.Model):
    sno = models.AutoField(primary_key=True)
    bankid = models.CharField(max_length=20)
    branch = models.CharField(max_length=30)
    employee_name = models.TextField()
    bankname = models.TextField()
    ifsccode = models.TextField()
    branchname = models.TextField()
    spoc = models.TextField()
    designation = models.TextField()
    contact = models.BigIntegerField()
    fulladdress = models.TextField()
    remarks = models.TextField()
    location = models.TextField()
    geolocation = models.TextField()
    area = models.TextField()
    city = models.TextField()
    state = models.TextField()
    pincode = models.TextField()
    cempid = models.CharField(max_length=10)
    cdate = models.DateField()
    ctime = models.TimeField()
    status = models.TextField()

    class Meta:
        managed = False
        db_table = 'bank_details'


class BankLogsNew(models.Model):
    sno = models.AutoField(primary_key=True)
    ucid = models.CharField(max_length=20, db_collation='latin1_swedish_ci')
    empid = models.CharField(max_length=10, db_collation='latin1_swedish_ci')
    pan = models.CharField(max_length=20, db_collation='latin1_swedish_ci')
    account = models.CharField(max_length=25, db_collation='latin1_swedish_ci')
    ifsc = models.CharField(max_length=20, db_collation='latin1_swedish_ci')
    branchname = models.CharField(max_length=25, db_collation='latin1_swedish_ci')
    createdon = models.DateTimeField()
    remarks = models.CharField(max_length=100, blank=True, null=True)
    bankholdername = models.CharField(max_length=60, blank=True, null=True)
    panattachments = models.CharField(max_length=200)
    bankattachments = models.CharField(max_length=200)
    bank_upd_remarks = models.CharField(max_length=150, blank=True, null=True)
    approval_remarks = models.CharField(max_length=100, blank=True, null=True)
    approval_data = models.CharField(max_length=60, blank=True, null=True)
    upino = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'bank_logs_new'


class Banner(models.Model):
    sno = models.AutoField(primary_key=True)
    name = models.TextField()
    image = models.CharField(max_length=300)

    class Meta:
        managed = False
        db_table = 'banner'


class BranchList(models.Model):
    id = models.IntegerField()
    branch_name = models.CharField(max_length=50)
    status = models.IntegerField()
    branch_code = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'branch_list'


class BranchListDum(models.Model):
    id = models.IntegerField(primary_key=True)
    branch_name = models.CharField(max_length=50)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'branch_list_dum'


class CallReportMaster(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    emp_id = models.CharField(max_length=20)
    ref_type = models.TextField()
    unique_id = models.TextField()
    name = models.TextField()
    design = models.TextField()
    contact = models.TextField()
    camp = models.TextField()
    camp_details = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.TextField()
    latitude = models.TextField()
    longitude = models.TextField()
    area = models.TextField()
    city = models.TextField()
    state = models.TextField()
    pincode = models.CharField(max_length=50)
    district = models.TextField()
    station = models.TextField()
    branch = models.TextField()
    source = models.TextField()
    attendance = models.TextField()
    reason = models.TextField()
    type = models.TextField(db_column='Type')  # Field name made lowercase.
    ldate = models.DateField()
    category = models.CharField(max_length=1)
    status = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'call_report_master'


class CampCreate(models.Model):
    sno = models.AutoField(primary_key=True)
    empid = models.TextField()
    empname = models.TextField()
    state = models.TextField()
    zone = models.TextField()
    area = models.TextField()
    colonyname = models.CharField(max_length=100)
    camptype = models.TextField()
    transid = models.CharField(max_length=15)
    branch = models.TextField()
    date_time = models.DateTimeField()
    status = models.TextField()

    class Meta:
        managed = False
        db_table = 'camp_create'


class CampGuestLogin(models.Model):
    sno = models.AutoField(primary_key=True)
    name = models.TextField()
    mobile = models.BigIntegerField()
    transid = models.CharField(max_length=16)
    date_time = models.DateTimeField()
    status = models.TextField()
    accesskey = models.CharField(max_length=50)
    branch = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'camp_guest_login'


class CampReg(models.Model):
    sno = models.AutoField(primary_key=True)
    transid = models.CharField(max_length=16)
    patient_name = models.TextField()
    age = models.IntegerField()
    mobile = models.BigIntegerField()
    qualification = models.CharField(max_length=50)
    date_time = models.DateTimeField()
    submit_person = models.TextField()
    ccemp = models.CharField(max_length=100)
    ccremarks = models.TextField()
    cccreatedon = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'camp_reg'


class Category(models.Model):
    sno = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    leave_names = models.CharField(max_length=50)
    camp = models.TextField()

    class Meta:
        managed = False
        db_table = 'category'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type_id = models.IntegerField(blank=True, null=True)
    user_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DoctorAgentList(models.Model):
    sno = models.AutoField(primary_key=True)
    emp_id = models.CharField(max_length=20)
    unique_id = models.CharField(max_length=20)
    agent_type = models.TextField()
    agent_name = models.TextField()
    reg_no = models.TextField()
    designation = models.TextField()
    department = models.TextField()
    mobile = models.BigIntegerField()
    landline = models.TextField()
    company = models.TextField()
    pancard = models.TextField()
    bank_name = models.CharField(max_length=80)
    bankac_holdername = models.CharField(max_length=50)
    bank_branch_name = models.CharField(max_length=80)
    bank_ac = models.TextField()
    ifsc = models.TextField()
    email = models.CharField(max_length=100)
    location = models.TextField()
    latitude = models.TextField()
    longitude = models.TextField()
    area = models.TextField()
    city = models.CharField(max_length=250)
    district = models.TextField()
    state = models.CharField(max_length=250)
    pincode = models.CharField(max_length=50)
    date = models.DateField()
    time = models.TimeField()
    branch = models.TextField()
    source = models.TextField()
    type = models.TextField(db_column='Type')  # Field name made lowercase.
    url = models.TextField()
    r_status = models.TextField()
    category = models.CharField(max_length=1)
    last_per_referral = models.IntegerField()
    last_pername_referral = models.CharField(max_length=10)
    include_phar_consum = models.CharField(max_length=10)
    bank_details_updatedby = models.CharField(max_length=30)
    bankattachments = models.CharField(max_length=50)
    panattachments = models.CharField(max_length=50)
    audit_stat = models.CharField(max_length=50)
    upino = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'doctor_agent_list'


class Dummy(models.Model):
    oldemp = models.CharField(max_length=100, blank=True, null=True)
    newemp = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dummy'


class DummyDoctorAgentList(models.Model):
    sno = models.IntegerField(blank=True, null=True)
    emp_id = models.CharField(max_length=20)
    unique_id = models.CharField(max_length=20)
    r_status = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'dummy_doctor_agent_list'


class HomeSampleVisits(models.Model):
    sno = models.AutoField(primary_key=True)
    empid = models.CharField(max_length=20)
    branch = models.CharField(max_length=20)
    patient_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=20)
    age = models.IntegerField()
    remarks = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    location = models.TextField()
    created_on = models.DateTimeField()
    created_by = models.CharField(max_length=20)
    modified_on = models.DateTimeField()
    modified_by = models.CharField(max_length=20)
    source = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'home_sample_visits'


class LoginPermissions(models.Model):
    sno = models.IntegerField()
    designation = models.CharField(max_length=50)
    menu = models.CharField(max_length=60)
    submenu = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'login_permissions'


class Logins(models.Model):
    emp_name = models.CharField(db_column='Emp_name', max_length=30, blank=True, null=True)  # Field name made lowercase.
    personal_number = models.BigIntegerField(db_column='Personal_Number')  # Field name made lowercase.
    office_number = models.BigIntegerField(db_column='Office_number')  # Field name made lowercase.
    designation = models.TextField(db_column='Designation')  # Field name made lowercase.
    emp_id = models.CharField(db_column='Emp_ID', max_length=20)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=50)  # Field name made lowercase.
    branch = models.TextField(db_column='Branch')  # Field name made lowercase.
    old_branch = models.CharField(max_length=50)
    page = models.TextField(db_column='Page')  # Field name made lowercase.
    orginal_design = models.TextField(db_column='Orginal_Design')  # Field name made lowercase.
    original_type = models.TextField(db_column='Original_Type')  # Field name made lowercase.
    last_location = models.CharField(db_column='Last_Location', max_length=50)  # Field name made lowercase.
    last_loc_datetime = models.DateTimeField(blank=True, null=True)
    date = models.DateField(db_column='Date')  # Field name made lowercase.
    time = models.TimeField(db_column='Time')  # Field name made lowercase.
    head = models.TextField(db_column='Head')  # Field name made lowercase.
    type = models.CharField(max_length=50)
    join_date = models.DateField(db_column='Join_Date')  # Field name made lowercase.
    visibility = models.TextField(db_column='Visibility')  # Field name made lowercase.
    job_status = models.CharField(db_column='Job_Status', max_length=50)  # Field name made lowercase.
    levels = models.IntegerField()
    bank_acc = models.TextField()
    ifsc = models.CharField(max_length=20)
    pan = models.CharField(max_length=20)
    allow = models.IntegerField()
    img_link = models.CharField(max_length=300)
    model = models.CharField(max_length=50)
    version = models.CharField(max_length=50)
    firebase_token = models.CharField(max_length=3000)
    deviceid = models.CharField(max_length=50)
    accesskey = models.CharField(max_length=100)
    state = models.TextField()
    branch_access = models.TextField()
    new_type = models.TextField()
    ref_count = models.IntegerField()
    mpassword = models.CharField(max_length=100, blank=True, null=True)
    androidpermissions = models.CharField(max_length=100, blank=True, null=True)
    inactive_dt = models.DateField(blank=True, null=True)
    androidsubmenu = models.CharField(max_length=100, blank=True, null=True)
    loginstatus = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'logins'


class MisStatus(models.Model):
    s_no = models.IntegerField(db_column='s.no')  # Field renamed to remove unsuitable characters.
    header = models.CharField(max_length=200)
    msg = models.CharField(max_length=3000)
    status = models.CharField(max_length=50)
    link = models.CharField(max_length=250)
    target_link = models.TextField()
    action = models.CharField(max_length=50)
    date = models.DateTimeField()
    app = models.TextField()
    catogery = models.TextField()
    share = models.TextField()

    class Meta:
        managed = False
        db_table = 'mis_status'


class MyFifty(models.Model):
    sno = models.AutoField(primary_key=True)
    emp_id = models.CharField(max_length=35)
    ucid = models.CharField(max_length=25)
    doctor_name = models.CharField(max_length=35)
    designation = models.CharField(max_length=20)
    mobile = models.BigIntegerField()
    area = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'my_fifty'


class OwnershipDummy(models.Model):
    s_no = models.IntegerField(db_column='s.no')  # Field renamed to remove unsuitable characters.
    empid = models.CharField(max_length=100)
    ucid = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'ownership_dummy'


class PatientData(models.Model):
    sno = models.AutoField(primary_key=True)
    ipno = models.CharField(unique=True, max_length=50)
    umr = models.CharField(max_length=50)
    pname = models.TextField()
    adate = models.DateField()
    time = models.TimeField()
    isbilldone = models.CharField(max_length=15)
    mobile = models.BigIntegerField()
    alt_mobile = models.BigIntegerField()
    branch = models.CharField(max_length=20)
    admntype = models.TextField()
    consultant = models.CharField(max_length=80)
    department = models.TextField()
    wardname = models.CharField(max_length=50)
    deptcode = models.CharField(max_length=50)
    organization = models.CharField(max_length=80)
    admpurpose = models.CharField(max_length=50)
    last_login = models.DateTimeField()
    discharge_datetime = models.DateTimeField()
    whatsapstatus = models.TextField()
    ip_no = models.CharField(max_length=100)
    os_version = models.CharField(max_length=200)
    model = models.CharField(max_length=200)
    udid = models.CharField(max_length=200)
    accesskey = models.TextField()
    token = models.TextField()
    referralstatus = models.TextField()
    admissiontype = models.TextField(db_column='Admissiontype')  # Field name made lowercase.
    referralname = models.TextField()
    referraldepartment = models.TextField()
    referralmobile = models.TextField()
    referralremarks = models.TextField()
    referralpercentage = models.FloatField()
    referralpercentagename = models.CharField(max_length=10)
    referral_cal_by = models.CharField(max_length=50)
    referral_cal_on = models.DateTimeField()
    paymentmode = models.CharField(max_length=25)
    acc_holdername = models.CharField(max_length=80)
    accnumber = models.TextField()
    ifsccode = models.TextField()
    pancard = models.TextField()
    clashstatus = models.TextField()
    clashremarks = models.TextField()
    referralcreatedon = models.DateTimeField()
    referralcreatedby = models.TextField()
    mhapproval = models.TextField()
    mh_approved_on = models.DateTimeField()
    chapproval = models.TextField()
    chapproval_by = models.CharField(max_length=50)
    ch_approved_on = models.DateTimeField()
    billamount = models.FloatField()
    referralamount = models.FloatField()
    referralmode = models.TextField()
    assign_empid = models.TextField()
    referralcode = models.TextField()
    discounts = models.FloatField()
    netbill = models.IntegerField()
    phar_consum_billamount = models.FloatField()
    consultantentry = models.TextField()
    consultantremarks = models.TextField()
    doctor_dateon = models.DateTimeField()
    ucid = models.CharField(db_column='UCID', max_length=50)  # Field name made lowercase.
    cluster_approval = models.TextField()
    cluster_approval_by = models.CharField(max_length=50)
    cluster_approved_on = models.DateTimeField()
    fh_approval = models.CharField(max_length=35)
    fh_by = models.CharField(max_length=30)
    fh_on = models.DateTimeField()
    referral_type = models.TextField()
    marketing_executive = models.CharField(db_column='Marketing_executive', max_length=50)  # Field name made lowercase.
    sms_jobid = models.CharField(db_column='sms_jobId', max_length=20)  # Field name made lowercase.
    psms_status = models.TextField()
    dsms_iobid = models.IntegerField()
    dsms_status = models.TextField()
    api_status = models.TextField()
    orgconcession = models.FloatField()
    labsamount = models.FloatField()
    lastinsert_on = models.DateTimeField()
    last_discharge_time = models.DateTimeField()
    utr_no = models.CharField(max_length=300)
    utrcreated_by = models.CharField(max_length=50)
    utr_on = models.DateTimeField()
    remarks = models.CharField(max_length=50)
    dummy_status = models.CharField(max_length=50)
    discharge_status = models.CharField(max_length=50)
    branch_cluster = models.CharField(max_length=30)
    old_status = models.IntegerField()
    new_referral_status = models.IntegerField()
    panattachments = models.CharField(max_length=200, blank=True, null=True)
    bankattachments = models.CharField(max_length=200, blank=True, null=True)
    ref_country = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'patient_data'


class PatientDataOlddata(models.Model):
    sno = models.AutoField(primary_key=True)
    branch = models.CharField(max_length=40)
    facility_name = models.CharField(max_length=50)
    registration_number = models.CharField(max_length=50)
    encounterno = models.CharField(max_length=30)
    pname = models.CharField(max_length=150)
    age_gender = models.CharField(db_column='age/gender', max_length=15)  # Field renamed to remove unsuitable characters.
    bill_location = models.CharField(max_length=50)
    invoice_no = models.CharField(max_length=30)
    invoice_date = models.DateTimeField()
    visit_data = models.DateTimeField()
    serviceid = models.CharField(max_length=30)
    item_cate = models.CharField(max_length=20)
    item_sub_cate = models.CharField(max_length=20)
    item_no = models.CharField(max_length=25)
    billing_group = models.CharField(max_length=30)
    department_name = models.CharField(max_length=30)
    sub_department_name = models.CharField(max_length=30)
    service_name = models.TextField()
    under_package = models.CharField(max_length=20)
    package_name = models.CharField(max_length=20)
    advising_doctor = models.CharField(max_length=50)
    advising_dept = models.CharField(max_length=30)
    advising_coe = models.CharField(max_length=10)
    rendering_doctor = models.CharField(max_length=25)
    rendering_specialisation = models.CharField(max_length=25)
    rendering_department = models.CharField(max_length=25)
    rendering_coe = models.CharField(max_length=25)
    revenue_doctor = models.CharField(max_length=50)
    revenue_spec = models.CharField(max_length=40)
    revenue_dept = models.CharField(max_length=25)
    revenue_coe = models.CharField(max_length=15)
    company_name = models.CharField(max_length=50)
    company_type = models.CharField(max_length=50)
    payment_type = models.CharField(max_length=50)
    service_unit = models.FloatField()
    serviceamount = models.FloatField()
    servicediscount = models.FloatField()
    itemcostprice = models.FloatField()
    totalcostprice = models.FloatField()
    grossamount = models.FloatField()
    discounts = models.FloatField()
    patshare = models.FloatField()
    netbill = models.FloatField()
    deductable = models.FloatField()
    coinsurance = models.FloatField()
    copay = models.FloatField()
    spondiscount = models.FloatField()
    patdiscount = models.FloatField()
    settlementtype = models.CharField(max_length=50)
    tax_percentage = models.IntegerField()
    vatamount = models.FloatField()
    taxnetamount = models.FloatField()
    discauthremark = models.TextField()
    admissionbillingcategory = models.CharField(max_length=30)
    servicebillingcategory = models.CharField(max_length=30)
    servicebedcategory = models.CharField(max_length=30)
    nationality = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    country = models.CharField(max_length=30)
    leadsource = models.CharField(max_length=50)
    referralsourcename = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    invoiceid = models.CharField(max_length=20)
    activeinvoiceid = models.CharField(max_length=20)
    servicetype = models.CharField(max_length=20)
    network_sponsor = models.CharField(max_length=20)
    moudiscount = models.FloatField()
    insuranceapproved = models.IntegerField()
    primarybillcode = models.CharField(db_column='PrimaryBillCode', max_length=40)  # Field name made lowercase.
    uploadedon = models.DateTimeField()
    referral_type = models.CharField(max_length=25)
    referralname = models.CharField(max_length=150)
    ucid = models.CharField(db_column='UCID', max_length=40)  # Field name made lowercase.
    admntype = models.CharField(max_length=20)
    referralamount = models.FloatField()
    referralpercentage = models.FloatField()
    referralpercentagename = models.CharField(max_length=20)
    referralstatus = models.CharField(max_length=30)
    referralcreatedon = models.DateTimeField()
    referralcreatedby = models.CharField(max_length=30)
    ucidcreatedon = models.DateTimeField()
    ucidcreatedby = models.CharField(max_length=20)
    marketing_executive = models.CharField(db_column='Marketing_executive', max_length=100)  # Field name made lowercase.
    chapproval = models.TextField()
    chapproval_by = models.CharField(max_length=50)
    ch_approved_on = models.DateTimeField()
    acc_holdername = models.CharField(max_length=50)
    accnumber = models.CharField(max_length=20)
    ifsccode = models.CharField(max_length=25)
    pancard = models.CharField(max_length=25)
    cluster_approval = models.CharField(max_length=100, blank=True, null=True)
    referral_cal_by = models.CharField(max_length=100, blank=True, null=True)
    discharge_datetime = models.DateTimeField(blank=True, null=True)
    isbilldone = models.CharField(max_length=100, blank=True, null=True)
    utr_no = models.CharField(max_length=100, blank=True, null=True)
    admissiontype = models.CharField(db_column='Admissiontype', max_length=100, blank=True, null=True)  # Field name made lowercase.
    referraldepartment = models.CharField(max_length=100, blank=True, null=True)
    referralmobile = models.CharField(max_length=100, blank=True, null=True)
    referralremarks = models.CharField(max_length=100, blank=True, null=True)
    paymentmode = models.CharField(max_length=100, blank=True, null=True)
    clashstatus = models.CharField(max_length=100, blank=True, null=True)
    assign_empid = models.CharField(max_length=100, blank=True, null=True)
    referralmode = models.CharField(max_length=100, blank=True, null=True)
    organization = models.CharField(max_length=100, blank=True, null=True)
    phar_consum_billamount = models.CharField(max_length=100, blank=True, null=True)
    consultantentry = models.CharField(max_length=100, blank=True, null=True)
    consultantremarks = models.CharField(max_length=100, blank=True, null=True)
    utr_on = models.DateTimeField(blank=True, null=True)
    cluster_approved_on = models.DateTimeField(blank=True, null=True)
    cluster_approval_by = models.CharField(max_length=100, blank=True, null=True)
    upinumber = models.CharField(max_length=100, blank=True, null=True)
    patient_sanharsno = models.IntegerField()
    new_referral_status = models.IntegerField()
    fh_approval = models.CharField(max_length=50)
    fh_by = models.CharField(max_length=50)
    fh_on = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'patient_data_olddata'


class PatientReferrals(models.Model):
    s_no = models.AutoField(db_column='s.no', primary_key=True)  # Field renamed to remove unsuitable characters.
    emp_id = models.TextField(db_column='Emp_ID')  # Field name made lowercase.
    emp_name = models.TextField()
    branch = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    patient_name = models.TextField(db_column='Patient_Name')  # Field name made lowercase.
    uniquecode = models.CharField(max_length=50)
    doctor_no = models.BigIntegerField(db_column='Doctor_NO')  # Field name made lowercase.
    sources = models.CharField(db_column='Sources', max_length=50)  # Field name made lowercase.
    treatment = models.TextField(db_column='Treatment')  # Field name made lowercase.
    location = models.TextField()
    area = models.CharField(db_column='Area', max_length=250)  # Field name made lowercase.
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    pincode = models.CharField(db_column='pinCode', max_length=50)  # Field name made lowercase.
    latitude = models.TextField(db_column='Latitude')  # Field name made lowercase.
    longitude = models.TextField(db_column='Longitude')  # Field name made lowercase.
    date = models.DateField(db_column='Date')  # Field name made lowercase.
    time = models.TimeField(db_column='Time')  # Field name made lowercase.
    source = models.TextField(db_column='Source')  # Field name made lowercase.
    ip_no = models.CharField(db_column='IP_NO', max_length=15)  # Field name made lowercase.
    status = models.TextField(db_column='Status')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'patient_referrals'


class PatientReferralsLogs(models.Model):
    sno = models.AutoField(primary_key=True)
    ipno = models.CharField(max_length=50)
    ucid = models.CharField(max_length=50)
    referral_doctorname = models.CharField(max_length=60)
    agent_type = models.CharField(max_length=50)
    category = models.CharField(max_length=3)
    referrralstatus = models.CharField(max_length=20)
    executivename = models.CharField(max_length=35)
    empid = models.CharField(max_length=35)
    remarks = models.CharField(max_length=100)
    created_by = models.CharField(max_length=50)
    created_by_name = models.CharField(max_length=50)
    created_designation = models.CharField(max_length=50)
    created_on = models.DateTimeField()
    source = models.CharField(max_length=50)
    ref_sno = models.IntegerField()
    status = models.CharField(max_length=50)
    referral_amount = models.FloatField()
    referral_percentage = models.FloatField()
    referral_per_type = models.CharField(max_length=50)
    paymentmode = models.CharField(max_length=50)
    include_pharm = models.CharField(max_length=50)
    item_deletestatus = models.IntegerField()
    modified_by = models.CharField(max_length=50)
    modified_on = models.DateTimeField()
    utr_no = models.CharField(max_length=300)
    referral_mobile = models.BigIntegerField()
    bank_ac = models.CharField(max_length=20)
    ifsc = models.CharField(max_length=20)
    pancard = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'patient_referrals_logs'


class PatientReferralsNew(models.Model):
    sno = models.AutoField(primary_key=True)
    pname = models.TextField(db_collation='latin1_swedish_ci')
    pmobile = models.BigIntegerField()
    executive_name = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    empid = models.TextField(db_collation='latin1_swedish_ci')
    ref_doc_ucid = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    ref_doc_name = models.CharField(max_length=100, db_collation='latin1_swedish_ci')
    category = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    agent_type = models.CharField(max_length=30, db_collation='latin1_swedish_ci')
    consultant = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    speciality = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    remarks = models.CharField(max_length=100, db_collation='latin1_swedish_ci')
    ipno = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    mapped_by = models.CharField(max_length=40)
    mapped_on = models.DateTimeField()
    status = models.TextField(db_collation='latin1_swedish_ci')
    created_by = models.CharField(max_length=40, db_collation='utf8mb4_unicode_ci')
    created_on = models.DateTimeField()
    branch = models.CharField(max_length=50)
    agent_mobile = models.BigIntegerField()
    executive_mobile = models.BigIntegerField()
    paymentmode = models.CharField(max_length=50)
    source = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'patient_referrals_new'


class Patientdatasanhar(models.Model):
    sno = models.AutoField(primary_key=True)
    facility_name = models.CharField(max_length=50)
    registration_number = models.CharField(max_length=50)
    encounterno = models.CharField(max_length=30)
    patient_name = models.CharField(max_length=150)
    age_gender = models.CharField(db_column='age/gender', max_length=15)  # Field renamed to remove unsuitable characters.
    bill_location = models.CharField(max_length=50)
    invoice_no = models.CharField(max_length=30)
    invoice_date = models.DateTimeField()
    visit_data = models.DateTimeField()
    serviceid = models.CharField(max_length=30)
    item_cate = models.CharField(max_length=20)
    item_sub_cate = models.CharField(max_length=20)
    item_no = models.CharField(max_length=25)
    billing_group = models.CharField(max_length=30)
    department_name = models.CharField(max_length=30)
    sub_department_name = models.CharField(max_length=30)
    service_name = models.TextField()
    under_package = models.CharField(max_length=20)
    package_name = models.CharField(max_length=20)
    advising_doctor = models.CharField(max_length=50)
    advising_dept = models.CharField(max_length=30)
    advising_coe = models.CharField(max_length=10)
    rendering_doctor = models.CharField(max_length=25)
    rendering_specialisation = models.CharField(max_length=25)
    rendering_department = models.CharField(max_length=25)
    rendering_coe = models.CharField(max_length=25)
    revenue_doctor = models.CharField(max_length=50)
    revenue_spec = models.CharField(max_length=40)
    revenue_dept = models.CharField(max_length=25)
    revenue_coe = models.CharField(max_length=15)
    company_name = models.CharField(max_length=50)
    company_type = models.CharField(max_length=50)
    payment_type = models.CharField(max_length=50)
    service_unit = models.FloatField()
    serviceamount = models.FloatField()
    servicediscount = models.FloatField()
    itemcostprice = models.FloatField()
    totalcostprice = models.FloatField()
    grossamount = models.FloatField()
    discount = models.FloatField()
    patshare = models.FloatField()
    netamount = models.FloatField()
    deductable = models.FloatField()
    coinsurance = models.FloatField()
    copay = models.FloatField()
    spondiscount = models.FloatField()
    patdiscount = models.FloatField()
    settlementtype = models.CharField(max_length=50)
    tax_percentage = models.IntegerField()
    vatamount = models.FloatField()
    taxnetamount = models.FloatField()
    discauthremark = models.TextField()
    admissionbillingcategory = models.CharField(max_length=30)
    servicebillingcategory = models.CharField(max_length=30)
    servicebedcategory = models.CharField(max_length=30)
    nationality = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    country = models.CharField(max_length=30)
    leadsource = models.CharField(max_length=50)
    referralsourcename = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    invoiceid = models.CharField(max_length=20)
    activeinvoiceid = models.CharField(max_length=20)
    servicetype = models.CharField(max_length=20)
    network_sponsor = models.CharField(max_length=20)
    moudiscount = models.FloatField()
    insuranceapproved = models.IntegerField()
    primarybillcode = models.CharField(db_column='PrimaryBillCode', max_length=40)  # Field name made lowercase.
    branch_subcode = models.CharField(max_length=80)
    last_updatedon = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'patientdatasanhar'


class Patientdatasanhar1(models.Model):
    facility_name = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    registration_number = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    encounterno = models.CharField(max_length=30, db_collation='latin1_swedish_ci')
    patient_name = models.CharField(max_length=150, db_collation='latin1_swedish_ci')
    age_gender = models.CharField(db_column='age/gender', max_length=15, db_collation='latin1_swedish_ci')  # Field renamed to remove unsuitable characters.
    bill_location = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    invoice_no = models.CharField(max_length=30, db_collation='latin1_swedish_ci')
    invoice_date = models.DateTimeField()
    visit_data = models.DateTimeField()
    serviceid = models.CharField(max_length=30, db_collation='latin1_swedish_ci')
    item_cate = models.CharField(max_length=20, db_collation='latin1_swedish_ci')
    item_sub_cate = models.CharField(max_length=20, db_collation='latin1_swedish_ci')
    item_no = models.CharField(max_length=25, db_collation='latin1_swedish_ci')
    billing_group = models.CharField(max_length=30, db_collation='latin1_swedish_ci')
    department_name = models.CharField(max_length=30, db_collation='latin1_swedish_ci')
    sub_department_name = models.CharField(max_length=30, db_collation='latin1_swedish_ci')
    service_name = models.TextField(db_collation='latin1_swedish_ci')
    under_package = models.CharField(max_length=20, db_collation='latin1_swedish_ci')
    package_name = models.CharField(max_length=20, db_collation='latin1_swedish_ci')
    advising_doctor = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    advising_dept = models.CharField(max_length=30, db_collation='latin1_swedish_ci')
    advising_coe = models.CharField(max_length=10, db_collation='latin1_swedish_ci')
    rendering_doctor = models.CharField(max_length=25, db_collation='latin1_swedish_ci')
    rendering_specialisation = models.CharField(max_length=25, db_collation='latin1_swedish_ci')
    rendering_department = models.CharField(max_length=25, db_collation='latin1_swedish_ci')
    rendering_coe = models.CharField(max_length=25, db_collation='latin1_swedish_ci')
    revenue_doctor = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    revenue_spec = models.CharField(max_length=40, db_collation='latin1_swedish_ci')
    revenue_dept = models.CharField(max_length=25, db_collation='latin1_swedish_ci')
    revenue_coe = models.CharField(max_length=15, db_collation='latin1_swedish_ci')
    company_name = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    company_type = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    payment_type = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    service_unit = models.FloatField()
    serviceamount = models.FloatField()
    servicediscount = models.FloatField()
    itemcostprice = models.FloatField()
    totalcostprice = models.FloatField()
    grossamount = models.FloatField()
    discount = models.FloatField()
    patshare = models.FloatField()
    netamount = models.FloatField()
    deductable = models.FloatField()
    coinsurance = models.FloatField()
    copay = models.FloatField()
    spondiscount = models.FloatField()
    patdiscount = models.FloatField()
    settlementtype = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    tax_percentage = models.IntegerField()
    vatamount = models.FloatField()
    taxnetamount = models.FloatField()
    discauthremark = models.TextField(db_collation='latin1_swedish_ci')
    admissionbillingcategory = models.CharField(max_length=30, db_collation='latin1_swedish_ci')
    servicebillingcategory = models.CharField(max_length=30, db_collation='latin1_swedish_ci')
    servicebedcategory = models.CharField(max_length=30, db_collation='latin1_swedish_ci')
    nationality = models.CharField(max_length=30, db_collation='latin1_swedish_ci')
    city = models.CharField(max_length=30, db_collation='latin1_swedish_ci')
    state = models.CharField(max_length=30, db_collation='latin1_swedish_ci')
    country = models.CharField(max_length=30, db_collation='latin1_swedish_ci')
    leadsource = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    referralsourcename = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    username = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    invoiceid = models.CharField(max_length=20, db_collation='latin1_swedish_ci')
    activeinvoiceid = models.CharField(max_length=20, db_collation='latin1_swedish_ci')
    servicetype = models.CharField(max_length=20, db_collation='latin1_swedish_ci')
    network_sponsor = models.CharField(max_length=20, db_collation='latin1_swedish_ci')
    moudiscount = models.FloatField()
    insuranceapproved = models.IntegerField()
    primarybillcode = models.CharField(db_column='PrimaryBillCode', max_length=40, db_collation='latin1_swedish_ci')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'patientdatasanhar1'


class RecoveryDetails(models.Model):
    sno = models.AutoField(primary_key=True)
    uniqueid = models.CharField(max_length=20)
    branch = models.TextField()
    catogery = models.TextField()
    spoc = models.TextField()
    designation = models.TextField()
    contact = models.BigIntegerField()
    email_id = models.TextField()
    company = models.TextField()
    fulladdress = models.TextField()
    remarks = models.TextField()
    location = models.TextField()
    geolocation = models.TextField()
    area = models.TextField()
    city = models.TextField()
    state = models.TextField()
    pincode = models.BigIntegerField()
    cempid = models.TextField()
    cdate = models.DateField()
    ctime = models.TimeField()
    status = models.TextField()

    class Meta:
        managed = False
        db_table = 'recovery_details'


class ReferralLogins(models.Model):
    emp_name = models.CharField(db_column='Emp_name', max_length=30, db_collation='latin1_swedish_ci', blank=True, null=True)  # Field name made lowercase.
    personal_number = models.BigIntegerField(db_column='Personal_Number')  # Field name made lowercase.
    office_number = models.BigIntegerField(db_column='Office_number')  # Field name made lowercase.
    designation = models.CharField(db_column='Designation', max_length=50, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    emp_id = models.CharField(db_column='Emp_ID', max_length=20, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=50, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    mpassword = models.CharField(max_length=100, db_collation='latin1_swedish_ci')
    branch = models.CharField(db_column='Branch', max_length=30, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    old_branch = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    page = models.CharField(db_column='Page', max_length=20, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    orginal_design = models.TextField(db_column='Orginal_Design', db_collation='latin1_swedish_ci')  # Field name made lowercase.
    original_type = models.TextField(db_column='Original_Type', db_collation='latin1_swedish_ci')  # Field name made lowercase.
    last_location = models.CharField(db_column='Last_Location', max_length=50, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    last_loc_datetime = models.DateTimeField()
    date = models.DateField(db_column='Date')  # Field name made lowercase.
    time = models.TimeField(db_column='Time')  # Field name made lowercase.
    head = models.TextField(db_column='Head', db_collation='latin1_swedish_ci')  # Field name made lowercase.
    type = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    join_date = models.DateField(db_column='Join_Date')  # Field name made lowercase.
    visibility = models.TextField(db_column='Visibility', db_collation='latin1_swedish_ci')  # Field name made lowercase.
    job_status = models.CharField(db_column='Job_Status', max_length=50, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    levels = models.IntegerField()
    bank_acc = models.TextField(db_collation='latin1_swedish_ci')
    ifsc = models.CharField(max_length=20, db_collation='latin1_swedish_ci')
    pan = models.CharField(max_length=20, db_collation='latin1_swedish_ci')
    allow = models.IntegerField()
    img_link = models.CharField(max_length=300, db_collation='latin1_swedish_ci')
    model = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    version = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    firebase_token = models.CharField(max_length=3000, db_collation='latin1_swedish_ci')
    deviceid = models.CharField(max_length=50, db_collation='latin1_swedish_ci')
    accesskey = models.CharField(max_length=100, db_collation='latin1_swedish_ci')
    state = models.TextField(db_collation='latin1_swedish_ci')
    branch_access = models.TextField(db_collation='latin1_swedish_ci')
    new_type = models.TextField(db_collation='latin1_swedish_ci')
    ref_count = models.IntegerField()
    inactive_dt = models.DateField()
    up_bank_details = models.IntegerField()
    androidpermissions = models.CharField(max_length=100, db_collation='latin1_swedish_ci')
    androidsubmenu = models.CharField(max_length=100, db_collation='latin1_swedish_ci')
    loginstatus = models.IntegerField()
    old_status = models.IntegerField()
    last_location_tt = models.CharField(db_column='Last_Location_tt', max_length=80, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    branch_cluster = models.CharField(max_length=50, db_collation='latin1_swedish_ci')

    class Meta:
        managed = False
        db_table = 'referral_logins'


class ReferralLogs(models.Model):
    sno = models.IntegerField()
    referral_sno = models.IntegerField()
    referralname_consult = models.CharField(max_length=50)
    consult_remarks = models.CharField(max_length=100)
    referralamount = models.FloatField()
    ucid = models.CharField(max_length=10)
    emp_details = models.CharField(max_length=50)
    status = models.TextField()
    agent_name = models.CharField(max_length=10)
    referral_type = models.TextField()
    marketing_executive = models.CharField(db_column='Marketing_executive', max_length=50)  # Field name made lowercase.
    update_on = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'referral_logs'


class StateAreas(models.Model):
    sno = models.AutoField(primary_key=True)
    state = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    zone = models.CharField(max_length=200)
    areas = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'state_areas'


class SupportForm(models.Model):
    sno = models.IntegerField()
    fullname = models.TextField()
    emp_id = models.TextField()
    contact_no = models.BigIntegerField()
    problem_category = models.TextField()
    problem_msg = models.TextField()
    model = models.CharField(max_length=200)
    version = models.CharField(max_length=200)
    deviceid = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()

    class Meta:
        managed = False
        db_table = 'support_form'


class TourExpence(models.Model):
    sno = models.AutoField(primary_key=True)
    emp_id = models.TextField()
    name = models.CharField(max_length=100)
    purpose = models.CharField(max_length=250)
    refid = models.CharField(max_length=250)
    amount = models.IntegerField()
    trans_id = models.CharField(max_length=250)
    type = models.TextField()
    branch = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    location = models.CharField(max_length=2000)
    date = models.DateField()
    time = models.TimeField()
    source = models.TextField()

    class Meta:
        managed = False
        db_table = 'tour_expence'


class TourPlan(models.Model):
    sno = models.AutoField(primary_key=True)
    emp_id = models.TextField()
    empname = models.CharField(max_length=250)
    tourname = models.CharField(max_length=250)
    area = models.CharField(max_length=250)
    trans_id = models.CharField(max_length=250)
    distance = models.BigIntegerField()
    travel_time = models.TimeField()
    location = models.CharField(max_length=2000)
    geo_area = models.TextField()
    geo_city = models.TextField()
    geo_state = models.TextField()
    geo_pincode = models.BigIntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    date = models.DateField()
    time = models.TimeField()
    branch = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    source = models.CharField(max_length=250)
    status = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'tour_plan'


class TourPlanReferral(models.Model):
    sno = models.AutoField(primary_key=True)
    trans_id = models.TextField()
    emp_id = models.TextField()
    emp_name = models.TextField()
    branch = models.TextField()
    unique_id = models.TextField()
    refferal_name = models.TextField()
    designation = models.TextField()
    mobile = models.BigIntegerField()
    from_add = models.CharField(max_length=300)
    to_add = models.CharField(max_length=300)
    distance = models.TextField()
    duration = models.TextField()
    location = models.TextField()
    latitude = models.TextField()
    longitude = models.TextField()
    date = models.DateField()
    time = models.TimeField()

    class Meta:
        managed = False
        db_table = 'tour_plan_referral'


class UtrUpdate(models.Model):
    id = models.BigAutoField(primary_key=True)
    upload_csv_file = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'utr_update'


class WebLogins(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    emp_name = models.CharField(db_column='Emp_name', max_length=30, blank=True, null=True)  # Field name made lowercase.
    personal_number = models.BigIntegerField(db_column='Personal_Number', blank=True, null=True)  # Field name made lowercase.
    office_number = models.BigIntegerField(db_column='Office_number', blank=True, null=True)  # Field name made lowercase.
    designation = models.TextField(db_column='Designation', blank=True, null=True)  # Field name made lowercase.
    emp_id = models.CharField(db_column='Emp_ID', unique=True, max_length=50, blank=True, null=True)  # Field name made lowercase.
    branch = models.TextField(db_column='Branch', blank=True, null=True)  # Field name made lowercase.
    old_branch = models.CharField(max_length=50, blank=True, null=True)
    page = models.TextField(db_column='Page', blank=True, null=True)  # Field name made lowercase.
    orginal_design = models.TextField(db_column='Orginal_Design', blank=True, null=True)  # Field name made lowercase.
    original_type = models.TextField(db_column='Original_Type', blank=True, null=True)  # Field name made lowercase.
    last_location = models.CharField(db_column='Last_Location', max_length=50, blank=True, null=True)  # Field name made lowercase.
    last_loc_datetime = models.DateTimeField(blank=True, null=True)
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    time = models.TimeField(db_column='Time', blank=True, null=True)  # Field name made lowercase.
    head = models.TextField(db_column='Head', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(max_length=50, blank=True, null=True)
    join_date = models.DateField(db_column='Join_Date', blank=True, null=True)  # Field name made lowercase.
    visibility = models.TextField(db_column='Visibility', blank=True, null=True)  # Field name made lowercase.
    job_status = models.CharField(db_column='Job_Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    levels = models.IntegerField(blank=True, null=True)
    bank_acc = models.TextField(blank=True, null=True)
    ifsc = models.CharField(max_length=20, blank=True, null=True)
    pan = models.CharField(max_length=20, blank=True, null=True)
    allow = models.IntegerField(blank=True, null=True)
    img_link = models.CharField(max_length=300, blank=True, null=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    version = models.CharField(max_length=50, blank=True, null=True)
    firebase_token = models.CharField(max_length=3000, blank=True, null=True)
    deviceid = models.CharField(max_length=50, blank=True, null=True)
    accesskey = models.CharField(max_length=100, blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    branch_access = models.TextField(blank=True, null=True)
    new_type = models.TextField(blank=True, null=True)
    ref_count = models.IntegerField(blank=True, null=True)
    mpassword = models.CharField(max_length=100, blank=True, null=True)
    androidpermissions = models.CharField(max_length=100, blank=True, null=True)
    inactive_dt = models.DateField(blank=True, null=True)
    androidsubmenu = models.CharField(max_length=100, blank=True, null=True)
    loginstatus = models.CharField(max_length=100, blank=True, null=True)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'web_logins'


class WebLoginsGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    weblogins_id = models.BigIntegerField()
    group_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'web_logins_groups'
        unique_together = (('weblogins_id', 'group_id'),)


class WebLoginsUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    weblogins_id = models.BigIntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'web_logins_user_permissions'
        unique_together = (('weblogins_id', 'permission_id'),)
