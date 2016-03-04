#!/usr/bin/env python

import os
import sys
import requests
import requests_cache
from bs4 import BeautifulSoup
from pprint import pprint
 
def main():
 
    requests_cache.install_cache('scraper_cache')
    
    mfers = {}    

    fields = {'city': 'locality',
              'street': 'street-address',
              'state': 'locality',
              'zipcode': 'postal-code'}

    baseurl = "http://web.raleighchamber.org"
    topsite = "%s/Industrial-Manufacturing" % baseurl
    r = requests.get(topsite)
    soup = BeautifulSoup(r.text, 'html.parser')

    # <li class="ListingCategories_AllCategories_CATEGORY">
    subcategories = soup.findAll('li', {'class': 'ListingCategories_AllCategories_CATEGORY'})
    for subcat in subcategories:
        #print subcat
        link = subcat.find('a')
        href = link.attrs['href']
        #print baseurl + href

        catr = requests.get(baseurl + href)
        catlines = catr.text.split('\n')
        catsoup = BeautifulSoup(catr.text, 'html.parser')

        '''
        for idx,x in enumerate(catlines):
            if 'Pilot' in x:
                print idx,x
        '''

        if catr.url == baseurl + href:
            divs = catsoup.findAll('div', {'class': 'ListingResults_All_CONTAINER ListingResults_Level1_CONTAINER'})
            for div in divs:
                #print div.attr
                mfername = div.find('img').attrs['alt']
                mfers[mfername] = {}
                mfers[mfername]['name'] = mfername
                mfers[mfername]['industry'] = href.replace('/', '')
                #import pdb; pdb.set_trace()
                #print "\t",mfername
                for k,v in fields.iteritems():
                    try:
                        mfers[mfername][k] = div.find('span', {'itemprop': v}).text.strip()                    
                    except Exception as e:
                        mfers[mfername][k] = ""

                ## find the phone number
                try:
                    mfers[mfername]['phone'] = \
                        div.find('img', {'src': '/external/wcpages/images/phone.gif'}).text.strip()
                except Exception as e:
                    mfers[mfername]['phone'] = ""

                ## find the contact <img src="/external/wcpages/images/maincontact.gif">
                try:
                    mfers[mfername]['contact'] = \
                        div.find('img', {'src': '/external/wcpages/images/maincontact.gif'}).text.strip()
                except Exception as e:
                    mfers[mfername]['contact'] = ""

                ## find the website
                mfers[mfername]['website'] = ""
                links = div.findAll('a')
                for link in links:
                    if link.text.lower() == 'visit site':
                        mfers[mfername]['website'] = link.attrs['href']

                #pprint(mfers[mfername])
                #import pdb; pdb.set_trace()
            #import pdb; pdb.set_trace()

        else:
            ## some pages have a single bolded company which was a redirect
            l5headerboxes = catsoup.findAll('div', {'class': 'ListingDetails_Level5_HEADERBOX'})
            for box in l5headerboxes:
                #print box
                try:
                    mfername = box.find('span', {'class': " ListingDetails_Level5_SITELINK "}).text.strip()
                except Exception as e:
                    #print e
                    try:
                        mfername = box.find('a', {'target': '_blank'}).text.strip()
                    except Exception as e2:
                        print e2
                        import pdb; pdb.set_trace()

                mfers[mfername] = {}
                mfers[mfername]['name'] = mfername
                mfers[mfername]['industry'] = href.replace('/', '')
                for k,v in fields.iteritems():
                    try:
                        mfers[mfername][k] = box.find('span', {'itemprop': v}).text.strip()                    
                    except Exception as e:
                        mfers[mfername][k] = ""

                ## find the website <a class="ListingDetails_Level5_SITELINK">
                try:
                    mfers[mfername]['website'] = \
                        box.find('a', {'class': 'ListingDetails_Level5_SITELINK'}).attrs['href']
                except Exception as e:
                    mfers[mfername]['website'] = ""


                ## find the phone number
                try:
                    mfers[mfername]['phone'] = \
                        box.find('img', {'src': '/external/wcpages/images/phone.gif'}).text.strip()
                except Exception as e:
                    mfers[mfername]['phone'] = ""

                ## find the contact name
                contact = None
                links = box.findAll('a')
                for link in links:
                    if hasattr(link, 'attrs') and hasattr(link, 'text'):
                        #print link
                        if 'directory/' in link.attrs['href']:
                            if link.text == 'map' or link.text == 'directions':
                                continue
                            #print link
                            mfers[mfername]['contact'] = link.text

                #import pdb; pdb.set_trace()
                #pprint(mfers[mfername])        

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

if __name__ == "__main__":
    main() 
