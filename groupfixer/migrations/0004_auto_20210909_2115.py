# Generated by Django 3.1.12 on 2021-09-09 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupfixer', '0003_auto_20190226_2153'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='barn',
            options={'ordering': ['name'], 'verbose_name': 'Fadderbarn', 'verbose_name_plural': 'Fadderbarn'},
        ),
        migrations.AddField(
            model_name='barn',
            name='ntnu_username',
            #the field is unique=True but we need a default because we are adding a new field
            #if you are runnig into unique constraint error try clearing database
            field=models.CharField(default='default', max_length=10, unique=True, verbose_name='NTNU-brukernavn'),
            preserve_default=False,
        ),
    ]