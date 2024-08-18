import os
import re

#the bidix patch gen build patches from filtered priors
#the frequency from filtered priors is removed and that file is fed to this script


# consider an entry in the filtered priors without the frequency
# it should look something like this 
# and<cnjcoo> y<cnjcoo> 
# we need to extract each tag and place it within a <s n=""> tag
# we shall employ regex matching for extracting the text withing tags like before
# regex matching comes with its own set of problems, but we shall continue with regex until something better comes up - retratosv3 :) 

# defining a custom function to extract tags from text - returns a list of tags
def extr_tags(word):
    # matching a regex expression to extract all the tags from a tagged form and storing it in a list called tags
    tags = re.findall(r'<([^>]+)>', word)
    return tags

def pad_word(word):
    base_word = word.split('<')[0]
    tags_here = extr_tags(word)
    final_pad = [base_word]
    for tag in tags_here:
        final_pad.append(f"<s n=\"{tag}\">")
    return ''.join(final_pad)


# creating a function to make it importable

def gen_bidix_patch(file, workdir, output_filename="bidix.patches"):
    os.chdir(workdir)
    patches = []
    with open(f'./{file}', 'r') as f:
        for line in f:
            print()
            l = "<l>" + pad_word(line.split(' ')[0]) + "</l>"
            r = "<r>" + pad_word(line.split(' ')[1]) + "</r>"
            entry = "<e>" + "\t" + "<p>" + l + r + "</p>" + "</e>" + "\n"
            patches.append(entry)
        f.close()

    with open(f"./{output_filename}", 'w') as g:
        for entry in patches:
            g.write(entry)
        g.close()

    print("finished generating bidix patches")

# test
# gen_bidix_patch("filtered_p.priors", "./")
        

