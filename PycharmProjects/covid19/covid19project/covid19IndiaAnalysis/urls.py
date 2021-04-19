from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='covid19-home'),
    path('about/', views.about, name='covid19-about'),
    path('stateComp/',views.stateCompPage, name='covid19-statecomp'),
    path('refreshData/',views.refreshData, name='covid19-refreshData'),
    path('top10States/',views.top10StatesPage, name='covid19-top10States')
]
