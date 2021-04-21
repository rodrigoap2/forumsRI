import pickle
import numpy as np
from unidecode import unidecode
import re
import sys

def taat(inverted_index):
    pass

def qt_docs(inverted_index: dict):
    documents = []
    for term, v in inverted_index.items():
        for i in v[1]:
            documents.append(i[0])
    
    return len(set(documents))

def tfidf(inverted_index: dict, N: int):
    tfidf_table = {}
    for k, v in inverted_index.items():
        idf = np.log2(N / v[0])
        term_dict = {}
        for docs in v[1]:
            # docs[1] = docs[1] * idf
            term_dict[docs[0]] = docs[1] * idf
        
        tfidf_table[k] = term_dict

    return tfidf_table

def preprocess_phrase(phrase):
    return re.sub('[^A-Za-z0-9 ]+', '', unidecode(phrase)).lower()

def query(query_term: str, table_score: dict):
    query_term = preprocess_phrase(query_term)
    terms = query_term.split(' ')

    scores = {}
    for term in terms:
        if term in table_score:
            for doc, score in table_score[term].items():
                if doc not in scores:
                    scores[doc] = score
                else:
                    scores[doc] += score
    
    scores = sorted_data = {item[0]: item[1]
                            for item in sorted(scores.items(), key=lambda x: -x[1])}
    return scores
    

if __name__ == "__main__":

    inverted_index = {}
    bw = {}
    with open('../invertedindex/index.txt', 'rb') as index_file:
        inverted_index = pickle.load(index_file)

    with open('../invertedindex/bagofwords.txt', 'rb') as bw_file:
        bw = pickle.load(bw_file)

    N = qt_docs(inverted_index)

    tfidf_table = tfidf(inverted_index, N)

    arg = sys.argv[1]
    # 'Perdi minha situação do serviço, o que fazer???'
    q = query(arg, tfidf_table)

    print(q)


