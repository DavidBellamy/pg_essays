import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('pg_essays_wc.csv')

# Print the total word count of all essays
print(f"Total word count: {df['Word Count'].sum()}")

# Histogram of word counts
df['Word Count'].plot(kind='hist', bins=30, alpha=0.7)
plt.title('Histogram of Word Counts in Paul Graham Essays')
plt.xlabel('Word Count')
plt.ylabel('Frequency')
plt.show()
