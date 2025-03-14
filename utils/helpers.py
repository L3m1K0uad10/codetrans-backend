import re 


pattern = r"[ ,.():\"\[\]]+" # delimiters used to split our string

def find_all(string):
    """  
    find all the words in a string and return a dictionary of the words and their positions
    along with the number of their occurences
    """
    word_pos = {}

    string_list = re.split(pattern, string) # splitting by whitespace

    for word in string_list: # loop through string: word after word
        positions = set() # iniatilizing a specific word occurence position tracking
        index = string.find(word) 

        """ if index != -1: """
        positions.add(index)
        word_length = len(word)
        i = index + word_length # stepping to the new starting point of the substring

        prev_index = index + word_length # getting the prev index ready for adding to the next index
            
        for word_ in re.split(pattern, string[i:]): # traversing the substring
            if word_ == word:
                next_index = string[i:].find(word_)
                positions.add(next_index + prev_index) # we add previous index because the substring is going to start at a new index 0 that it is going to consider
                
                i = next_index + prev_index + word_length  

                prev_index = next_index + prev_index + word_length 

        word_pos[word] = positions

    return word_pos


def string_token_length(string):
    """  
    gets the number of tokens in a string
    e.g "hello world" -> 2
    """
    string_list = string.split()
    
    return len(string_list)


def construct_tokenized_string(string):
    """  
    reconstructs the untokenized string to the tokenized string
    e.g "hello_world" -> "hello world"
    """
    string_list = string.split("_")

    return " ".join(string_list)