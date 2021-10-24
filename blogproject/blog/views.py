from django.shortcuts import render, get_object_or_404
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post
from django.views.generic import ListView
from .forms import EmailPostForm
from django.core.mail import send_mail


# Showing posts on main page
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


# Showing post details
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request, 'blog/post/detail.html', {'post': post})


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
            post_url = request.build_absolute_url(post.get_absolute_url())
            subject = '{} ({}) Zachęca do przeczytania "{}"'.format(cd['name'], ['email'], post.title)
            message = 'Przeczytaj post "{}" na stronie {}\n \n Komentarz dodany przez {}: {} '.format(post.title,
                                                                                                      post_url,
                                                                                                      cd['name'],
                                                                                                      cd['comments'])
            send_mail(subject, message, email_from, [cd['to']])
            sent = True
        else:
            form = EmailPostForm()
        return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
