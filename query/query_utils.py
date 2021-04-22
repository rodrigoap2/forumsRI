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

    if not len(results_1) or not len(results_2):
        return 0

    if len(results_1) == 1 or len(results_2) == 1:
        return 1 if results_1[0] == results_2[0] else 0

    n = len(pairs_1)

    delta = 0
    for i in range(len(pairs_1)):
        if pairs_1[i] not in pairs_2:
            delta += 1

    delta *= 2
    return 1 - 2 * delta / (2 * n)
