

import requests
import pandas as pd

from bs4 import BeautifulSoup
from tqdm import tqdm

# Essay links obtained from the RSS feed
url = "http://www.aaronsw.com/2002/feeds/pgessays.rss"

# Fetch the RSS feed content
response = requests.get(url)
xml_content = response.text

soup = BeautifulSoup(xml_content, 'xml')

# Initialize a list to store dictionaries of essay information
data = []

# Process each essay item
for item in tqdm(soup.find_all('item')):
    link = item.find('link').text
    title = item.find('title').text

    # If link contains "sep.turbifycdn" strip the erroneous preface 'http://www.paulgraham.com/' from it
    if "sep.turbifycdn" in link:
        link = link.replace('http://www.paulgraham.com/', '')

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
