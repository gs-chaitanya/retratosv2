import argparse
import os
from align import align_file
from generate_priors import genpriors
from filter import filter_priors
from bidix_patch_gen import gen_bidix_patch

parser = argparse.ArgumentParser()

    #parser arguments
parser.add_argument('--mode', help='set working mode - choose out of align or filter', \
                    required=True, choices = ["align", "filter", "generate_priors", "suggest"])

parser.add_argument('--workdir',required=True, help='specify the working directory')

parser.add_argument('--tag-config', help='specify a config file that \
                    details which tags are to be included in the priors') #required=True - needed

    # align mode - align a small corpus using priors
parser.add_argument('--file', help='corpus in fast align format')

    # filter mode - filters the priors file using given constraints for dictionary induction
parser.add_argument('--min_freq', help='min frequency to include')
parser.add_argument('--priors', help='specify priors file - if not given default priors file in the workspace is used')
parser.add_argument('--keep_top', help='specify priors file - if not given default priors file in the workspace is used')
parser.add_argument('--include_unknowns', help='specify priors file - if not given default priors file in the workspace is used')

    # generate-priors mode - will align two text files in the fast align format - s1 ||| s2
parser.add_argument('--left', help='source language corpus')
parser.add_argument('--right', help='target language corpus')
parser.add_argument("--lang_dir")
parser.add_argument("--left_lang")
parser.add_argument("--right_lang")
parser.add_argument("--output")

args = vars(parser.parse_args())

class RetratosError(Exception):
    pass

workdir = ''
if args['workdir'] == None:
    workdir = os.getcwd()
else:
    workdir = args['workdir']

if(args['mode'] == 'generate_priors'):
    required_args = ['left', 'right', 'lang_dir']
    missing = [arg for arg in required_args if args[arg] is None]
    if missing:
        parser.error(f"The following arguments are required when mode is 'generate_priors': {', '.join(missing)}")

    left_lang = args['left_lang']
    right_lang = args['right_lang']
    if (args['left_lang'] == None or args['right_lang'] == None):
        
        if args['lang_dir'][-1] == '/':
            args['lang_dir'] = args['lang_dir'][:-1]

        left_lang = args['lang_dir'].split('/')[-1].split('-')
        righ_lang = args['lang_dir'].split('/')[-1].split('-')
    if args['output'] == None:
        genpriors(workdir, args['left'], args['right'], args['lang_dir'], left_lang, right_lang)
    else:
        genpriors(workdir, args['left'], args['right'], args['lang_dir'], left_lang, right_lang, args['output'])
    
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


if(args['mode'] == 'align'):
    if (args['corpus'] == None):
        raise RetratosError("Corpus not provided")
    align_file(workdir, args['file'], args['priors'], args['output'])

# suggest mode is used to create bidix patches from filtered priors - uses arguents : file and workdir 
if(args['mode'] == 'suggest'):
    if (args['file'] == None):
        raise RetratosError("FIltered priors not provided")
    gen_bidix_patch(args['file'], args['workdir'])
    
