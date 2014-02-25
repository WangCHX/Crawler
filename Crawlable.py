__author__ = 'WangCHX'

import CheckUrl
import RobotExclusionRulesParser
import urllib2

robotHash = {}
def isCrawlable(url):
    # use naive method to get root for given url
    url = CheckUrl.validifyUrl(url)
    strs = url.split('/')
    if len(strs) > 2:
        url = strs[0] + "//" + strs[2]

    robotUrl = url + "/robots.txt"

    if robotHash.get(robotUrl) == None:
         rerp = RobotExclusionRulesParser.RobotExclusionRulesParser()
         try:
             rerp.fetch(robotUrl,3)
         except urllib2.URLError as e:
             return False
         if rerp.is_allowed("*",url):
             return True
         else:
             return False
    else:
        rerp = robotHash[robotUrl]
        if rerp.is_allowed("*", url):
            return True
        else:
            return False



