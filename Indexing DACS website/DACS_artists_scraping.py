import requests
from bs4 import BeautifulSoup
import time

template_url = 'https://forms.dacs.org.uk/for-art-market-professionals/artist-search/artist-details?ArtistId=ARTS'

def check_artists_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Artist name
    name_tag = soup.find('h1')
    artist_name = name_tag.get_text(strip=True) if name_tag else "Unknown"
    artist_name = artist_name.replace(',', ' ')
    
    # Nationality
    nationality_tag = soup.find('span', id='p_lt_zoneDocument_pageplaceholder_pageplaceholder_lt_zoneLeft_ArtistDetails_lbNationality')
    nationality = nationality_tag.get_text(strip=True) if nationality_tag else ""
    
    # Date of birth
    dob_tag = soup.find('span', id='p_lt_zoneDocument_pageplaceholder_pageplaceholder_lt_zoneLeft_ArtistDetails_lblDateOfBirth')
    dob = dob_tag.get_text(strip=True) if dob_tag else ""
    
    # Date of death
    dod_tag = soup.find('span', id='p_lt_zoneDocument_pageplaceholder_pageplaceholder_lt_zoneLeft_ArtistDetails_lblDateofDeath')
    dod = dod_tag.get_text(strip=True) if dod_tag else ""
    dod = dod[1:] if dod else ""
    
    # ARR eligibility
    arr_status = "Unknown"
    arr_verified = soup.find('li', string=lambda s: s and "Verified by DACS as eligible for ARR Royalties" in s)
    arr_dacs_allocated = soup.find('dt', string=lambda s: s and "ARR payments are necessary" in s)
    arr_sister_agency = soup.find('li', string=lambda s: s and "DACS is acting as the collecting agency through a Sister Society" in s)
    arr_may_be = soup.find('li', string=lambda s: s and "DACS has not confirmed this artists nationality." in s)
    arr_not_necessary = soup.find('dt', string=lambda s: s and "ARR payments are not necessary" in s)
    

    if arr_may_be:
        arr_status = "Unknown"
    if arr_verified or arr_dacs_allocated or arr_sister_agency:
        arr_status = "Eligible"
    if arr_not_necessary:
        arr_status = "Not eligible"

    allocated = 'True' if arr_dacs_allocated or arr_sister_agency else 'False'
    
    return artist_name, nationality, dob, dod, arr_status, allocated
    

artist_infos = []
for i in range(1, 10):
    num_str = f"{i:06d}"  # Pad with zeros, e.g. 000001
    url = template_url + num_str
    info = check_artists_page(url)
    artist_infos.append(info)
    time.sleep(0.1)  # Be polite

with open('dacs_artist_names.csv', 'w', encoding='utf-8') as f:
    f.write("name\tnationality\tdob\tdod\tarr_status\n")
    for info in artist_infos:
        f.write('\t'.join(info) + '\n')