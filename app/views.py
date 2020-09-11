from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import login as auth_login, authenticate, login as Login
from .forms import RegistrationForm
from app.utils import crawl_web


def healthz(request):
    return JsonResponse({"result": "OK"})


def home(request):
    return render(request, 'app/templates/pages/home.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return HttpResponseRedirect('/')
        else:
            return render(request, 'app/templates/pages/register.html', {"form": form})
    if request.user.is_authenticated:
        if request.user.is_staff != 0:
            return HttpResponseRedirect('/admin')
        return HttpResponseRedirect('/')
    else:
        form = RegistrationForm()
        return render(request, 'app/templates/pages/register.html', {'form': form})


def login(req):
    if req.method == 'POST':
        email = req.POST.get('email').strip()
        password = req.POST.get('password').strip()
        user = authenticate(username=email,
                            password=password)
        if user is not None:
            auth_login(req, user)
            if user.is_staff != 0:
                return HttpResponseRedirect('/admin')
            return HttpResponseRedirect('/')
        else:
            return render(req, 'app/templates/pages/login.html',
                          {"result": "Tài khoản hoặc mật khẩu sai.",
                           "email": email})
    elif req.user.is_authenticated:
        if req.user.is_staff != 0:
            return HttpResponseRedirect('/admin')
        return HttpResponseRedirect('/')
    else:
        return render(req, 'app/templates/pages/login.html')


def password_reset(req):
    return render(req, 'app/templates/pages/password_reset.html')


def websites(req):
    crawl_web(uri_id="12")
    return render(req, 'app/templates/pages/websites.html')
    
