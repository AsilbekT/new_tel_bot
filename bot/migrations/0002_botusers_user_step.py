# Generated by Django 3.2.5 on 2021-07-27 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='botusers',
            name='user_step',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]