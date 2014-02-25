__author__ = 'WangCHX'

import os
import datetime
import sys
import urllib
import urllib2
import json
import CheckUrl
import Crawlable
import htmllib
import CheckContent
import urlparse
import formatter
import threading
import Queue
import heapdict
argv = sys.argv
"""
if len(sys.argv) < 3:
    sys.exit("invalid arguments, please insert query and a number")
"""

#query = argv[1]
#total = argv[2]
query = "ggg"
total = 500
# split keyword into list e.g. "dog cat" => ["dog", "cat"]
keywords = query.lower().split()
queue = heapdict.heapdict() # container of url, used as heap in next
dict = {} # hash table of url, (url, score)

def computeScore(content):
    """
    this is used to computer priority score of that page, use naive method
    compute the number of keywords in the content of that page
    """
    content = content.lower()
    content = content.split()
    priorityScore = 0
    for keyword in keywords:
        for word in content:
            if keyword == word:
                priorityScore += 1
    return priorityScore

queryUrl = "https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=" + urllib.quote(query)
response1 = urllib2.urlopen(queryUrl + "&rsz=8")
for result in json.load(response1)['responseData']['results']:
    url = CheckUrl.validifyUrl(result['unescapedUrl'])
    queue[url] = -1000 # put them into heap, [-1000, url] represents the score is -1000, and url is url.
    dict[url] = -1000

response1.close()
response2 = urllib2.urlopen(queryUrl + "&rsz=2&start=8")

for result in json.load(response2)['responseData']['results']:
    url = CheckUrl.validifyUrl(result['unescapedUrl'])
    #heapq.heappush(queue, [-1000,url])
    queue[url] = -1000
    """
    because heapq in python is small root based, so using negative num can make it big-root-based.
    """
    dict[url] = -1000

response2.close()
class Parser(htmllib.HTMLParser):
    global queue
    def __init__(self, baseUrl, score):
        """
        :param score: The score of each page, i.e., the number of keywords in that page.
        :param base_url: The base URL to use for all relative URLs contained within a document.
        """
        htmllib.HTMLParser.__init__(self, formatter.NullFormatter())
        self.score = score
        self.baseUrl = baseUrl
        # Usage Note: If multiple <base> elements are specified, only the first href and first target value are used;
        # All others are ignored.
        self.parsedBaseElement = False

    def start_base(self, attrs):
        """
        Usage Note: If multiple <base> elements are specified, only the first href and first target value are used;
        All others are ignored.

        """
        if not self.parsedBaseElement:
            self.parsedBaseElement = True
            for attr in attrs:
                if attr[0] == "href":
                    href = attr[1]
                    if "://" in href:
                        # Absolute URIs.
                        self.baseUrl = href
                    else:
                        # Relative URIs.
                        self.baseUrl = urlparse.urljoin(self.baseUrl, href)


    def anchor_bgn(self, href, name, type):
        """This method is called at the start of an anchor region.

        href:This is attribute of anchors defining a hypertext source link. here we just need this
        """
        self.processUrl(href)

    def start_frame(self, attrs):
        #Override handler of <frame ...>...</frame> tags.
        for attr in attrs:
            if attr[0] == "src":
                self.processUrl(attr[1])

    def processUrl(self, href):
        """
        :param href: Current url to be processed.
        if this href is not in dict, so we just push it in;
        else this href is already in dict, we must compute new score for it,
        In this way, I just give average score for it.
        """
        href = urlparse.urljoin(self.baseUrl, href)
        href = CheckUrl.validifyUrl(href)
        if not href == -1:
        # in dict ,first find that url, then compute new score, and heapify it again.
            if not dict.get(href) == None:
                #heapq.heappush(queue, [self.score, href])
                if not queue.get(href) == None:
                    if self.score < queue[href]:
                        queue[href] = self.score
            else :
                # not in dict, just add it
                queue[href] = self.score
                dict[href] = self.score


pagesDirectory = "pages"
if not os.path.exists(pagesDirectory):
    os.mkdir(pagesDirectory)

bgnTime = datetime.datetime.now()
visited = open("visited.txt", "a")
numberOf404 = 0
numberCollectedUrl = 0
totalSize = 0

def doParse():
    global numberCollectedUrl
    global totalSize
    global numberOf404
    page = queue.popitem()
    url = page[0]
    score = page[1]
    #check the root's robot.txt, and check whether this can be crawled or not.
    if Crawlable.isCrawlable(url):
        try:
            # Open the URL
            pageToVisit = urllib2.urlopen(urllib2.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36",
                # Only html and xhtml are acceptable for the response.
                # If the server cannot send a response which is acceptable according to the combined Accept field value,
                # then the server SHOULD send a 406 (not acceptable) response.
                "Accept": "text/html,application/xhtml+xml"
            }), timeout=3)
        except urllib2.HTTPError as e:
            if e.code == 404:
                numberOf404 += 1
            elif e.code == 401:
                print url
                print "Authorization required"
            return
        except urllib2.URLError:
            return
        except:
            # Unexpected error.
            print "Unexpected error:", sys.exc_info()[0]
            return


        #numberCollectedUrl += 1
        #print "Number: " + str(numberCollectedUrl) + "  " + url + "   " + str(-score)

        # Ask for the MIME type of a file.
        mime = pageToVisit.info().gettype()
        # Only html and xhtml are acceptable for the response.
        if mime != "text/html" and mime != "application/xhtml+xml":
            return

        # Each page should be stored in a file in your directory.
        urlFileName = pagesDirectory + "/" + url.replace("/", "#")
        try:
            pageVisited = open(urlFileName, "w")
            pageContent = pageToVisit.read()
            if not CheckContent.checkContent(pageContent):
                #numberCollectedUrl -= 1
                return
            pageVisited.write(pageContent)
            pageVisited.close()
        except:
            # Unexpected error.
            #print "Unexpected error:", sys.exc_info()[0]
            return
        numberCollectedUrl += 1
        print "Number: " + str(numberCollectedUrl) + "  " + url + "   " + str(-score)
        # page size
        size = os.stat(urlFileName).st_size
        totalSize += size

        try:
            # try a list of all visited URLs, in the order they are visited, into a file.
            # In each line, in addition to the URL of the crawled page, you should also print the time when it was crawled,
            # its size, and the return code (e.g., 200, 404).
            visited.write(", ".join([
                "URL: " + url, "time: " + datetime.datetime.now().isoformat(),
                "size: " + str(size) + " bytes",
                "return code: " + str(pageToVisit.getcode()),
                "score: " + str(-score)
            ]) + "\n")
            visited.flush()
            os.fsync(visited.fileno())
        except:
            print url
            return
        pageToVisit.close()
        score = computeScore(pageContent)
        # Parse the file in order to find links from this to other pages.
        try:
            parser = Parser(url, -score)
            parser.feed(pageContent)
            parser.close()
        except htmllib.HTMLParseError as e:
            print "parse error: " + url
        except IOError as e:
            print "IOError" + url
        except urllib2.URLError as e:
            print "URLError" + url
        except:
            # Unexpected error.
            #print "Unexpected error:", sys.exc_info()[0]
            pass


def Producer():
    global total
    while len(queue) > 0 and numberCollectedUrl < total:
        try:
            # A new thread to parse a new page.
            thread = threading.Thread(target=doParse)
            #thread.setDaemon(True)
            thread.start()
            # Put thread into the queue. Block if necessary until a free slot is available.
            q.put(thread, True)
        except:
            print "parse_thread error: ", sys.exc_info()[0]
            return

# Number of pages parsed by threads.

numberConsumedUrl = 0
def Consumer():
    global numberConsumedUrl
    while numberConsumedUrl < numberCollectedUrl or numberCollectedUrl < total:
        thread = q.get(True)
        # Wait until the thread terminates. This blocks the calling thread until the thread whose join() method is
        thread.join(3)
        # Number of pages parsed by threads.
        numberConsumedUrl += 1
    print "join_parse_thread"


# Queue of parsing threads.
q = Queue.Queue(4)
# The main thread to parse pages.
parsing_thread = threading.Thread(target=Producer)
parsing_thread.setDaemon(True)
# The main thread to join parsing threads.
joining_thread = threading.Thread(target=Consumer)
joining_thread.setDaemon(True)
parsing_thread.start()
joining_thread.start()
# Join these two threads with our main thread.
parsing_thread.join(3)
joining_thread.join()

totalSplit = divmod(totalSize, 1000000)
visited.write(", ".join(
    ["number of files: " + str(numberCollectedUrl),
     "total size: " + "{0}.{1}".format(totalSplit[0], totalSplit[1]) + " MB",
     "total time: " + str((datetime.datetime.now() - bgnTime).total_seconds()) + " seconds",
     "number of 404 errors: " + str(numberOf404),
     "number of similar page: " + str(CheckContent.numberOfSimilar)
     ]) + "\n")
visited.flush()
os.fsync(visited.fileno())
visited.close()