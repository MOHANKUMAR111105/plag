import nltk
from nltk import tokenize

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

def get_sentences(text):
    """Splits text into sentences."""
    if not text or not text.strip():
        return []
    return tokenize.sent_tokenize(text)
