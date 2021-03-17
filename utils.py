from unidecode import unidecode

def get_parsed_body(soup):
    # return [s.strip() for s in soup.find('body').text.split('\n') if s.strip() != '']
    return [preprocess_phrase(s) for s in soup.find('body').text.split('\n') if s.strip() != '']

def preprocess_phrase(phrase):
    return unidecode(''.join(c for c in phrase.lower().strip() if c.isalnum() or c == ' '))
