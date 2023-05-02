

import babelnet as bn
from babelnet import Language, BabelSynset
from babelnet.resources import BabelSynsetID
from joblib import Memory

memory = Memory("datasets/cache")

@memory.cache
def get_synset(word: str = 'bn:03566112n') -> BabelSynset:
    print('RUNNING FUNCTION')
    return bn.get_synset(BabelSynsetID('bn:03566112n'))


by = get_synset()
# bs = by.main_sense(Language.EN)
# print('\n'.join([str(((g.gloss, g.token_ids))) for g in by.glosses()]))
# print(by.categories(Language.EN))
# print(by.domains)
print(by.senses_by_word('systems', Language.EN))


# import concurrent.futures
# from datetime import datetime
# from sys import stdout

# # function called from the threads
# def func(name: str, word: str):
#     stdout.write(datetime.now().strftime("%H:%M:%S.%f") + " - Start - " + name + "\n")
#     synsets = bn.get_synsets(word, from_langs=[Language.EN])
#     glosses = []
#     for synset in synsets:
#         gloss = synset.main_gloss(Language.EN)
#         if gloss:
#             glosses.append(gloss.gloss)
#     stdout.write(datetime.now().strftime("%H:%M:%S.%f") + " - End   - " + name + "\n")
#     return {word: glosses}


# word_list = ["vocabulary", "article", "time", "bakery", "phoenix", "stunning", "judge", "clause", "anaconda",
#              "patience", "risk", "scribble", "writing", "zebra", "trade"]

# with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
#     future = []
#     for i, w in enumerate(word_list):
#         future.append(executor.submit(func, f'Thread {i} "{w}"', w))
#     results = {}
#     for f in future:
#         results.update(f.result())

# for w, gs in results.items():
#     for g in gs:
#         print(w, g, sep='\t')