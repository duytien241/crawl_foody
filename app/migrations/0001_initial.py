# Generated by Django 2.1.7 on 2020-01-15 03:36

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WebResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.TextField()),
                ('js_url', models.TextField()),
                ('css_url', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('uri', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='WebSourceCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_code', models.TextField()),
                ('title', models.TextField()),
                ('texts', models.TextField()),
                ('imageScreenShot', models.TextField()),
                ('pageHeight', models.IntegerField()),
                ('status', models.TextField()),
                ('original_data', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='web_source', to='app.Website')),
            ],
        ),
        migrations.CreateModel(
            name='WebSubUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_url', models.CharField(max_length=200)),
                ('quantity', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_url', to='app.Website')),
            ],
        ),
        migrations.AddField(
            model_name='webresource',
            name='website',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='web_resource', to='app.Website'),
        ),
        migrations.AlterUniqueTogether(
            name='websuburl',
            unique_together={('website', 'sub_url')},
        ),
    ]
