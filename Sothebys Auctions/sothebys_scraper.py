import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from difflib import SequenceMatcher
import time

def get_resale_right(slug_url):
    """Fetch the detail page for the artwork and check for ArtistsResaleRight in symbols."""
    try:
        response = requests.get(slug_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        tag = soup.find('a', id='0ArtistsResaleRight')
        if tag is None:
            tag = soup.find('a', id='1ArtistsResaleRight')
        if tag is None:
            tag = soup.find('a', id='2ArtistsResaleRight')
        if tag is None:
            tag = soup.find('a', id='3ArtistsResaleRight')
        if tag is None:
            tag = soup.find('a', id='4ArtistsResaleRight')
        return "Yes" if tag else "No"
    except Exception:
        return "Unknown"


def normalize_name(name):
    tokens = str(name).strip().lower().split()
    if len(tokens) == 0:
        return ''
    if len(tokens) == 1:
        return tokens[0]
    return f"{tokens[0]} {tokens[-1]}"

def similar(a, b, threshold=0.9):
    return SequenceMatcher(None, a, b).ratio() >= threshold

url = input("Paste your Sotheby's auction URL here: ")
# url = 'https://www.sothebys.com/en/buy/auction/2025/modern-contemporary-evening-auction-l25006?locale=en'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the embedded JSON data
script_tag = soup.find('script', id='__NEXT_DATA__')
if not script_tag:
    print("Could not find JSON data on the page.")
    exit(1)

data = json.loads(script_tag.string)
lots = []

# Traverse the JSON to find all creators, titles, estimates, slug, and resale right
try:
    hits = data['props']['pageProps']['algoliaJson']['hits']
    for lot in hits:
        creators = lot.get('creators', [])
        title = lot.get('title', '')
        low_estimate = lot.get('lowEstimate', '')
        high_estimate = lot.get('highEstimate', '')
        currency = lot.get('currency', '')
        lot_number = lot.get('lotNr', '')
        slug = lot.get('slug', '')
        resale_right = "Unknown"
        if slug:
            slug_url = f"https://www.sothebys.com{slug}"
            resale_right = get_resale_right(slug_url)
            time.sleep(0.5)  
        for artist in creators:
            if artist and isinstance(artist, str):
                lots.append({
                    'artist_name': artist.strip(),
                    'title': title.strip(),
                    'estimate': f"{low_estimate}-{high_estimate}" if low_estimate and high_estimate else '',
                    'lot_number': lot_number,
                    'resale_right': resale_right
                })
except Exception as e:
    print("Error parsing JSON:", e)
    exit(1)

# Convert lots to DataFrame
artist_names = pd.DataFrame(lots)

# Load ACS artists (assume first column is the name)
acs_artists = pd.read_csv('acs_artists.csv', sep='\t', dtype=str)
# Load DACS artists (assume first column is the name)
dacs_artists = pd.read_csv('dacs_artists.csv', sep='\t', dtype=str)

# Normalize names for matching
artist_names['norm'] = artist_names['artist_name'].apply(normalize_name)
acs_artists['norm'] = acs_artists.iloc[:, 0].apply(normalize_name)
dacs_artists['norm'] = dacs_artists.iloc[:, 0].apply(normalize_name)

# Drop rows with missing names
artist_names = artist_names.dropna(subset=['norm'])
acs_artists = acs_artists.dropna(subset=['norm'])
dacs_artists = dacs_artists.dropna(subset=['norm'])

acs_confirmed = set()
dacs_confirmed = set()

for idx, row in artist_names.iterrows():
    name = row['norm']
    original_name = row['artist_name']
    found_acs = False
    found_dacs = False
    for acs_name in acs_artists['norm']:
        if similar(name, acs_name):
            acs_confirmed.add(original_name)
            found_acs = True
            break
    if not found_acs:
        for dacs_name in dacs_artists['norm']:
            if similar(name, dacs_name):
                dacs_confirmed.add(original_name)
                found_dacs = True
                break

# Write results to CSV
with open('sothebys_artists.csv', 'w', encoding='utf-8') as f:
    f.write("artist_name\ttitle\testimate\tlot_number\tcollecting_society\tresale_right\n")
    for idx, row in artist_names.iterrows():
        artist = row['artist_name']
        title = row['title']
        estimate = row['estimate']
        lot_number = row['lot_number']
        resale_right = row['resale_right']
        society = ''
        if artist in acs_confirmed:
            society = 'ACS'
        elif artist in dacs_confirmed:
            society = 'DACS'
        f.write(f"{artist}\t{title}\t{estimate}\t{lot_number}\t{society}\t{resale_right}\n")

print(f"Found {len(artist_names)} lots. Saved to 'sothebys_artists.csv'.")
