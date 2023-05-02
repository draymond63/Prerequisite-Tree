

import spacy
import babelnet as bn

from spacy import displacy
from spacy.tokens.doc import Doc
from babelnet import Language, BabelSynset
from babelnet.resources import BabelSynsetID
from joblib import Memory
from typing import Dict, Set

memory = Memory("datasets/cache")
model = spacy.load('en_core_web_sm')

@memory.cache
def get_synset(babel_id: str = 'bn:03566112n') -> BabelSynset:
    print('RUNNING FUNCTION')
    return bn.get_synset(BabelSynsetID(babel_id))

def get_prerequisites(synset: BabelSynset) -> Dict[str, Set[BabelSynset]]:
    # TODO: Extract main phrase of sentence
    # TODO: For each noun chunk, find all possible synsets
    # TODO: Determine best synset for each noun chunk based on categorical similarity to original synset
    for gloss in synset.glosses():
        parsed = model(gloss.gloss)
        for noun in parsed.noun_chunks:
            print(f'"{noun.text}"', noun.root.dep_, noun.root.head.text)

def get_referenced_synsets(synset: BabelSynset) -> Set[BabelSynsetID]:
    referenced_synsets = set()
    for gloss in synset.glosses():
        for token in gloss.token_ids:
            referenced_synsets.add(token.id)
    return referenced_synsets

if __name__ == '__main__':
    by = get_synset('bn:03888638n')
    print(get_referenced_synsets(by))
    # get_prerequisites(by)
    # print('\n'.join([str(((g.gloss, g.token_ids))) for g in by.glosses()]))
