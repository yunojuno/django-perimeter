# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('perimeter', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesstoken',
            name='token',
            field=models.CharField(unique=True, max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='accesstokenuse',
            name='user_email',
            field=models.EmailField(max_length=75, verbose_name='Token used by (email)'),
            preserve_default=True,
        ),
    ]
