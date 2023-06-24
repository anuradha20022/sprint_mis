from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin, AbstractUser, User
from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.utils.timezone import now


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, emp_id, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        user = self.model(emp_id=emp_id, **extra_fields)
        # user.set_password(password)
        user.password = make_password(password)
        # user.make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, emp_id,  password=None, **extra_fields):
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(emp_id, password, **extra_fields)

    def create_superuser(self, emp_id, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(emp_id, password, **extra_fields)


class WebLogins(AbstractBaseUser, PermissionsMixin):
    emp_name = models.CharField(db_column='Emp_name', max_length=30, blank=True, null=True)
    personal_number = models.BigIntegerField(db_column='Personal_Number', null=True)
    office_number = models.BigIntegerField(db_column='Office_number', null=True)
    designation = models.TextField(db_column='Designation', null=True)
    emp_id = models.CharField(max_length=50, db_column='Emp_ID', unique=True, null=True)
    branch = models.TextField(db_column='Branch', null=True)
    old_branch = models.CharField(max_length=50, null=True)
    page = models.TextField(db_column='Page', null=True, default='Marketing')
    orginal_design = models.TextField(db_column='Orginal_Design', null=True)
    original_type = models.TextField(db_column='Original_Type', null=True)
    last_location = models.CharField(db_column='Last_Location', max_length=50, null=True)
    last_loc_datetime = models.DateTimeField(null=True)
    date = models.DateField(db_column='Date', null=True)
    time = models.TimeField(db_column='Time', null=True)
    head = models.TextField(db_column='Head', null=True)
    type = models.CharField(max_length=50, null=True)
    join_date = models.DateField(db_column='Join_Date', null=True)
    visibility = models.TextField(db_column='Visibility', null=True, default='Hidden')
    job_status = models.CharField(db_column='Job_Status', max_length=50, null=True, default='Active')
    levels = models.IntegerField(null=True)
    bank_acc = models.TextField(null=True)
    ifsc = models.CharField(max_length=20, null=True)
    pan = models.CharField(max_length=20, null=True)
    allow = models.IntegerField(null=True)
    img_link = models.CharField(max_length=300, null=True)
    model = models.CharField(max_length=50, null=True)
    version = models.CharField(max_length=50, null=True)
    firebase_token = models.CharField(max_length=3000, null=True)
    deviceid = models.CharField(max_length=50, null=True)
    accesskey = models.CharField(max_length=100, null=True)
    state = models.TextField(null=True)
    branch_access = models.TextField(null=True)
    new_type = models.TextField(null=True)
    ref_count = models.IntegerField(null=True, default=0)
    mpassword = models.CharField(max_length=100, blank=True, null=True)
    androidpermissions = models.CharField(max_length=100, blank=True, null=True)
    inactive_dt = models.DateField(null=True)
    androidsubmenu = models.CharField(max_length=100, blank=True, null=True)
    loginstatus = models.CharField(max_length=100, blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'emp_id'
    REQUIRED_FIELDS = ['emp_name']
    objects = UserManager()

    class Meta:
        db_table = 'web_logins'

    def __str__(self):
        return self.emp_name or ' '


# class Logins(models.Model):
#     emp_name = models.CharField(db_column='Emp_name', max_length=30, blank=True, null=True)  # Field name made lowercase.
#     personal_number = models.BigIntegerField(db_column='Personal_Number')  # Field name made lowercase.
#     office_number = models.BigIntegerField(db_column='Office_number')  # Field name made lowercase.
#     designation = models.TextField(db_column='Designation')  # Field name made lowercase.
#     emp_id = models.CharField(db_column='Emp_ID', max_length=20)  # Field name made lowercase.
#     password = models.CharField(db_column='Password', max_length=50)  # Field name made lowercase.
#     branch = models.TextField(db_column='Branch')  # Field name made lowercase.
#     old_branch = models.CharField(max_length=50)
#     page = models.TextField(db_column='Page')  # Field name made lowercase.
#     orginal_design = models.TextField(db_column='Orginal_Design')  # Field name made lowercase.
#     original_type = models.TextField(db_column='Original_Type')  # Field name made lowercase.
#     last_location = models.CharField(db_column='Last_Location', max_length=50)  # Field name made lowercase.
#     last_loc_datetime = models.DateTimeField()
#     date = models.DateField(db_column='Date')  # Field name made lowercase.
#     time = models.TimeField(db_column='Time')  # Field name made lowercase.
#     head = models.TextField(db_column='Head')  # Field name made lowercase.
#     type = models.CharField(max_length=50)
#     join_date = models.DateField(db_column='Join_Date')  # Field name made lowercase.
#     visibility = models.TextField(db_column='Visibility')  # Field name made lowercase.
#     job_status = models.CharField(db_column='Job_Status', max_length=50)  # Field name made lowercase.
#     levels = models.IntegerField()
#     bank_acc = models.TextField()
#     ifsc = models.CharField(max_length=20)
#     pan = models.CharField(max_length=20)
#     allow = models.IntegerField()
#     img_link = models.CharField(max_length=300)
#     model = models.CharField(max_length=50)
#     version = models.CharField(max_length=50)
#     firebase_token = models.CharField(max_length=3000)
#     deviceid = models.CharField(max_length=50)
#     accesskey = models.CharField(max_length=100)
#     state = models.TextField()
#     branch_access = models.TextField()
#     new_type = models.TextField()
#     ref_count = models.IntegerField()
#     mpassword = models.CharField(max_length=100, blank=True, null=True)
#     androidpermissions = models.CharField(max_length=100, blank=True, null=True)
#     inactive_dt = models.DateField()
#     androidsubmenu = models.CharField(max_length=100, blank=True, null=True)
#     loginstatus = models.CharField(max_length=100, blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'logins'


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


class AdmissionType(models.Model):
    sno = models.AutoField(primary_key=True)
    type = models.TextField()
    catogery = models.TextField()
    status = models.TextField()

    class Meta:
        managed = False
        db_table = 'admission_type'


class AndroidPermissions(models.Model):
    sno = models.IntegerField()
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


class Banner(models.Model):
    sno = models.AutoField(primary_key=True)
    name = models.TextField()
    image = models.CharField(max_length=300)

    class Meta:
        managed = False
        db_table = 'banner'


class BranchListDum(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    branch_name = models.CharField(max_length=50)
    status = models.IntegerField()

    class Meta:
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
        db_table = 'category'


class DoctorAgentList(models.Model):
    sno = models.AutoField(primary_key=True)
    emp_id = models.CharField(max_length=20)
    unique_id = models.CharField(max_length=20)
    agent_type = models.TextField()
    agent_name = models.TextField()
    reg_no = models.TextField()
    designation = models.TextField()
    department = models.TextField()
    mobile = models.CharField(max_length=13)
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

    class Meta:
        managed = False
        db_table = 'doctor_agent_list'


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
    sno = models.AutoField(primary_key=True)
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
    last_loc_datetime = models.DateTimeField(null=True, blank=True)
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
    inactive_dt = models.DateField()
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


class OwnershipDummy(models.Model):
    s_no = models.IntegerField(db_column='s.no')  # Field renamed to remove unsuitable characters.
    empid = models.CharField(max_length=100)
    ucid = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'ownership_dummy'


class PatientData(models.Model):
    sno = models.AutoField(primary_key=True)
    branch = models.CharField(max_length=40)
    facility_name = models.CharField(max_length=50)
    registration_number = models.CharField(max_length=50)
    encounterno = models.CharField(max_length=30)
    patient_name = models.CharField(max_length=150)
    age_gender = models.CharField(db_column='age/gender', max_length=15)  # Field renamed to remove unsuitable characters.
    bill_location = models.CharField(max_length=50)
    invoice_no = models.CharField(max_length=30)
    invoice_date = models.DateTimeField(null=True, blank=True)
    visit_data = models.DateTimeField(null=True, blank=True)
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

    class Meta:
        managed = False
        db_table = 'patient_data'


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


class Patientdatasanhar(models.Model):
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
    sno = models.AutoField(primary_key=True)
    invoice_no = models.CharField(max_length=30)
    patient_name = models.CharField(max_length=150)
    branch = models.CharField(max_length=40)
    service_name = models.TextField(blank=True)
    grossamount = models.CharField(max_length=50, null=True)
    discount = models.CharField(max_length=50, null=True)
    netamount = models.CharField(max_length=50, null=True)
    referralamount = models.CharField(max_length=50, null=True)
    utr_no = models.CharField(max_length=50, null=True)
    utr_created_by = models.CharField(max_length=50, null=True)
    utr_date = models.DateField(auto_now_add=now)

    class Meta:
        db_table = "utrupdate"