from .models import Website, Changes, web_resource, web_source_code, web_sub_url
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4.element import Comment
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from diff_match_patch import diff_match_patch
import urllib
import os
import requests
from django.utils import timezone
import numpy as np
import cv2
import time
from django.conf import settings
from webdriver_manager.chrome import ChromeDriverManager


def CrawlWeb(uri_id):
    # website = Website.objects.get(id=uri_id)
    # if website is None:
    #     return ;
    chrome_options = Options()
    WINDOW_SIZE = settings.WINDOW_SIZE
    chrome_options.add_argument("--enable-overlay-scrollbar")
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    driver = webdriver.Chrome(executable_path=os.getenv('Webdriver', ChromeDriverManager().install()),
                              chrome_options=chrome_options)
    driver.get('https://www.instagram.com/ngoctrinh89')
    time.sleep(3)
    # web_source = web_source_code()
    # resource = web_resource()
    # sub_url = web_sub_url()
    # web_source.website = website
    elem = driver.find_element_by_xpath("//html")
    source_code = elem.get_attribute("outerHTML")
    # web_source.pageHeight, web_source.imageScreenShot = fullpage_screenshot(driver,
    #                                                             website.id,
    #                                                             website.user_id.username)
    # driver.close()
    soup = BeautifulSoup(source_code, 'lxml')
    # web_source.title = soup.find('title').string
    texts = soup.findAll(text=True)
    print(texts)
    # visible_texts = filter(tag_visible, texts)
    followers= soup.find_element_by_xpath('.//*[contains(text(), "followers")]/span')
    print(followers)
    # for t in visible_texts:
    #     if(len(t.strip()) != 0):
    #         web_source.texts = web_source.texts + t.strip() + '\n'
    # web_source.source_code = source_code
    # script = ''
    # script_links = soup.find_all('script', src=True)
    # for src in script_links:
    #     src = urllib.parse.urljoin(website.uri, src['src'])
    #     if src.find('http') != -1:
    #         script = script + src + '\n'
    # resource.js_url = script
    # css = ''
    # css_links = soup.find_all('link', src=True)
    # for src in script_links:
    #     src = urllib.parse.urljoin(website.uri, src['src'])
    #     if src.find('http') != -1:
    #         css = css + src + '\n'
    # resource.css_url = css
    # img_links = soup.find_all('img', src=True)
    # img = ''
    # for src in img_links:
    #     src = urllib.parse.urljoin(website.uri, src['src'])
    #     if src.find('http') != -1:
    #         img = img + src + '\n'
    # resource.image_url = img
    # a_links = soup.find_all('a',href=True)
    # derections = ''
    # for links in a_links:
    #     link = urllib.parse.urljoin(website.uri, links['href'])
    #     if link.find('http') != -1:
    #         derections = derections + link + '\n'
    # sub_url.directions = derections
    # web_source.status = requests.get(website.uri).status_code
    # last_crawl = web_source_code.objects.filter(original_data=True)
    # if not last_crawl:
    #     web_source.original_data = True
    # web_source.save()
    # return web_source


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def fullpage_screenshot(driver, uri, username):
    js = """ return Math.max(document.body.offsetHeight,
                            document.body.scrollHeight,
                            document.documentElement.scrollHeight,
                            document.documentElement.offsetHeight,
                            document.documentElement.clientHeight);"""
    scroll = 'return window.pageYOffset'
    scrollheight = driver.execute_script(js)
    first_shot = 0
    slices = []
    offset = 0
    last_scroll = -1
    count_scroll = 0
    scrollbar_height = 0
    while offset < scrollheight:
        scrollheight_current = driver.execute_script(js)
        if scrollheight < scrollheight_current:
            count_scroll += 1
            scrollheight = scrollheight_current
        if count_scroll == 3:
            break
        driver.execute_script("window.scrollTo(0, %s);" % offset)
        if count_scroll != 0:
            time.sleep(0.5)
        time.sleep(0.5)
        img = Image.open(BytesIO(driver.get_screenshot_as_png()))
        current_scroll = driver.execute_script(scroll)
        if last_scroll == current_scroll:
            break
        else:
            if len(slices) > 0:
                img_tmp = slices[len(slices) - 1]
                slices[len(slices) - 1] = img_tmp.crop((0, 0, img_tmp.size[0],
                                                        img_tmp.size[1] - first_shot))
            img = img.crop((0, first_shot, img.size[0], img.size[1]))
            scrollbar_height = img.size[1] + 100
            offset = offset + img.size[1] - (200 - first_shot)
        last_scroll = current_scroll
        slices.append(img)
        first_shot = 100
    screenshot = Image.new('RGB', (slices[0].size[0], scrollheight))
    last_scroll += scrollbar_height
    offset = 0
    print(timezone.now())
    for i in range(len(slices)):
        if i == len(slices) - 1 and len(slices) > 1:
            slices[i] = slices[i].crop((0,
                                        slices[i].size[1] - (last_scroll - offset),
                                        slices[i].size[0],
                                        slices[i].size[1]))
        screenshot.paste(slices[i], (0, offset))
        offset += slices[i].size[1]
    screenshot = screenshot.crop((0,
                                  0,
                                  driver.execute_script('return document.body.offsetWidth;'),
                                  offset))
    if not os.path.exists('app/static'):
        os.mkdir('app/static')
    if not os.path.exists('app/static/screenshot'):
        os.mkdir('app/static/screenshot')
    if not os.path.exists('app/static/screenshot/%s' % username):
        os.mkdir('app/static/screenshot/%s' % username)
    time_scan = str(timezone.localtime())
    screenshot.save('app/static/screenshot/%s/%s_%s.png' % (username,
                                                            uri,
                                                            time_scan.replace(" ", "_")
                                                                     .replace(":", "_")))
    return offset, ('/screenshot/%s/%s_%s.png' % (username,
                                                  uri,
                                                  time_scan.replace(" ", "_")
                                                           .replace(":", "_")))


def compare_edit(data):
    data_old = DataCrawl.objects.filter(original_data=True, uri_id=data.uri_id)[0]
    dmp = SideBySideDiff()
    dmp.Diff_Timeout = 0.0
    s_html = dmp.diff_main(data_old.source_code, data.source_code)
    s_text = dmp.diff_main(data_old.texts, data.texts)
    s_direction = dmp.diff_main(data_old.directions, data.directions)
    common_text = sum([len(txt) for op, txt in s_html if op == 0])
    text_length = max(len(data_old.source_code), len(data.source_code))
    sim = common_text / text_length
    a = Changes()
    a.similar_percentages = sim
    a.data_crawl = data
    a.data_old = data_old.id
    a.source_old = dmp.old_content(s_html)
    a.source_new = dmp.new_content(s_html)
    a.source_compare = dmp.diff_prettyHtml(s_html).replace("&para;", "")
    a.source_changes = dmp.diff_prettyHtml2(s_html)
    a.text_old = dmp.old_content(s_text)
    a.text_new = dmp.new_content(s_text)
    a.text_compare = dmp.diff_prettyHtml(s_text).replace("&para;", "")
    a.text_changes = dmp.diff_prettyHtml2(s_text)
    a.directions_old = dmp.old_content(s_direction)
    a.directions_new = dmp.new_content(s_direction)
    a.directions_compare = dmp.diff_prettyHtml(s_direction).replace("&para;", "")
    a.directions_changes = dmp.diff_prettyHtml2(s_direction)
    link_img_compare = data.imageScreenShot.rstrip('.png') + '_compare.png'
    print(link_img_compare)
    compare_image('app/static' + data.imageScreenShot,
                  'app/static' + data_old.imageScreenShot,
                  link_img_compare)
    a.image_changes = link_img_compare
    a.save()


class SideBySideDiff(diff_match_patch):

    def old_content(self, diffs):
        html = []
        for (flag, data) in diffs:
            text = (data.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\n", "<br>"))

            if flag == self.DIFF_DELETE:
                html.append('<del style=\"background:#ffe6e6;">%s</del>' % text)
            elif flag == self.DIFF_EQUAL:
                html.append("<span>%s</span>" % text)
        return "".join(html)

    def new_content(self, diffs):
        html = []
        for (flag, data) in diffs:
            text = (data.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\n", "<br>"))
            if flag == self.DIFF_INSERT:
                html.append('<ins style="background:#e6ffe6;">%s</ins>' % text)
            elif flag == self.DIFF_EQUAL:
                html.append("<span>%s</span>" % text)
        return "".join(html)

    def diff_prettyHtml2(self, diffs):
        html = []
        for (flag, data) in diffs:
            text = (data.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\n", "<br>"))
            if flag == self.DIFF_INSERT:
                html.append('<ins style="background:#e6ffe6;">%s</ins>' % text)
            elif flag == self.DIFF_DELETE:
                html.append('<del style="background:#ffe6e6;">%s</del>' % text)
            else:
                html.append('<br>')
        if(("".join(html)) == '<br>'):
            return '<br>Không có sự thay đổi nào ở lần quét này!'
        return "".join(html)


def overlayImages(background_img, img_to_overlay_t, x, y, overlay_size=None):
    bg_img = background_img.copy()

    if overlay_size is not None:
        img_to_overlay_t = cv2.resize(img_to_overlay_t.copy(), overlay_size)
    # Extract the alpha mask of the RGBA image, convert to RGB
    b, g, r, a = cv2.split(img_to_overlay_t)
    overlay_color = cv2.merge((b, g, r))

    # Apply some simple filtering to remove edge noise
    mask = cv2.medianBlur(a, 1)

    h, w, _ = overlay_color.shape
    roi = bg_img[y:y + h, x:x + w]

    # Black-out the area behind the logo in our original ROI
    img1_bg = cv2.bitwise_and(roi.copy(), roi.copy(), mask=cv2.bitwise_not(mask))

    # Mask out the logo from the logo image.
    img2_fg = cv2.bitwise_and(overlay_color, overlay_color, mask=mask)

    # Update the original image with our new ROI
    bg_img[y:y + h, x:x + w] = cv2.add(img1_bg, img2_fg)

    return bg_img


def compare_image(imagebefore_link, imageafter_link, comparedImage_link):
    image1 = cv2.imread(imagebefore_link)
    image2 = cv2.imread(imageafter_link)
    difference = cv2.subtract(image1, image2)
    # if difference is all zeros it will return False
    result = not np.any(difference)
    if result is True:
        return "The images are the same"
    else:
        imageFile = 'app/static' + comparedImage_link
        colors_high = np.array([255, 255, 255])
        colors_lo1 = np.array([1, 0, 0])
        mask1 = cv2.inRange(difference, colors_lo1, colors_high)
        colors_lo2 = np.array([0, 1, 0])
        mask2 = cv2.inRange(difference, colors_lo2, colors_high)
        colors_lo3 = np.array([0, 0, 1])
        mask3 = cv2.inRange(difference, colors_lo3, colors_high)
        difference[mask1 > 0] = (255, 0, 0)
        difference[mask2 > 0] = (255, 0, 0)
        difference[mask3 > 0] = (255, 0, 0)
        image = cv2.cvtColor(difference, cv2.COLOR_BGR2RGBA)
        image[np.all(image == [0, 0, 0, 255], axis=2)] = [0, 0, 0, 0]
        cv2.imwrite(imageFile, image)
        time.sleep(2)
        image3 = cv2.imread(imageFile, -1)
        finalImage = overlayImages(image1, image3, 0, 0)
        cv2.imwrite(imageFile, finalImage)
        return "the images are different"
