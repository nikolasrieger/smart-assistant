from googlesearch import search

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
