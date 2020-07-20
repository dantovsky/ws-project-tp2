from django.urls import path, include
from . import views
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index_raw'),
    path('booksguru/Books', views.search_books, name='search_books'),
    path('booksguru/ShowBooks', views.show_books, name='show_books'),
    path('booksguru/Book/<str:book_id>', views.book_details, name='book_details'),
    path('booksguru/MostRecent', views.most_recent, name='most_recent'),
    path('booksguru/TopRated', views.top_rated, name='top_rated'),
    path('booksguru/MostPopular', views.most_popular, name='most_popular'),
    path('booksguru/404Error', views.error, name='error'),
    path('booksguru/About', views.about, name='about'),
    path('booksguru/Terms', views.terms, name='terms'),
    path('booksguru/', views.index, name='index'),
    path("signup/", views.signup, name="signup"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('post_comment/<str:book_id>', views.post_comments_controller, name='post_comment'),
]
