#!/usr/bin/env python

import os
import sys
import requests
import requests_cache
from bs4 import BeautifulSoup
from pprint import pprint
from lib.csvtools import dict_to_csv
 
def main():
 
    requests_cache.install_cache('scraper_cache')
    
    mfers = {}    

    website = 'http://southcarolinasccoc.weblinkconnect.com/Manufacturing'
    r = requests.get(website)
    soup = BeautifulSoup(r.text, 'html.parser')

    ## Get the manufacturer names and addresses from the json script
    scripts = soup.findAll('script')
    for script in scripts:
        if 'var listingLatitude' in script.text:
            lines = script.text.split('\n')
            for line in lines:
                if 'addressesToMap' in line:
                    continue
                if not line.strip():
                    continue
                if line.startswith('var'):
                    line = line[135:]
                #print line
                try:
                    name = line.split(';')[2].split('>')[2].split('<')[0] 
                except Exception as e:
                    print e
                    print line
                    import pdb; pdb.set_trace()
                street = line.split(';')[2].split('>')[4].split('<')[0]
                city = line.split(';')[2].split('>')[5].split('<')[0].split(',')[0]
                state = line.split(';')[2].split('>')[5].split('<')[0].split(',')[1].replace('&nbsp', '').strip() 
                zipcode = line.split(';')[4].split('<')[0]
                #import pdb; pdb.set_trace()
                mfers[name] = {}
                mfers[name]['name'] = name
                mfers[name]['street'] = street
                mfers[name]['city'] = city
                mfers[name]['state'] = state
                mfers[name]['zipcode'] = zipcode
                mfers[name]['phone'] = ""
                mfers[name]['contact'] = ""
                mfers[name]['website'] = ""

    ## Get the contact names and phone numbers from the ListingResults divs
    listresults1 = soup.findAll('div', {'class': 'ListingResults_Level1_CONTAINER'})
    listresults2 = soup.findAll('div', {'class': 'ListingResults_Level2_CONTAINER'})
    listresults3 = soup.findAll('div', {'class': 'ListingResults_Level3_CONTAINER'})
    listresults4 = soup.findAll('div', {'class': 'ListingResults_Level4_CONTAINER'})

    all_listresults = listresults1 + listresults2 + listresults3 + listresults4
    for lr1 in all_listresults:
        #print lr1
        mfername = ""
        phone_num = ""
        contact = ""
    
        ## use the hrefs+imgs to figure out the mfer name in this cell
        links = lr1.findAll('a')
        for link in links:
            badwords = ['learn more', 'visit site', 'show on map']
            if link.text.lower() in badwords:
                continue
            href = link.attrs['href']
            mfername = link.find('img').attrs['alt']
            break

        ## more names here than in the js ... huwhat?
        if mfername not in mfers:
            mfers[mfername] = {}
            mfers[mfername]['name'] = mfername
            mfers[mfername]['street'] = ""
            mfers[mfername]['city'] = ""
            mfers[mfername]['state'] = ""
            mfers[mfername]['zipcode'] = ""
            mfers[mfername]['phone'] = ""
            mfers[mfername]['contact'] = ""
            mfers[mfername]['website'] = ""
            #import pdb; pdb.set_trace()

        ## get the location if not already known
        if not mfers[mfername]['state']:
            addydiv = lr1.find('div', {'itemprop': 'address'})
            mfers[mfername]['street'] = addydiv.find('span', {'itemprop': 'street-address'}).text
            mfers[mfername]['city'] = addydiv.find('span', {'itemprop': 'locality'}).text
            mfers[mfername]['state'] = addydiv.find('span', {'itemprop': 'region'}).text
            mfers[mfername]['zipcode'] = addydiv.find('span', {'itemprop': 'postal-code'}).text
            #import pdb; pdb.set_trace()

        ## phone number is set as an image (not all have a phone)...
        try:
            phone_img = lr1.find('img', {'src': '/external/wcpages/images/phone.gif'})
            phone_num = phone_img.text.strip().encode('ascii', 'ignore')
            mfers[mfername]['phone'] = phone_num
        except Exception as e:
            pass

        ## set the website
        try:
            mfers[mfername]['website'] = lr1.find('a', {'target': '_blank'}).attrs['href']
        except Exception as e:
            #print e
            #import pdb; pdb.set_trace()
            pass

        # ListingResults_Level3_MAINCONTACT
        try:
            mfers[mfername]['contact'] = lr1.find('div', {'class': 'ListingResults_Level3_MAINCONTACT'}).text
        except Exception as e:
            pass

        #if mfername == 'Bose Corporation':
        #    import pdb; pdb.set_trace()


    ####################################################
    # CSV PRINT
    ####################################################

    #pprint(mfers)
    mfnames = sorted(mfers.keys())
    keys = mfers[mfnames[0]].keys()
    keys = [x for x in keys if x != 'name']
    print "manufacturer," + ','.join(keys)
    for k in mfnames:
        v = mfers[k]
        sys.stdout.write('"' + k + '"' + ',')
        for key in keys:
            sys.stdout.write('"' + v.get(key, "") + '"' + ',')
        sys.stdout.write('\n')
    #import pdb; pdb.set_trace()
    dict_to_csv(mfnames, 'manufacturers.csv')

if __name__ == "__main__":
    main() 
