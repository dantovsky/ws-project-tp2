# Generated by Django 3.0.5 on 2020-07-17 00:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booksguru', '0003_comment_created_on'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='created_on',
            new_name='created_at',
        ),
    ]