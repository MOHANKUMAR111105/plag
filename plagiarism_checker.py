import os
import requests
import random
import pandas as pd
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
]

BLOCKED_DOMAINS = ["facebook.com", "instagram.com", "twitter.com", "tiktok.com"]

def get_random_headers():
    """Returns a random User-Agent header."""
    return {'User-Agent': random.choice(USER_AGENTS)}

def get_url(sentence):
    """Fetches the first URL result for the sentence from Google Search."""
    if not SERPAPI_KEY:
        print("Warning: SERPAPI_KEY not set in .env")
        return None
    params = {
        "q": sentence,
        "api_key": SERPAPI_KEY,
        "engine": "google",
    }
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        if 'organic_results' in results and results['organic_results']:
            return results['organic_results'][0].get('link', None)
    except Exception as e:
        print(f"Error fetching URL: {e}")
    return None

def get_text_from_url(url):
    """Fetches and returns the textual content from a URL."""
    try:
        if any(domain in url for domain in BLOCKED_DOMAINS):
            print(f"Skipping unsupported URL: {url}")
            return ""
        response = requests.get(url, headers=get_random_headers(), timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = [p.get_text(separator=" ", strip=True) for p in soup.find_all('p')]
        return ' '.join(paragraphs)
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch from {url}: {e}")
        return ""

def get_similarity(text1, text2):
    """Calculates cosine similarity between two texts."""
    if not text1 or not text2:
        return 0.0
    try:
        vectorizer = CountVectorizer().fit_transform([text1, text2])
        score = cosine_similarity(vectorizer[0:1], vectorizer[1:2])[0][0]
        return round(float(score), 4)
    except Exception as e:
        print(f"Similarity error: {e}")
        return 0.0

def get_similarity_between_files(file_texts):
    """Calculates cosine similarity between multiple file texts."""
    similarity_list = []
    for i in range(len(file_texts)):
        for j in range(i + 1, len(file_texts)):
            similarity = get_similarity(file_texts[i], file_texts[j])
            similarity_list.append({
                'File 1': f"File {i + 1}",
                'File 2': f"File {j + 1}",
                'Similarity': similarity,
                'Similarity_pct': f"{round(similarity * 100, 2)}%"
            })
    return similarity_list

def check_plagiarism(sentences, text):
    """Checks for plagiarism in given sentences."""
    similarity_list = []

    for idx, sentence in enumerate(sentences):
        # Skip very short sentences (less than 6 words)
        if len(sentence.split()) < 6:
            continue

        url = get_url(sentence)
        if not url:
            continue

        try:
            text_from_url = get_text_from_url(url)
            if text_from_url.strip():
                similarity = get_similarity(text, text_from_url)
                similarity_list.append({
                    'Sentence': sentence,
                    'Source': url,
                    'Similarity': similarity,
                    'Similarity_pct': f"{round(similarity * 100, 2)}%"
                })
        except Exception as e:
            print(f"Error processing sentence {idx}: {e}")

    if not similarity_list:
        return pd.DataFrame()

    df = pd.DataFrame(similarity_list)
    df = df.sort_values(by='Similarity', ascending=False).reset_index(drop=True)
    return df
