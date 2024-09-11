from googlesearch import search

class SearchEngine():
    def search(self, search_text: str):
        search_result_object = search(search_text, advanced=True)
        search_results = []
        for object in search_result_object:
            search_dict = {"url": object.url, "info": object.title + "\n" + object.description}
            search_results += [search_dict]
        return search_results

if __name__ == "__main__":
    s = SearchEngine()
    print(s.search("How to code an AI?"))