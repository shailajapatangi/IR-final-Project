from django.urls import path
from . import views
urlpatterns = [
    path('', views.getClimateData, name='home-page'),
    path('getCustomResults', views.getCustomResults, name='getCustomResults'),
    path('getGoogleResults', views.getGoogleResults, name='getGoogleResults'),
    path('getBingResults', views.getBingResults, name='getBingResults'),
    path('getClusterResults', views.getClusterResults, name='getClusterResults'),
    path('getQueryExpansionResults', views.getQueryExpansionResults, name='getQueryExpansionResults'),
    path('getSearchQuery', views.getSearchQuery, name='getSearchQuery')
]