#!/usr/bin/env python

import sys
import requests
import requests_cache
from bs4 import BeautifulSoup
from pprint import pprint

def main() :
    requests_cache.install_cache('scraper_cache')
    
    domain = "http://web.raleighchamber.org"
    caturls = []
    compurls = []
    comps = dict()
    
    r = requests.get(domain + "/Industrial-Manufacturing")
    soup = BeautifulSoup(r.text, 'html.parser')
    
    ## get all category urls from top level site
    for li in soup.findAll('li', {'class' : 'ListingCategories_AllCategories_CATEGORY'}):
        link = li.findAll('a')
        caturls.append(link[0].get('href'))

    ## get all company urls from category urls
    for caturl in caturls:
        r = requests.get(domain + caturl)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # some category urls redirect to a company url, if this is a company url, add it to the list, and move to the next category
        if soup.find('span', {'class' : 'ListingDetails_Level5_MAINCONTACT'}):
            compurls.append(caturl)
            continue
        
        for div in soup.findAll('div', {'class' : 'ListingResults_All_ENTRYTITLELEFTBOX'}):
            link = div.findAll('a')
            compurls.append(link[0].get('href'))
        #import pdb; pdb.set_trace()
    
    #TEMPcompurls = ["/TelecommunicationsEquipment-Service/Link-US,-LLC-20451", "/Asphalt-Crushing/Old-School-Crushing-Company-21400"]
    
    itemkeys = {'street': ('span', 'itemprop', 'street-address'),
                'city': ('span', 'itemprop', 'locality'),
                'state': ('span', 'itemprop', 'region'),
                'zipcode': ('span', 'itemprop', 'postal-code'),
                'contact': ('span', 'class', 'ListingDetails_Level5_MAINCONTACT')}

    ## visit all the company urls and get company attributes
    for idx,compurl in enumerate(compurls):

        print idx,len(compurls),compurl

        r = requests.get(domain + compurl)
        soup = BeautifulSoup(r.text, 'html.parser')
        name = soup.title.string.strip()

        comps[name] = {}
        comps[name]['name'] = name

        for k,v in itemkeys.iteritems():
            try:
                comps[name][k] = soup.find(v[0], {v[1] : v[2]}).text.strip()
            except Exception as e:
                comps[name][k] = ""
            
        #contact = soup.find('span', {'class' : 'ListingDetails_Level5_MAINCONTACT'}).text.strip()
        #comps[name]['contact'] = contact
               
    ## print column headings then all attributes for each company
    f = open('output.csv', 'w')   
    
    columns = [x for x in comps[comps.keys()[0]].keys() if x != 'name']
    columns = ['name'] + columns

    f.write(','.join(columns) + '\n')
    for k,v in comps.items():
        for column in columns:
            f.write('"' + v[column] + '"' + ',')
        f.write('\n')
    
    f.close()
    import pdb; pdb.set_trace()

        
        
if __name__ == "__main__" :
    main()
