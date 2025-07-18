import pandas as pd
from difflib import SequenceMatcher

def normalize_name(name):
    """Lowercase, strip, and keep only first and last name."""
    tokens = str(name).strip().lower().split()
    if len(tokens) == 0:
        return ''
    if len(tokens) == 1:
        return tokens[0]
    # Use only first and last token
    return f"{tokens[0]} {tokens[-1]}"

def similar(a, b, threshold=0.9):
    """Return True if names are similar enough."""
    return SequenceMatcher(None, a, b).ratio() >= threshold

# Load artist names to check (one name per line, no header)
artist_names = pd.read_csv('artist_names.csv', header=None, names=['artist_name'], dtype=str)
# Load ACS artists (assume first column is the name)
acs_artists = pd.read_csv('acs_artists.csv', sep='\t', dtype=str)

# Normalize names for matching
artist_names['norm'] = artist_names['artist_name'].apply(normalize_name)
acs_artists['norm'] = acs_artists.iloc[:, 0].apply(normalize_name)

# Drop rows with missing names
artist_names = artist_names.dropna(subset=['norm'])
acs_artists = acs_artists.dropna(subset=['norm'])

matches = set()

for name in artist_names['norm']:
    for acs_name in acs_artists['norm']:
        if similar(name, acs_name):
            # Find the original artist name (not normalized) for output
            original_name = artist_names[artist_names['norm'] == name]['artist_name'].iloc[0]
            matches.add(original_name)
            break

# Write matches to file
with open('matched_artist_names.csv', 'w', encoding='utf-8') as f:
    for match in sorted(matches):
        f.write(match + '\n')