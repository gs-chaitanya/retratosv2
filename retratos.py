import argparse
import os
from align import align_file
from generate_priors import genpriors
from filter import filter_priors
from bidix_patch_gen import gen_bidix_patch

parser = argparse.ArgumentParser(prog="retratosv2",
                                description="""Retratos can produce bidix patches from parallel corpora. It has three working modes 
                                                - generate_priors : create priors from a large corpus
                                                - filter : filter the best priors to be considered for bidix patching
                                                - suggest : generate bidix patches using filtered priors
                                                - align : align a smaller corpus using previously generated priors""",
                                epilog="Thanks for using retratos :)")

    #parser arguments
parser.add_argument('--mode', help='set working mode - choose out of generate_priors, suggest, filter', \
                    required=True, choices = ["align", "filter", "generate_priors", "suggest"])

parser.add_argument('--workdir',required=True, help='specify the working directory. all your working files are saved here and default files are automatically picked up from the workdir')

parser.add_argument('--tag-config', help='specify a config file that \
                    details which tags are to be included in the priors. It is a json file that needs to be kept in the workdir') #required=True - needed

    # align mode - align a small corpus using priors
parser.add_argument('--file', help='specify a custom input file in any mode in case you do not want to go with the default file in the workdir')

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

# suggest mode is used to create bidix patches from filtered priors - uses arguents : file, workdir, output
if(args['mode'] == 'suggest'):
    if (args['file'] == None):
        print("Priors file not specified so proceeding with the workspace defaults \n")
        if (os.path.exists(f"{args['workdir']}/filtered.priors")):
            gen_bidix_patch(f"{args['workdir']}/filtered.priors", args['workdir'])
        else:
            print("Bidix patch generation failed")
            print("You have not provided a path to filtered priors and the default file does not exist. \nFirst generate the filtered priors or provide the correct pathname.")
    else:
        gen_bidix_patch(args['file'], args['workdir'])
