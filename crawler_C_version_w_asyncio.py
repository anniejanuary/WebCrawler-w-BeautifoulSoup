import asyncio #asyncio allows to create event loops used to create a series of tasks to be run asynchrously
import aiohttp #asynchronous request library
import aiofiles #to save a website's sourcecode asynchronously to file I cant use a local file i/o bc it's being blocked 
from bs4 import BeautifulSoup
import csv

urls = ('https://crawler-test.com/', 'https://python.org')


class WebScraper(): 
    def __init__(self, urls):
        self.urls = urls
        self.all_data = []
        self.master_dict = {} 
        self.internal_urls = 0
        self.internal_urls_dict = {}
        self.external_urls = 0
        self.external_urls_dict = {}
        # Running the scraper
        asyncio.run(self.main())

    async def fetch(self, session, url):
        try:
            async with session.get(url) as response:
                # extracting the text
                text = await response.text()
                self.soup = BeautifulSoup(text, 'html.parser')
                #extracting the title tag
                title_tag = await self.extract_title_tag(text)
                return text, url, title_tag
        except Exception as e: 
            print(str(e))

    # async def write_to_file(self, file, text):
    #     async with aiofiles.open(file, 'w') as f: 
    #         await f.write(text)

#     async def extract_title_tag(self, text):
#         try:
#             self.soup = BeautifulSoup(text, 'html.parser')
#             return self.soup.title
#         except Exception as e: 
#             print(str(e))

    async def main(self): 
        tasks = []  # each coroutine will create a task that will be spawned asynchronously. The tasks will be saved into a list.
        async with aiohttp.ClientSession(headers=headers) as session:  # an "async with" statement calls async methods
            for url in self.urls:
                tasks.append(self.fetch(session, url))

            htmls = await asyncio.gather(*tasks) # Scheduling the coroutines to run asap by gathering the tasks inside a coroutine list "htmls"
            self.all_data.extend(htmls)

            # Storing the raw HTML data
            for html in htmls:
                if html is not None:
                    url = html[1]
                    print(url)
                    self.master_dict[url] = {'Raw Html': html[0], 'Title': html[2]} 
                    print(self.master_dict[url]['Title'])
                    if 'a href="http' in html[0]:
                        if url in html[0]:
                            print()
                            self.internal_urls += 1
                        if url not in html[0]:
                            self.external_urls += 1
                    print(html[0])

                    self.internal_urls_dict[html] = self.internal_urls
                    print(self.internal_urls_dict[html])
                    self.internal_urls = 0
                    self.external_urls_dict[html] = self.external_urls
                    print(self.external_urls_dict[html])
                    self.external_urls = 0

                    print("---------------\n")

                else:
                    continue
            #print(self.soup)
            
    # async def internal_links_count(self):
    #     for link in self.soup.find_all('a', href=True):
    #         title = link.a.get('Title')
    #         print(title)
            # if readable_website_name in link.get('href'):
            #     internal_url_links.append(link['href'])
            #
            # if readable_website_name not in link.get('href') and len(link.get('href')) > 3:
            #     external_url_links.append(link['href'])

        # print(internal_url_links, '\n')
        # print(external_url_links, '\n')

            # for url in urls:
            #     file = f'{url.split("//")[-1]}.txt'  # Constructing the file name to which I write the source code for each url
            #     html = await self.fetch(session, url)
            #     tasks.append(self.write_to_file(file, html))


scraper = WebScraper(urls=urls)
