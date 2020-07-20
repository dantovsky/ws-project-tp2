import json
import urllib

from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from django.shortcuts import render, redirect
from .models import Book, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Imports from new implementations
from .forms import SignUpForm
from django.contrib.auth import login, authenticate
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseBadRequest


endpoint = "http://localhost:7200"
repo_name = "booksguru"
client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)
numb_results_per_page = 18


def index(request):
    """ This function runs three queries to return a set of book to show on home page. """
    top_recent = []
    popular = []
    best_rated = []
    query = """
        PREFIX books: <http://books.com/resource/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT ?title ?image ?rating ?id
        WHERE { 
            ?s books:original_title ?title .
            ?s books:image_url ?image .
            ?s books:average_rating ?rating .
            ?s books:book_id ?id .
            ?s books:original_publication_year ?year .
        } ORDER BY DESC(xsd:decimal(?year))
        LIMIT 12
        """
    query2 = """
        PREFIX books:<http://books.com/resource/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?title ?image ?rating ?id
        WHERE {
            ?s books:original_title ?title .
            ?s books:image_url ?image .
            ?s books:average_rating ?rating .
            ?s books:book_id ?id .
            ?s books:work_ratings_count ?work_ratings_count .
        } ORDER BY DESC (xsd:integer(?work_ratings_count))
        LIMIT 12
    """
    query3 = """
        PREFIX books:<http://books.com/resource/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?title ?image ?rating ?id
        WHERE {
            ?s books:original_title ?title .
            ?s books:book_id ?id .
            ?s books:image_url ?image .
            ?s books:average_rating ?rating .
            ?s books:work_ratings_count ?work_ratings_count .
            filter (xsd:integer(?work_ratings_count) > 1000) .
        } ORDER BY DESC (?rating)
        LIMIT 12
    """
    payload_query = {"query": query}
    payload_query2 = {"query": query2}
    payload_query3 = {"query": query3}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res2 = accessor.sparql_select(body=payload_query2, repo_name=repo_name)
    res3 = accessor.sparql_select(body=payload_query3, repo_name=repo_name)
    res = json.loads(res)
    res2 = json.loads(res2)
    res3 = json.loads(res3)

    for e in res['results']['bindings']:
        top_recent.append(Book(title=e['title']['value'], image_url=e['image']['value'],
                               average_rating=e['rating']['value'], book_id=e['id']['value']))

    for e in res2['results']['bindings']:
        popular.append(Book(title=e['title']['value'], image_url=e['image']['value'],
                            average_rating=e['rating']['value'], book_id=e['id']['value']))

    for e in res3['results']['bindings']:
        best_rated.append(Book(title=e['title']['value'], image_url=e['image']['value'],
                               average_rating=e['rating']['value'], book_id=e['id']['value']))

    context = {'top_recent': top_recent, 'popular': popular, "top_rated": best_rated, }
    return render(request, 'booksguru/index.html', context)


def search_books(request):
    """ Query used to searching books. """
    books = list()
    identifier = request.POST.get('search', None)
    type_identifier = request.POST.get('select', 'book')
    page = request.GET.get('page', 1)
    query = None

    if page == 1:
        request.session['identifier'] = identifier
        request.session['type_identifier'] = type_identifier

    else:
        type_identifier = request.session['type_identifier']
        identifier = request.session['identifier']

    if type_identifier == 'book':
        query = """
            PREFIX books: <http://books.com/resource/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
            SELECT ?title ?image ?rating ?isbn ?isbn13 ?authors ?id ?otherId ?language
            WHERE { 
                ?s books:original_title ?title .
                ?s books:image_url ?image .
                ?s books:average_rating ?rating .
                ?s books:book_id ?id .
                filter( regex(lcase(str(?title)), """ + "\'" + str.lower(identifier) + "\'" + """)) .
            }
        """
    elif type_identifier == 'isbn':
        query = """
            PREFIX books: <http://books.com/resource/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            
            SELECT ?title ?image ?rating ?id
            WHERE { 
                ?s books:original_title ?title .
                ?s books:image_url ?image .
                ?s books:average_rating ?rating .
                ?s books:book_id ?id .
                ?s books:isbn ?isbn .
                filter( regex(str(?isbn), """ + "\'" + identifier + "\'" + """)) .
            }
        """
    elif type_identifier == 'isbn13':
        query = """
           PREFIX books: <http://books.com/resource/>
           PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
           
           SELECT ?title ?image ?rating ?id
           WHERE { 
                ?s books:original_title ?title .
               ?s books:image_url ?image .
               ?s books:average_rating ?rating .
               ?s books:book_id ?id .
               ?s books:isbn13 ?isbn13 .
               filter( regex(str(?isbn13), """ + "\'" + identifier + "\'" + """)) .
            }
        """
    elif type_identifier == 'author':
        query = """
            PREFIX books: <http://books.com/resource/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?title ?image ?rating ?id
            WHERE { 
                ?s books:original_title ?title .
                ?s books:image_url ?image .
                ?s books:average_rating ?rating .
                ?s books:book_id ?id .
                ?s books:authors ?authors.
                filter( regex(lcase(str(?authors)), """ + "\'" + str.lower(identifier) + "\'" + """)) .
            }
        """
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)

    for e in res['results']['bindings']:
        books.append(Book(title=e['title']['value'], image_url=e['image']['value'],
                          book_id=e['id']['value'], average_rating=float(e['rating']['value'])))

    paginator = Paginator(books, numb_results_per_page)

    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

    if page == 1 and len(books) == 0:
        return render(request, 'booksguru/404.html')
    else:
        context = {'size': len(books), 'results': results}
        return render(request, 'booksguru/bookgridfw.html', context)


def show_books(request):
    """ Query to show all books. """
    books = list()
    page = request.GET.get('page', 1)
    query = """
        PREFIX books:<http://books.com/resource/>
        SELECT ?title ?image ?rating ?id
        WHERE { 
            ?s books:original_title ?title .
            ?s books:image_url ?image .
            ?s books:average_rating ?rating .
            ?s books:book_id ?id .
        }
    """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)

    for e in res['results']['bindings']:
        books.append(Book(title=e['title']['value'], image_url=e['image']['value'],
                          book_id=e['id']['value'], average_rating=e['rating']['value']))

    paginator = Paginator(books, numb_results_per_page)

    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

    context = {'size': len(books), 'results': results}
    return render(request, 'booksguru/bookgridfw.html', context)


def most_recent(request):
    """ Query for most recent books. """
    books = list()
    page = request.GET.get('page', 1)

    query = """
        PREFIX books:<http://books.com/resource/>
        SELECT ?title ?image ?rating ?id
        WHERE { 
            ?s books:original_title ?title .
            ?s books:image_url ?image .
            ?s books:average_rating ?rating .
            ?s books:book_id ?id .
            ?s books:original_publication_year ?year .
        } ORDER BY DESC(xsd:decimal(?year))
    """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)

    for e in res['results']['bindings']:
        books.append(Book(title=e['title']['value'], image_url=e['image']['value'],
                          book_id=e['id']['value'], average_rating=e['rating']['value']))

    paginator = Paginator(books, numb_results_per_page)

    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

    context = {'size': len(books), 'results': results}
    return render(request, 'booksguru/mostRecent.html', context)


def top_rated(request):
    """ Query for top rated books. """
    books = list()
    page = request.GET.get('page', 1)

    query = """
        PREFIX books:<http://books.com/resource/>
        SELECT ?title ?image ?rating ?id
        WHERE { 
            ?s books:original_title ?title .
            ?s books:image_url ?image .
            ?s books:average_rating ?rating .
            ?s books:book_id ?id .
        } ORDER BY DESC (?rating)
    """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)

    for e in res['results']['bindings']:
        books.append(Book(title=e['title']['value'], image_url=e['image']['value'],
                          book_id=e['id']['value'], average_rating=e['rating']['value']))

    paginator = Paginator(books, numb_results_per_page)

    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

    context = {'size': len(books), 'results': results}
    return render(request, 'booksguru/topRated.html', context)


def most_popular(request):
    """ Query for most popular books. """
    books = list()
    page = request.GET.get('page', 1)

    query = """
        PREFIX books:<http://books.com/resource/>
        SELECT ?title ?image ?rating ?id
        WHERE { 
            ?s books:original_title ?title .
            ?s books:image_url ?image .
            ?s books:average_rating ?rating .
            ?s books:book_id ?id .
            ?s books:work_ratings_count ?work_ratings_count .
        } ORDER BY DESC (xsd:integer(?work_ratings_count))
    """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)

    for e in res['results']['bindings']:
        books.append(Book(title=e['title']['value'], image_url=e['image']['value'],
                          book_id=e['id']['value'], average_rating=e['rating']['value']))

    paginator = Paginator(books, numb_results_per_page)

    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

    context = {'size': len(books), 'results': results, 'numb_books': numb_results_per_page}
    return render(request, 'booksguru/mostPopular.html', context)


def error(request):
    """ This function to return  a 404 page not found. """
    return render(request, 'booksguru/404.html',)


def book_details(request, book_id):
    """ This function get all information about one book, from your ID catched on URL. """
    book = None
    query = """
        PREFIX books:<http://books.com/resource/>
        SELECT ?id ?title ?image_url ?authors ?rating ?pub_year ?ratings_count ?isbn13 ?language_code
        WHERE { 
            ?s books:book_id ?id .
            ?s books:original_title ?title .
            ?s books:image_url ?image_url .
            ?s books:authors ?authors .
            ?s books:average_rating ?rating .
            ?s books:original_publication_year ?pub_year .
            ?s books:work_ratings_count ?ratings_count .
            ?s books:isbn13 ?isbn13 .
            ?s books:language_code ?language_code .
            ?s books:book_id """ + "\'" + book_id + "\'" + """ .
        }
    """

    # Searching book

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)

    for e in res['results']['bindings']:
        book = Book(title=e['title']['value'], image_url=e['image_url']['value'],
                    authors=e['authors']['value'], book_id=e['id']['value'],
                    average_rating=e['rating']['value'], pub_year=e['pub_year']['value'],
                    ratings_count=e['ratings_count']['value'], isbn13=e['isbn13']['value'], language_code=e['language_code']['value'])

    print('\n\n', book.__dict__)

    # Searching comments for one book

    comments = Comment.objects.filter(book_id=book_id)

    return render(request, 'booksguru/bookDetails.html', {'book': book, 'comments': comments})


def terms(request):
    return render(request, 'booksguru/terms.html')


def about(request):
    """ About page """
    return render(request, 'booksguru/about.html')


def signup(request):
    print('\n\nEntrou no signup')
    """ Signup page to register new users """
    form = SignUpForm(request.POST)
    if form.is_valid():
        print('Form é válido')
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('index_raw')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def post_comments_controller(request, book_id):
    """ Allow a user post a comment for a book. """
    from .forms import CommentForm

    comment_form = CommentForm(request.POST or None)
    # print(comment_form.errors)
    # print(request.POST)

    if comment_form.is_valid():
        print('\nO form é valido!\n')
        comment_obj = comment_form.save(commit=False)
        comment_obj.book_id = book_id
        comment_obj.name = request.user.first_name + ' ' + request.user.last_name
        comment_obj.save()
        # return HttpResponse("Done")
        return redirect('/booksguru/Book/' + book_id)
    else:
        print('\nO form não é valido!\n')
        return HttpResponseBadRequest()
        # return None
        # return redirect('/booksguru/Book/' + book_id)