from bioblend import galaxy
from bioblend.galaxy.tools.inputs import inputs, dataset
import os
import requests

# Endpoints for the Naturalis production instance. Domain can also be an IP address.
domain = 'galaxy.naturalis.nl'
dlbase = f'https://{domain}/api/datasets'

# The API key can be obtained from https://galaxy.naturalis.nl/user/api_key
# The approach we take here is that we get the key from env var $GALAXY_API_KEY
api_key = os.environ.get('GALAXY_API_KEY')
gi = galaxy.GalaxyInstance(domain, key=api_key)

# Get or create a new history. The civilized thing would be to delete this when done.
histories = gi.histories.get_histories(name='bioblend')
if len(histories) == 0:
    history = gi.histories.create_history('bioblend')
else:
    history = histories[0]

# Upload FASTA data into the history
with open('raxml-ready.fa', 'r') as file:
    fasta_contents = file.read()
fasta_id = gi.tools.paste_content(fasta_contents, history['id'], file_type='fasta')['outputs'][0]['id']

# Upload Newick data into the history
with open('raxml-ready.tre', 'r') as file:
    newick_contents = file.read()
newick_id = gi.tools.paste_content(newick_contents, history['id'], file_type='newick')['outputs'][0]['id']

# Lookup raxml
raxml = gi.tools.get_tools(name='RAxML')[0]

# Prepare input params. This part is the hard bit as it is essentially not documented at all. The way to
# do it is to:
# 1. prototype in the GUI what you want to do
# 2. check the tool XML file for the structure inside `inputs`
# 3. nested XML maps to dict keys by collapsing to pipe-separated
# Alternatively, the inputs from the tool can be fetched and serialized, e.g. as inputs.json
# Option 'd' is 'New rapid hill-climbing', which is actually the default
params = inputs().set('infile', dataset(fasta_id))\
    .set('search_model_selector|base_model', 'GTRGAMMAI')\
    .set('search_model_selector|model_type', 'nucleotide')\
    .set('selExtraOpts|extraOptions', 'full')\
    .set('selExtraOpts|search_algorithm', 'd')\
    .set('selExtraOpts|outgroup_name', 'GBMTG3032-16,CAB015-06,GTICO087-18')\
    .set('selExtraOpts|constraint_file', dataset(newick_id))

# Run raxml. When incorrectly parameterized this will trigger a ConnectionError, which is status code 500,
# i.e. a server-side error. No additional info is made available to the client. Conceivably the error logs
# on the server might help if you have access to them.
try:

    # This output is written to outputs.json to figure out the structure.
    raxml_results = gi.tools.run_tool(history['id'], raxml['id'], params)

    # We have to poll the job until it is done. For this we need the job ID.
    job = raxml_results['jobs'][0]
    jc = galaxy.jobs.JobsClient(galaxy_instance=gi)
    jc.wait_for_job(job_id=job['id'])

    # In this case there is a list of multiple outputs. The order seems to be unpredictable, so we have
    # to probe what we're looking for.
    for output in raxml_results['outputs']:
        if output['output_name'] == 'result':

            # The download URL should be composed as follows:
            # https://galaxy.naturalis.nl/api/datasets/8baaa5f7fc118c6e/display?to_ext=nhx
            url = f'{dlbase}/{output["id"]}/display?to_ext=nhx'
            response = requests.get(url)
            with open("output_tree.nhx", "w") as file:
                file.write(response.text)

except ConnectionError as e:
    print(e.body)

