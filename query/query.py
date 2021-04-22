import pickle
import numpy as np
import sys
from query_utils import preprocess_phrase, qt_docs


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
    

def cosine(query: str):
    pass

 # TODO: score com coseno
def query_cosine(query_input: str, table_score: dict):
    query_input = preprocess_phrase(query_input)
    terms = query_input.split(' ')

    scores = {}
    for term in terms:
        if term in table_score:
            for doc, score in table_score[term].items():
                if doc not in scores:
                    scores[doc] = score
                else:
                    scores[doc] += score
    
    scores = {item[0]: item[1]
                            for item in sorted(scores.items(), key=lambda x: -x[1])}
    
    return scores
    
def ordered_pairs(result: list):
    ans = []

    for i in range(len(result)):
        for j in range(i + 1, len(result)):
            ans.append([result[i], result[j]])

    return ans

def kendall_tau(results_1, results_2):
    results_1 = list(results_1)
    results_2 = list(results_2)
    pairs_1 = ordered_pairs(results_1)
    pairs_2 = ordered_pairs(results_2)

    n = len(pairs_1)
    delta = 0
    for i in range(len(pairs_1)):
        if pairs_1[i] not in pairs_2:
            delta += 1
    
    delta *= 2
    return 1 - 2 * delta / (2 * n)

# R e r são 0 na formula
def bm25(query_input: str):
    query_input = preprocess_phrase(query_input)
    terms = query_input.split(' ')

    query_frequencies = {}
    for term in terms:
        if term not in query_frequencies:
            query_frequencies[term] = 1
        else:
            query_frequencies[term] += 1

    

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
    q1 = query_cosine(arg, tfidf_table)
    q2 = query_tf(arg, inverted_index)

    print(q1)
    print(q2)


    kt = kendall_tau(q1, q2)
    print(kt)




