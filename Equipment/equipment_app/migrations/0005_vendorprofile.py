# Generated by Django 5.1.6 on 2025-02-25 09:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment_app', '0004_remove_userprofile_is_active_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('phone_number', models.CharField(max_length=15)),
                ('business_license', models.FileField(upload_to='business_licenses/')),
                ('is_approved', models.BooleanField(default=False)),
                ('payment_details', models.JSONField(default=dict)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
