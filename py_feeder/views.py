from django.shortcuts import render, redirect
from .models import Article, Feed
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .services import sync_all_feeds

def article_list(request):
    articles = Article.objects.all()[:100]  # the 100 newest articles
    return render(request, 'py_feeder/article_list.html', {'articles': articles})

def refresh_function_view(request):
    if request.method == 'POST':
        sync_all_feeds()
        return redirect(article_list)

def feeds_check(view_request):
    class External_Feed:
        def __init__(self, title, url):
            self.title = title
            self.url = url

    xml_feeds = [
        External_Feed("TableTop Battles", "https://goonhammer.com/feed"),
        External_Feed("CaShock 40k Blog", "https://cadianshock.com/feed/"),
        External_Feed("Awesome Lies", "https://awesomeliesblog.wordpress.com/feed/"),
        External_Feed("Bell of Lost Souls", "https://www.belloflostsouls.net/category/warhammer-40k/feed/"),
        External_Feed("Can you Roll a Crit", "https://canyourollacrit.com/feed/"),
        External_Feed("Baldermort", "https://media.rss.com/baldermort-s-guide-to-warhammer/feed.xml"),
        External_Feed("Lore Beards", "https://media.rss.com/lorebeards/feed.xml"),
        External_Feed("Grim Dark", "https://www.grimdarkfilthycasuals.com/feed/"),
        External_Feed("Variance Hammer", "https://variancehammer.com/feed/"),
        External_Feed("Sepulchre of Heroes", "https://feeds.feedburner.com/SepulchreOfHeroes"),
        External_Feed("Warhamateur", "https://warhamateur.com/feed/"),
        External_Feed("Ill Met", "https://illmetbymorrslieb.wordpress.com/feed/")
    ]
    subscribed_feeds = set(Feed.objects.values_list('url', flat=True))
    subscribed_status = []
    for feed in xml_feeds:
        subscribed_status.append({
            'url': feed.url,
            'title': feed.title,
            'subscribed': feed.url in subscribed_feeds,
        })
    return render(view_request, 'py_feeder/feed_list.html', {'subscribed_status': subscribed_status})
@require_POST
def toggle_feed(toggle_request):
    url = toggle_request.POST.get('url')
    action = toggle_request.POST.get('action') # EXPECTS ADD OR REMOVE
    if not url:
        return JsonResponse({'success': False, 'error': 'No URL provided'}, status=400)
    if action == 'add':
        Feed.objects.get_or_create(url=url)
        sync_all_feeds()
        return JsonResponse({'success': True, 'action': 'added'}) # SEND ADDED BACK
    elif action == 'remove':
        Feed.objects.filter(url=url).delete()
        sync_all_feeds()
        return JsonResponse({'success': True, 'action': 'removed'}) # SEND REMOVE BACK
    return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)

#def feed_list(request):
    #return render(request, 'py_feeder/feed_list.html')