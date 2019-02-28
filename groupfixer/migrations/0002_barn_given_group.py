# Generated by Django 2.1.7 on 2019-02-20 14:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groupfixer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='barn',
            name='given_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member', to='groupfixer.Gruppe', verbose_name='Tildelt gruppe'),
        ),
    ]