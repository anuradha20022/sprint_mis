
from .models import Logins,HomeSampleVisits
from rest_framework import serializers
from .models import PatientDataOlddata


class LoginsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logins
        fields = [
            'personal_number',
            'office_number',
            'designation',
            'emp_id',
            'password',
            'branch',
            'old_branch',
            'page',
        ]


class PatientDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDataOlddata
        fields = '__all__'


class HomeSampleVisitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeSampleVisits
        fields = '__all__'
