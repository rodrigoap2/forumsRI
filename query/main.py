from query import query_cosine, query_tf, bm25
from query_term import query_cosine_term, query_tf_term
from query_utils import print_query, tfidf
import pickle

if __name__ == "__main__":

    inverted_index = {}
    inverted_index_fields = {}

    bw = {}
    items_count = {}
    with open('../invertedindex/index.txt', 'rb') as index_file:
        inverted_index = pickle.load(index_file)

    with open('../invertedindex/indexfields.txt', 'rb') as index_file:
        inverted_index_fields = pickle.load(index_file)

    with open('../invertedindex/bagofwords.txt', 'rb') as bw_file:
        bw = pickle.load(bw_file)

    with open('../invertedindex/documentsitemscount.txt', 'rb') as ic_file:
        items_count = pickle.load(ic_file)

    option = "-1"
    N = len(items_count)

    tfidf_table = tfidf(inverted_index, N)

    while option != "0":
        print('Selecione o tipo da consulta:')
        print('     0: Sair')
        print('     1: Consulta normal')
        print('     2: Consulta por campo')
        option = input()
        
        query_option = '-1'

        if option == '1':
            while query_option != '0':
                print('Qual tipo de ranqueamento?')
                print('     0: Sair')
                print('     1: Básico')
                print('     2: Coseno')
                print('     3: BM25')
                
                query_option = input()
                query_string = ''
                if query_option == '1':
                    query_string = input('Insira a frase da consulta: ')
                    print_query(query_tf(query_string, inverted_index))
                elif query_option == '2':
                    query_string = input('Insira a frase da consulta: ')
                    print_query(query_cosine(
                        query_string, tfidf_table, N, inverted_index))
                elif query_option == '3':
                    query_string = input('Insira a frase da consulta: ')
                    print_query(
                        bm25(query_string, items_count, inverted_index, N))

                print('\n\n\n')

        elif option == '2':
            while query_option != '0':
                print('Qual tipo de ranqueamento?')
                print('     0: Sair')
                print('     1: Básico')
                print('     2: Coseno')

                query_option = input()

                date = ''
                question_title = ''
                question_author = ''
                question_text = ''
                answers_author = ''
                answers_text = ''

                if query_option == '1':
                    date = input('Insira a data: ')
                    question_title = input('Insira o titulo da pergunta: ')
                    question_author = input('Insira o autor da pergunta: ')
                    question_text = input('Insira o texto da pergunta: ')
                    answers_author = input('Insira o autor da resposta: ')
                    answers_text = input('Insira o texto da resposta: ')

                    print_query(query_tf_term(title=question_title, date=date, question_author=question_author, 
                                question_text=question_text, answers_author=answers_author, answers_text=answers_text,
                                inverted_index_fields=inverted_index_fields))
                
                elif query_option == '2':
                    date = input('Insira a data: ')
                    question_title = input('Insira o titulo da pergunta: ')
                    question_author = input('Insira o autor da pergunta: ')
                    question_text = input('Insira o texto da pergunta: ')
                    answers_author = input('Insira o autor da resposta: ')
                    answers_text = input('Insira o texto da resposta: ')

                    print_query(query_cosine_term(title=question_title, date=date, question_author=question_author,
                                              question_text=question_text, answers_author=answers_author, answers_text=answers_text,
                                              inverted_index_fields=inverted_index_fields))
