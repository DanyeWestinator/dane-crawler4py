import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from PartA import tokenize, computeWordFrequencies

valid_urls = set()
freqs = {}

#gets the stopwords
tokenChars = "[ .,'\"\[\]{}?!\n\t\r()-*:;#/\_\-\$%^&`~<>+=\“\’\”\‘]+"
stopwords = set()
for word in open("stopwords.txt", "r").readlines():
    # have to split stopwords based on the same token logic
    words = set(re.split(tokenChars, word))
    stopwords = words.union(stopwords)
stopwords.remove("")


def scraper(url, resp):
    print(stopwords)
    return []
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


# cleans the link, gets it ready to be checked for validity
def clean_link(link, url):
    # If link is to subdomain
    if link.startswith("/") and link != "/" and "www" not in link:
        link = url + link
    # Regex to cut
    link = re.sub(r"(?(?=.+_))#.+", "", link)
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
    print(f"Checking {url} for valid links")
    html = resp.raw_response.content
    soup = BeautifulSoup(html, 'html.parser')
    out = f"\nTitle: {soup.title.string}\n"
    # handle the links
    for a in soup.find_all('a'):
        link = a.get('href')
        link = clean_link(link, url)

        # ignore invalid links or empty links
        if is_valid(link) == False or link == "":
            continue
        # Skip the link we are currently on
        if link.startswith("/") and link == "/":
            continue
        links.append(link)

    for link in links[:10]:
        out += f"\t{link}\n"
    text = soup.get_text()
    tokens = tokenize()
    print(out)
    # EMPTY RETURN, DON'T RECURSE!!
    return list()
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
            print(f"Ignoring {url} because we already saw it")
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
            print(f"Ignoring {url} because extension was invalid")
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
    # Gross to be reading over the entire webpage as one object in memory
    # However, it is already stored as a string inside the soup get_text() attribute

    for token in re.split(tokenChars, text):
        if token.strip() == "":
            continue
        token = token.lower()
        #tokens.append(token)