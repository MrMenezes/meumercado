from unicodedata import normalize
from stringcase import snakecase
import re

def snake(source):
    source = source.split(":")[0].strip() if source.find(
        ":") > 0 else source.strip()
    source = re.sub(r'[\W_]+ ', '', source)
    source = re.sub(' +', ' ', source)
    return snakecase(normalize('NFKD', source.lower()).encode(
        'ASCII', 'ignore').decode('ASCII'))