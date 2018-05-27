#!/usr/bin/env python3

"""
FeedScrapy is software that collect specifics news from a feed and
send it to an e-mail (or email list).
author: Clederson Cruz
Year: 2018
License: GNU GENERAL PUBLIC LICENSE (GPL)
"""

try:
    import requests
    from requests.exceptions import ConnectionError
except ModuleNotFoundError:
    url = 'https://pypi.org/project/requests/'
    msg = f'O módulo "requests" é necessário. Instale-o visitando {url}'
    raise Exception(msg)

try:
    import feedparser
except ModuleNotFoundError:
    url = 'https://pypi.org/project/feedparser/'
    msg = f'O módulo "requests" é necessário. Instale visitando {url}'
    raise Exception(msg)


class Feeder:
    """
    Feeder class is responsible to handle RSS and its content.
    """
    def __init__(self, maxfeed=10):
        self.rss = None
        self.maxfeed = maxfeed  # default = 10

    def set_rss(self, rss):
        """
        Set the RSS if it receives a valid link.
        :param rss: is the RSS URL
        :return: None
        """
        rss = rss

        try:
            headers = {'User-Agent': 'FeedScrapy/1.0'}
            response = requests.request('GET', rss, headers=headers)
        except ConnectionError:
            raise Exception(f'Erro ao estabelecer conexão com feed <{rss}>')
        except requests.exceptions.MissingSchema:
            raise Exception('URL inválida')

        if response.status_code == 200:
            self.rss = feedparser.parse(rss)
            response.close()
        else:
            raise Exception('Link inacessível')

    def set_maxfeed(self, maxfeed):
        """
        Set the max number of content to be returned.
        :param maxfeed: max number of content
        :return: None
        """
        self.maxfeed = maxfeed

    def get_entries(self, keyword_list, stype=0):
        """
        Get a list of content parsed by a scraper.
        :param keyword_list: keyword list to be researched in feed content
        :param stype: search type, 0 means OR (default) and 1 means AND (all keywords are researched)
        :return:
        """
        entries = []
        scraper = Scraper()

        for entry in self.rss['entries']:
            scraper.set_content(entry)

            if stype == 0:
                if scraper.is_scrap(keyword_list):
                    entries.append(scraper.get_formated_content())
            elif stype == 1:
                if scraper.is_scrap_and(keyword_list):
                    entries.append(scraper.get_formated_content())
            else:
                raise Exception('Invalid search type')

            if len(entries) > self.maxfeed:
                break

        return entries

    def get_first_entry(self):
        return self.rss['entries'][0]['title']


class Scraper:
    """
    Scraper class is responsible to scrap the content and format it.
    """
    def __init__(self):
        self.content = None
        self.link = None
        self.title = None
        self.summary = None

    def set_content(self, content):
        """
        Set the content of this scraper.
        :param content: the content is a piece of article from feed RSS
        :return: None
        """
        self.content = content
        self.link = content['link']
        self.title = content['title']
        self.summary = content['summary'][:1000]+'...'

    def get_formated_content(self):
        """
        Get a formated content from entry.
        :return: formated content like <title>, <summary> and <link>
        """
        return f'<h1>{self.title}</h1><p>{self.summary}<br>[<a href="{self.link}">Link</a>]</p>'

    def is_scrap(self, keyword_list):
        """
        Test if any keyword in keyword list is present in the content.
        :param keyword_list: a list of keywords
        :return: True, if any keyword is present, else False
        """
        find = False
        
        for word in keyword_list:
            if word in self.summary.lower():
                find = True
            if word in self.title.lower():
                find = True

        return find

    def is_scrap_and(self, keyword_list):
        """
        Test if each keyword in keyword list is present in the content.
        :param keyword_list: a list of keywords
        :return: True, if each keyword is present, else False
        """
        find_title = True
        find_body = True

        for word in keyword_list:
            if word in self.summary.lower():
                continue
            else:
                find_body = False
                break

        for word in keyword_list:
            if word in self.title.lower():
                continue
            else:
                find_title = False
                break

        return find_title or find_body
