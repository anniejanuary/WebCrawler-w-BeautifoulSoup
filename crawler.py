import requests
# import aiofiles #to save a website's sourcecode asynchronously to file
from bs4 import BeautifulSoup
import csv
import pandas # when exporting to csv from a nested dict


BASE_URL = "https://crawler-test.com" #"https://python/org"


class WebScraper:
    def __init__(self, URL):
        self.base_url = ''
        self.main_page_and_subpages = []
        URL.rstrip('/')
        self.base_url = URL
        self.main_page_and_subpages.append(self.base_url)
        self.titles = {}
        self.question_mark_hrefs = []
        self.internal_links = {}
        self.external_links = {}
        self.call_count = {} # TODO
        self.final_results = []

    def crawl(self):
        for current_master_page in self.main_page_and_subpages:
            self.internal_links[current_master_page] = set()
            self.external_links[current_master_page] = set()
            self.call_count[current_master_page] = {}

            print("iterating:", current_master_page)
            # if 'status_codes' in current_master_page:
            #     continue

            raw_html = requests.get(current_master_page, allow_redirects=False )  # dont allow redirects cause https://crawler-test.com has redirects > 30 but then it might not catch some subpages

            if raw_html.status_code != 200:
                print("wrong status code!", raw_html.status_code)
                continue

            soup = BeautifulSoup(raw_html.content, 'html.parser')
            soup.prettify()

            try:  # TODO possibility of not catching content - might be fixable with Selenium https://stackoverflow.com/questions/62638350/beautifulsoup-not-catching-the-content
                self.titles[current_master_page] = soup.find('title').contents[0]
            except Exception as ex:
                print(ex)


            # LOOP: GETTING LINKS INSIDE MAIN AND SUBPAGES
            for link in soup.find_all('a'):
                print("Now working on: ", link)
                if not link.has_attr('href'):
                    continue
                if str(link['href']).startswith('#'):  # skip navigation through page
                    continue

                if str(link["href"]).startswith((str(self.base_url))):
                    if str(link['href']) not in self.main_page_and_subpages:
                        self.main_page_and_subpages.append(link['href'])
                    self.internal_links[current_master_page].add(link["href"])

                # if href link starts with "/" AND is more tha just "/":
                elif str(link["href"]).startswith('/') and len(str(link["href"])) >= 2:  # TODO take care of relative links such as ./ ../ ../../../
                    # getting rid of "?(text)" if there's a question mark inside a href:
                    if '?' in link['href']:
                        sep = '?'
                        link_before_question_mark = link['href'].split(sep, 1)[0]
                        link['href'] = link_before_question_mark
                        # self.question_mark_hrefs.append(link['href'])
                    link_with_http = self.base_url + link["href"]
                    self.internal_links[current_master_page].add(link_with_http)
                    if link_with_http not in self.main_page_and_subpages:
                        self.main_page_and_subpages.append(link_with_http)

                elif str(link["href"]).startswith('http'):
                    self.external_links[current_master_page].add(link["href"])

                else:
                    print("weird link encountered, ignoring... :", link["href"])



                current_master_page = current_master_page.rstrip('/')
                print('\n--------------------------------\n')
                print("url:", current_master_page)

                call_count = 0
                if current_master_page in self.internal_links:
                    call_count += 1

                print("call_count:", call_count)
                      # self.call_count[current_master_page] if current_master_page in self.call_count else "0")
                print("title:", self.titles[current_master_page] if current_master_page in self.titles else "")
                print("internal links:",
                      len(self.internal_links[current_master_page]) if current_master_page in self.internal_links else "0")
                print("external links:",
                      len(self.external_links[current_master_page]) if current_master_page in self.external_links else "0")
                print("--------------------------------\n")

                new_sublinks_dict = {'url': link["href"] if self.base_url in link["href"] else (self.base_url+link["href"]), 'Title': (
                    self.titles[current_master_page] if current_master_page in self.titles else ""),
                                     'No of internal links': (len(self.internal_links[
                                                                      current_master_page]) if current_master_page in self.internal_links else "0"),
                                     'No of external links': (len(self.external_links[
                                                                      current_master_page]) if current_master_page in self.external_links else "0"),
                                     'No of times url was referenced by other pages': "..."}
                self.final_results.append(new_sublinks_dict)

            # if len(self.main_page_and_subpages) > 300:  # if crawling takes too long over all the subpages
            #     break



    def export_to_csv(self):
        # for exporting from a dict:
        # df = pandas.DataFrame.from_dict(self.final_results)
        # df.to_csv(r'test2.csv', index=False, header=True)
        keys = self.final_results[0].keys()

        with open('scraper2.csv', 'w', encoding="utf-8", newline='') as output_file: # "encoding="utf-8" to avoid "UnicodeEncodeError: 'charmap' codec can't encode characters" error
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.final_results)


scraper = WebScraper(BASE_URL)
scraper.crawl()
scraper.export_to_csv()

#print(scraper.final_results)


