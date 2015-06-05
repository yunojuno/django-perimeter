# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import perimeter.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(unique=True, max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('expires_on', models.DateField(default=perimeter.models.default_expiry)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AccessTokenUse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_email', models.EmailField(max_length=254, verbose_name=b'Token used by (email)')),
                ('user_name', models.CharField(max_length=100, verbose_name=b'Token used by (name)')),
                ('client_ip', models.CharField(max_length=15, verbose_name=b'IP address', blank=True)),
                ('client_user_agent', models.CharField(max_length=150, verbose_name=b'User Agent', blank=True)),
                ('timestamp', models.DateTimeField()),
                ('token', models.ForeignKey(to='perimeter.AccessToken')),
            ],
        ),
    ]
