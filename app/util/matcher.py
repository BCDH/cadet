
def matcher(text, term, label):
    #Find occurences of a string pattern in a larger string.
    index = 0
    matches = []
    while True:
        index = text.find(term, index + 1)
        matches.append((index, index + len(term), label))
        if index == -1:
            break

    return matches[:-1]

def update_sentences(text, sentences):
    #open text of sentences.py 
    #find start and end of `sentences = [ ]`
    # format sentences into valid list
    # replace new sentences in sentences.py 
    pass