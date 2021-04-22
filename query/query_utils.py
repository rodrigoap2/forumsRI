from unidecode import unidecode
import re

def preprocess_phrase(phrase: str):
    return re.sub('[^A-Za-z0-9 ]+', '', unidecode(phrase)).lower()


def qt_docs(inverted_index: dict):
    documents = []
    for term, v in inverted_index.items():
        for i in v[1]:
            documents.append(i[0])

    return len(set(documents))
