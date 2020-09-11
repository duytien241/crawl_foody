from django.db import models
from django.utils import timezone


# Create your models here.
class Website(models.Model):
    name = models.CharField(max_length=200)
    uri = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class WebSourceCode(models.Model):
    website = models.ForeignKey(
        Website, related_name="web_source", on_delete=models.CASCADE)
    source_code = models.TextField()
    title = models.TextField()
    texts = models.TextField()
    imageScreenShot = models.TextField()
    pageHeight = models.IntegerField()
    status = models.TextField()
    original_data = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __init__(self, website, *args, **kwargs):
        super(WebSourceCode, self).__init__(*args, **kwargs)
        self.website = website


class WebSubUrl(models.Model):
    website = models.ForeignKey(Website,
                                related_name="sub_url",
                                on_delete=models.CASCADE)
    sub_url = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)

    def __init__(self, website, *args, **kwargs):
        super(WebSubUrl, self).__init__(*args, **kwargs)
        self.website = website

    class Meta:
        unique_together = ('website', 'sub_url',)


class WebResource(models.Model):
    website = models.ForeignKey(Website,
                                related_name="web_resource",
                                on_delete=models.CASCADE)
    image_url = models.TextField()
    js_url = models.TextField()
    css_url = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __init__(self, website, *args, **kwargs):
        super(WebResource, self).__init__(*args, **kwargs)
        self.website = website


class TradeMark(models.Model):
    name = models.CharField(max_length=200)
    uri = models.CharField(max_length=200)
    number_store = models.IntegerField(default=0)


class Category(models.Model):
    name = models.CharField(max_length=200)


class District(models.Model):
    district = models.CharField(max_length=200)
    city = models.CharField(max_length=200)

    class Meta:
        unique_together = ('district', 'city')


class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    uri = models.CharField(max_length=200)
    cost = models.TextField()
    rating = models.FloatField(default=0)
    description = models.TextField()
    time_open = models.TextField()
    address = models.TextField()
    image_url = models.TextField()
    category = models.ForeignKey(Category,
                                 related_name="Category",
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True,)
    tradmark = models.ForeignKey(TradeMark,
                                 related_name="trademark",
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True,
                                 )
    district = models.ForeignKey(District,
                                 related_name="district_store",
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True,)


class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant,
                                   related_name="menu_r1estaurant",
                                   on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    total_order = models.IntegerField(default=0)
    price = models.TextField()
    image_url = models.TextField()
