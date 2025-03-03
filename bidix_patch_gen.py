import os
import re
from collections import defaultdict

def extr_tags(word):
    """Extracts tags from a tagged word using regex."""
    return re.findall(r'<([^>]+)>', word)

def pad_word(word):
    """Wraps words with <s n=""> tags."""
    base_word = word.split('<')[0]
    tags_here = extr_tags(word)
    final_pad = [base_word]
    for tag in tags_here:
        final_pad.append(f"<s n=\"{tag}\">")
    return ''.join(final_pad)

def get_pos_tag(tags):
    """Extracts POS tag from the tag list (assuming first tag is POS)."""
    return tags[0] if tags else "unknown"  # Ensure a default POS tag

def gen_bidix_patch(file, workdir, output_filename="bidix.patches"):
    patches_by_pos = defaultdict(list)

    input_path = os.path.join(workdir, file)
    output_path = os.path.join(workdir, output_filename)

    with open(input_path, 'r', encoding="utf-8") as f:
        for line in f:
            words = line.strip().split()  # Splitting on any whitespace
            if len(words) < 2:
                continue  # Skip malformed lines
            
            l_word, r_word = words[0], words[1]
            l_tags, r_tags = extr_tags(l_word), extr_tags(r_word)
            pos_tag = get_pos_tag(l_tags)  # Use left word POS

            l_entry = "<l>" + pad_word(l_word) + "</l>"
            r_entry = "<r>" + pad_word(r_word) + "</r>"
            entry = "<e>\t<p>" + l_entry + r_entry + "</p></e>\n"

            patches_by_pos[pos_tag].append(entry)

    # Sort POS keys
    sorted_pos_keys = sorted(patches_by_pos.keys())

    # Write to output file
    with open(output_path, 'w', encoding="utf-8") as g:
        for pos in sorted_pos_keys:
            for entry in patches_by_pos[pos]:
                g.write(entry)

    print(f"Finished generating bidix patches in {output_path}, sorted by POS.")

# Test:
# gen_bidix_patch("filtered_p.priors", "./")
