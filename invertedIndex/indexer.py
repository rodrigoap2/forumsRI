import nltk
import pickle
from unidecode import unidecode
from nltk import tokenize

tokenized_elements = []
tokenized_elements_fields = []
bag_of_words = {}

def sort_tokens():
    global tokenized_elements
    tokenized_elements.sort(key=lambda tup: tup[0])

def preprocess_document(document, document_id):
    ascii_folded_document = ascii_fold_document(document)
    tokenize_document(ascii_folded_document, document_id)

def decode(text):
    return unidecode(''.join(c for c in text.lower() if c.isalnum() or c == ' ' or '\n'))

def ascii_fold_document(document):
    for key in document:
        if key == 'title' or key == 'date':
            document[key] = decode(document[key])
        else:
            if key == 'question':
                document[key]['author'] = decode(document[key]['author'])
                document[key]['text'] = decode(document[key]['text'])
            else:
                for element in document[key]:
                    for inner_key in element:
                        element[inner_key] = decode(element[inner_key])
    return document

def tokenize_document(document, document_id):
    global tokenized_elements, tokenized_elements_fields, bag_of_words
    document_name = 'document' + str(document_id)
    bag_of_words[document_name] = set()
    for key in document:
        if key == 'title' or key == 'date':
            tokens = tokenize_text(document[key])
            for element in tokens:
                tokenized_elements_fields.append((element + '.' + key, document_id))
                tokenized_elements.append((element, document_id))
                bag_of_words[document_name].add(element)
        else:
            if key == 'question':
                for element in document[key]:
                    tokens = tokenize_text(document[key][element])
                    for token in tokens:
                        tokenized_elements_fields.append((token + '.' + key + '.' + element   , document_id))
                        tokenized_elements.append((token, document_id))
                        bag_of_words[document_name].add(token)
            else:
                for element in document[key]:
                    for inner_key in element:
                        tokens = tokenize_text(element[inner_key])
                        for token in tokens:
                            if token != ')' or token != '(' or token != ':':
                                tokenized_elements_fields.append((token + '.' + key + '.' + inner_key, document_id))
                                tokenized_elements.append((token, document_id))
                                bag_of_words[document_name].add(token)

def tokenize_text(text):
    return tokenize.word_tokenize(text, language='portuguese')

def create_index(tokenized_elements):
    inv_index = {}
    for element in tokenized_elements:
        if(element[0] == 'novamente'):
            print(element)
        #element[0] == token
        #element[1] == id from the document
        if not element[0] in inv_index:
            inv_index[element[0]] = (1, [(element[1], 1)])
        else:
            try:
                element_position = [y[0] for y in inv_index[element[0]][1]].index(element[1])
                inv_index[element[0]][1][element_position] = (inv_index[element[0]][1][element_position][0], inv_index[element[0]][1][element_position][1] + 1)
            except ValueError:
                inv_index[element[0]][1].append((element[1], 1))
            length = len(inv_index[element[0]][1])
            inv_index[element[0]] = (length, inv_index[element[0]][1])
    return inv_index
if __name__ == "__main__":
    document_id = 0
    bag_of_words = {}
    for idx in range(0, 10):
        document = {}
        with open('../extractor/documents/document' + str(idx) + '.txt', 'rb') as file:
            document = pickle.load(file)
            file.close()
        preprocess_document(document, idx)
    sort_tokens()
    inv_index = create_index(tokenized_elements)
    inv_index_fields = create_index(tokenized_elements_fields)
    with open('./index.txt', 'wb') as arquivo:
        pickle.dump(inv_index, arquivo)
    with open('./indexfields.txt', 'wb') as arquivo:
        pickle.dump(inv_index_fields, arquivo)
    with open('./bagofwords.txt', 'wb') as arquivo:
        pickle.dump(bag_of_words, arquivo)
    print(inv_index)
    print(inv_index_fields)
    print(bag_of_words)