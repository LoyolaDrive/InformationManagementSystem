# Generated by Django 5.1.7 on 2025-03-24 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailLevel',
            fields=[
                ('level_id', models.AutoField(primary_key=True, serialize=False)),
                ('level_desc', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='EmailType',
            fields=[
                ('type_id', models.AutoField(primary_key=True, serialize=False)),
                ('type_desc', models.CharField(max_length=200)),
            ],
        ),
    ]
