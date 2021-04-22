import pickle
from query_utils import preprocess_phrase

def query_tf_aux(terms, field, inverted_index_fields, scores):
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
    
    field_values = [title, date, question_author, question_text, answers_author, answers_text]
    fields_strings = ['title', 'date', 'question.author', 'question.text', 'answers.author', 'answers.text']

    scores = {}

    for field, value in zip(fields_strings, field_values):
        if len(value) > 0:
            query_tf_aux(value.split(' '), field, inverted_index_fields, scores)


    scores = {item[0]: item[1]
                            for item in sorted(scores.items(), key=lambda x: -x[1])}

    return scores





if __name__ == "__main__":

    inverted_index_fields = {}
    bw = {}
    with open('../invertedindex/indexfields.txt', 'rb') as index_file:
        inverted_index_fields = pickle.load(index_file)

    with open('../invertedindex/bagofwords.txt', 'rb') as bw_file:
        bw = pickle.load(bw_file)

    # Campos:
    # - title
    # - date
    # - question.author
    # - question.text
    # - answers.author
    # - answers.text
    # print(inverted_index_fields)

    print(query_tf(answers_author='nathan', inverted_index_fields=inverted_index_fields))
