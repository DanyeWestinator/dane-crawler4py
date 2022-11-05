import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

valid_urls = set()
freqs = {}
MAX_LEN = -1
longest = []
scraped = 0
total = 0
# gets the stopwords
tokenChars = "[ .,'\"\[\]{}?|!\n\t\r()-*:;#/\_\-\$%^&`~<>+=\“\’\”\‘]+"
stopwords = set()
for word in open("stopwords.txt", "r").readlines():
    # have to split stopwords based on the same token logic
    words = set(re.split(tokenChars, word))
    stopwords = words.union(stopwords)
stopwords.remove("")

# url : (600 codes, total calls)
# if there are ever 50+ calls to a website, and 75% + of them are 600 code
# blacklist that site
err_urls = {}

f = open("blacklist.txt", "r")
# The sites that have thrown too many 600 errors
blacklisted = [i for i in f.read().split("\n") if i.strip() != ""]
blacklisted = set(blacklisted)
f.close()

def scraper(url, resp):
    links = extract_next_links(url, resp)
    global freqs
    global MAX_LEN
    global scraped
    global total
    total += 1
    print(f"Frequencies for {url}. Longest page had {MAX_LEN}. "
          f"Now scraped {scraped} pages successfully, Tried with {total} total pages")
    for word in sorted(freqs.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(word[0], word[1], end="\t")
    print("\n")
    # only valid links get passed,
    # makes more sense to only add valid links to the list in the first place
    return links


# cleans the link, gets it ready to be checked for validity
def clean_link(link, url):
    if link == None or link.strip() == "":
        return ""
    parsed = None
    try:
        parsed = urlparse(url)
    except TypeError:
        pass
        #print("Ignoring failed parse of ", url)

    # if link points to an external site
    invalid = ["http", "www", ".edu", ".com"]
    notlink = True
    for i in invalid:
        if i in link:
            notlink = False

    # If link is to subdomain AND not just to the current page
    if link.startswith("/") and link != "/" and notlink:
        link = parsed.netloc + link
    # if the first character is a letter
    elif link[0].isalpha() and notlink:
        link = parsed.netloc + "/" + link
    link = link[:2].replace("/", "") + link[2:]
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
    handle_status(url, resp.status)
    # quit for non 200 status urls
    if resp.status != 200:
        # Handle 600 code links, and blacklist any site that throws too many

        return links
    # ignore empty pages
    if resp.raw_response == None:
        return links
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

    # helper function to handle the logic of counting the
    # longest web pages
    count_words(length, url)


    # only add when we know it was scraped successfully
    global scraped
    global valid_urls
    if url not in valid_urls:
        valid_urls.add(url)
    scraped += 1
    #then update the logs
    updateLogs()
    return links


# Handles
def handle_status(url : str, status : int):
    parsed = None
    try:
        parsed = urlparse(url)
    # Do nothing if we can't parse the url
    except TypeError:
        return
    root = parsed.netloc
    #never block these 4 roots, or any sub domain
    whitelist = {"ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"}
    for white in whitelist:
        if white in root:
            return
    global err_urls
    if root not in err_urls.keys():
        # Init to 0 600 codes thrown, 0 pages visited
        err_urls[root] = [0, 0]
    # always increase visited by 1
    err_urls[root][1] += 1
    # if the status starts with 600
    if 600 <= status <= 699:
        # increase 600 count by 1
        err_urls[root][0] += 1
        ratio = float(err_urls[root][0]) / float(err_urls[root][1])
        global blacklisted
        
        # if there were enough urls scraped from that root
        # Min number of times to check a domain
        THRESHOLD = 5
        # Min % of items that can return a 600 code
        RATIO = .75
        thresh_met = THRESHOLD < err_urls[root][1]
        
        # if the ratio goes over the threshold, AND there were more than 50
        # add to blacklist
        if ratio >= RATIO and thresh_met and root not in blacklisted:
            print(f"\n\n\n{'-' * 7}\nADDED {root} TO BLACKLIST with ratio of {ratio} and {err_urls[root][1]} total\n{'-' * 7}\n\n")
            #Add to the blacklist, and update the source
            blacklisted.add(root)
            f = open("blacklist.txt", "w")
            for item in blacklisted:
                f.write(item + "\n")
            f.close()



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
            return False
        # Ignore email links
        if "mailto" in url:
            return False
        # Ignore links to sections on the page
        if url.startswith("#"):
            return False
        # Ignore blacklisted sites
        if parsed.netloc in blacklisted:
            return False
        # We ignore pdfs entirely
        if "pdf" in url.lower():
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


        return extension_valid

    except TypeError:
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
        token = token.lower().strip()
        if token == "" or len(token) == 1:
            continue
        # Skip stopwords
        if token in stopwords:
            continue
        addWord(token)


# Updates the url list and word freq list
def updateLogs():
    global freqs
    global valid_urls
    global MAX_LEN
    global scraped
    global total
    stats = f"Max length: {MAX_LEN}\n"
    stats += f"Scraped {scraped} pages, visited a total of {total} pages\n"
    i = 1
    for word in sorted(freqs.items(), key=lambda x: x[1], reverse=True)[:150]:
        stats += f"{i}. {word[0]}: {word[1]}\n"
        i += 1
    f = open("word_freqs.txt", "w")
    f.write(stats)
    f.close()
    f = open("urls.txt", "w")
    s = ""
    for url in sorted(valid_urls):
        s += url + "\n"
    f.write(s)
    f.close()

def count_words(length, url):
    #global MAX_LEN
    #if length > MAX_LEN:
    #    MAX_LEN = length
    global longest
    #TODO Fix hardcoded max # to save, currently top 100 longest web pages
    cap = 200
    # if below threshold, just add to the list of longest
    # Can't go over
    if len(longest) < cap:
        longest.append((length, url))
    else:
        # longest will have at least one val, since >= cap
        # Need to get length
        old_max = longest[-1][0]

        # if the old max is bigger, no need to make any changes
        # just return
        if old_max >= length:
            return
        # Length is at least bigger than the smallest of the top 100
        longest[-1] = (length, url)

    # List has been changed, need to sort Large -> Small
    longest = sorted(longest, reverse=True)

    # Once val is either added or not, update .txt file
    f = open("longest_texts.txt", "w")
    txt = ""
    i = 1
    for link in longest:
        if i < 10:
            txt += "0"
        txt += f"{i}: {link[0]} words - {link[1]}\n"
        i += 1
    f.write(txt)
    f.close()
    global MAX_LEN
    MAX_LEN = longest[0][0]
