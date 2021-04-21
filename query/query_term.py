import pickle


if __name__ == "__main__":

    inverted_index_fields = {}
    bw = {}
    with open('../invertedindex/indexfields.txt', 'rb') as index_file:
        inverted_index_fields = pickle.load(index_file)

    with open('../invertedindex/bagofwords.txt', 'rb') as bw_file:
        bw = pickle.load(bw_file)
