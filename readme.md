A list of the files in submission and what they do.
 
===========
 
HOW TO RUN
 
1. open the terminal
2. Reach the directory of "Crawler.py"
3. Run "python WebCrawler.py 'query' n"
 
query: keywords 
n: the number of total pages to be downloaded
 

===========

FILE LIST:

1. Crawler.py:

The entrance of this crawler.
Given query and a number, the crawler will first connect to Google, and return top-10 results(we give them highest priority score(1000)), and then crawl starting from them in focused strategy manner until we download all n pages.

2. CheckUrl.py

CheckUrl.validifyUrl function is used for normalizing url, like delete index/main/default from the end of url

3. Crawlable.py

Given a url, return its root site, and decide whether this url can be crawled or not by robot.txt

4. CheckContent.py

Check if two pages are similar but with different url.(There are some bugs in it, not 100% correct)

5. SimHash.py

The sim-hash function and hanging distance function used in CheckContent.py
