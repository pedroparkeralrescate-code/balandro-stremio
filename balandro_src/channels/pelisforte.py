# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, servertools

host = 'https://www2.pelisforte.se/'

# ~ por si viene de enlaces guardados
ant_hosts = ['https://pelisforte.co/', 'https://pelisforte.nu/', 'https://www1.pelisforte.se/']

# Intentar importar cloudscraper para saltarse Cloudflare
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
    logger.info("✓ Cloudscraper disponible")
except Exception:
    CLOUDSCRAPER_AVAILABLE = False
    logger.info("✗ Cloudscraper NO disponible")


# ---------------------------------------------------------------------------
# Descarga con fallback a cloudscraper
# ---------------------------------------------------------------------------

def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    """Descarga una URL con cloudscraper si disponible, si no con httptools."""
    # Reemplazar dominios antiguos
    for ant in ant_hosts:
        url = url.replace(ant, host)

    if not CLOUDSCRAPER_AVAILABLE:
        return httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    try:
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )
        if headers:
            scraper.headers.update(headers)
        if post:
            response = scraper.post(url, data=post, timeout=20)
        else:
            response = scraper.get(url, timeout=20)

        data = response.text
    except Exception as e:
        logger.error("Cloudscraper falló (%s), usando httptools" % str(e))
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    # Detectar Cloudflare challenge
    if '<title>Just a moment...</title>' in data or '<title>You are being redirected...</title>' in data:
        logger.info("⚠ Cloudflare detectado, reintentando con httptools")
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


# ---------------------------------------------------------------------------
# Menús principales
# ---------------------------------------------------------------------------

def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title='Buscar película ...', action='search', search_type='movie', text_color='deepskyblue'))
    itemlist.append(item.clone(title='Catálogo', action='list_all', url=host + 'todas-las-peliculas/', search_type='movie'))
    itemlist.append(item.clone(title='Por idioma', action='idiomas', search_type='movie'))
    itemlist.append(item.clone(title='Por género', action='generos', search_type='movie'))
    itemlist.append(item.clone(title='Por año', action='anios', search_type='movie'))
    itemlist.append(item.clone(title='Por letra (A - Z)', action='alfabetico', search_type='movie'))
    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title='Castellano', action='list_all', url=host + 'pelis/idiomas/castellano/', text_color='moccasin'))
    itemlist.append(item.clone(title='Latino', action='list_all', url=host + 'pelis/idiomas/espanol-latino/', text_color='moccasin'))
    itemlist.append(item.clone(title='Subtitulado', action='list_all', url=host + 'pelis/idiomas/subtituladas/', text_color='moccasin'))
    return itemlist


def generos(item):
    logger.info()
    itemlist = []
    data = do_downloadpage(host + 'portal003/')
    bloque = scrapertools.find_single_match(data, r'>Géneros<(.*?)</ul>')
    matches = scrapertools.find_multiple_matches(bloque, r'<a href="(.*?)">(.*?)</a>')
    if not matches:
        matches = scrapertools.find_multiple_matches(bloque, r'<a href=(.*?)>(.*?)</a>')
    for url, title in matches:
        itemlist.append(item.clone(action='list_all', title=title, url=url, text_color='deepskyblue'))
    return itemlist


def anios(item):
    logger.info()
    itemlist = []
    from datetime import datetime
    current_year = int(datetime.today().year)
    url = host + 'release/'
    for x in range(current_year, 1939, -1):
        itemlist.append(item.clone(title=str(x), url=url + str(x), action='list_all', text_color='deepskyblue'))
    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []
    url_letra = host + 'letter/'
    for letra in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if letra == '#':
            url = url_letra + '0-9/'
        else:
            url = url_letra + letra + '/'
        itemlist.append(item.clone(title=letra, action='list_all', url=url, text_color='deepskyblue'))
    return itemlist


# ---------------------------------------------------------------------------
# Listado de películas (catalog + paginación)
# ---------------------------------------------------------------------------

def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    if not data:
        logger.error("❌ HTML vacío para: " + item.url)
        return itemlist

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    # Extraer bloque de resultados
    bloque = scrapertools.find_single_match(data, r'<h1(.*?)<p class="copy">© PelisForte')
    if not bloque:
        # Fallback: usar todo el HTML (ej. búsquedas)
        bloque = data

    matches = scrapertools.find_multiple_matches(bloque, r'<article(.*?)</article>')

    logger.info("🎬 Artículos encontrados: %d" % len(matches))

    for match in matches:
        url = scrapertools.find_single_match(match, r'<a href="(.*?)"')
        if not url:
            url = scrapertools.find_single_match(match, r'href=(.*?) ').strip()

        title = scrapertools.find_single_match(match, r'class="entry-title">(.*?)</')
        if not title:
            title = scrapertools.find_single_match(match, r'<h2[^>]*>(.*?)</h2>')

        if not url or not title:
            continue

        title = scrapertools.decodeHtml(title).strip()

        thumb = scrapertools.find_single_match(match, r'src="(.*?)"')

        # El original usa <span class="Year"> (Y mayúscula)
        year = scrapertools.find_single_match(match, r'<span class="Year">(.*?)</span>')
        if not year:
            year = scrapertools.find_single_match(match, r'<span class="year">(.*?)</span>')
        if not year:
            if '/release/' in item.url:
                year = scrapertools.find_single_match(item.url, r'/release/(.*?)$')
            else:
                year = '-'

        # Detectar si es serie
        content_type = 'movie'
        action = 'findvideos'
        if '/series/' in url or 'temporada' in title.lower():
            content_type = 'tvshow'
            action = 'episodios'

        itemlist.append(item.clone(
            action=action,
            url=url,
            title=title,
            thumbnail=thumb,
            contentType=content_type,
            contentTitle=title,
            infoLabels={'year': year}
        ))

    # Paginación — igual que el original
    if itemlist:
        if '>SIGUIENTE' in data:
            next_page = scrapertools.find_single_match(
                data, r'class="page-link current".*?class="page-link".*?</a>.*?href=\'(.*?)\'.*?</section>')
            if not next_page:
                next_page = scrapertools.find_single_match(
                    data, r'class="page-link current".*?class="page-link".*?</a>.*?href="(.*?)".*?</section>')
            if not next_page:
                next_page = scrapertools.find_single_match(
                    data, r'class="page-link current".*?</a>.*?class=page-link.*?href=(.*?)>.*?</section>')
            if next_page:
                next_page = next_page.replace('&#038;', '&')
                if '/page/' in next_page:
                    itemlist.append(item.clone(url=next_page, title='Siguientes ...', action='list_all', text_color='coral'))

    return itemlist


def series(item):
    return list_all(item)


# ---------------------------------------------------------------------------
# Episodios de serie
# ---------------------------------------------------------------------------

def episodios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    if not data:
        return itemlist

    data = re.sub(r'\n|\r|\t|\s{2}', '', data)

    patron = r'<div class="numerando">(\d+)\s*-\s*(\d+)</div>.*?<a href="([^"]+)">([^<]+)</a>'
    matches = scrapertools.find_multiple_matches(data, patron)

    for season, episode, url, title in matches:
        ep_title = "%sx%s - %s" % (season, episode, title.strip())
        itemlist.append(Item(
            channel=item.channel,
            action='findvideos',
            title=ep_title,
            url=url,
            thumbnail=item.thumbnail,
            contentType='episode',
            contentSeason=season,
            contentEpisode=episode,
            contentSerieName=item.contentTitle
        ))

    return itemlist


# ---------------------------------------------------------------------------
# Buscar vídeos (extraer opciones de servidor)
# ---------------------------------------------------------------------------

def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    if not data:
        logger.error("❌ Error descargando: " + item.url)
        return itemlist

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    # Bloque de opciones — igual que el original
    bloque = scrapertools.find_single_match(data, r'>OPCIONES<(.*?)</section>')
    if not bloque:
        bloque = data

    # Patron: href="#options-N" ... <span class="server">SERVIDOR-IDIOMA</span>
    matches = scrapertools.find_multiple_matches(
        bloque, r'href="#options-(.*?)">.*?<span class="server">(.*?)-(.*?)</span>')
    if not matches:
        # Fallback sin espacios (HTML minificado)
        matches = scrapertools.find_multiple_matches(
            bloque, r'href=#options-(.*?)>.*?<spanclass=server>(.*?)-(.*?)</span>')

    ses = 0

    for opt, srv, idioma in matches:
        ses += 1

        srv = srv.lower().strip()

        if not srv:
            continue
        elif srv == 'trailer':
            continue
        elif srv in ('+ veloz', 'sdav', 'guayhd', 'pf', 'w1tv'):
            continue

        idioma = idioma.strip()

        if 'Latino' in idioma:
            lang = 'Lat'
        elif 'Castellano' in idioma:
            lang = 'Esp'
        elif 'Subtitulado' in idioma:
            lang = 'Vose'
        else:
            lang = idioma

        # URL del iframe para esta opción
        url = scrapertools.find_single_match(data, r'<div id="options-' + opt + r'".*?src="([^"]+)"')
        if not url:
            url = scrapertools.find_single_match(data, r'<divid=options-' + opt + r'.*?data-src="(.*?)"')

        if not url:
            continue

        servidor = servertools.corregir_servidor(srv)

        ref = ''
        other = ''

        if srv == 'ok':
            servidor = 'directo'
            srv = 'ok'
        elif srv == 'okhd':
            servidor = 'directo'
            srv = 'tiwi'
            ref = item.url
        elif srv in ('playpf', 'ds'):
            servidor = 'directo'

        if servidor == 'directo':
            other = srv
        elif servidor == 'various':
            other = servertools.corregir_other(srv)

        itemlist.append(Item(
            channel=item.channel,
            action='play',
            server=servidor,
            title='',
            url=url,
            ref=ref,
            language=lang,
            other=other.capitalize()
        ))

    return itemlist


# ---------------------------------------------------------------------------
# Play: resolución final de URL (mp4.nu y similares)
# ---------------------------------------------------------------------------

def play(item):
    logger.info()
    itemlist = []

    item.url = (item.url
                .replace('&amp;#038;', '&')
                .replace('&#038;', '&')
                .replace('&amp;', '&'))

    url = item.url

    if item.other:
        # Caso mp4.nu — redirigir a la URL real del servidor
        if '/mp4.nu/' in url:
            new_url = (url
                       .replace('/mp4.nu//?h=', '/mp4.nu/r.php?h=')
                       .replace('/mp4.nu/', '/mp4.nu/r.php'))

            try:
                resp = httptools.downloadpage(
                    new_url, headers={'Referer': host},
                    follow_redirects=False, only_headers=True)
            except Exception:
                resp = None

            if resp and 'location' in resp.headers:
                url = resp.headers['location']
            else:
                url = ''

            if url:
                if '/rehd.net/' in url:
                    data = do_downloadpage(url)
                    url = scrapertools.find_single_match(data, r'"url": "(.*?)"')

                if not url:
                    return itemlist

                if 'gounlimited' in url:
                    return itemlist
                if '/guayhd.me/' in url or '/playpf.link/' in url:
                    return itemlist

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = _add_referer(url, item)
                itemlist.append(item.clone(server=servidor, url=url))
                return itemlist

        # Resolución genérica: descargar página y buscar iframe
        data = do_downloadpage(url, headers={'Referer': host})
        url = scrapertools.find_single_match(data, r'<div class="Video">.*?src="(.*?)"')
        if not url:
            url = scrapertools.find_single_match(data, r'<IFRAME SRC="(.*?)"')
        if not url:
            url = scrapertools.find_single_match(data, r'<iframe.*?src="(.*?)"')
        if not url:
            url = scrapertools.find_single_match(data, r'src=(.*?) ').strip()

        if 'trhide' in url:
            try:
                import codecs
                new_url = scrapertools.find_single_match(url, r'tid=([A-z0-9]+)')[::-1]
                new_url = codecs.decode(new_url, 'hex')
                data = do_downloadpage(new_url, headers={'Referer': item.url})
                if 'grecaptcha.execute' in data:
                    return itemlist
                url = new_url
            except Exception:
                pass

        elif url and url.startswith(host):
            if url.endswith('&'):
                url = url.replace('&', '')
            data = do_downloadpage(url, headers={'Referer': item.url})
            url = scrapertools.find_single_match(data, r'<div class="Video">.*?src="(.*?)"')
            if not url:
                url = scrapertools.find_single_match(data, r'<IFRAME SRC="(.*?)"')

    if url:
        if 'gounlimited' in url:
            return itemlist

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith('http'):
                return itemlist
            servidor = new_server

        url = _add_referer(url, item)
        itemlist.append(item.clone(server=servidor, url=url))

    return itemlist


def _add_referer(url, item):
    """Añade Referer=... a la URL según las reglas del original."""
    _wish_domains = (
        'streamwish', 'strwish', 'embedwish', 'wishembed', 'awish', 'dwish',
        'mwish', 'wishfast', 'sfastwish', 'doodporn', 'flaswish', 'obeywish',
        'cdnwish', 'asnwish', 'flastwish', 'jodwish', 'swhoi', 'fsdcmo',
        'swdyu', 'wishonly', 'playerwish', 'hlswish', 'wish', 'iplayerhls',
        'hlsflast', 'ghbrisk'
    )

    if item.ref:
        if 'vgfplay' not in url and 'listeamed' not in url:
            if '/ok.ru/' not in url:
                url += '|Referer=' + url
            else:
                url += '|Referer=https://mp4.nu/'
        else:
            url += '|Referer=https://mp4.nu/'
    else:
        if any(d in url for d in _wish_domains):
            url += '|Referer=https://mp4.nu/'
        else:
            if 'vgfplay' not in url and 'listeamed' not in url:
                if '/ok.ru/' not in url:
                    url += '|Referer=' + url
                else:
                    url += '|Referer=https://mp4.nu/'
            else:
                url += '|Referer=https://mp4.nu/'

    return url


# ---------------------------------------------------------------------------
# Búsqueda
# ---------------------------------------------------------------------------

def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(' ', '+')
        return list_all(item)
    except Exception:
        import sys
        for line in sys.exc_info():
            logger.error('%s' % line)
        return []