import spacy
from spacy.matcher import Matcher

nlp = spacy.blank("en")
matcher = Matcher(nlp.vocab)
matcher.add("PORT_CODE", [[{"TEXT": {"REGEX": "^[A-Z]{2}[A-Z0-9]{3}$"}}]])

doc = nlp("Shipment from INNSA to USNYC")
for match_id, start, end in matcher(doc):
    print("Port code:", doc[start:end].text)
