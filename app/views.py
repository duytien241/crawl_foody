from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import login as auth_login, authenticate, login as Login
from django.contrib.auth.decorators import login_required
from .models import Address, Website, DataCrawl, Changes
from .forms import RegistrationForm
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.authtoken.models import Token
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
import pytz
from django.utils import timezone
import datetime
from .utils import CrawlWeb, compare_image, compare_edit
from .tasks import add
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import re


def healthz(request):
    return JsonResponse({"result": "OK"})


def home(request):
    page='https://www.instagram.com/ngoctrinh89/?__a=1'
    user = "ngoctrinh89"
    url = 'https://www.instagram.com/' + user
    r = requests.get(url).text
    print(r)
    followers = re.search('"edge_followed_by":{"count":([0-9]+)}',r).group(1)

    print(followers)
    CrawlWeb('1')
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
                          {"result": "Incorrect username or password.",
                           "email": email})
    if req.user.is_authenticated:
        if req.user.is_staff != 0:
            return HttpResponseRedirect('/admin')
        return HttpResponseRedirect('/')
    else:
        return render(req, 'app/templates/pages/login.html')


def websites(req):
    return render(req, 'app/templates/pages/websites.html')


@login_required(login_url="login")
def manageNotificationAddress(request):
    listUrl = Website.objects.filter(user_id=request.user)
    if request.is_ajax():
        url = 'http://127.0.0.1:8000/api/address/'
        token, created = Token.objects.get_or_create(user=request.user)
        headers = {"Authorization": "Token " + token.key}
        if request.GET.get('action') == 'addAddress':
            data = {'typeAddress': request.GET.get('typeAddress'),
                    'address': request.GET.get('address'),
                    'uri_id': request.GET.get('uri'),
                    'active': 1,
                    'user_id': request.user.id}
            r = requests.post(url, data=data, headers=headers)
            if(r.status_code == 201):
                return JsonResponse({"result": "OK"})
            else:
                return r
        elif request.GET.get('action') == 'delAddress':
            url = url + request.GET.get('id') + "/"
            r = requests.delete(url, headers=headers)
            if(r.status_code == 204):
                return JsonResponse({"result": "OK"})
            else:
                return r
        elif request.GET.get('action') == 'editAddress':
            data = {'typeAddress': request.GET.get('typeAddress'),
                    'address': request.GET.get('address'),
                    'uri_id': request.GET.get('uri').strip(),
                    'user_id': request.user.id,
                    'active': request.GET.get('active')}
            url = url + request.GET.get('id') + "/"
            r = requests.put(url, data=data, headers=headers)
            if(r.status_code != 400):
                return JsonResponse({"result": "OK"})
            else:
                return r
    ListAddress = Address.objects.filter(user_id=request.user.id)
    if 'search' in request.GET:
        text = request.GET.get('textsearch')
        filter_address = request.GET.get('filterAddress')
        filter_state = request.GET.get('filterState')
        if(filter_address == 'all'):
            filter_address = ""
        if(filter_state == 'all'):
            ListAddress = Address.objects.filter((Q(address__contains=text) |
                                                  Q(uri_id__uri__contains=text)),
                                                 user_id=request.user.id,
                                                 typeAddress__contains=filter_address)
        else:
            ListAddress = Address.objects.filter((Q(address__contains=text) |
                                                  Q(uri_id__uri__contains=text)),
                                                 user_id=request.user.id,
                                                 typeAddress__contains=filter_address,
                                                 active=filter_state)
    if 'o' in request.GET:
        arr = {'1':'address', '2': '-address', '3': 'uri_id__uri', '4': '-uri_id__uri','5':'typeAddress',
        '6': '-typeAddress', '7': 'active', '8': '-active'}
        print(request.GET.get('o'))
        ListAddress = ListAddress.order_by(arr[request.GET.get('o')])
    paginator = Paginator(ListAddress, 10)
    page = request.GET.get('page', 1)
    try:
        ListAddress_paged = paginator.page(page)
    except PageNotAnInteger:
        ListAddress_paged = paginator.page(1)
    except EmptyPage:
        ListAddress_paged = paginator.page(paginator.num_pages)
    return render(request,
                  'app/templates/pages/manage_address_notify.html',
                  {"ListAddress": ListAddress_paged, "list": listUrl})


@login_required(login_url="login")
def manageNotificationAddressOfUrl(request, id):
    listUrl = Website.objects.filter(user_id=request.user)
    ListAddress = Address.objects.filter(user_id=request.user.id, uri_id=id)
    if 'search' in request.GET:
        text = request.GET.get('textsearch')
        filter_address = request.GET.get('filterAddress')
        filter_state = request.GET.get('filterState')
        if(filter_address == 'all'):
            filter_address = ""
        if(filter_state == 'all'):
            ListAddress = Address.objects.filter(address__contains=text,
                                                 user_id=request.user.id,
                                                 typeAddress__contains=filter_address,
                                                 uri_id=id)
        else:
            ListAddress = Address.objects.filter(address__contains=text,
                                                 user_id=request.user.id,
                                                 typeAddress__contains=filter_address,
                                                 active=filter_state,
                                                 uri_id=id)
    if 'o' in request.GET:
        arr = {'1': 'address', '2': '-address', '3': 'typeAddress',
               '4': '-typeAddress', '5': 'active', '6': '-active'}
        ListAddress = ListAddress.order_by(arr[request.GET.get('o')])
    paginator = Paginator(ListAddress, 10)
    page = request.GET.get('page', 1)
    try:
        ListAddress_paged = paginator.page(page)
    except PageNotAnInteger:
        ListAddress_paged = paginator.page(1)
    except EmptyPage:
        ListAddress_paged = paginator.page(paginator.num_pages)
    return render(request,
                  'app/templates/pages/manage_address_uri.html',
                  {"ListAddress": ListAddress_paged, "list": listUrl})


@login_required(login_url="login")
def viewChanges(request,id):
    #compare_edit(CrawlWeb(uri_id='a2fe5ad6a615496aa149fa06144388be'))
    data = Changes.objects.get(data_crawl_id=id)
    data.img_screen = DataCrawl.objects.get(id=id).imageScreenShot
    data.img_old = DataCrawl.objects.get(id=data.data_old).imageScreenShot
    datas = Changes.objects.all().order_by('-data_crawl_id__timeCrawl')
    for i in datas:
        i.timeCrawl = DataCrawl.objects.get(id=i.data_crawl_id).timeCrawl
    if request.GET.get('active'):
        active = request.GET.get('active')
    else:
        active = 1
    return render(request,
                  'app/templates/pages/changes.html',
                  {"data": data, "active": active, "datas": datas})


@login_required(login_url="login")
def viewHistoryCompare(request, id):
    DataCompare = DataCrawl.objects.filter(uri_id=id).order_by('-timeCrawl')
    if request.is_ajax():
        DataCrawl.objects.filter(original_data=True).update(original_data=False)
        DataCrawl.objects.filter(id=request.GET.get('id')).update(original_data=True)
        return JsonResponse({"result": "ok"})
    for i in DataCompare:
        i.timeCrawl = format_datetime(timezone.localtime(i.timeCrawl), locale='vi_VN')
        try:
            change = Changes.objects.get(data_crawl_id=i.id)
            percent = change.similar_percentages
            i.data_old = DataCrawl.objects.get(id=change.data_old).timeCrawl
            percent = 100 * percent
        except Changes.DoesNotExist:
            percent = -1
        i.similar_percentages = round(percent, 2)
    paginator = Paginator(DataCompare, 10)
    page = request.GET.get('page', 1)
    try:
        DataCompare_paged = paginator.page(page)
    except PageNotAnInteger:
        DataCompare_paged = paginator.page(1)
    except EmptyPage:
        DataCompare_paged = paginator.page(paginator.num_pages)
    return render(request,
                  'app/templates/pages/history_compare.html',
                  {"DataCompare": DataCompare_paged})
