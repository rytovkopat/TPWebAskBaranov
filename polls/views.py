from django.http import HttpResponse
from django.template.loader import get_template 
from django.template import Context



def index(request):
    templ = get_template('index.html')
    html = templ.render()
    return HttpResponse(html)


def question(request):
    templ = get_template('ask.html')
    html = templ.render()
    return HttpResponse(html)


def login(request):
    templ = get_template('login.html')
    html = templ.render()
    return HttpResponse(html)

def register(request):
    templ = get_template('signup.html')
    html = templ.render()
    return HttpResponse(html)
