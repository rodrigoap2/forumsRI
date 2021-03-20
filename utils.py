from unidecode import unidecode

def get_parsed_phrase(soup):
    title = preprocess_phrase(soup.find('title').text)
    body = get_parsed_body(soup)
    return title + " " + max(body[1:], key=lambda s: len(s))

def get_parsed_body(soup):
    return [preprocess_phrase(s) for s in soup.find('body').text.split('\n') if s.strip() != '']

def preprocess_phrase(phrase):
    return unidecode(''.join(c for c in phrase.lower().strip() if c.isalnum() or c == ' '))
