import re

from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateAPIView

from ussdke.models import USSD, Company, Code
from ussdke.serializers import UssdSerializer, CompanySerializer, CodeSerializer, CompanyUssdSerializer


def home(request):
    companies = Company.objects.all()
    #context={'companies': CompanySerializer(companies,many=True).data}
    context={'companies': Company.objects.all(),'ussds':USSD.objects.all()[:5]}
    #print context
    return render(request, 'ussdke/index.html', context)


def companies(request):
    pass


def company_ussds(request,pk):
    company=Company.objects.get(id=pk)
    ussds_items=USSD.objects.filter(company=company)
    paginator=Paginator(ussds_items,5)
    page = request.GET.get('page',1)
    try:
        ussds = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        ussds = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        ussds = paginator.page(paginator.num_pages)

    return render_to_response('ussdke/ussd/list.html', {"ussds": ussds,"company":company})



def normalize_query(query_string, find_terms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    norm_space=re.compile(r'\s{2,}').sub):
    return [norm_space(' ', (t[0] or t[1]).strip()) for t in find_terms(query_string)]


def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


class UssdViewSet(ListCreateAPIView):
    """
    API endpoint that allows USSD to be viewed or edited.
    """
    queryset = USSD.objects.all().order_by('-created_at')
    serializer_class = UssdSerializer


class UssdDetailViewSet(RetrieveUpdateAPIView):
    """
    API endpoint that allows USSD to be viewed or edited.
    """
    queryset = USSD.objects.all().order_by('-created_at')
    serializer_class = UssdSerializer


class CompanyViewSet(ListCreateAPIView):
    """
    API endpoint that allows Company to be viewed or edited.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class UssdSuggest(APIView):
    """
    API endpoint that allows USSD to be suggested.
    """
    authentication_classes = ()
    def get(self, request, format=None):
        ussds = USSD.objects.all()
        serializer = UssdSerializer(ussds, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UssdSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanySuggest(APIView):
    """
    API endpoint that allows Company to be suggested.
    """
    authentication_classes = ()

    def get(self, request, format=None):
        companies = USSD.objects.all()
        serializer = UssdSerializer(companies, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UssdList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        if ('q' in request.GET) and request.GET['q'].strip():
            query_string = request.GET['q']
            entry_query = get_query(query_string, ['description', ])
            ussds = USSD.objects.filter(entry_query).order_by('-created_at')
        else:
            ussds = USSD.objects.all()

        serializer = UssdSerializer(ussds, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UssdSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyList(APIView):
    """
    List all Companies, or create a new Company.
    """

    def get(self, request, format=None):
        query_string = ''
        companies = None

        if ('q' in request.GET) and request.GET['q'].strip():
            query_string = request.GET['q']
            entry_query = get_query(query_string, ['name', ])
            companies = Company.objects.filter(entry_query).order_by('-created_at')
        else:
            companies = Company.objects.all()

        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UssdDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_object(self, pk):
        try:
            return USSD.objects.get(pk=pk)
        except USSD.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        query_string = ''
        ussd = self.get_object(pk)
        serializer = UssdSerializer(ussd,many=True)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        ussd = self.get_object(pk)
        serializer = UssdSerializer(ussd, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        ussd = self.get_object(pk)
        ussd.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CompanyDetail(APIView):
    """
    Retrieve, update or delete a Company instance.
    """

    def get_object(self, pk):
        try:
            return Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        company = self.get_object(pk)
        serializer = CompanySerializer(company)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        company = self.get_object(pk)
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        company = self.get_object(pk)
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CompanyUSSDDetail(APIView):
    """
    Retrieve, update or delete a Company instance.
    """

    def get_object(self, pk):
        try:
            return Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        company = self.get_object(pk)
        serializer = CompanyUssdSerializer(company.ussds.all(),many=True)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        print ('put a ussd')
        company = self.get_object(pk)
        serializer = CompanySerializer(company, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        company = self.get_object(pk)
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, pk, format=None):

        serializer = CompanyUssdSerializer(data=request.data,many=True,partial=True)
        if serializer.is_valid():
            print ('[*] Serializer is valid')
            serializer.save(company=self.get_object(pk))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

