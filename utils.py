from urllib.parse import urlparse

def printSubdomains():
    # K : subdomain v : Set{ unique pages }
    subs = {}
    with open("urls.txt", "r") as f:
        for line in f:
            line = line.strip().lower()
            try:
                parsed = urlparse(line)
            except TypeError:
                print("Type error parsing ", line)
                continue
            root = parsed.netloc
            root = root.replace("www.", "").replace("www-", "")
            if ("ics.uci.edu") not in root:
                continue
            if root not in subs.keys():
                subs[root] = set(line)
            else:
                subs[root].add(line)

    for item in sorted(subs.keys()):
        print(f"{item} : {len(subs[item])}")



if __name__ == "__main__":
    printSubdomains()