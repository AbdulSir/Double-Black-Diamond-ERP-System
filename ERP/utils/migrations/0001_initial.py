# Generated by Django 3.1.7 on 2021-03-18 00:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('subject', models.CharField(max_length=100)),
                ('message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='FakeModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmailNotificationUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('sent', models.BooleanField(default=False)),
                ('read', models.DateTimeField(blank=True, null=True)),
                ('email_notification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='utils.emailnotification')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='emailnotification',
            name='users',
            field=models.ManyToManyField(related_name='notifications', through='utils.EmailNotificationUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'content_type', 'object_id')},
            },
        ),
    ]
