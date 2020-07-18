from django.http import HttpResponse
from django.shortcuts import render
from firebaseModels import *


def index(request):
    gate_dict = gate_dataImport('Gates','Gate-1234')
    counting_dict = gate_dataImport('Counting','Occupancy-Jul-12-2020')
    allowed_in = counting_dict["MaxOccupancy"]-counting_dict["Current"]
    wait_time = 0
    if allowed_in > 0:
        return render(request,'mainPage_YES.html',context={'wait_time': wait_time,'allowed_in' : allowed_in})
    else:
        return render(request, 'mainPage_NO.html', context={'wait_time': wait_time, 'allowed_in': allowed_in})

