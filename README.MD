# ReTraTos v2 - GSoC 2024

# Usage
+ retratos.y is the main script
+ a mode has to be specfied out of generate_priors, align, filter using the argument --mode
+ specify working directory using --workdir

## generating priors
<b> generate priors </b>

- use --mode generate_priors

example usage <br>
```python retratos.py --mode generate_priors --workdir "./" --left "./data/eng-small.txt" --right "./data/spa-small.txt" --lang_dir "/home/user/apertium-eng-spa" --output "latest.priors" --left_lang eng --right_lang spa```

## filtering
<b> filter the generated priors </b>

example usage <br>
```python retratos.py --mode filter --workdir "./" --include_unknowns True --min_freq 1 --keep_top 100 --output filtered.priors```

## align
refer --help

### workspace defaults
- priors file saved as latest.priors
- file to be aligned is alignment_file.txt by default

### config file
- config is saved to config.json
- can be directly edited or use config_creatory.py
- currently only keeping the first tag unless the config specifies which other tags to include