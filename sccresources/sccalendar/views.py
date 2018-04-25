from django.shortcuts import render
from . import google_auth

# Create your views here.
def index(request):
    return render(
        request,
        'index.html',
        #passes the contents of the brackets to the template
        context={},
    )