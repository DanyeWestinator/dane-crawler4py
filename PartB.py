import sys

import PartA

#IMPORTANT: PRINTING OUT THE WORDS IN COMMON IS A COMMAND LINE ARGUMENT
#To print, add {"-t", "true", "t", "y", "yes", "1"} after the last file arg


#Not counting PartA performance, runs in linear time with respect to the larger number of tokens
#set and dictionary operations ensure all "contains" checks run in constant time
def intersection(path1 : str, path2: str, p = False):
    errPath = path1
    try:
        tokenList = PartA.tokenize(path1)
        #ensures no word is counted twice
        tokenList = set(tokenList)
        first_dict = PartA.computeWordFrequencies(tokenList)
        errPath = path2
        tokenList = PartA.tokenize(path2)
        common_words = set()
    except UnicodeDecodeError:
        PartA.throw_not_text(errPath)
        return
    except FileNotFoundError:
        PartA.throw_not_text(path)
        return
    #iterates once over each token in file1
    for token in tokenList:
        #both checks are O(1) time, thanks to set and dict operations
        if (token in first_dict and token not in common_words):
            common_words.add(token)
    print(len(common_words))
    if p == False:
        return
    for token in common_words:
        print(token)
if __name__ == "__main__":
    path = sys.argv
    path = [i for i in path if "PartB" not in i]
    if (len(path) < 2):
        print("Please provide 2 paths to the text files")
    else:

        p1 = path[0]
        p2 = path[1]
        p = False
        if (len(path) >= 3):
            trues = {"-t", "true", "t", "y", "yes", "1"}
            p = path[2].lower() in trues
        intersection(p1, p2, p)