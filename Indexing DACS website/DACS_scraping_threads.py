# import requests
# from bs4 import BeautifulSoup
# from concurrent.futures import ThreadPoolExecutor

# template_url = 'https://forms.dacs.org.uk/for-art-market-professionals/artist-search/artist-details?ArtistId=ARTS'

# def check_artists_page(i):
#     num_str = f"{i:06d}"
#     url = template_url + num_str
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     name_tag = soup.find('h1')
#     artist_name = name_tag.get_text(strip=True) if name_tag else "Unknown"
#     artist_name = artist_name.replace(',', ' ')

#     arr_dacs_allocated = soup.find('dt', string=lambda s: s and "ARR payments are necessary" in s)
#     arr_sister_agency = soup.find('li', string=lambda s: s and "DACS is acting as the collecting agency through a Sister Society" in s)
#     allocated = 'True' if arr_dacs_allocated or arr_sister_agency else 'False' 
#     return artist_name, allocated

# artist_infos = []
# with ThreadPoolExecutor(max_workers=10) as executor:
#     results = executor.map(check_artists_page, range(40000, 60000))  # Increase range as needed
#     for info in results:
#         artist_infos.append(info)

# with open('dacs_artist_names.csv', 'w', encoding='utf-8') as f:
#     f.write("name\tallocated\n")
#     for info in artist_infos:
#         if info[1] == "True":
#             f.write('\t'.join(info) + '\n')



import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

template_url = 'https://forms.dacs.org.uk/for-art-market-professionals/artist-search/artist-details?ArtistId=ARTS'

def check_artists_page(i):
    num_str = f"{i:06d}"
    url = template_url + num_str
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    name_tag = soup.find('h1')
    artist_name = name_tag.get_text(strip=True) if name_tag else "Unknown"
    lastname= artist_name.split(",")[0] if artist_name else "Unknown"
    firstname = artist_name.split(",")[-1] if artist_name else "Unknown"
    fullname = firstname + " " + lastname

    arr_dacs_allocated = soup.find('dt', string=lambda s: s and "ARR payments are necessary" in s)
    arr_sister_agency = soup.find('li', string=lambda s: s and "DACS is acting as the collecting agency through a Sister Society" in s)
    allocated = 'True' if arr_dacs_allocated or arr_sister_agency else 'False'

    # Split artist name into first and last name

    firstname = firstname.split(" ")[0] if firstname else "Unknown"
    lastname = lastname.split(" ")[-1] if lastname else "Unknown"

    
    return firstname, lastname, fullname, allocated, num_str

artist_infos = []
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(check_artists_page, range(1, 30000))
    for info in results:
        artist_infos.append(info)

with open('dacs_artist_names.csv', 'w', encoding='utf-8') as f:
    f.write("firstname\tlastname\tfullname\tpage_number\n")
    for info in artist_infos:
        if info[3] == "True":
            f.write(f"{info[0]}\t{info[1]}\t{info[2]}\t{info[4]}\n")
