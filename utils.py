#contains the tagging function and tag filter based on the config file

import subprocess
import re
import string
from subprocess import Popen, PIPE
import json

def does_binary_exist(name):
    """Check whether `name` is on PATH."""
    from distutils.spawn import find_executable
    return find_executable(name) is not None

def remove_punctuation(sentence):
    return sentence.translate(str.maketrans('', '', string.punctuation))

# def tag_filter(word):
#     match = re.search(r'<([^>]+)>', word)
#     if match:
#         base_word = word.split('<')[0]
#         first_tag = match.group(1)
#         return f"{base_word}<{first_tag}>"
#     return word

def filter_tags(word, config_file = "config.json"):
    with open('config.json', 'r') as f:
        config = json.load(f)
    pattern = r'(\*?\w+)(<[^>]+>)+'

    #check if word is unknown
    if re.match(pattern, word) == None:
        return word
    
    base_word = word.split('<')[0]
    # tags = re.findall(r'<([^>]+)>', word)
    tags = re.findall(r'<([^>]+)>', word)
    
    if not tags:
        return word
    
    buffer = [base_word, f"<{tags[0]}>"]
    try:
        confs = config[tags[0]]
        for tag in tags[1:]:
            if tag in confs:
                buffer.append(f"<{tag}>")
    except:
        pass

    return (('').join(buffer))

def tagger(sentence, apertium_dir, tag_mode, tag_config_file="config.json"):
    escaped_sentence = remove_punctuation(sentence.replace("'", r"\'").replace('"',r'\"').replace('!','\!'))
        # command = f'echo "{escaped_sentence}" | apertium -d {apertium_dir} {tag_mode}'
        # process = Popen(command, stdout=PIPE, stderr=PIPE)
        # raw_tagged_output, error = process.communicate()
    raw_tagged_output = subprocess.run([f'echo "{escaped_sentence}" | apertium -d {apertium_dir} {tag_mode}'], shell=True, capture_output=True, text=True).stdout
    tagged_tokens = re.findall(r'\^([^$]+)\$', raw_tagged_output)
    tagged_tokens = [filter_tags(x) for x in tagged_tokens if x != '.<sent>']
    return str((' ').join(tagged_tokens))

#print(tagger("hey there Julie", "/home/chirag/apertium-eng-spa", "eng-spa-tagger"))
# print(filter_tags("*hey<tag>"))

# Test the function
# test_words = [
#     "word",
#     "word<tag1>",
#     "word<tag1><tag2>",
#     "*word<tag1><tag2>",
#     "unknown<tag>"
# ]

# for word in test_words:
#     print("\nTesting:", word)
#     result = filter_tags(word)
#     print("Result:", result)