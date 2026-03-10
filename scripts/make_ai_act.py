#! /usr/bin/env python

import wget
import os
import pdfplumber
import utils
import pickle
from mkdata.ai_act_functions import crop_page
from mkdata.ai_act_functions import ai_act_extract_docPart
from mkdata.ai_act_functions import ai_act_gather_recitals
from mkdata.ai_act_functions import ai_act_parse_sequential_recitals
from mkdata.ai_act_functions import ai_act_tokenize_recitals
from mkdata.ai_act_functions import ai_act_gather_articles
from mkdata.ai_act_functions import ai_act_tokenize_articles
from mkdata.ai_act_functions import ai_act_gather_annexes
from mkdata.ai_act_functions import ai_act_tokenize_annexes

AI_ACT_PDF_URL = 'https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689'
AI_ACT_RECITAL_RANGE = list(range(0, 43))
AI_ACT_ARTICLE_RANGE = list(range(43, 123))
AI_ACT_ANNEX_RANGE = list(range(123, 144))
AI_ACT_RECITAL_INIT_NUM = 1

AI_ACT_RECITALS_BOT_RATES = [0.89, 0.9, 0.7, 0.9, 0.95, 0.95, 0.95, 0.9, 0.9,
                             0.9, 0.95, 0.85, 0.8, 0.8, 0.95, 0.95, 0.95, 0.88,
                             0.95, 0.95, 0.9, 0.9, 0.9, 0.95, 0.9, 0.95, 0.9,
                             0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95,
                             0.88, 0.9, 0.95, 0.84, 0.83, 0.95, 0.9, 0.88, 0.95]
AI_ACT_RECITALS_TOP_RATE = [0.1] * len(AI_ACT_RECITALS_BOT_RATES)


AI_ACT_ARTICLES_TOP_RATES = [0.7, 0.1, 0.1]
AI_ACT_ARTICLES_BOT_RATES = [0.95, 0.9, 0.9]
AI_ACT_ARTICLES_PAGE_INDEXES = [43, 105, 120]

AI_ACT_DEFAULT_TOP_RATE = 0.1
AI_ACT_DEFAULT_BOT_RATE = 0.95

DEFAULT_OUT = 'data/datasets'


def make_main_path(out=DEFAULT_OUT):
    if not os.path.isdir(out):
        os.makedirs(out)


def pdf_to_text(pdf_path, page_range=None):
    assert isinstance(page_range, list), "Range of pages should be a list"
    assert all(i >= 0 for i in page_range), "Can not have page below 0"
    pdf_reader = pdfplumber.open(pdf_path)
    if page_range is None:
        page_range = range(len(pdf_reader.pages))
    text = ''
    for page_num in page_range:
        crop_page(pdf_reader.pages[page_num], 1, 1)
        input()
        if page_num < len(pdf_reader.pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        else:
            print(f"Page {page_num} is out of range.")
    pdf_reader.close()
    return text


def make_ai_act_recitals(file_name, out=DEFAULT_OUT, prefix='ai_act',
                         validate=False):
    raw_recs_text = ai_act_extract_docPart(pdf_path=file_name,
                                           top_rate=AI_ACT_RECITALS_TOP_RATE,
                                           bot_rates=AI_ACT_RECITALS_BOT_RATES,
                                           page_range=AI_ACT_RECITAL_RANGE,
                                           is_recital=True)
    per_recital_list = ai_act_gather_recitals(raw_recs_text)
    connected_recitals = ai_act_parse_sequential_recitals(per_recital_list)

    if validate:
        out_str = out + '/' + prefix + '/' + 'ai_act_recitals.txt'
        with open(out_str, 'w', encoding='utf-8') as txt_file:
            for recital in connected_recitals:
                txt_file.write(recital.replace('\n', ' '))
                txt_file.write('\n')
                txt_file.write('\n')

    pickle_out = out + '/' + prefix + '/' + 'ai_act_recitals.pkl'
    with open(pickle_out, 'wb') as file:
        pickle.dump(connected_recitals, file)
    recitals2sentence, labels = ai_act_tokenize_recitals(connected_recitals)
    pickle_out = out + '/' + prefix + '/' + 'ai_act_recitals_tokenized.pkl'
    with open(pickle_out, 'wb') as file:
        pickle.dump(recitals2sentence, file)
    pickle_out = out + '/' + prefix + '/' + \
        'ai_act_recitals_tokenized_labels.pkl'
    with open(pickle_out, 'wb') as file:
        pickle.dump(labels, file)


def make_ai_act_articles(file_name, out=DEFAULT_OUT, prefix='ai_act',
                         validate=False):
    raw_arts_text = ai_act_extract_docPart(pdf_path=file_name,
                                           top_rate=AI_ACT_ARTICLES_TOP_RATES,
                                           bot_rates=AI_ACT_ARTICLES_BOT_RATES,
                                           page_range=AI_ACT_ARTICLE_RANGE,
                                           page_indexes=AI_ACT_ARTICLES_PAGE_INDEXES,
                                           )
    per_article_list = ai_act_gather_articles(raw_arts_text)

    if validate:
        out_str = out + '/' + prefix + '/' + 'ai_act_articles.txt'
        with open(out_str, 'w', encoding='utf-8') as txt_file:
            for article in per_article_list:
                txt_file.write(article.replace('\n', ' '))
                txt_file.write('\n')
                txt_file.write('\n')

    articles2sentence, labels = ai_act_tokenize_articles(per_article_list)

    pickle_out = out + '/' + prefix + '/' + 'ai_act_articles.pkl'
    with open(pickle_out, 'wb') as file:
        pickle.dump(per_article_list, file)
    pickle_out = out + '/' + prefix + '/' + 'ai_act_articles_tokenized.pkl'
    with open(pickle_out, 'wb') as file:
        pickle.dump(articles2sentence, file)
    pickle_out = out + '/' + prefix + '/' + \
        'ai_act_articles_tokenized_labels.pkl'
    with open(pickle_out, 'wb') as file:
        pickle.dump(labels, file)


def make_ai_act_annexes(file_name, out=DEFAULT_OUT, prefix='ai_act',
                        validate=False):
    raw_annex_text = ai_act_extract_docPart(pdf_path=file_name,
                                            top_rate=AI_ACT_DEFAULT_TOP_RATE,
                                            bot_rates=AI_ACT_DEFAULT_BOT_RATE,
                                            page_range=AI_ACT_ANNEX_RANGE,
                                            )
    per_annex_list = ai_act_gather_annexes(raw_annex_text)

    if validate:
        out_str = out + '/' + prefix + '/' + 'ai_act_annexes.txt'
        with open(out_str, 'w', encoding='utf-8') as txt_file:
            for annex in per_annex_list:
                txt_file.write(annex.replace('\n', ' '))
                txt_file.write('\n')
                txt_file.write('\n')

    annex2sentence = ai_act_tokenize_annexes(per_annex_list)

    pickle_out = out + '/' + prefix + '/' + 'ai_act_annexes.pkl'
    with open(pickle_out, 'wb') as file:
        pickle.dump(per_annex_list, file)
    pickle_out = out + '/' + prefix + '/' + 'ai_act_annexes_tokenized.pkl'
    with open(pickle_out, 'wb') as file:
        pickle.dump(annex2sentence, file)


def make_ai_act(out=DEFAULT_OUT, prefix='ai_act'):
    file_name = out + '/' + prefix + '/' + 'ai_act.pdf'
    if os.path.isfile(file_name):
        utils.log('AI Act file already exists!')
    else:
        if not os.path.isdir(out + '/' + prefix):
            os.makedirs(out + '/' + prefix)
        wget.download(AI_ACT_PDF_URL, out=file_name)

    make_ai_act_recitals(file_name, validate=True)
    utils.log('Completed the extraction of AI Act recitals')
    make_ai_act_articles(file_name, validate=True)
    utils.log('Completed the extraction of AI Act articles')
    make_ai_act_annexes(file_name, validate=True)
    utils.log('Completed the extraction of AI Act annexes')


def ai_act():
    make_main_path()
    make_ai_act()


if __name__ == "__main__":
    ai_act()
