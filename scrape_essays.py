

import requests
import pandas as pd

from bs4 import BeautifulSoup
from tqdm import tqdm

# Essay links obtained from Paul Graham's articles page
url = "https://paulgraham.com/articles.html"

# Fetch the articles page
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

# Collect essay links and titles from the page
essays = []
for a in soup.find_all('a', href=True):
    href = a['href']
    title = a.get_text(strip=True)
    if not title or not href.endswith('.html'):
        continue
    # Skip self-links and non-essay pages
    if href in ('articles.html', 'index.html'):
        continue
    # Build full URL from relative href
    if href.startswith('http'):
        link = href
    else:
        link = 'http://www.paulgraham.com/' + href
    essays.append((title, link))

# Initialize a list to store dictionaries of essay information
data = []

# Process each essay
for title, link in tqdm(essays):
    # Fetch each essay page to calculate word count
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the title text and word count
    if soup.find('body'):
      body_text = soup.find('body').get_text(separator=' ', strip=True)
    else:
      body_text = soup.get_text(separator=' ', strip=True)

    word_count = len(body_text.split())

    # Append the information as a dictionary to the data list
    data.append({
        'Essay Title': title,
        'Essay Link': link,
        'Word Count': word_count
    })

# Create a DataFrame from the data list
df = pd.DataFrame(data)

# Write the DataFrame to a CSV file
df.to_csv('pg_essays_wc.csv', index=False, encoding='utf-8')
