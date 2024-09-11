from transformers import RobertaTokenizer, RobertaModel

class EmbeddingModel():
    def __init__(self):
        self.__tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
        self.__model = RobertaModel.from_pretrained('roberta-base')

    def generate_embeddings(self, text: str):
        encoded_input = self.__tokenizer(text, return_tensors='pt')
        result = self.__model(**encoded_input)
        return result
    
if __name__ == "__main__":
    model = EmbeddingModel()
    text = "Sample text for embedding"
    embeddings = model.generate_embeddings(text)
    print(embeddings)
