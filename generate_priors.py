import subprocess
import os
from utils import tagger
import time
from tqdm import tqdm
import os.path
import sys
import shutil

class RetratosError(Exception):
    pass

def genpriors(workdir, left_corpus, right_corpus, apertium_lang_directory, left_lang, right_lang, output_filename="latest.priors"):
    os.chdir(workdir)

    # we generate a temp file directory for eflomal to store forward and backward links for generating priors
    if not os.path.exists("./temp_files"):
        os.mkdir("temp_files")
    temp_file_dir = "temp_files"

    # the commented code below deleted the temp file directory which prevented re running of retratos in the same directory - you need to delete it manually now
    # if os.path.isdir(temp_file_dir):
    #     shutil.rmtree(f'./{temp_file_dir}')

    # opening the files
    with open(left_corpus, 'r') as l, open(right_corpus, 'r') as r:
        left_text = l.readlines()
        right_text = r.readlines()
        l.close()
        r.close()

    # the following code was commented to prevent automatic deletion of temp files that the user should be able to inspect between subsequent runs
    
    # if os.path.isfile("latest.priors"):
    #     print("Priors file already generated. Do you want to overwrite ?")
    #     ans = str(input("y or n - "))
    #     if ans == "y" or ans == "yes":
    #         print("overwriting")
    #         os.remove("latest.priors")
    #     else:
    #         print("specify output filename and try again")
    #         sys.exit()
        

    #tagging the sentences
    print('started tagging left corpus')
    start_time = time.time()
    tagged_left_corpus = [tagger(line, apertium_lang_directory, f"{left_lang}-{right_lang}-tagger") for line in tqdm(left_text)]
    print("time taken : %s seconds" %(time.time() - start_time))
    print('tagged left corpus\n')
    
    print('started tagging right corpus')
    start_time = time.time()
    tagged_right_corpus = [tagger(line, apertium_lang_directory, f"{right_lang}-{left_lang}-tagger") for line in tqdm(right_text)]
    print("time taken : %s seconds" %(time.time() - start_time))
    print('tagged right corpus\n')

    tagged_fwd = [a + " ||| " + b for a,b in zip(tagged_left_corpus, tagged_right_corpus)]
    tagged_rev = [b + " ||| " + a for a,b in zip(tagged_left_corpus, tagged_right_corpus)]

    if not os.path.exists(temp_file_dir):
        os.makedirs(temp_file_dir)

    # generating tagged forward and reverse files for tagged forms
    with open(f'./{temp_file_dir}/tagged.fwd', 'w') as f:
        for line in tagged_fwd:
            f.write(f"{line}\n")
    f.close()

    with open(f'./{temp_file_dir}/tagged.rev', 'w') as g:
        for line in tagged_rev:
            g.write(f"{line}\n")
    g.close()

    print("generated tagged and paired sentences\n")
    #now generating priors
    subprocess.run([f"eflomal-align -i {workdir}/{temp_file_dir}/tagged.fwd --model 3 -f {workdir}/{temp_file_dir}/fwd.links -r {workdir}/{temp_file_dir}/rev.links"], shell=True)
    print("aligned \n")
    subprocess.run([f"eflomal-makepriors -i {workdir}/{temp_file_dir}/tagged.fwd -f {workdir}/{temp_file_dir}/fwd.links -r {workdir}/{temp_file_dir}/rev.links --priors {output_filename}"], shell=True)
    print(f"generated priors - saved as {output_filename} in workdir")


#example usage
# genpriors('/media/chirag/DATA/GSOC/Apertium/retratos-chaitanya', './data/eng-small.txt', './data/spa-small.txt', '/home/chirag/apertium-eng-spa', 'eng', 'spa')
