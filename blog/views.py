from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from . models import Post


from django.conf import settings
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Avg, Count, F, Q

from django.utils.text import slugify
from markdownx.utils import markdownify
# from .forms import ArticleForm, CategoryForm, TagForm
from .models import Article, Tag, Category


# Create your views here.
def postlist(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts' : posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def home(request):
    request.session['current_page'] = 'blog'
    art_list = Article.objects.filter(published=True, featured=True)
    paginator = Paginator(art_list, 7, orphans=3)

    # Populate tag cloud
    tags = Tag.objects.annotate(total=Count('article', filter=Q(article__published=True))).filter(total__gt=0)
    average = Tag.objects.annotate(total=Count('article', filter=Q(article__published=True))).aggregate(average_total=Avg('total'))['average_total']
    # min weight (in rem) is 1, while max weight is 3
    weight = []
    for t in tags:
        w = t.total/average if average > 0 else 0
        w = float('{0:.2f}'.format(w))
        if w > 3:
            w = 3
        weight.append(w if w >= 1 else 1)
    #print('weights: {}'.format(weight))
    tags = zip(tags, weight)

    # Get all categories
    categories = Category.objects.annotate(total=Count('article'))
    
    page = request.GET.get('page')
    arts = paginator.get_page(page)
    return render(request, 'blog/home.html', {
        'canonical': 'https://{}/'.format(request.get_host()),
        'arts': arts,
        # 'pop_arts': _get_hot_articles(),
        'tags': tags,
        'cats': categories,
        'debug': settings.DEBUG,
    })

def article(request, year, slug):
    """Render an article."""
    art = get_object_or_404(Article, date_created__year=year, slug=slug)
    # redirect to homepage if the art is not published
    if not art.published:
        return redirect('blog:home')
    art_content_html = markdownify(art.content)
    response = render(request, 'blog/article.html', {
        'art': art,
        'art_content_html': art_content_html,
        # 'pop_arts': _get_hot_articles(),
        'debug': settings.DEBUG,
        'canonical': 'https://{}{}'.format(request.get_host(), art.get_absolute_url()),
    })
    # update article's view count using cookies
    if request.COOKIES.get(art.slug) is None and not request.user.is_authenticated:
        import datetime
        now = datetime.datetime.now()
        three_days = now + datetime.timedelta(days=3)
        response.set_signed_cookie(art.slug, art.id, expires=three_days)
        art.view_count = F('view_count') + 1
        art.save()
    return response