#!/usr/bin/env  python

import sys
import requests
import requests_cache
from bs4 import BeautifulSoup
from pprint import pprint
from lib.csvtools import dict_to_csv

def main():

    requests_cache.install_cache('scraper_cache')

    datacenters = {}

    #top level websites
    websites = ['http://www.datacentermap.com/usa/north-carolina/',
                'http://www.datacentermap.com/usa/south-carolina/']
    websites2 = []
    for website in websites:
        r = requests.get(website)
        soup = BeautifulSoup(r.text, 'html.parser')
        links = soup.findAll('a')
        for link in links:
            if 'title' not in link.attrs:
                continue
            if 'Colocation Data Centers' in link.attrs['title']:
                if link.attrs['href'] != "/datacenters.html":
                    websites2.append(link.attrs['href']) 
                #import pdb; pdb.set_trace()

    #second level websites
    for website2 in websites2:
        #print website2
        website2 = "http://www.datacentermap.com" + website2
        r2 = requests.get(website2)
        soup = BeautifulSoup(r2.text, 'html.parser')
        divs = soup.findAll('div', {'class': "DCColumn1"})
        for div in divs:
            #print div
            lines = \
                [x.strip().encode('ascii', 'ignore') for x in div.text.split('\n')]
            for idx,line in enumerate(lines):
                print idx,line
            dcname = lines[1]
            zipcode = ''.join([x for x in lines[4] if x.isdigit()])
            city  = ''.join([x for x in lines[4] if not x.isdigit()])
            state = lines[5].split(',')[0]
            country = lines[5].split(',')[1]

            if dcname in datacenters:
                dcname = dcname + " (%s)" % city
                #import pdb; pdb.set_trace()

            datacenters[dcname] = {}
            datacenters[dcname]['street'] = lines[3]
            datacenters[dcname]['city'] = city
            datacenters[dcname]['zipcode'] = zipcode
            datacenters[dcname]['country'] = country
            datacenters[dcname]['state'] = state

            # get the website url now ...
            # http://www.datacentermap.com/usa/south-carolina/charleston/immedion-palmetto.html
            links = div.findAll('a')
            for link in links:
                #print link.attrs
                href = link.attrs['href']
                if '?view=' in href: 
                    print href
                    #dcurl = div.find('a').attrs['href']
                    dcurl = 'http://www.datacentermap.com' + href
                    r3 = requests.get(dcurl)
                    soup3 = BeautifulSoup(r3.text, 'html.parser')
                    redirect = soup3.find('a', {'class': 'black'}) 
                    datacenters[dcname]['website'] = redirect.attrs['href']
                    #import pdb; pdb.set_trace()

    #addresses
    pprint(datacenters)
    dcs = datacenters.keys()    
    keys = datacenters[dcs[0]].keys() 
    print "datacenter," + ','.join(keys)
    for k,v in datacenters.iteritems():
        sys.stdout.write(k + ',')
        for key in keys:
            sys.stdout.write(v[key] + ',')
        sys.stdout.write('\n')
    #import pdb; pdb.set_trace()
    dict_to_csv(datacenters, 'datacenters.csv')


if __name__ == "__main__":
    main()
