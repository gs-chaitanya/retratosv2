import os
import subprocess

def align_file(workdir, file, priors, output ):
    os.chdir(workdir)
    subprocess.run([f'eflomal-align -i {file} --priors {priors} --model 3 -f {output}'], shell=True)  # omitting reverse links -r en-sv.small.rev