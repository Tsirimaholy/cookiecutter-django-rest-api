# Generated by Django 4.2.13 on 2024-06-13 16:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import {{cookiecutter.projectslug}}.users.managers
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', {{cookiecutter.projectslug}}.users.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(choices=[('ADMIN', 'Admin')], max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
