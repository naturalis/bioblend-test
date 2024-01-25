from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.tools.inputs import inputs
from bioblend import ConnectionError
import os

# The API key can be obtained under https://galaxy.naturalis.nl/user/api_key
api_key = os.environ.get('GALAXY_API_KEY')
gi = GalaxyInstance('galaxy.naturalis.nl', key=api_key)

# Get or create a new history
histories = gi.histories.get_histories(name='bioblend')
if len(histories) == 0:
    history = gi.histories.create_history('bioblend')
else:
    history = histories[0]

# Lookup raxml
raxml = gi.tools.get_tools(name='RAxML')[0]

# Get inputs => saved as inputs.json
# inputs = gi.tools.show_tool(tool_id, io_details=True, link_details=False)
# print(inputs)

# Prepare input params
# These correspond with the 'name' keys in the JSON inputs.json
params = inputs().set('infile', 'raxml-ready.fa')\
    .set('base_model', 'GTRGAMMA')\
    .set('model_type', 'nucleotide')\
    .set('search_algorithm', 'y')\
    .set('constraint_file', 'raxml-ready.tre')

# Run raxml
try:
    gi.tools.run_tool(history['id'], raxml['id'], params)
except ConnectionError as e:
    print(e.body)
