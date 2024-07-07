import os
import subprocess

def align_file(workdir, file = "alignment_file.txt", priors="latest.priors", output="alignments.fwd" ):
    os.chdir(workdir)
    subprocess.run([f'eflomal-align -i {file} --priors {priors} --model 3 -f {output}'], shell=True)  # omitting reverse links -r en-sv.small.rev