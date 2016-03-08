#!/usr/bin/env python

# http://sccommerce.com/sc-industrial-directory

import requests
import requests_cache
from pprint import pprint
from bs4 import BeautifulSoup
from lib.csvtools import dict_to_csv

def main():

    # This page has a search form that must be submitted to get the list of companies.
    # To post data to a form in python, a dictionary of parameters should be created 
    # and passed into the post url. The parameters and values for this form were found
    # by opening the developers tools in firefox and inspecting the parameters sent
    # by pressing the 'search' button.

    companies = {}

    requests_cache.install_cache('scommerce_cache')

    # Use sessions to persist cookies and formdata
    baseurl = 'http://sccommerce.com'
    s = requests.Session()
    r = s.get('%s/sc-industrial-directory' % baseurl)
    rsoup = BeautifulSoup(r.text, 'html.parser')
    souplines = [x for x in rsoup.prettify().split('\n')]


    # Grab the unique form ID specific to this session ...
    #   <input type="hidden" name="form_build_id" value="form-ucL4nG9DvogNwbCLlTuXeHfME05gn4KrK1AA1mPmW0M" />
    iform = rsoup.find('input', {'name': 'form_build_id', 'type': 'hidden'})
    params = {'keywords': '',
              'name': '',
              'operation_type': '',
              'employee_count': 0,
              'parent_company': '',
              'op': 'Search',
              'form_build_id': iform.attrs['value'],
              'form_id': 'scapi_search_form' }

    # Keep all the result page(s) soups
    result_soups = []

    # Keep all the company pages
    company_pages = []

    # Post the parameters
    pr = s.post('http://sccommerce.com/sc-industrial-directory', data=params)
    prsoup = BeautifulSoup(pr.text, 'html.parser')
    result_soups.append(prsoup)

    # Iterate through every page of results by following the 'next' href ...
    next_page = prsoup.find('a', {'class': 'page-next active'}).attrs['href']
    print next_page
    while next_page:
        try:
            nr = s.get('%s/%s' % (baseurl, next_page))
            nrsoup = BeautifulSoup(nr.text, 'html.parser')
            result_soups.append(nrsoup)
            next_page = nrsoup.find('a', {'class': 'page-next active'}).attrs['href']
            print next_page
        except Exception as e:
            print e
            next_page = None    

    # Results are in <table class="results-table">
    for rs in result_soups:
        rtable = rs.find('table', {'class': 'results-table'})
        #for th in rtable.findAll('th'):
        #    print th
        for tr in rtable.findAll('tr'):
            #print tr
            link = tr.find('a').attrs['href']
            link = baseurl + link
            if '/company/' in link:
                #print link
                if link not in company_pages:
                    company_pages.append(link)

    '''
    <h1 class="title">680 Screened Tees</h1>
    <div class="details">
    <p>
    <b>Address:</b> 680 Violet St</p>
    <p>
    <b>City:</b> West Columbia</p>
    <p>
    <b>Zip:</b> 29169</p>
    '''

    # sort the company pages
    company_pages = sorted(set(company_pages))                
    total_companies = len(company_pages)

    # iterate through each and get details
    for idx,cp in enumerate(company_pages):
        cdata = {}
        print idx,total_companies,cp
        cr = s.get('%s/%s' % (cp, next_page))
        csoup = BeautifulSoup(cr.text, 'html.parser')
        cname = csoup.find('h1', {'class': 'title'}).text.strip().encode('ascii', 'ignore')
        cdata['name'] = cname
        ddiv = csoup.find('div', {'class': 'details'})
        for par in ddiv.findAll('p'):
            #print par
            parts = par.text.strip().split(':', 1)
            key = parts[0].strip().encode('ascii', 'ignore')
            cdata[key] = parts[1].strip().encode('ascii', 'ignore')
        companies[cname] = cdata
        pprint(cdata)
        #import pdb; pdb.set_trace()

    dict_to_csv(companies, 'scommerce.csv') 
    #import pdb; pdb.set_trace()



if __name__ == "__main__":
    main()
