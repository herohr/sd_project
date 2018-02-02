# Generated by Django 2.0.1 on 2018-02-01 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sd_project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageStorage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField()),
                ('verified', models.BooleanField(default=False)),
                ('oss_key', models.CharField(max_length=512)),
                ('create_time', models.DateTimeField()),
            ],
        ),
    ]