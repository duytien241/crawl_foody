from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone


class Website(models.Model):
    name = models.CharField(max_length=200)
    uri = models.CharField(max_length=200)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    time_scan = models.FloatField()
    limit_change = models.FloatField()
    def __str__(self):
        return self.name

class web_source_code(models.Model):
    website = models.ForeignKey(Website, related_name="web_source", on_delete=models.CASCADE)
    source_code = models.TextField()
    title = models.TextField()
    texts = models.TextField()
    imageScreenShot = models.TextField()
    pageHeight = models.IntegerField()
    status = models.TextField()
    original_data = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

class web_sub_url(models.Model):
    website = models.ForeignKey(web_source_code, related_name="sub_url", on_delete=models.CASCADE)
    sub_url = models.CharField(max_length=200)

class web_resource(models.Model):
    website = models.ForeignKey(web_source_code, related_name="web_resource", on_delete=models.CASCADE)
    image_url = models.TextField()
    js_url = models.TextField()
    css_url = models.TextField()


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    typeAddress = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    uri_id = models.ForeignKey(Website, on_delete=models.CASCADE)
    active = models.BooleanField()
    imageScreenShot = models.TextField()

    class Meta:
        unique_together = ('typeAddress', 'uri_id', 'address')

class DataCrawl(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uri_id = models.ForeignKey(Website, on_delete=models.CASCADE)
    title = models.TextField()
    source_code = models.TextField()
    texts = models.TextField()
    directions = models.TextField()
    imageScreenShot = models.TextField()
    status = models.TextField()
    pageHeight = models.IntegerField()
    original_data = models.BooleanField(default=False)
    timeCrawl = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.original_data:
            DataCrawl.objects.filter(origin_data=True).update(original_data=False)
        super(DataCrawl, self).save(*args, **kwargs)

class Changes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    similar_percentages = models.FloatField(default=1.0)
    data_crawl = models.ForeignKey(DataCrawl, on_delete=models.CASCADE)
    data_old = models.TextField()
    source_old = models.TextField()
    source_new = models.TextField()
    source_compare = models.TextField()
    source_changes = models.TextField()
    text_old = models.TextField()
    text_new = models.TextField()
    text_compare = models.TextField()
    text_changes = models.TextField()
    directions_old = models.TextField()
    directions_new = models.TextField()
    directions_compare = models.TextField()
    directions_changes = models.TextField()
    image_changes = models.TextField()

    def save(self, *args, **kwargs):
        try:
            DataCrawl.objects.get(id=self.data_old)
        except DataCrawl.DoesNotExist:
            pass
        super(Changes, self).save(*args, **kwargs)
        