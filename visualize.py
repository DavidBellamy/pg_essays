import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('pg_essays_wc.csv')

total_wc = df['Word Count'].sum()

# Histogram of word counts
df['Word Count'].plot(kind='hist', bins=30, alpha=0.7)
plt.title(f'Histogram of Word Counts in Paul Graham Essays \n Total word count = {total_wc}')
plt.xlabel('Word Count')
plt.ylabel('Frequency')
plt.savefig('word_count_histogram.png', dpi=300)
