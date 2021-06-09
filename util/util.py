from unicodedata import normalize
from stringcase import snakecase
import re

def normalize_data(text):
    return normalize('NFKD', text)


def snake(source):
    source = source.split(':')[0].strip() if source.find(
        ':') > 0 else source.strip()
    source = re.sub(r'[\W_]+ ', '', source)
    source = re.sub(' +', ' ', source)
    return snakecase(normalize_data(source.lower()).encode(
        'ASCII', 'ignore').decode('ASCII'))


