# Generated by Django 3.2.5 on 2021-08-04 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_auto_20210804_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='botusers',
            name='text',
            field=models.TextField(blank=True),
        ),
    ]