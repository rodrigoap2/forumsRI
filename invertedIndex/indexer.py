import nltk
import pickle
from unidecode import unidecode
from nltk import tokenize
from struct import pack, unpack

tokenized_elements = []
tokenized_elements_fields = []
bag_of_words = {}
items_count = {}

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
    global tokenized_elements, tokenized_elements_fields, bag_of_words, items_count
    document_name = 'document' + str(document_id)
    bag_of_words[document_name] = set()
    items_count[document_name] = 0
    for key in document:
        if key == 'title' or key == 'date':
            tokens = tokenize_text(document[key])
            for element in tokens:
                tokenized_elements_fields.append((element + '.' + key, document_id))
                tokenized_elements.append((element, document_id))
                bag_of_words[document_name].add(element)
                items_count[document_name] += 1
        else:
            if key == 'question':
                for element in document[key]:
                    tokens = tokenize_text(document[key][element])
                    for token in tokens:
                        tokenized_elements_fields.append((token + '.' + key + '.' + element   , document_id))
                        tokenized_elements.append((token, document_id))
                        bag_of_words[document_name].add(token)
                        items_count[document_name] += 1
            else:
                for element in document[key]:
                    for inner_key in element:
                        tokens = tokenize_text(element[inner_key])
                        for token in tokens:
                            if token != ')' or token != '(' or token != ':':
                                tokenized_elements_fields.append((token + '.' + key + '.' + inner_key, document_id))
                                tokenized_elements.append((token, document_id))
                                bag_of_words[document_name].add(token)
                                items_count[document_name] += 1

def tokenize_text(text):
    return tokenize.word_tokenize(text, language='portuguese')

def create_gap_and_convert_binary(ids_array):
    new_ids_array = []
    new_ids_array.append((encode_number(ids_array[0][0]), ids_array[0][1]))
    for idx in range(1, len(ids_array)):
        new_ids_array.append((encode_number(ids_array[idx][0] - ids_array[idx-1][0]), ids_array[idx][1]))
    return new_ids_array

def encode_number(number):
    binary = decimalToBinary(number)
    count = 0
    encoded_number = ''
    parts = 0
    for idx in range(len(binary), 0, -1):
        if count != 6:
            encoded_number = binary[idx-1] + encoded_number
            count += 1
        else:
            if parts == 0:
                encoded_number = '1' + binary[idx-1] + encoded_number
                parts += 1
            else:
                encoded_number = '0' + binary[idx-1] + encoded_number
                parts += 1
            count = 0
    if len(encoded_number) % 8 != 0:
        zeros_needed = 8 - (len(encoded_number) % 8)
        for idx in range(0, zeros_needed):
            if idx == zeros_needed - 1:
                if parts == 0:
                    encoded_number = '1' + encoded_number
                else:
                    encoded_number = '0' + encoded_number
            else:
                encoded_number = '0' + encoded_number
    encoded_number = bin(int(encoded_number,2))
    return encoded_number
        
def decimalToBinary(n):
    return "{0:b}".format(int(n))

def compress(index):
    new_index = {}
    for element in index:
        new_index[element] = (index[element][0], create_gap_and_convert_binary(index[element][1]))
    return new_index

def create_index(tokenized_elements):
    inv_index = {}
    for element in tokenized_elements:
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
    items_count = {}
    for idx in range(0, 10):
        document = {}
        with open('../extractor/documents/document' + str(idx) + '.txt', 'rb') as file:
            document = pickle.load(file)
            file.close()
        preprocess_document(document, idx)
    sort_tokens()
    inv_index = create_index(tokenized_elements)
    inv_index_fields = create_index(tokenized_elements_fields)
    inv_index_comp = compress(inv_index)
    inv_index_fields_comp = compress(inv_index_fields)
    with open('./index.txt', 'wb') as file:
        pickle.dump(inv_index, file)
    with open('./indexfields.txt', 'wb') as file:
        pickle.dump(inv_index_fields, file)
    with open('./bagofwords.txt', 'wb') as file:
        pickle.dump(bag_of_words, file)
    with open('./indexcompressed.txt', 'wb') as file:
        pickle.dump(inv_index_comp, file)
    with open('./indexfieldscompressed.txt', 'wb') as file:
        pickle.dump(inv_index_fields_comp, file)
    with open('./documentsitemscount.txt', 'wb') as file:
        pickle.dump(items_count, file)
    #print(inv_index)
    #print(inv_index_fields)
    #print(bag_of_words)
    #print(inv_index_comp)
    #print(inv_index_fields_comp)
    #print(items_count)