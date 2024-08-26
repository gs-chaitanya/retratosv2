import re
import json
#contains the tagging function and tag filter based on the config file

import subprocess
import re
import string
from subprocess import Popen, PIPE

config_file = None

def remove_punctuation(sentence):
    return sentence.translate(str.maketrans('', '', string.punctuation))

def filter_tags(word, config_file):
    with open('config.json', 'r') as f:
        config = json.load(f)
    # pattern = r'(\*?\w+)(<[^>]+>)+'
    # match = re.match(pattern, word)

    # extract the base word from the tagged form
    base_word = word.split('<')[0]
    # here we are matching a regex expression to extract all the tags from a tagged form and storing it in a list called tags
    tags = re.findall(r'<([^>]+)>', word)
    # the buffer list stores the base word and the first tag which usually contains the POS
    buffer = [base_word, f"<{tags[0]}>"]

    # now, we look in the config file for additional tags to be included. this depends on the POS. if further tags are supplied in the config file
    # to be included with the main POS, for example gender with noun, we specify this in the config file and then add them here to the buffer 
    try:
        confs = config[tags[0]]
        for tag in tags[1:]:
            if tag in confs:
                buffer.append(f"<{tag}>")
    except:
        pass
    # return the final buffer with any addition tags specified in the config
    return (('').join(buffer))

def raw_tagger(sentence, apertium_dir, tag_mode):
    escaped_sentence = remove_punctuation(sentence.replace("'", r"\'").replace('"',r'\"').replace('!',r"\!"))
        # command = f'echo "{escaped_sentence}" | apertium -d {apertium_dir} {tag_mode}'
        # process = Popen(command, stdout=PIPE, stderr=PIPE)
        # raw_tagged_output, error = process.communicate()
    raw_tagged_output = subprocess.run([f'echo "{escaped_sentence}" | apertium -d {apertium_dir} {tag_mode}'], shell=True, capture_output=True, text=True).stdout
    tagged_tokens = re.findall(r'\^([^$]+)\$', raw_tagged_output)
    tagged_tokens = [filter_tags(x, config_file) for x in tagged_tokens if x != '.<sent>']
    return str((' ').join(tagged_tokens))

# just for testing
# raw_tagged_sentence = raw_tagger("Everybody wants sunshine nobody wants rain", "/home/chirag/apertium-eng-spa", "eng-spa-tagger")
# print(raw_tagged_sentence)