import time
from bs4 import BeautifulSoup
from selenium import webdriver
import lxml.html
from dateutil.parser import parse
import pickle

def generate_xpath(element):
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:  # type: bs4.element.Tag
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
                )
            )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)

def extractor(link, index):
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--incognito")
    options.headless = True
    options.add_argument("--no-sandbox")
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=options)
    driver.get(link)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "lxml")
    if 'community.shopify' in link:
        result = soup.findAll('div',  {"class": ["lia-message-view-forum-message"]})
    else: 
        result = soup.findAll('article')
    file_path = './documentsNew/document' + str(index) + '.txt'
    f = open(file_path, 'wb')
    post_description = {'date': '', 'question': {'author': '', 'text': '', 'title':''}, 'answers': []}
    posts = 0
    for article in result:
        text = ''
        line = 0
        valid_post = True
        for div in article.findAll('div', recursive=False):
            current_text = driver.find_element_by_xpath(generate_xpath(div)).text
            if current_text != '\n' and current_text != '' and current_text != ' ':
                valid_post = True
                text += current_text + '\n'
                splitted_text = current_text.split('\n')
                if posts == 0:
                    for line in range(0, len(splitted_text)):
                        current_line = splitted_text[line]
                        if post_description['date'] == '':
                            if validate_date(current_line):
                                post_description['date'] = current_line
                                continue
                        if post_description['question']['author'] == '':
                            if not current_line.isnumeric() and not validate_date(current_line):
                                post_description['question']['author'] = current_line
                        elif post_description['question']['author'] != '' and post_description['date'] != '':
                            if post_description['question']['title'] == '':
                                post_description['question']['title'] = current_line
                            post_description['question']['text'] += current_line + '\n'
                else:
                    post_description['answers'].append({'date': '', 'author': '', 'text': ''})
                    total_answers = len(post_description['answers'])
                    for line in range(0, len(splitted_text)):
                        current_line = splitted_text[line]
                        if post_description['answers'][total_answers-1]['date'] == '':
                            if validate_date(current_line):
                                post_description['answers'][total_answers-1]['date'] = current_line
                                continue
                        if post_description['answers'][total_answers-1]['author'] == '':
                            if not current_line.isnumeric() and not validate_date(current_line):
                                post_description['answers'][total_answers-1]['author'] = current_line
                        elif post_description['answers'][total_answers-1]['author'] != '' and post_description['answers'][total_answers-1]['date'] != '':
                            post_description['answers'][total_answers-1]['text'] += current_line + '\n'
            else:
                valid_post = False
        if valid_post:
            posts += 1
    pickle.dump(post_description, f)
    f.close()

def validate_date(text):
    months = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez']
    has_month = False
    has_date = False
    text = text.lower()
    text_divided = text.split()
    for element in text_divided: 
        if not has_month:
            for month in months:
                if month in element:
                    has_month = True
                    break
        if element.isnumeric():
            has_date = True
    if (has_month and has_date) or ('há' in text and ('mês' in text or 'ano' in text or 'meses')):
        return True
    else:
        try:
            parse(text)
            return True
        except ValueError:
            return False
    

if __name__ == "__main__":
    f = open("linkshopify.txt", "r")
    links = f.read().split('\n')
    link_counter = 30
    for link in links:
        extractor(link, link_counter)
        print(link, 'terminou esse link')
        link_counter += 1