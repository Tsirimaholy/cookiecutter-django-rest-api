# Generated by Django 4.2.13 on 2024-06-14 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_managers_role'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='role',
            constraint=models.UniqueConstraint(fields=('user', 'name'), name='unique_together_role_user'),
        ),
    ]
