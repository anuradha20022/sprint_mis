from django import forms
from App.models import Logins, DoctorAgentList
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit


class LoginForm(forms.ModelForm):
    class Meta:
        model = Logins
        fields = "__all__"


# class BankForm(forms.ModelForm):
#     class Meta:
#         model = DoctorAgentList
#         fields = "__all__"

#
# class Upload(forms.ModelForm):
#     class Meta:
#         model = UtrUpdate
#         fields = "__all__"


class EmpForm(forms.ModelForm):
    class Meta:
        model = Logins
        fields = "__all__"


class Update(forms.ModelForm):
    class Meta:
        model = DoctorAgentList
        fields = "__all__"
