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


def breadcrumbs(request):
    urls = get_parent_urls(request.path)
    kwargs = resolve(request.path).kwargs

    breadcrumbs = []
    prefix = ''

    for url in urls:
        crumb = url[len(prefix):].strip('/')
        prefix = url

        url = '/' + url

        for k, v in kwargs.items():
            url = url.replace(f'<{k}>', v)
            crumb = crumb.replace(f'<{k}>', v)

        if '/' in crumb:
            # URL parts are not seperated => ['profile', 'edit/image']
            # split them, link the last one
            for c in crumb.split('/'):
                breadcrumbs.append({
                    'crumb': c,
                    'url': None,
                })

            breadcrumbs[-1]['url'] = url
        else:
            # URL parts are seperated => ['profile', 'edit', 'image']
            breadcrumbs.append({
                'crumb': crumb,
                'url': url,
            })

    return {'breadcrumbs': breadcrumbs}
