# Generated by Django 5.0.6 on 2024-06-27 14:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pic_keywords', models.TextField()),
                ('display_keywords', models.TextField()),
                ('reverse', models.BooleanField(default=False)),
                ('titlebar', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Imgpath',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paths', models.TextField(default='')),
                ('fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webcreatorApp.keyword')),
            ],
        ),
    ]
