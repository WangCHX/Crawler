__author__ = 'Wang'



def validifyUrl(url):
    """
    validify url, 1: delete last slash 2: delete last index.html etc.
                3: delete main 4:delete default
    """
    if "#" in url:
        url = url[0:url.rfind("#")]
    if url[len(url) - 1] == '/':
        url = url[0:len(url) - 1]
    if "javascript" in url or "mailto" in url:
        return -1
    strs = url.split('.')
    last = strs[len(strs) - 2].split('/')
    if last[len(last) - 1] == "index":
        url = url[0:url.rfind("index")]
    elif last[len(last) - 1] == "main":
        url =  url[0:url.rfind("main")]
    elif last[len(last) - 1] == "default":
        url = url[0:url.rfind("default")]
    else:
        pass

    if url[len(url) - 1] == '/':
        url = url[0:len(url) - 1]
    url = url.lower()
    return url


