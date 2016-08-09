#  simple script to get metadata from an OC collection and write to json file
#  @schuyberg 2016
# 

# import utils
import urllib2, json, sys


print "working..."
# set vars
collection = '18861';
base_url = 'https://oc-index.library.ubc.ca/collections/';
items_url = base_url + collection + '/items';

# get all items in collection
all_items_data = json.loads(urllib2.urlopen(items_url).read());

# create output file
with open('output.json', 'w') as output:
    output.write('[');

# loop through items in collection
for idx,itm in enumerate(all_items_data['data']):
    iid = itm['_id'];
    item_url = base_url + collection + '/items/' + iid

    # get item metadata
    item_data = json.loads(urllib2.urlopen(item_url).read())

    # get the metadata we want
    item_handle = item_data['data']['URI'][0]['value'];
    item_text = item_data['data']['FullText'][0]['value'];
    item_json = { 'handle' : item_handle, 'text_snippet' : item_text[0:5000]};

    # write to output
    with open('output.json', 'a') as output:
        json.dump(item_json, output, indent=4, sort_keys=True, separators=(',', ':'));
        output.write(',');

    #print update (still working)
    progress = float(idx) / len(all_items_data['data']) * 100;
    sys.stdout.write('---> ' + str(progress)[0:4] + '%\r');
    sys.stdout.flush(); 

# close output array
with open('output.json', 'a') as output:
    output.write(']')

print 'data extraction complete: output written to output.json';