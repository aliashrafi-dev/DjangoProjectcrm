from django.shortcuts import render, redirect
from multiprocessing import context

def home(request):
    context= {}
    return render(request, 'home.html', {})