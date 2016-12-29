import json

import re,logging
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView
from rest_framework import status
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateAPIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from ussdke.models import *
from ussdke.forms import *
from ussdke.serializers import UssdSerializer, CompanySerializer, CompanyUssdSerializer, InvalidationSerializer

log = logging.getLogger('ussdke')

def about(request):
    context = {
        'title': 'About',
    }
    return render(request, 'ussdke/about.html', context)

def home(request):
    companies = Company.objects.all()
    #context={'companies': CompanySerializer(companies,many=True).data}
    context={'companies': Company.objects.all(),'ussds':USSD.objects.all()[:5]}
    #print context
    return render(request, 'ussdke/main.html', context)


def companies(request):
    pass


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


class CompanyUssdViewSet(ListCreateAPIView):
    """
    API endpoint that allows a Company USSDs to be viewed or edited.
    """
    queryset = USSD.objects.all()
    serializer_class = UssdSerializer
    #pagination_class = StandardResultsSetPagination

    template_name = 'ussdke/ussd/list.html'
    renderer_classes = (TemplateHTMLRenderer,)


    def list(self, request, *args, **kwargs):
        company = Company.objects.get(id=kwargs.get('pk'))
        queryset = self.get_queryset().filter(company=company).order_by('-created_at')


        paginator = Paginator(queryset, 5)
        page = request.GET.get('page', 1)
        try:
            ussds = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            ussds = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            ussds = paginator.page(paginator.num_pages)

        #return render_to_response('ussdke/ussd/list.html', )

        data = {"ussds": ussds, "company": company}#{'users': queryset}
        return Response(data)


class UssdDetailViewSet(RetrieveUpdateAPIView):
    """
    API endpoint that allows USSD to be viewed or edited.
    """
    queryset = USSD.objects.all().order_by('-created_at')
    serializer_class = UssdSerializer

class UssdDetailInvalidationList(RetrieveUpdateAPIView):
    """
    API endpoint that allows USSD to be viewed or edited.
    """
    queryset = Invalidation.objects.all()
    serializer_class = InvalidationSerializer


    def list(self, request, *args, **kwargs):
        ussd = USSD.objects.get(id=kwargs.get('pk'))
        queryset = self.get_queryset().filter(ussd=ussd).order_by('-created_at')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


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

class UssdDetailInvalidate(APIView):
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

    def post(self, request, pk, format=None):
        ussd = self.get_object(pk)

        invalidated_ussd = ussd.invalidate(request.data)
        serializer = UssdSerializer(invalidated_ussd)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        ussd = self.get_object(pk)
        ussd.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CompanyDetailViewSet(RetrieveUpdateAPIView):
    """
    API endpoint that allows Company to be viewed or edited.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


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
        serializer = CompanySerializer(company,context={'request': request})
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

class CompanyUSSDDetail(ListCreateAPIView):
    """
    API endpoint that allows a Company USSDs to be viewed or edited.
    """
    queryset = USSD.objects.all()
    serializer_class = UssdSerializer
    #pagination_class = StandardResultsSetPagination

    #renderer_classes = (JSONRenderer,)


    def list(self, request, *args, **kwargs):
        company = Company.objects.get(id=kwargs.get('pk'))
        queryset = self.get_queryset().filter(company=company).order_by('-created_at')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        #return Response(self.get_serializer_class()(queryset,context={'request': request},many=True).data)


class CompanyUSSDDetailOld(APIView):
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


class LoginView(FormView):
    """
    Provides the ability to login as a user with a username and password
    """
    template_name = 'ussdke/login.html'
    success_url = '/'
    form_class = AuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(ensure_csrf_cookie)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        log.info("Dispatch")

        # Sets a test cookie to make sure the user has cookies enabled
        # request.session.set_test_cookie()
        # log.info("Test Cookie Set")
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        log.info('Next: auth_login')
        auth_login(self.request, form.get_user())
        log.info('After: auth_login')

        # If the test cookie worked, go ahead and
        # delete it since its no longer needed
        # if self.request.session.test_cookie_worked():
        #    log.info('test cookie worked')
        #    self.request.session.delete_test_cookie()

        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        redirect_to = self.request.GET.get(self.redirect_field_name)
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = self.success_url
        return redirect_to

class LogoutView(RedirectView):
    """
    Provides users the ability to logout
    """
    template_name = 'web/logout.html'
    url = '/'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)

class RegisterView(FormView):
    """
    Provides the ability to register as a user with a username and password
    """
    template_name = 'ussdke/register.html'
    success_url = '/'
    form_class = UserCreateForm
    redirect_field_name = REDIRECT_FIELD_NAME

    @method_decorator(sensitive_post_parameters('password1', 'password2'))
    @method_decorator(csrf_protect)
    @method_decorator(ensure_csrf_cookie)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        new_user = form.save()
        # user.set_password(user.password)
        # user.save()

        user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1']
                            )
        login(self.request, user)

        # If the test cookie worked, go ahead and
        # delete it since its no longer needed
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return super(RegisterView, self).form_valid(form)

    def get_success_url(self):
        redirect_to = self.request.GET.get(self.redirect_field_name)
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = self.success_url
        return redirect_to

def star_company(request, pk):
    if request.method == 'POST':
        response_data = {}

        company = Company.objects.get(pk=pk)
        author = request.user

        star, created = CompanyStar.objects.get_or_create(author=author, company=company)

        response_data['result'] = 'Company Star successful!'
        response_data['company'] = company.pk

        response_data['next'] = "UnStar"
        response_data['next_url'] = "/companies/" + str(company.pk) + "/unstar/"

        response_data['count'] = company.stars.count()
        response_data['created'] = star.created_date.strftime('%B %d, %Y %I:%M %p')
        response_data['author'] = star.author.username

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

def un_star_post(request, pk):
    if request.method == 'POST':
        response_data = {}

        company = Company.objects.get(pk=pk)
        author = request.user

        star = CompanyStar.objects.get(author=author, company=company)
        star.delete()

        response_data['result'] = 'Company UnStar successful!'
        response_data['post'] = company.pk

        response_data['next'] = "Star"
        response_data['next_url'] = "/companies/" + str(company.pk) + "/star/"

        response_data['count'] = company.stars.count()
        response_data['created'] = star.created_date.strftime('%B %d, %Y %I:%M %p')
        response_data['author'] = star.author.username

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )