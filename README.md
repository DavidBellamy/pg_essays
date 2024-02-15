A simple program that visits every Paul Graham essay listed in the RSS feed 
made by Aaron Swartz (http://www.aaronsw.com/2002/feeds/pgessays.rss) and gathers word counts. 

Can be adapted to gather all sorts of other essay-specific statistics or data.

Built using Python 3.11.6. Install requirements with `pip install -r requirements.txt`. 
Run the word counter with `python scrape.py`, which produces a CSV file with the word counts, `pg_essays_wc.csv`.
Sum the word counts and plot a histogram with `python visualize.py`. 