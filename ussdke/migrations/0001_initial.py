# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-13 08:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('is_template', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='USSD',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('confirmed', models.BooleanField(default=False)),
                ('last_confirmed', models.DateTimeField()),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField()),
                ('code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ussdke.Code')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ussds', related_query_name=b'ussd', to='ussdke.Company')),
            ],
        ),
    ]