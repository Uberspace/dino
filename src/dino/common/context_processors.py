import re

from django.conf import settings
from django.urls import URLPattern, URLResolver, resolve


def _list_urls(lis, acc=None):
    # https://stackoverflow.com/a/54531546/2486196
    if acc is None:
        acc = []
    if not lis:
        return
    i = lis[0]
    if isinstance(i, URLPattern):
        yield acc + [str(i.pattern)]
    elif isinstance(i, URLResolver):
        yield from _list_urls(i.url_patterns, acc + [str(i.pattern)])

    yield from _list_urls(lis[1:], acc)


def normalize(url):
    url = re.sub(r'[/]+', '/', url)
    url = url.lstrip('^').rstrip('$')
    url = url.strip('/')
    return url


def assemble(url):
    """ ['/profile', '^edit', 'image$'] => 'profile/edit/image' """
    return normalize('/'.join(map(normalize, url)))


def list_urls():
    """ get a list of all URLs in this django installation, e.g. ['/home', '/profile', '/profile/edit/image'] """
    urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])
    lis = urlconf.urlpatterns
    return [assemble(url) for url in _list_urls(lis)]


def get_parent_urls(path):
    route = normalize(resolve(path).route)
    urls = []

    for url in list_urls():
        if url and route.startswith(url):
            urls.append(url)

    urls.sort(key=len)

    return urls


def get_breadcrumb(url, kwargs, prefix):
    crumb = url[len(prefix):].strip('/')
    url = '/' + url

    for k, v in kwargs.items():
        url = re.sub(fr'<([^>]+:)?{k}>', v, url)
        crumb = re.sub(fr'<([^>]+:)?{k}>', v, crumb)

    if '/' in crumb:
        # URL parts are not seperated => ['profile', 'edit/image']
        # split them and only link the last one
        crumbs = crumb.split('/')

        for c in crumbs[:-1]:
            yield {
                'crumb': c,
                'url': None,
            }

        yield {
            'crumb': crumbs[-1],
            'url': url,
        }
    else:
        # URL parts are seperated => ['profile', 'edit', 'image']
        yield {
            'crumb': crumb,
            'url': url,
        }


def get_breadcrumbs(path):
    urls = get_parent_urls(path)
    kwargs = resolve(path).kwargs

    prefix = ''

    for url in urls:
        yield from get_breadcrumb(url, kwargs, prefix)
        prefix = url


def breadcrumbs(request):
    return {'breadcrumbs': list(get_breadcrumbs(request.path))}
