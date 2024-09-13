from googlesearch import search
from requests import get
from bs4 import BeautifulSoup

class SearchResult():
    def __init__(self, url: str, info: str):
        self.url = url
        self.info = info


class SearchEngine():
    def search(search_text: str):
        search_result_object = search(search_text, advanced=True)
        search_results = []
        for object in search_result_object:
            search_dict = SearchResult(object.url, object.title + "\n" + object.description)
            search_results += [search_dict]
        return search_results
    
    def get_text_from_url(url: str):
        response = get(url)
        if response.status_code != 200: raise Exception(f"Failed to fetch the page: {url}")
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = '\n'.join([p.get_text() for p in paragraphs])
        return text

