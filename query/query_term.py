import pickle
from query_utils import preprocess_phrase, qt_docs, tfidf, get_document_tfidf, get_document_size, kendall_tau
import numpy as np

fields_strings = ['question.title', 'date', 'question.author',
                  'question.text', 'answers.author', 'answers.text']


def query_tf_aux(terms: [str], field: str, inverted_index_fields: dict, scores: dict):
    for term in terms:
        term = term + '.' + field
        if term in inverted_index_fields:
            N, frequencies = inverted_index_fields[term]
            for doc, tf in frequencies:
                if doc not in scores:
                    scores[doc] = tf
                else:
                    scores[doc] += tf


def query_tf(title: str = '', date: str = '', question_author: str = '', question_text: str = '', answers_author: str = '', answers_text: str = '', inverted_index_fields: dict = {}):
    title = preprocess_phrase(title)
    date = preprocess_phrase(date)
    question_author = preprocess_phrase(question_author)
    question_text = preprocess_phrase(question_text)
    answers_author = preprocess_phrase(answers_author)
    answers_text = preprocess_phrase(answers_text)
    
    field_values = [title, date, question_author,
                    question_text, answers_author, answers_text]
    global fields_strings

    scores = {}

    for field, value in zip(fields_strings, field_values):
        if len(value) > 0:
            query_tf_aux(value.split(' '), field,
                         inverted_index_fields, scores)

    scores = {item[0]: item[1]
                            for item in sorted(scores.items(), key=lambda x: -x[1])}

    return scores


def cosine(query_terms: [str], field: str, tfidf_terms, document_tfidf, N: int, inverted_index_fields: dict):
    
    idfs = []
    for term in query_terms:
        term = term + '.' + field
        if term in inverted_index_fields:
            idfs.append(np.log2(N / inverted_index_fields[term][0]))

    return sum(q * d for q in idfs for d in tfidf_terms) / np.linalg.norm(document_tfidf)


def query_cosine_aux(terms: [str], field: str, inverted_index_fields: dict, table_score: dict, N: int, scores: dict):
    for term in terms:
        term = term + '.' + field
        if term in inverted_index_fields:
            for doc, score in table_score[term].items():
                if doc not in scores:
                    scores[doc] = [score]
                else:
                    scores[doc].append(score)

    for doc, tfidf_terms in scores.items():
        document_tfidf = get_document_tfidf(doc, table_score)

        scores[doc] = cosine(terms, field, tfidf_terms,
                             document_tfidf, N, inverted_index_fields)
        

def query_cosine(title: str = '', date: str = '', question_author: str = '', question_text: str = '', answers_author: str = '', 
        answers_text: str = '', inverted_index_fields: dict = {}, table_score: dict = {}, N: int = 0):
    title = preprocess_phrase(title)
    date = preprocess_phrase(date)
    question_author = preprocess_phrase(question_author)
    question_text = preprocess_phrase(question_text)
    answers_author = preprocess_phrase(answers_author)
    answers_text = preprocess_phrase(answers_text)

    field_values = [title, date, question_author,
                    question_text, answers_author, answers_text]
    global fields_strings

    scores_final = {}

    for field, value in zip(fields_strings, field_values):
        scores = {}
        if len(value) > 0:
            query_cosine_aux(value.split(' '), field,
                             inverted_index_fields, table_score, N, scores)

        for k, v in scores.items():
            if k in scores_final:
                scores_final[k] += v
            else:
                scores_final[k] = v

    scores_final = {item[0]: item[1]
              for item in sorted(scores_final.items(), key=lambda x: -x[1])}
    
    return scores_final

if __name__ == "__main__":

    inverted_index = {}
    inverted_index_fields = {}
    bw = {}
    with open('../invertedindex/index.txt', 'rb') as index_file:
        inverted_index = pickle.load(index_file)

    with open('../invertedindex/indexfields.txt', 'rb') as index_file:
        inverted_index_fields = pickle.load(index_file)

    with open('../invertedindex/bagofwords.txt', 'rb') as bw_file:
        bw = pickle.load(bw_file)

    N = qt_docs(inverted_index)

    tfidf_table = tfidf(inverted_index_fields, N)

    # Campos:
    # - title
    # - date
    # - question.author
    # - question.text
    # - answers.author
    # - answers.text
    # print(inverted_index_fields)

    q1 = query_cosine(answers_author='nathan',
                      inverted_index_fields=inverted_index_fields, table_score=tfidf_table, N=N)
    
    q2 = query_tf(answers_author='nathan',
                  inverted_index_fields=inverted_index_fields)

    print(q1)
    print(q2)

    kt = kendall_tau(q1, q2)
    print(kt)

