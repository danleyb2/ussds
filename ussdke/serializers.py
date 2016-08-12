from django.utils import timezone
from rest_framework import serializers
from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination
from rest_framework.fields import Field, ReadOnlyField

from ussdke.models import USSD, Company, Code, Invalidation
from rest_framework import serializers


class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Code
        fields = (
            'value',
            'pk',
        )

class InvalidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invalidation
        fields = ('__all__')

class UssdSerializer(serializers.ModelSerializer):
    code = CodeSerializer(read_only=False)
    # company = CompanySerializer(read_only=False)
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    invalidation_count = serializers.SerializerMethodField('_invalidation_count')
    invalidation_list_url = serializers.SerializerMethodField('_invalidation_list_url')
    '''
    description = serializers.CharField()
    last_confirmed = serializers.DateTimeField(default=timezone.now())
    updated_at = serializers.DateTimeField(default=timezone.now())

    def create(self, validated_data):
        ussd = USSD()
        ussd.code = Code.objects.get_or_create(value=validated_data['code'])
        ussd.last_confirmed = timezone.now()
        ussd.updated_at = timezone.now()
        ussd.save()

        return ussd


    def update(self, instance, validated_data):
        pass

    '''

    class Meta:
        model = USSD
        fields = (
            '__all__'
            # 'id',
            # 'company',
            # 'description',
            # 'code',
            # 'confirmed',
            # 'last_confirmed',
            # 'created_at',
            # 'updated_at'
        )
        depth = 1

    def _invalidation_count(self,ussd):
        return ussd.invalidation_set.count()

    def _invalidation_list_url(self,ussd):
        return (self.context['request']).build_absolute_uri(ussd.get_invalidation_list_url())

class CompanyUssdSerializer(UssdSerializer):
    code = serializers.CharField(read_only=False)

    last_confirmed = serializers.DateTimeField(default=timezone.now())
    updated_at = serializers.DateTimeField(default=timezone.now())

    class Meta:
        model = USSD
        fields = (
            'id',
            'description',
            'code',
            'confirmed',
            'last_confirmed',
            'created_at',
            'updated_at'
        )

    def create(self, validated_data):
        print repr(validated_data)
        ussd = USSD()
        ussd.code = Code.objects.get_or_create(value=validated_data['code'])[0]
        ussd.company = validated_data['company']
        ussd.description = validated_data['description']
        ussd.last_confirmed = timezone.now()
        ussd.updated_at = timezone.now()
        ussd.save()
        return ussd


class CompanySerializer(serializers.HyperlinkedModelSerializer):
    # ussds = serializers.StringRelatedField(many=True,read_only=True)
    #ussds = CompanyUssdSerializer(many=True, read_only=True)
    ussd_count = serializers.SerializerMethodField('_ussd_count')
    ussds_url = serializers.SerializerMethodField('_ussds_url')
    # ussds = serializers.SerializerMethodField('paginate_ussds')
    # ussds = UssdSerializer(many=True)
    # updated_at=serializers.DateTimeField(default=timezone.now())
    icon=serializers.ImageField()


    class Meta:
        fields = (
            # '__all__'
            'id',
            'name',
            'icon',
            'website',
            'created_at',
            'ussd_count',
            'ussds_url',


        )
        model = Company
        # read_only_fields = ('ussds',)


    def _ussd_count(self,obj):
        '''
        :type obj Company
        :param obj:
        :return:
        '''
        return obj.ussds.count()

    def _ussds_url(self,obj):
        '''
        :type obj Company
        :param obj:
        :return:
        '''
        return (self.context['request']).build_absolute_uri(obj.get_ussds_url())