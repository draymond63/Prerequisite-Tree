import pandas as pd

from util import TOPICS, CITATIONS, get_text

def get_year(article):
    text = get_text(article)
    ...

def get_topics_years(save_incr=True):
    topics = pd.read_csv(TOPICS, index_col='Unnamed: 0')
    # topics = [
    #     'Continuous_function', 'Absolute_value', 'Shell_integration', 
    #     'Trigonometry', 'Square', 'Isosceles_triangle', 'Pythagorean_theorem',
    #     'Hamiltonian_mechanics', 'Classical_mechanics', 'Lagrangian_mechanics',
    #     'Probability'
    # ]

    # Get citations for each topic
    citations = {}
    for i, topic in enumerate(topics.index):
        year = get_year(topic)
        if year:
            citations[topic] = year
        # Save every hundred articles
        if save_incr and (i % 100) == 0:
            df = pd.Series(citations)
            df.to_csv(CITATIONS)
    # Final save
    df = pd.Series(citations)
    df.to_csv(CITATIONS)

if __name__ == "__main__":
    get_topics_years()