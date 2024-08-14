import re
import os
import itertools
from tqdm import tqdm

# filter by matching first tag - that is left

def filter_priors(workdir, priors_file="latest.priors", min_freq = 1, include_unknowns=False, keep_top=3, filename="filtered_p.priors"):
    os.chdir(workdir)
    lex_additions = {}
    with open(priors_file) as f:
        # lex_additions = dict((tuple(line.strip()[4:-2].split('\t'))[0:2], int(re.search(r'\d+$', line).group())) for line in f if line.startswith('LEX'))
        for line in f:
            if line.startswith('LEX'):
                # an entry in the priors file generally looks like this - LEX	merit<n>	mérito<n>	5
                # the number at the end of each entry represents frequency and is an import metric for consideration for patching into the bidix
                # we shall create a dictionary that stores all the entries in the priors witht the key as the lexical pair and the value as the frequency

                aligned_lex = tuple(line.strip()[4:-2].split('\t'))[0:2]
                # we extract only the alignment pairs and leave out the frequency at the end

                alignment_frequency = int(re.search(r'\d+$', line).group())
                # the above line looks for the frequency at the end of each entry in the priors file

                lex_additions[aligned_lex] = alignment_frequency

        f.close()
    
    print("sorting dictionary by frequency now \n")

    sorted_by_freq = dict(sorted(((k, v) for k, v in tqdm(lex_additions.items()) \
                                if int(v) >= int(min_freq) and (not(k[0][0] == "*") or include_unknowns)), key=lambda item: item[1], reverse=True))
    print("sorted \n")
    print("filtering priors now \n")
    with open(f'{workdir}/{filename}', 'w') as g:
        for line in tqdm(list(itertools.islice(([k[0], k[1], v] for k,v in sorted_by_freq.items()), int(keep_top)))):
            g.write(f"{line[0]} {line[1]} {line[2]} \n") #should I keep frequency in final output ?
        g.close()

    print(f"saved top {keep_top} entries to {filename}")

# example usage
# filter_priors("./", "latest.priors", 2, False, 10, "test.pr")

