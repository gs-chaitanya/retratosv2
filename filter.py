import re
import os
import itertools
from tqdm import tqdm

# filter by matching first tag - that is left

def filter_priors(workdir, priors_file="latest.priors", min_freq = 1, include_unknowns=False, keep_top=3, filename="filtered_p.priors"):
    os.chdir(workdir)
    with open(priors_file) as f:
        lex_additions = dict((tuple(line.strip()[4:-2].split('\t'))[0:2], int(re.search(r'\d+$', line).group())) for line in f if line.startswith('LEX'))
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
filter_priors("./", "latest.priors", 2, False, 10)

