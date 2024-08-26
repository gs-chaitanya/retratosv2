#contains the tagging function and tag filter based on the config file

import subprocess
import re
import string
from subprocess import Popen, PIPE
import json
import os

class RetratosError(Exception):
    pass

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

def tag_nullflush(paragraph, config):
    escaped_paragraph = remove_punctuation(paragraph.replace("'", r"\'").replace('"',r'\"').replace('!','\!'))
    escaped_paragraph = escaped_paragraph.replace("\n", "\n\0")


def direct(path_to_corpus, path_to_config, source_lang, target_lang, apertium_dir):
    """
    corpus is piped directly to the tagger in the shell 

    args:
    path_to_corpus - absolute path of the corpus to be tagged
    path_to_config - absolute path of the json config file 
    source-lang - apertium abbreviation of the source language
    target-lang - apertium abbreviation of the target language
    apertium dir - absolute path of the apertium language directory
    """
    path_to_corpus = os.path.abspath(path_to_corpus)
    path_to_config = os.path.abspath(path_to_config)

    # we shall try to check if the config file provided specifies a tagger
    with open(path_to_config) as f:
        cfg = json.load(f)
        f.close()

    if cfg["tagger"] == "":
        tagger = f"apertium -d {apertium_dir} {source_lang}-{target_lang}-tagger"
    else:
        tagger = cfg["tagger"]

    command = f"cat {path_to_corpus} | {tagger}"

    print(command)
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output:\n{e.stderr}")
        raise RetratosError("Exiting the program")        

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

print(direct("example_data/eng-small.txt", "config.eng.json", "eng", "spa", "/home/chirag/apertium-eng-spa"))