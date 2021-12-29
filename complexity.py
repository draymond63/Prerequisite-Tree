import os
from typing import List
from requests import get
import pandas as pd
from tqdm import tqdm
from nltk.corpus import stopwords
import nltk

from util import COMPLEXITY, TOPICS

nltk.download("stopwords")
nltk.download('punkt')

# mediawiki.org/w/api.php?action=help&modules=query%2Bextracts
def get_text(site, ignore=False):
    url = f"https://en.wikipedia.org/w/api.php?"
    resp = get(url, params={
        'action': 'query',
        'format': 'json',
        'origin': '*',
        'titles': site,
        'prop': 'extracts',
        'explaintext': 1,
        'exsectionformat': 'plain',
        'exlimit': 1
    }).json()
    try:
        # Parse out extract
        pages = list(resp['query']['pages'].values())
        for page in pages:
            if page and 'extract' in page:
                return page['extract']
    except (KeyError, IndexError) as e:
        if not ignore:
            raise e
        return ""

# ! Unused
# Type-Token Ration (TTR)
def TTR(text: str):
    # Tokenize the text
    text = nltk.word_tokenize(text)
    # Remove stop words and bad words
    text = [word for word in text if word not in stopwords.words('english')]
    stop_symbols = (',', '.', '=', '`', "'", ':', ';', ']', '[', ')', '(', '{', '}', '\\', '→')
    text = [word for word in text if not any(s in word for s in stop_symbols)]
    # Calculation
    return len(set(text))/len(text)

# Automated Readability Index
def ARI(text: str):
    words = text.count(' ')
    chars = len(text) - words
    sentences = len(nltk.sent_tokenize(text))
    return 4.71*(chars/words) + 0.5*(words/sentences) - 21.43

# https://towardsdatascience.com/linguistic-complexity-measures-for-text-nlp-e4bf664bd660
def get_complexity(site):
    text = get_text(site, ignore=True)
    if not text:
        return None
    return ARI(text)

def get_topic_complexity(restart=False, save_incr=True):
    topics = pd.read_csv(TOPICS, index_col='Unnamed: 0')
    # topics = [
    #     'Continuous_function', 'Absolute_value', 'Shell_integration', 
    #     'Trigonometry', 'Square', 'Isosceles_triangle', 'Pythagorean_theorem',
    #     'Hamiltonian_mechanics', 'Classical_mechanics', 'Lagrangian_mechanics',
    #     'Probability'
    # ]

    # Remove topics we already have done
    if not restart and os.path.exists(COMPLEXITY):
        comps = pd.read_csv(COMPLEXITY, index_col='Unnamed: 0')
        topics.drop(comps.index, inplace=True)

    # Get complexity for each topic
    complexities = {}
    for i, topic in tqdm(enumerate(topics.index), total=len(topics)):
        comp = get_complexity(topic)
        if comp:
            complexities[topic] = comp
        # Save every hundred articles
        if save_incr and not (i % 100):
            df = pd.Series(complexities)
            df.to_csv(COMPLEXITY)
    # Final save
    df = pd.Series(complexities)
    df.to_csv(COMPLEXITY)

if __name__ == '__main__':
    get_topic_complexity()