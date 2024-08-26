import argparse
import os
from generate_priors import genpriors
from generate_priorsv2 import genpriorsv2
from filter import filter_priors
from bidix_patch_gen import gen_bidix_patch
from utils import does_binary_exist
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict

parser = argparse.ArgumentParser(prog="retratosv2",
                                description="""Retratos can produce bidix patches from parallel corpora. It has three working modes 
                                                - generate_priors : create priors from a large corpus
                                                - filter : filter the best priors to be considered for bidix patching
                                                - suggest : generate bidix patches using filtered priors""",
                                epilog="Thanks for using retratos :)")

    #parser arguments
parser.add_argument('--mode', help='set working mode - choose out of generate_priors, suggest, filter', \
                    required=True, choices = ["filter", "generate_priors", "suggest"])

parser.add_argument('--workdir',required=True, help='specify the working directory. all your working files are saved here and default files are automatically picked up from the workdir')

parser.add_argument('--left_config', help='specify a config file that \
                    details which tags are to be included in the priors. It is a json file that needs to be kept in the workdir')
parser.add_argument('--right_config', help='specify a config file that \
                    details which tags are to be included in the priors. It is a json file that needs to be kept in the workdir') 

    # filter mode - filters the priors file using given constraints for dictionary induction
parser.add_argument('--min_freq', help='min frequency below which the priors are excluded from the filtered priors')
parser.add_argument('--priors', help='specify priors file - if not given default priors file in the workspace is used')
parser.add_argument('--keep_top', help='after setting a minimum frequency, you can choose to keep only the top n priors sorted by frequency, where n is specified by this argument')
parser.add_argument('--include_unknowns', help='Keep \'Yes\' to include unknown words in the filtered priors, default is \'No\'')

    # generate-priors mode - will align two text files in the fast align format - s1 ||| s2
parser.add_argument('--left', help='specify source language corpus')
parser.add_argument('--right', help='specify target language corpus')
parser.add_argument("--lang_dir", help='path to the apertium language pair repository on your system')
parser.add_argument("--left_lang", help='specify the source(left) language')
parser.add_argument("--right_lang", help='specify the target(right) language')
parser.add_argument("--output", help='specify an output filename instead of the default in any of the modes')

args = vars(parser.parse_args())
 
class RetratosError(Exception):
    pass

# before we do anything else, we should first check if the required dependencies - elfomal and tqdm are installed
# we check for eflomal below
if not does_binary_exist("eflomal"):
    print("eflomal is required to run this tool, follow the readme for install instrunctions")
    raise RetratosError

# now we check for module dependencies - (do we really need this ?)
with open("requirements.txt", "r") as reqs:
    dependencies = reqs.read().splitlines()
    reqs.close()
pkg_resources.require(dependencies)

workdir = os.path.abspath(args['workdir'])

if not os.path.exists(workdir):
    print("specified workdir path does not exist, create the workdir, place the corpus in it and rerun the tool with the correct arguments for corpus paths")
    raise RetratosError("Workdir error")

os.chdir(workdir)

if(args['mode'] == 'generate_priors'):
    required_args = ['left', 'right', 'lang_dir', 'left_lang', 'right_lang']
    missing = [arg for arg in required_args if args[arg] is None]
    if missing:
        parser.error(f"The following arguments are required when mode is 'generate_priors': {', '.join(missing)}")

    left_lang = args['left_lang']
    right_lang = args['right_lang']

    left_corpus_path = os.path.abspath(args['left'])
    right_corpus_path = os.path.abspath(args['right'])

    left_config = os.path.abspath(args['left_config'])
    right_config = os.path.abspath(args['right_config'])

    lang_dir = os.path.abspath(args['lang_dir'])
    # if (args['left_lang'] == None or args['right_lang'] == None):
        
    #     if args['lang_dir'][-1] == '/':
    #         args['lang_dir'] = args['lang_dir'][:-1]

    #     left_lang = args['lang_dir'].split('/')[-1].split('-')
    #     righ_lang = args['lang_dir'].split('/')[-1].split('-')
    # if args['output'] == None:
    #     genpriors(workdir, args['left'], args['right'], args['lang_dir'], left_lang, right_lang)
    # else:
    #     genpriors(workdir, args['left'], args['right'], args['lang_dir'], left_lang, right_lang, args['output'])

    if args['output'] == None:
        genpriorsv2(workdir, left_corpus_path, right_corpus_path, lang_dir, left_lang, right_lang, left_config, right_config)
    else:
        genpriorsv2(workdir, left_corpus_path, right_corpus_path, lang_dir, left_lang, right_lang, left_config, right_config, args['output'])
    
    #sample usage in script
    # genpriors('/media/chirag/DATA/GSOC/Apertium/retratos-chaitanya', './data/eng-small.txt', './data/spa-small.txt', '/home/chirag/apertium-eng-spa', 'eng', 'spa')


if(args['mode'] == 'filter'):
    required_args = ['include_unknowns', 'min_freq', 'keep_top']
    missing = [arg for arg in required_args if args[arg] is None]
    if missing:
        parser.error(f"The following arguments are required when mode is 'generate_priors': {', '.join(missing)}")
    os.chdir(workdir)
                                    #improvement - add option for priors - going with default workdir.priors right now
    priors_file = 'latest.priors'
    if args['priors'] != None:
        priors_file = args['priors']
    filter_priors(workdir, priors_file, args['min_freq'], args['include_unknowns'], args['keep_top'], args['output'])


# suggest mode is used to create bidix patches from filtered priors - uses arguents : file, workdir, output
if(args['mode'] == 'suggest'):
    if (args['file'] == None):
        print("Priors file not specified so proceeding with the workspace default file - filtered.priors \n")
        if (os.path.exists(f"{workdir}/filtered.priors")):
            gen_bidix_patch(f"{workdir}/filtered.priors", workdir)
        else:
            print("Bidix patch generation failed")
            print("You have not provided a path to filtered priors and the default file does not exist. \nFirst generate the filtered priors or provide the correct pathname.")
    else:
        gen_bidix_patch(args['file'], workdir)
