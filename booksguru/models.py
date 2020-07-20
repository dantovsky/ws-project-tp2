from django.db import models
import datetime


class Book(models.Model):
    book_id = models.IntegerField(default=0)
    good_reads_book_id = models.IntegerField(default=0)
    isbn = models.CharField(max_length=10)
    isbn13 = models.CharField(max_length=13)
    authors = models.CharField(max_length=250)
    pub_year = models.IntegerField(default=2020)
    title = models.CharField(max_length=250)
    language = models.CharField(max_length=10)
    average_rating = models.FloatField(default=0)
    ratings_count = models.IntegerField(default=0)
    ratings_1 = models.IntegerField(default=0)
    ratings_2 = models.IntegerField(default=0)
    ratings_3 = models.IntegerField(default=0)
    ratings_4 = models.IntegerField(default=0)
    ratings_5 = models.IntegerField(default=0)
    image_url = models.URLField(max_length=500)
    small_image_url = models.URLField()
    language_code = models.CharField(max_length=10)

    def __str__(self):
        return self.title


class Comment(models.Model):
    book_id = models.IntegerField(default=0)
    name = models.CharField(max_length=75, default='Guest')
    comment = models.TextField(max_length=400, default='New comment...')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name
