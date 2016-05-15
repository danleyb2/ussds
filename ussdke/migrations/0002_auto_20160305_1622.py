# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ussdke', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='icon',
            field=models.ImageField(default='images/icons/default.jpg', upload_to='images/icons'),
        ),
        migrations.AddField(
            model_name='company',
            name='website',
            field=models.URLField(default='/'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ussd',
            name='company',
            field=models.ForeignKey(related_name='ussds', to='ussdke.Company', related_query_name='ussd'),
        ),
    ]
