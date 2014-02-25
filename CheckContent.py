__author__ = 'WangCHX'

import SimHash
# contain parsed page hash computed from SimHash
hashContent = []
numberOfSimilar = 0
def checkContent(content):
    global numberOfSimilar
    global hashContent
    # compute the hash of this the content of this url
    Nowhash = SimHash.simhash(content.split())
    # compare the hamming distance of this page' hash to other page's, the smaller value, the higher similarity they have
    for value in hashContent:
        if Nowhash.hamming_distance(value) < 1:
            print "Similar Content"
            numberOfSimilar += 1
            return False
    hashContent.append(Nowhash)
    return True


