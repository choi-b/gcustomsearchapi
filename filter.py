#Filtering our results and reranking them.
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from settings import *

with open("blacklist.txt") as f:
    bad_domain_list = set(f.read().split("\n")) #read it in, split it up by line


def get_page_content(row):
    soup = BeautifulSoup(row["html"]) #strip all of the HTML and get only the text back
    text = soup.get_text()
    return text

def tracker_urls(row):
    soup = BeautifulSoup(row["html"])
    scripts = soup.find_all("script", {"src": True})
    srcs = [s.get("src") for s in scripts]

    links = soup.find_all("a", {"href":True})
    href = [l.get("href") for l in links]
    all_domains = [urlparse(s).hostname for s in srcs + href] #look through list of URLs, and pull out hostnames
    bad_domains = [a for a in all_domains if a in bad_domain_list] #will get this from a list of bad domains, some malicious, etc.
    return len(bad_domains)

class Filter():
    def __init__(self, results):
        self.filtered = results.copy()

    def content_filter(self):
        page_content = self.filtered.apply(get_page_content, axis=1) #apply the function get_page_content to each row of the dataframe
        word_count = page_content.apply(lambda x: len(x.split(" "))) #find how many words appear on that page
        word_count /= word_count.median()
        #divide by the median. Does a page have more words or fewer words than the median of the set of search results. Idea: few words = probably low quality

        word_count[word_count <= .5] = RESULT_COUNT #too little content on page -> pushes the search to the end of the ranking
        word_count[word_count != RESULT_COUNT] = 0
        self.filtered["rank"] += word_count

    def tracker_filter(self):
        tracker_count = self.filtered.apply(tracker_urls, axis=1)
        tracker_count[tracker_count > tracker_count.median()] = RESULT_COUNT * 2 #severely penalize it
        self.filtered["rank"] += tracker_count

    def filter(self):
        self.content_filter()
        self.tracker_filter()
        self.filtered = self.filtered.sort_values("rank", ascending=True)
        self.filtered["rank"] = self.filtered["rank"].round()
        return self.filtered