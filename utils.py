#contains the tagging function and tag filter based on the config file

import subprocess
import re
import string
from subprocess import Popen, PIPE
import json
import os
import time

class RetratosError(Exception):
    pass

def does_binary_exist(name):
    """Check whether `name` is on PATH."""
    from distutils.spawn import find_executable
    return find_executable(name) is not None

def remove_punctuation(sentence):
    return sentence.translate(str.maketrans('', '', string.punctuation))

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

################## new tagging functions for genpriorsv2 ##########################################################################################################

def filter_tagged_token(token, path_to_config):
    path_to_config = os.path.abspath(path_to_config)

    with open(path_to_config, 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)

    allowed_tags = list(config["subpos_tags"].keys())
    for key, values in config["subpos_tags"].items():
        allowed_tags.extend(values)
    
    pattern = r'(\*?\w+)(<[^>]+>)+'
    if re.match(pattern, token) == None:
        return token
    
    base_word = token.split('<')[0]
    tags_in_token = re.findall(r'<([^>]+)>', token)
    final_tag_list = [ele for ele in tags_in_token if ele in allowed_tags]

    filtered_token = [base_word]
    for tag in final_tag_list:
        filtered_token.append(f"<{tag}>")

    return (('').join(filtered_token))


def tagfilterv2(path_to_corpus, path_to_config, workdir, lang):
    path_to_corpus = os.path.abspath(path_to_corpus)
    path_to_config = os.path.abspath(path_to_config)

    output_filename = f"{lang}.tagged"
    temp_file_dir = os.path.join(os.path.abspath(workdir), "temp_files")
    output_path = os.path.join(temp_file_dir, output_filename)

    try:     
        with open(path_to_corpus, 'r', encoding='utf-8') as infile, open(output_path, "a") as outfile:
            for line in infile:
                line.replace("+", "$ ^")
                tokens = re.findall(r'\^([^\$]+)\$', line)
                filtered_tokens = [filter_tagged_token(ele, path_to_config) for ele in tokens]
                outfile.write(" ".join(filtered_tokens) + "\n")
    except Exception as e:
        print(f"Error: {e}")
        print("there was an issue with filtering tags")


def direct(path_to_corpus, path_to_config, source_lang, target_lang, apertium_dir, workdir):
    """
    this generates tagged forms
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
        tagger = f"apertium -z -f none -d {apertium_dir} {source_lang}-{target_lang}-tagger"
    else:
        tagger = cfg["tagger"]

    command = f"sed 's/$/\\x00/' {path_to_corpus} | tr -d \"'\" | tr -d '\"' | sed 's/[\^\$\¿\¡\;\!\,]//g' | {tagger}"

    # first we tag the file - store it in lang.raw.tagged
    try:
        start_time = time.time()
        subprocess.run(command + " | tr -d '\\000' " + f"> {os.path.abspath(workdir)}/temp_files/{source_lang}.raw.tagged", shell=True, check=True, text=True)
        end_time = time.time()
        print(f"tagged {source_lang} successfully in {end_time - start_time} seconds")

    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output:\n{e.stderr}")
        raise RetratosError("Exiting the program - there was an error while attempting to tag")
    
    # now we filter the tagged files and store them in lang.tagged
    try:
        raw_tagged_filepath = f"{os.path.abspath(workdir)}/temp_files/{source_lang}.raw.tagged"
        start_time = time.time()
        tagfilterv2(raw_tagged_filepath, path_to_config, workdir, source_lang)
        end_time = time.time()
        print(f"filtered the raw {source_lang} tagged corpus successfully in {end_time - start_time} seconds")

    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output:\n{e.stderr}")
        raise RetratosError("Exiting the program - there was an error while attempting to filter the tags")


# direct("example_data/eng-small.txt", "config.eng.json", "eng", "spa", "/home/chirag/apertium-eng-spa", "./")