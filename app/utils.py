from .models import Website, WebResource, WebSourceCode, WebSubUrl, Menu, Restaurant, Category, TradeMark, District
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4.element import Comment
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from django.conf import settings
from django.utils import timezone
from webdriver_manager.chrome import ChromeDriverManager
from django.db.models import F
import urllib
import os
import requests
import time
from selenium.common.exceptions import NoSuchElementException


def crawl_web(uri_id):
    links_crawl = Website.objects.all()
    first_time = True
    for crawl in links_crawl:
        print(Website.objects.get(id=crawl.id))

        try:
            website = Website.objects.get(pk=crawl.id)
        except Website.DoesNotExist:
            website = None
        if website is None:
            return
        chrome_options = Options()
        chrome_options.add_argument(settings.ENABLE_OVERLAY_SCROLLBAR)
        chrome_options.add_argument("--window-size=%s" % settings.WINDOW_SIZE)
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("enable-automation")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--dns-prefetch-disable")
        chrome_options.add_argument("--disable-gpu")
        # Setup webdriver selenium use Chrome.
        # Download Webdriver for Chrome and make sure that
        # the same version of Chrome is installed on your machine.
        driver = webdriver.Chrome(
            ChromeDriverManager().install(), chrome_options=chrome_options)
        driver.get(website.uri)
        # disable position fixed and sticky for screenshot
        driver.execute_script('''
        x=document.querySelectorAll('*');
        for(i=0;i<x.length;i++){
            elementStyle=getComputedStyle(x[i]);
            if(elementStyle.position=="fixed"||elementStyle.position=="sticky")
            {x[i].style.position="absolute";}}''')
        if first_time:
            time.sleep(100)
            first_time = False
        time.sleep(1)
        source = WebSourceCode(website)
        fullpage_screenshot(driver, website.id)
        elem = driver.find_element_by_xpath("//html")
        source_code = elem.get_attribute("outerHTML")
        soup = BeautifulSoup(source_code, 'lxml')
        source.title = soup.find('title').string
        texts = soup.findAll(text=True)
        visible_texts = filter(tag_visible, texts)
        # crawl texts
        for t in visible_texts:
            if(len(t.strip()) != 0):
                source.texts = source.texts + t.strip() + '\n'
        source.source_code = source_code
        source.status = requests.get(website.uri).status_code
        last_crawl = WebSourceCode.objects.filter(
            original_data=True, website=website).count()
        if last_crawl == 0:
            source.original_data = True
        get_resource(soup, website)
        get_sub_url(driver, soup, website)


# get sub url
def get_sub_url(driver, soup, website):
    a_links = soup.find_all('a', href=True)
    for links in a_links:
        link = urllib.parse.urljoin(website.uri, links['href'])
        if link.find('http') != -1 and link.find('thanh-vien') == -1 and link.find('o-dau') == -1 and link.find('binh-luan') == -1 and link.find('hinh-anh') == -1 and links.text == links.get('title'):
            if link.find('thuong-hieu') != -1:
                print('thuong hieu' + link)
                crawl_TH(driver, link)
            else:
                crawl_store(driver, link, links.text.strip())
            if WebSubUrl.objects.filter(website=website, sub_url=link).count() == 0:
                web_sub_url = WebSubUrl(website)
                web_sub_url.sub_url = link
            else:
                WebSubUrl.objects.filter(website=website,
                                         sub_url=link).update(quantity=F('quantity') + 1)


# get url of js, css, img
def get_resource(soup, website):
    resource = WebResource(website)
    # find script url
    script_links = soup.find_all('script', src=True)
    for src in script_links:
        src = urllib.parse.urljoin(website.uri, src['src'])
        if src.find('http') != -1:
            resource.js_url = resource.js_url + src + '\n'
    # find css url
    css_links = soup.find_all('link', type='text/css', href=True)
    for src in css_links:
        src = urllib.parse.urljoin(website.uri, src['href'])
        if src.find('http') != -1:
            resource.css_url = resource.css_url + src + '\n'
    # find img url
    img_links = soup.find_all('img', src=True)
    for src in img_links:
        src = urllib.parse.urljoin(website.uri, src['src'])
        if src.find('http') != -1:
            resource.image_url = resource.image_url + src + '\n'
    for tag in soup.findAll(itemprop="image"):
        resource.image_url = resource.image_url + src + '\n'


# set tag visible for crawl texts
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def crawl_TH(driver, uri):
    driver.get(uri)
    time.sleep(1)
    elem = driver.find_element_by_xpath("//html")
    source_code = elem.get_attribute("outerHTML")
    soup = BeautifulSoup(source_code, 'lxml')
    name = soup.find(class_="brand-name")
    tradeMartRes = TradeMark()
    tradeMartRes.uri = uri
    # imgUrl = soup.find(class_="bc-avatar")
    # if imgUrl:
    #     img = imgUrl.find('img', src=True)
    #     if img:
    #         tradeMartRes.
    if name:
        tradeMartRes.name = name.text.strip()
        tradeMartRes.save()
    a_links = soup.find_all('a', href=True)
    count = 0
    for links in a_links:
        link = urllib.parse.urljoin(uri, links['href'])
        if link.find('http') != -1 and link.find('thanh-vien') == -1 and links.text == links.get('title'):
            count = count + 1
            crawl_store(driver, link, links.text.strip(), tradeMartRes)
    tradeMartRes.number_store = count
    tradeMartRes.save()


def crawl_store(driver, uri, name=None, tradmark=None):
    restaurant = Restaurant()
    driver.get(uri)
    time.sleep(2)
    elem = driver.find_element_by_xpath("//html")
    source_code = elem.get_attribute("outerHTML")
    soup = BeautifulSoup(source_code, 'lxml')
    menu = soup.find('a', {"itemprop": "menu"})
    if uri:
        restaurant.uri = uri
    if name:
        restaurant.name = name
    minmaxprice = soup.find(class_="res-common-minmaxprice")
    if minmaxprice:
        restaurant.cost = minmaxprice.text.strip()
    imgPlace = soup.find('img', class_="pic-place", src=True)
    if imgPlace:
        restaurant.image_url = imgPlace['src']
    rating = soup.find(class_="microsite-point-avg")
    timeopen = soup.find(class_="micro-timesopen")
    if timeopen:
        for i in timeopen.find_all('span', text=True):
            restaurant.time_open = i.text.strip()
    address = soup.find(class_="address-restaurant")
    if address:
        restaurant.address = address.text.strip()
    else:
        address = soup.find('span',  {"itemprop": "streetAddress"})
        if address:
            restaurant.address = address.text.strip()
        district = soup.find('span',  {"itemprop": "addressLocality"})
        districtName = ''
        cityName = ''
        if district:
            districtName = district.text.strip()
        city = soup.find('span',  {"itemprop": "addressRegion"})
        if city:
            cityName = city.text.strip()
        category = soup.find(class_="category-items")
        if category:
            restaurant.description = category.getText(separator=u' ')
            cate = category.find('a', href=True)
            if cate:
                tmp = cate.getText(separator=u' ').strip().replace(",", '')
                if Category.objects.filter(name=tmp).count() == 0:
                    cateObj = Category()
                    cateObj.name = tmp
                    restaurant.category = cateObj
                    cateObj.save()
                else:
                    cateObj = Category.objects.get(name=tmp)
                    restaurant.category = cateObj
        else:
            category = soup.find(class_="kind-restaurant")
            if category:
                tmp = category.getText(
                    separator=u' ').strip().replace(",", '')
                if Category.objects.filter(name=tmp).count() == 0:
                    cateObj = Category()
                    cateObj.name = tmp
                    restaurant.category = cateObj
                    cateObj.save()
                else:
                    cateObj = Category.objects.get(name=tmp)
                    restaurant.category = cateObj

        # districObj = District.objects.filter(district=restaurant.district)
        #     districObj.city = city
        # districObj.save()
        #             districObj = District.objects.filter(district=district.text.strip())[0]
        #     restaurant.district = districObj
        if District.objects.filter(district=districtName, city=cityName).count() == 0:
            districObj = District()
            districObj.district = districtName
            districObj.city = cityName
            restaurant.district = districObj
            districObj.save()
        else:
            districObj = District.objects.filter(
                district=districtName, city=cityName)[0]
            restaurant.district = districObj
        if tradmark:
            restaurant.tradmark = tradmark
            tradmark
    if rating:
        if rating.text.strip() == '_._':
            restaurant.rating = 5
        else:
            restaurant.rating = float(rating.text.strip())
        restaurant.save()
    loadmore = soup.find(class_="view-all-menu")
    if loadmore:
        direct = loadmore.find('a', href=True)
        if direct:
            driver.get(direct['href'])
            time.sleep(2)
            elem2 = driver.find_element_by_xpath("//html")
            source_code2 = elem2.get_attribute("outerHTML")
            soup2 = BeautifulSoup(source_code2, 'lxml')
            items = soup2.find_all(class_="item-restaurant-row")
            for item in items:
                menuRes = Menu()
                imgCard = item.find(class_="item-restaurant-img")
                if imgCard:
                    img = imgCard.find('img', src=True)
                    if img:
                        menuRes.image_url = img['src']
                name = item.find(class_="item-restaurant-name")
                if name:
                    menuRes.name = name.text.strip()
                description = item.find(class_="item-restaurant-desc")
                if description:
                    menuRes.description = description.text.strip()
                price = item.find(class_="current-price")
                if price:
                    menuRes.price = price.text.strip()
                menuRes.restaurant = restaurant
                if name and len(name.text.strip()) > 0:
                    menuRes.save()
    else:

        if menu:
            link = urllib.parse.urljoin(uri, menu['href'])
            driver.get(link)
            time.sleep(2)
            elem2 = driver.find_element_by_xpath("//html")
            source_code2 = elem2.get_attribute("outerHTML")
            soup2 = BeautifulSoup(source_code2, 'lxml')
            items = soup2.find_all(class_="microsite-menu-item")
            for item in items:
                menuRes = Menu()
                imgCard = item.find(class_="thumb-dish")
                if imgCard:
                    img = imgCard.find('img', src=True)
                    if img:
                        menuRes.image_url = img['src']
                name = item.find(class_="dish-name")
                if name:
                    menuRes.name = name.text.strip()
                price = item.find(class_="price")
                if price:
                    menuRes.price = price.text.strip()
                menuRes.restaurant = restaurant
                if name and len(name.text.strip()) > 0:
                    menuRes.save()

        # items = soup.find_all( class_="delivery-dishes-item")
        else:
            get_menu(soup, "delivery-dishes-item", restaurant)


def get_menu(soup, className, restaurant):
    items = soup.find_all(class_=className)
    for item in items:
        menuRes = Menu()
        imgCard = item.find(class_="delivery-dishes-item-left")
        if imgCard:
            img = imgCard.find('img', {"src": True})
            if img:
                menuRes.image_url = str(img['src'])
        info = item.find(class_="delivery-dishes-item-right")
        name = info.find(class_="title-name")
        if name:
            menuRes.name = name.text.strip()
        price = info.find(class_="price")
        if price:
            menuRes.price = price.text
        menuRes.restaurant = restaurant
        menuRes.save()
# screenshot website


def fullpage_screenshot(driver, id):
    count_scroll = 0
    while True:
        count_scroll += 1
        if count_scroll != 0:
            time.sleep(0.5)
        time.sleep(1)
        # current_scroll = driver.execute_script(scroll)
        robot = driver.find_element_by_xpath(".//*[@id='scrollLoadingPage']")
        if not(robot) or count_scroll == 40:
            break
        driver.execute_script("arguments[0].click();", robot)
        time.sleep(2)
