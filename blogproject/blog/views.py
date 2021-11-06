from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
#from django.views.generic import ListView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count


def post_search(request):

    # Declare form query and result variables
    form = SearchForm()
    query = None
    results = []

    # Conditions for query
    if 'query' in request.GET:
        form = SearchForm(request.GET)

        # Form validation
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.objects.annotate(search=search_vector, rank=SearchRank(search_vector, search_query))\
                                  .filter(search=search_query).order_by('-rank')

    return render(request, 'blog/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page,
                                                   'posts': posts,
                                                   'tag': tag})


# Showing post details
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    comments = post.comments.filter(active=True)

    if request.method == 'POST':
        # Comment was published
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create comment object
            new_comment = comment_form.save(commit=False)
            # Add comment to Post
            new_comment.post = post
            # Save comment in Database
            new_comment.save()
            comment_form=CommentForm()
    else:
        comment_form = CommentForm()

    # Get all ids from tags in post in list
    post_tags_ids = post.tags.values_list('id', flat=True)

    # Get all published posts which have the same tags, without currrent post
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)

    # Count tags
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'comment_form': comment_form,
                                                     'similar_posts': similar_posts})


# Sharing posts
def post_share(request, post_id):
    email_from = 'uru1996@gmail.com'
    # Get post based on ID
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Veryfing post is success
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) Zachęca do przeczytania "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Przeczytaj post "{}" na stronie {}\n \n Komentarz dodany przez {}: {} '.format(post.title,
                                                                                                      post_url,
                                                                                                      cd['name'],
                                                                                                      cd['comments'])
            send_mail(subject, message, email_from, [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
