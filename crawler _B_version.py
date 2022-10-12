import requests
from bs4 import BeautifulSoup
import csv
import urllib.request
import pandas

BASE_URL = "https://crawler-test.com"


class WebScraper:
    def __init__(self):
        self.base_url = ''
        self.main_page_and_subpages = []
        self.titles = {}
        self.call_count = {}
        self.external_links = {}
        self.internal_links = {}
        self.question_mark_hrefs = []

    def increment_page_dict(self, dictionary,
                            key):  # apparently python dicts are stupid and don't assume 0... still need it as member for relative addresses
        new_key = key
        if key.startswith('/'):  # TODO take care of relative links such as ./ ../ ../../../
            new_key = self.base_url + key

        new_key.rstrip('/')  # unify all links to not include dash as last char
        if new_key in dictionary:
            dictionary[new_key] += 1
        else:
            dictionary[new_key] = 1

    def get_subpages(self, soup, page_url, URL):
        res = set()  # set of links
        self.base_url = URL
        hyperlinks = soup.find_all('a')
        for link in hyperlinks:
            print("Now working on: ", link)
            if not link.has_attr('href'):
                # print("href not in link: ", link)
                continue
            if str(link['href']).startswith('#'):  # skip navigation through page
                continue

            # print("Now working on link:", link['href'])
            self.increment_page_dict(self.call_count,
                                     link['href'])  # increment call count TODO - only one even if multiple

            if str(link["href"]).startswith((str(self.base_url))):
                self.increment_page_dict(self.internal_links, page_url)
                res.add(link["href"])

            elif str(link["href"]).startswith('/'):  # TODO take care of relative links such as ./ ../ ../../../
                if '?' in link['href']:
                    sep = '?'
                    link_before_question_mark = link['href'].split(sep, 1)[0]
                    link['href'] = link_before_question_mark
                    # self.question_mark_hrefs.append(link['href'])
                self.increment_page_dict(self.internal_links, page_url)
                res.add(self.base_url + link['href'])

            elif str(link["href"]).startswith('http'):
                self.increment_page_dict(self.external_links, page_url)
            else:
                print("weird link encountered, ignoring... :", link["href"])
        # print("returning set of links")
        return res

    def crawl(self, URL):
        URL.rstrip('/')
        self.base_url = URL
        self.main_page_and_subpages.append(URL)
        for page_url in self.main_page_and_subpages:
            print("iterating:", page_url)
            # if 'status_codes' in page_url:  
            #     continue

            # raw_html = requests.get( page_url, allow_redirects=False )  #TODO dont allow redirects cause https://crawler-test.com has infinite - but then it doesn't register some subpages
            raw_html = requests.get(page_url)
            if raw_html.status_code != 200:  # TODO for now continue, might parse other ones later
                print("wrong status code!", raw_html.status_code)
                continue

            soup = BeautifulSoup(raw_html.content, 'html.parser')

            try:  # TODO possibility of not catching content - might be fixable with Selenium https://stackoverflow.com/questions/62638350/beautifulsoup-not-catching-the-content
                self.titles[page_url] = soup.find('title').contents[0]
            except Exception as ex:
                print(ex)

            subpages = self.get_subpages(soup, page_url, URL)
            for subpage in subpages:
                if subpage not in self.main_page_and_subpages:
                    self.main_page_and_subpages.append(subpage)

            if len(self.main_page_and_subpages) > 300:  # srsly, it takes too long
                break

    def print_res(self):
        # print(self.internal_links)

        for page_url in self.main_page_and_subpages:
            # page_url = self.all_pages[0]
            page_url = page_url.rstrip('/')
            print('\n--------------------------------\n')
            print("url:", page_url)
            print("call_count:", self.call_count[page_url] if page_url in self.call_count else "0")
            print("title:", self.titles[page_url] if page_url in self.titles else "")
            for keys, value in self.internal_links.items():
                if page_url in keys:
                    print(value)
                else:
                    print("No internal links for this subpage found in 'self.internal_links'")

            print("internal links:", self.internal_links[page_url] if page_url in self.internal_links else "0")
            print("external links:", self.external_links[page_url] if page_url in self.external_links else "0")
            print("--------------------------------\n")
            print(self.internal_links)
            print(self.main_page_and_subpages)
            # print(self.question_mark_hrefs)


scraper = WebScraper()
scraper.crawl(BASE_URL)
scraper.print_res()
