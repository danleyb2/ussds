from django.conf.urls import url,include
from rest_framework import routers
from . import views

from rest_framework.urlpatterns import format_suffix_patterns


#router = routers.DefaultRouter()
#router.register(r'ussds', views.UssdViewSet)
#router.register(r'ussds/suggest', views.UssdSuggestViewSet)

#router.register(r'companies', views.CompanyList.as_view())
#router.register(r'companies/suggest', views.CompanyViewSet)



urlpatterns = format_suffix_patterns([
    url(r'^$', views.home, name='index'),
    url(r'^about$', views.about, name='about'),

    #url(r'^api2/',include(router.urls)),
    url(r'^ussds/', include(
        [
            url(r'^$', views.UssdViewSet.as_view(),name='info'),
            url(r'^suggest', views.UssdSuggest.as_view(),name='suggest'),
            # url(r'^api/ussds',views.companies),
            # url(r'^invalidate',views.companies),
            # url(r'^fav',views.companies),
            url(r'^(?P<pk>[0-9]+)/', include([
                url(r'^$', views.UssdDetailViewSet.as_view(), name='instance'),
                #url(r'invalidate', views.UssdDetailInvalidate.as_view(), name='invalidate'), #todo

            ], namespace='ussd')),
        ]),name='ussds'
        ),

    url(r'^companies/', include(
        [
            url(r'^$', views.CompanyViewSet.as_view(),name='info'),
            url(r'^suggest', views.CompanySuggest.as_view(),name='suggest'),
            # url(r'^ussds',views.ussds),
            url(r'^(?P<pk>[0-9]+)/', include([
                url(r'^$', views.CompanyDetail.as_view(),name='instance'),
                url(r'ussds', views.CompanyUssdViewSet.as_view(),name='ussds')
            ],namespace='company'),),
        ],namespace='companies'),
        ),

    url(r'^api/',include([

        url(r'^ussds/',include(
            [
                url(r'^$',views.UssdViewSet.as_view(),name='info'),
                url(r'^suggest',views.UssdSuggest.as_view(),name='suggest'),
                #url(r'^api/ussds',views.companies),
                #url(r'^invalidate',views.companies),
                #url(r'^fav',views.companies),
                url(r'^(?P<pk>[0-9]+)/',include([
                    url(r'^$',views.UssdDetailViewSet.as_view(), name = 'instance'),
                    url(r'invalidation/',include([
                        url(r'invalidate',views.UssdDetailInvalidate.as_view(), name = 'invalidate'),
                        url(r'list',views.UssdDetailInvalidationList.as_view(), name = 'list'),
                    ],namespace='invalidation'))

                ],namespace='ussd')),
            ],namespace='ussds'),
            ),

        url(r'^companies/',include(
            [
                url(r'^$',views.CompanyViewSet.as_view(),name='info'),
                url(r'^suggest',views.CompanySuggest.as_view(),name='suggest'),
                #url(r'^ussds',views.ussds),
                url(r'^(?P<pk>[0-9]+)/', include([
                    url(r'^$', views.CompanyDetailViewSet.as_view(),name='instance'), #todo
                    url(r'ussds',views.CompanyUSSDDetail.as_view(),name='ussds') #todo
                ],namespace='company')),
            ],namespace='companies')
            ),


        ],namespace='api'))

])

from rest_framework.authtoken import views
urlpatterns += [
    url(r'^api-token-auth/', views.obtain_auth_token)
]