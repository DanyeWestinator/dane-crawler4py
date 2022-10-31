import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from PartA import tokenize, computeWordFrequencies

valid_urls = set()
freqs = {}
MAX_LEN = -1

#gets the stopwords
tokenChars = "[ .,'\"\[\]{}?!\n\t\r()-*:;#/\_\-\$%^&`~<>+=\“\’\”\‘]+"
stopwords = set()
for word in open("stopwords.txt", "r").readlines():
    # have to split stopwords based on the same token logic
    words = set(re.split(tokenChars, word))
    stopwords = words.union(stopwords)
stopwords.remove("")


def scraper(url, resp):
    links = extract_next_links(url, resp)
    global freqs
    global MAX_LEN
    print(f"Frequencies for {url}. Longest page had {MAX_LEN}")
    for word in sorted(freqs.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(word[0], word[1], end="\t")
    print("\n")
    # only valid links get passed,
    # makes more sense to only add valid links to the list in the first place
    return links


# cleans the link, gets it ready to be checked for validity
def clean_link(link, url):
    if link == None or link.strip == "":
        return ""
    # If link is to subdomain AND not just to the current page
    if link.startswith("/") and link != "/":
        # If the sublink isn't already in the url, and the sublink doesn't have www
        if link.replace("/", "") not in url.replace("/", "") and "www" not in link:
            print(f"Adding {link} to {url}")
            link = url + link

    # Regex to cut
    link = re.sub(r"(?=.+)#.+", "", link)
    link = link.strip()
    return link


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    links = []
    # quit for non 200 status urls
    if resp.status != 200:
        return links
    # ignore empty pages
    if resp.raw_response == None:
        return links
    #print(f"Checking {url} for valid links")
    html = resp.raw_response.content
    soup = BeautifulSoup(html, 'html.parser')
    # handle the links
    for a in soup.find_all('a'):
        link = a.get('href')
        link = clean_link(link, url)

        # ignore invalid links or empty links
        if is_valid(link) == False or link == "" or link == None:
            continue
        # Skip the link we are currently on
        if link.startswith("/") and link == "/":
            continue
        links.append(link)

    print(f"Found {len(links)} links on {url}")
    text = soup.get_text()
    tokenizePage(text)
    global MAX_LEN
    length = len(text.split(" "))
    if length > MAX_LEN:
        MAX_LEN = length
    # EMPTY RETURN, DON'T RECURSE!!
    #return list()
    return links


# Determines if a link is valid to be crawled
def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        global valid_urls
        # Links we've already checked are not valid
        if url in valid_urls:
            #print(f"Ignoring {url} because we already saw it")
            return False
        if "mailto" in url:
            return False
        if url.startswith("#"):
            return False
        extension_valid = not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
        if extension_valid:
            valid_urls.add(url)
        else:
            pass
            #print(f"Ignoring {url} because extension was invalid")
        return extension_valid

    except TypeError:
        print("TypeError for ", parsed)
        raise


# adds a word to the global frequencies dict
def addWord(word):
    global freqs
    if word in freqs.keys():
        freqs[word] += 1
    else:
        freqs[word] = 1


def tokenizePage(text):
    global tokenChars
    global stopwords
    # Gross to be reading over the entire webpage as one object in memory
    # However, it is already stored as a string inside the soup get_text() attribute
    for token in re.split(tokenChars, text):
        # Skip empty tokens
        token = token.lower()
        if token.strip() == "":
            continue
        # Skip stopwords
        if token in stopwords:
            continue
        addWord(token)

#Updates the url list and word freq list
def updateLogs():
    f = open("urls.txt", "w")
    pass