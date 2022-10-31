import re
import builtins
import sys

# This function is linear with respect to the total number of characters in the file
        #(in terms of runtime)
    #in terms of space, it takes up O(n * f)
        #where n is the number of tokens, and f is the frequency of those tokens
        #since duplicates are stored in this step
def tokenize(TextFilePath: str):


    # create list of tokens, all lower case
    tokens = []
    f = open(TextFilePath, "r", encoding='utf-8')
    # opens the file, but doesn't load it all into RAM
    tokenChars = "[ .,'\"\[\]{}?!\n\t\r()-*:;#/\_\-\$%^&`~<>+=\“\’\”\‘]+"
    with f as file:
        # this outer loop is linear with respect to the number of lines in the file

        for line in file:
            # this loop is linear with respect to the length of each line
            for token in re.split(tokenChars, line):
                # Skip blank tokens
                if token.strip() == "":
                    continue
                token = token.lower()
                tokens.append(token)
    #This list can contain duplicates
    return list(tokens)



#this is linear with respect to the length of tokens
#all dict operations are constant time
def computeWordFrequencies(tokens  : list):
    wordCounts = {}
    for token in tokens:
        if token in wordCounts.keys():
            wordCounts[token] += 1
        else:
            wordCounts[token] = 1
    return wordCounts

#n log n with respect to length of wordCounts
#because of the sorting algorithm, once sorted it is linear
def print(wordCounts : dict):
    #If what was passed in wasn't a dictionary, call the default print function
    if type(wordCounts) != dict:
        builtins.print(wordCounts)
        return
    for word in sorted(wordCounts.items(), key=lambda x: x[1], reverse=True):
        builtins.print(word[0], word[1], sep="\t")

def throw_not_text(path):
    print(f"'{path}' was not a text file.\n\n{'-'*8}\nQUITTING\n{'-'*8}\n\n")


if __name__ == "__main__":
    path = sys.argv
    path = [i for i in path if "PartA" not in i]
    if (len(path) == 0):
        print("Please provide a path to the text file")
    else:

        path = path[0]
        #print(f"Input path was '{path}'")
        try:
            t = tokenize(path)

            d = computeWordFrequencies(t)
            print(d)
        except UnicodeDecodeError:
            throw_not_text(path)
        except FileNotFoundError:
            throw_not_text(path)
