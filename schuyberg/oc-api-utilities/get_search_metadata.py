
#  execute Open Collections search and write metadata to a json file
#  @schuyberg 2016
#
# thanks to @seanmcna for the query structure!

import json, requests, sys

###########################
# CONFIG

# endpoint vars
ocUrl = 'https://open.library.ubc.ca/'
ocApiUrl = 'https://oc-index.library.ubc.ca' # APPY URL
# your API key here:
apiKey = 'f8fe4ee14c553f163d8915db3af4fb4c554dbbf7e19f2e38aedfa95ab258f806'

# edit these to change the results
search_index = 'oc'
query = 'program: ("music")'
source_fields = ['title','_id', 'ubc.internal.repo.handle','degree', 'affiliation', 'program']

#edit these to set the output file(s)
filename = 'music'

# run with test as true for testing, false (or no argument) to write to file
test = False

###########################

# search
offset = 0
size = 50
total = 100
def doSearch():
    search = dict()
    search['from'] = offset
    search['size'] = size
    search['type'] = 'object'
    search['body'] = dict()
    # Sort settings
    search['body']['sort'] = dict()
    search['body']['sort']['_score'] = dict()
    search['body']['sort']['_score']['order'] = 'desc'
    # Fields to return
    search['body']['_source'] = []
    for idx,f in enumerate(source_fields):
        search['body']['_source'].append(f)
    search['body']['fields'] = ['ubc.transcript']
    # Query String
    search['body']['query'] = dict()
    search['body']['query']['query_string'] = dict()
    search['body']['query']['query_string']['query'] = query
    #Set the repo
    search['index'] = search_index
    jsonSearch = json.JSONEncoder(search)
    # print('QUERY:')
    # print(json.dumps(search, indent=4, sort_keys=True))
    #post the search
    searchUrl = ocApiUrl+'/search?apiKey='+apiKey
    apiResponse = requests.post(searchUrl, json=search).json()
    global total
    total = apiResponse['data']['data']['hits']['total']
    # print('RESPONSE:')
    # print(json.dumps(apiResponse, indent=4, sort_keys=True))
    return apiResponse['data']['data']['hits']['hits']

# user feedback (progress)
items_processed = 0
def progress():
    global items_processed, total
    items_processed += 1
    sys.stdout.write('---> ' + str(items_processed) + ' of ' + str(total) + ' items read' + '\r')
    sys.stdout.flush(); 

# parse data
#### edit this to modify ouput #####
def parseResults(results, resultAction):
    for idx,r in enumerate(results):
        d = dict()
        d = r['_source']
        d['id'] = r['_id']
        d['text_snippet'] = r['fields']['ubc.transcript'][0][:5000]
        # writeToFile()
        resultAction(jsonfile, d)
        progress()

# output
jsonfile = filename + '.json'
def createFile(file):
    with open(file, 'w') as output:
        output.write('[');

    # write to output
def writeToFile(file, data):
    with open(file, 'a') as output:
        json.dump(data, output, indent=4, sort_keys=True, separators=(',', ':'));
        output.write(',');

def endFile(file):
    with open(file, 'a') as output:
        output.write(']')

    # for testing
def printOutput(file, data):
    print('destination: ' + file)
    print(json.dumps(data, indent=4, sort_keys=True))

# loop through all results
def getAllResults(resultAction):
    results = doSearch()
    if len(results) < 1:
        return
    else:
        parseResults(results, resultAction)
        global offset 
        offset = offset + size
        getAllResults(resultAction)

#execute
def execute(test=False):
    print 'working...'
    if test:
        return getAllResults(printOutput)
    createFile(jsonfile)
    getAllResults(writeToFile)
    endFile(jsonfile)
    print 'data extraction complete: output written to ' + jsonfile

execute(test)



