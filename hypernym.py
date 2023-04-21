
import spacy
from page_retrieval import PageRetriever, parse_sections

glossary_article = 'Historical_Geology/Glossary_and_index'

model = spacy.load("en_core_web_sm")
text = PageRetriever().get_article_text(glossary_article)
sections = parse_sections(text)

for item, definition in sections.items():
    print(f'\n\n{item}')
    document = model(definition)
    for token in document:
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
                token.shape_, token.is_alpha, token.is_stop)
    spacy.displacy.serve(document, style="dep")

# for chunk in document.noun_chunks:
#     print(chunk)

# for token in document:
# 	print(
# 		f"""
# TOKEN: {token.text}
# =====
# {token.tag_ = }
# {token.head.text = }
# {token.dep_ = }"""
# 	)

# displacy.serve(document, style="dep")