from django.shortcuts import render
from django.http import HttpResponse
#import matplotlib.pyplot as plt
import sys
sys.path.append('covid19IndiaAnalysis/covid19/')
import project
from .forms import InputForm,StateCompForm,Top10StatesForm
import datetime
# Create your views here.

def home(request):
    res = project.show_misc_plots()
    #print(res)
    return render(request, 'covid19IndiaAnalysis/home.html', {'data1':res['uri1'], 'data2':res['uri2']})

def stateAnalysis(request):
    details = InputForm(request.GET)
    uri=""
    state="TT"
    start_date = datetime.date(year=2020, month=1, day=1)
    end_date = datetime.date(year=2021, month=12, day=31)
    categories = ['Confirmed']
    type = 'Daily '
    typeOfChart = "line"
    # print(request.GET.get('state'))
    if (request.GET.get('state')):
        state = request.GET.get('state')
    if (request.GET.get('start_date')):
        start_date = request.GET.get('start_date')
    if (request.GET.get('end_date')):
        end_date = request.GET.get('end_date')
    if (request.GET.get('categories')):
        categories = request.GET.getlist('categories')
    if (request.GET.get('type')):
        type = request.GET.get('type')
    if (request.GET.get('typeOfChart')):
        typeOfChart = request.GET.get('typeOfChart')

    #print(request.GET.getlist('categories'))

    if details.is_valid():
        uri = project.show_plot(state,start_date,end_date,categories,type,typeOfChart)
        #vacc_uri = project.show_vacc_plot(state, start_date, end_date)
    return render(request, 'covid19IndiaAnalysis/stateAnalysis.html', {'data':uri,'state':state,'categories':categories,'type':type,'form':InputForm(initial={'state': state,'start_date':start_date,'end_date':end_date,'categories':categories,'type':type,'typeOfChart':typeOfChart})})


def about(request):
    return render(request, 'covid19IndiaAnalysis/about.html')


def stateCompPage(request):
    details = StateCompForm(request.GET)
    uri=""
    state1="MH"
    state2="MP"
    start_date = datetime.date(year=2020, month=1, day=1)
    end_date = datetime.date(year=2021, month=12, day=31)
    category = ['Confirmed']
    type = 'Daily '
    typeOfChart = "line"
    # print(request.GET.get('state'))
    if (request.GET.get('state1')):
        state1 = request.GET.get('state1')
    if (request.GET.get('state2')):
        state2 = request.GET.get('state2')
    if (request.GET.get('start_date')):
        start_date = request.GET.get('start_date')
    if (request.GET.get('end_date')):
        end_date = request.GET.get('end_date')
    if (request.GET.get('category')):
        category = request.GET.get('category')
    if (request.GET.get('type')):
        type = request.GET.get('type')
    if (request.GET.get('typeOfChart')):
        typeOfChart = request.GET.get('typeOfChart')

    #print(request.GET.getlist('categories'))

    if details.is_valid():
        uri = project.show_sc_plot(state1,state2,start_date,end_date,category,type,typeOfChart)
        #vacc_uri = project.show_vacc_plot(state, start_date, end_date)
    return render(request, 'covid19IndiaAnalysis/stateComp.html', {'data':uri,'state1':state1,'state2':state2,'category':category,'type':type,'form':StateCompForm(initial={'state1': state1,'state2':state2,'start_date':start_date,'end_date':end_date,'category':category,'type':type,'typeOfChart':typeOfChart})})

def refreshData(request):
    project.load_data()
    return HttpResponse("Data loaded successfully")

def top10StatesPage(request):
    details = Top10StatesForm(request.GET)
    uri=""
    as_of_date = datetime.date(year=2021, month=1, day=31)
    category = ['Confirmed']
    type = 'Daily '
    # print(request.GET.get('state'))
    if (request.GET.get('as_of_date')):
        as_of_date = request.GET.get('as_of_date')
    if (request.GET.get('category')):
        category = request.GET.get('category')
    if (request.GET.get('type')):
        type = request.GET.get('type')

    #print(request.GET.getlist('categories'))

    if details.is_valid():
        uri = project.show_t10_plot(as_of_date,category,type)
        #vacc_uri = project.show_vacc_plot(state, start_date, end_date)
    return render(request, 'covid19IndiaAnalysis/stateComp.html', {'data':uri,'category':category,'type':type,'form':Top10StatesForm(initial={'as_of_date':as_of_date,'category':category,'type':type})})