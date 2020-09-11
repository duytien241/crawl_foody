# Generated by Django 3.0.4 on 2020-09-09 17:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20200909_2324'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menu',
            name='uri',
        ),
        migrations.AlterField(
            model_name='menu',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Category', to='app.Category'),
        ),
    ]
