import subprocess
import os
import time
from tqdm import tqdm
import os.path
import sys

from utils import direct

class RetratosError(Exception):
    pass

def make_priors(workdir, output_filename):
    #now generating priors
    temp_file_dir = os.path.abspath('temp_files')
    try:
        subprocess.run([f"eflomal-align -i {temp_file_dir}/tagged.fwd --model 3 -f {temp_file_dir}/fwd.links -r {temp_file_dir}/rev.links"], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output:\n{e.stderr}")
        raise RetratosError("Exiting the program - there was an error while attempting to generate priors - failed to generate fwd and rev links")

    try:
        subprocess.run([f"eflomal-makepriors -i {temp_file_dir}/tagged.fwd -f {temp_file_dir}/fwd.links -r {temp_file_dir}/rev.links --priors {output_filename}"], shell=True)
        # print(f"successfully saved priors as {output_filename} in {temp_file_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output:\n{e.stderr}")
        raise RetratosError("Exiting the program - there was an error while attempting to generate priors - failed to generate priors using eflomal-makepriors")    


def genpriorsv2(workdir, left_corpus, right_corpus, apertium_lang_directory, left_lang, right_lang, left_config, right_config, output_filename="latest.priors"):
    os.chdir(workdir)

    # we generate a temp file directory for eflomal to store forward and backward links for generating priors
    if not os.path.exists("temp_files"):
        os.mkdir("temp_files")
    temp_file_dir = os.path.abspath("temp_files")


    if os.path.isfile(os.path.abspath("temp_files/tagged.fwd")) or os.path.isfile(os.path.abspath("temp_files/tagged.rev")):
        print("Tagged files already found in the temp_files directory.")
        print("Do you want to proceed with the previously tagged files ? - (y/n)", end="")
        proceed = input()
        proceed = proceed.lower()
        if proceed == "y":
            make_priors(workdir, output_filename)
        elif proceed == "n":
            print("Exiting without any further action")
            sys.exit()
        else:
            print("answer in y/n")

    else:
        #tagging the left corpus
        direct(left_corpus, left_config, left_lang, right_lang, apertium_lang_directory, workdir)
        #tagging the right corpus
        direct(right_corpus, right_config, right_lang, left_lang, apertium_lang_directory, workdir)

        # now we will merge the tagged files in the <tagged_left_sentece> ||| <tagged_right_sentence>
        command_left = f"paste {temp_file_dir}/{left_lang}.tagged {temp_file_dir}/{right_lang}.tagged | sed 's/[\t]/ ||| /g' > {temp_file_dir}/tagged.fwd"
        command_right = f"paste {temp_file_dir}/{right_lang}.tagged {temp_file_dir}/{left_lang}.tagged | sed 's/[\t]/ ||| /g' > {temp_file_dir}/tagged.rev"

        try:
            subprocess.run(command_left, shell=True, check=True, text=True)
            print(f"generated tagged.fwd in temp_files directory")

        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(f"Error output:\n{e.stderr}")
            raise RetratosError("There was an error when trying to save tagged.fwd")      

        try:
            subprocess.run(command_right, shell=True, check=True, text=True)
            print(f"generated tagged.rev in temp_files directory")

        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(f"Error output:\n{e.stderr}")
            raise RetratosError("There was an error when trying to save tagged.rev")      
        
        make_priors(workdir, output_filename)

        print("done with priors generation - genpriorsv2")
