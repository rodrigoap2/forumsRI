import pickle
import numpy as np
import sys
from query_utils import preprocess_phrase, qt_docs, kendall_tau, tfidf, get_document_tfidf


def query_tf(query_input: str, inverted_index: dict):
    query_input = preprocess_phrase(query_input)
    terms = query_input.split(' ')

    scores = {}
    for term in terms:
        if term in inverted_index:
            N, frequencies = inverted_index[term]
            for doc, tf in frequencies:
                if doc not in scores:
                    scores[doc] = tf
                else:
                    scores[doc] += tf

    scores = {item[0]: item[1]
                            for item in sorted(scores.items(), key=lambda x: -x[1])}

    return scores


def cosine(query_terms: [str], tfidf_terms, document_tfidf, N: int, inverted_index: dict):
    idfs = []
    for term in query_terms:
        if term in inverted_index:
            idfs.append(np.log2(N / inverted_index[term][0]))

    return sum(q * d for q in idfs for d in tfidf_terms) / np.linalg.norm(document_tfidf)

def query_cosine(query_input: str, table_score: dict, N: int, inverted_index: dict):
    query_input = preprocess_phrase(query_input)
    terms = query_input.split(' ')

    scores = {}
    for term in terms:
        if term in table_score:
            for doc, score in table_score[term].items():
                if doc not in scores:
                    scores[doc] = [score]
                else:
                    scores[doc].append(score)
    
    for doc, tfidf_terms in scores.items():
        document_tfidf = get_document_tfidf(doc, table_score)
        
        scores[doc] = cosine(terms, tfidf_terms, document_tfidf, N, inverted_index)

    scores = {item[0]: item[1]
                            for item in sorted(scores.items(), key=lambda x: -x[1])}
    
    return scores
    


# R e r são 0 na formula
def bm25(query_input: str, items_count: dict, inverted_index: dict, N: int):
    query_input = preprocess_phrase(query_input)
    terms = query_input.split(' ')

    # Default value in Elasticsearch's BM25
    k1 = 1.2
    k2 = 10
    b = 0.75

    avdl = np.mean([v for _, v in items_count.items()])

    scores = {}

    query_frequencies = {}
    for term in terms:
        if term not in query_frequencies:
            query_frequencies[term] = 1
        else:
            query_frequencies[term] += 1

    for term in terms:
        if term in inverted_index:
            total, frequencies = inverted_index[term]
            for doc, tf in frequencies:
                # print(f"doc: {doc}  tf: {tf}  Freq: {frequencies}")
                # input()
                p1 = np.log2((N - len(frequencies) + 0.5) / (len(frequencies) + 0.5))
                K = k1 * ((1 - b) + b * items_count['document' + str(doc)] / avdl)
                p2 = ((k1 + 1) * tf) / (K + tf)
                p3 = ((k2 + 1) * query_frequencies[term]) / (k2 + query_frequencies[term])


                # print(f'term: {term}  doc: {doc}')
                # print(f'p1: {p1}  p2: {p2}  p3: {p3}')
                # input()

                if doc in scores:
                    scores[doc] += p1 * p2 * p3
                else:
                    scores[doc] = p1 * p2 * p3

    scores = {item[0]: item[1]
              for item in sorted(scores.items(), key=lambda x: -x[1])}

    return scores

    

def kendal_tau(results_1, results_2):
    pass


if __name__ == "__main__":
   

    inverted_index = {}
    bw = {}
    items_count = {}
    with open('../invertedindex/index.txt', 'rb') as index_file:
        inverted_index = pickle.load(index_file)

    with open('../invertedindex/bagofwords.txt', 'rb') as bw_file:
        bw = pickle.load(bw_file)

    with open('../invertedindex/documentsitemscount.txt', 'rb') as ic_file:
        items_count = pickle.load(ic_file)

    N = len(items_count)

    tfidf_table = tfidf(inverted_index, N)

    arg = sys.argv[1]
    # 'Perdi minha situação do serviço, o que fazer???'
    q1 = query_tf(arg, inverted_index)
    q2 = query_cosine(arg, tfidf_table, N, inverted_index)
    q3 = bm25(arg, items_count, inverted_index, N)

    print(f"Default: {q1}")
    print(f"Cosine: {q2}")
    print(f"BM25: {q3}")

    kt = kendall_tau(q1, q2)
    print(kt)
    




