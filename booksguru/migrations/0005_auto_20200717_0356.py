# Generated by Django 3.0.5 on 2020-07-17 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booksguru', '0004_auto_20200717_0035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='book_id',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='comment',
            field=models.TextField(max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='name',
            field=models.CharField(max_length=75, null=True),
        ),
    ]