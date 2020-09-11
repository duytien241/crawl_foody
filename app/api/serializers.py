from rest_framework import serializers
from ..models import Address
from django.core.validators import validate_email
import re


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = ('id', 'typeAddress', 'address', 'user_id', 'uri_id', 'active')

    def validate(self, data):
        if data['typeAddress'].lower() not in ['email', 'phone']:
            raise serializers.ValidationError('Enter a valid address type')
        if data['typeAddress'] == 'Email':
            validate_email(data['address'])
        if data['typeAddress'] == 'Phone':
            valid = re.compile(r'(09|03|07|08|05)([0-9]{8})')
            if not valid.match(data['address']):
                raise serializers.ValidationError('Enter a valid phone address')
        return data
