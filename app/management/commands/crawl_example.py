from app.models import Website
from app.utils import crawl_web
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crawl example website"

    def handle(self, *args, **options):
        try:
            website = Website(name="tiki", uri="https://tiki.vn/dien-thoai-may-tinh-bang")
            website.save()
        except KeyError as key_error:
            self.stderr.write(self.style.ERROR(f'Missing Key: "{key_error}"'))
        crawl_web(website.id)
        self.stdout.write(self.style.SUCCESS('Crawl successfully, see results in the database'))
