# bioblend-test

This repo demonstrates how to access the Naturalis galaxy portal from python using bioblend. There are the following
files:

- [client.py](client.py) - a script that runs a constrained ML search using RAxML
- [raxml-ready.fa](raxml-ready.fa) - aligned COI-5P sequences in FASTA format
- [raxml-ready.tre](raxml-ready.tre) - input constraint tree that partially covers the alignment taxa
- [output_tree.nxh](output_tree.nhx) - the ML tree that results from the analysis
- [inputs.json](inputs.json) - the inputs for the RAxML tool as JSON, obtained from the GalaxyInstance
- [outputs.json](outputs.json) - the outputs produced by the tool as JSON, obtained from the GalaxyInstance
- [requirements.txt](requirements.txt) - the required packages, i.e. `bioblend` and `requests`
