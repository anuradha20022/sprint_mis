
from rest_framework import serializers
from .models import Logins
from rest_framework import serializers
from .models import PatientData


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
        model = PatientData
        fields = '__all__'