#################################
##### Name: Shiyu Guo    ########
##### Uniqname: shiyuguo ########
#################################

from bs4 import BeautifulSoup
import requests
import time
import json
import secrets # file that contains your API key

CACHE_FILENAME = "cache.json"
CACHE_DICT = {}
MAPAPI_KEY = secrets.API_KEY

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

def make_html_request_using_cache(url,cache_dict):
    '''Check the cache for a saved result for the url. 
    If the result is found, return it. Otherwise send a new 
    request, save it, then return it.
    Parameters
    ----------
    url: string
        The URL 
    cache_dict: dictionary
        The saved dictionary or dictionary to save
    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    CACHE_DICT = open_cache()
    if url in cache_dict.keys():
        print("Using cache")
        return cache_dict[url]
    else:
        print("Fetching")
        time.sleep(1)
        response=requests.get(url)
        cache_dict[url]=response.text
        save_cache(cache_dict)
        return cache_dict[url]

def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs
    Returns
    -------
    string
        the unique key as a string
    '''
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector +  connector.join(param_strings)
    return unique_key
    
def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs
    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    response = requests.get(baseurl, params)
    return response.json()

def make_request_with_cache(baseurl, params):
    '''Check the cache for a saved result for this baseurl+params
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs
    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    CACHE_DICT=open_cache()
    request_key = construct_unique_key(baseurl, params)
    if request_key in CACHE_DICT.keys():
        print("Using cache")
        return CACHE_DICT[request_key]
    else:
        print("Fetching")
        CACHE_DICT[request_key] = make_request(baseurl, params)
        save_cache(CACHE_DICT)
        return CACHE_DICT[request_key]

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''

    def __init__(self, category,name,address,zipcode,phone):
        self.category=category
        self.name=name
        self.address=address
        self.zipcode=zipcode
        self.phone=phone
    
    def info(self):
        '''format attributes into a string that represent a nationalsit.

        Parameters
        ----------
        none

        Returns
        -------
        str
            <name> (<category>): <address> <zip>
        '''
        return f'{self.name} ({self.category}): {self.address} {self.zipcode}'

def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    baseurl='https://www.nps.gov'
    home_path = '/index.htm'
    home_page_url = baseurl+home_path
    response = make_html_request_using_cache(home_page_url,CACHE_DICT)
    soup= BeautifulSoup(response,'html.parser')

    state_url={}
    state_data = soup.find('ul',class_='dropdown-menu SearchBar-keywordSearch').find_all('li',recursive=False)
    for state in state_data:
        state_tag = state.find('a')
        state_path = state_tag['href']
        state_detail_url = baseurl + state_path
        state_name = str(state_tag.string).lower()
        state_url[state_name]=f'{state_detail_url}'
    return state_url

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''

    response=make_html_request_using_cache(site_url,CACHE_DICT)
    soup= BeautifulSoup(response,'html.parser')
    park_name= str(soup.find('a',class_='Hero-title').string)
    park_category= str(soup.find('span',class_='Hero-designation').string)
    if park_category is None:
        park_category = 'N/A'

    address_locality = str(soup.find('p',class_='adr').find(itemprop="addressLocality").string)
    if address_locality is None:
        address_locality='N/A'
    address_region= str(soup.find('p',class_='adr').find(itemprop="addressRegion").string)
    if address_region is None:
        address_region='N/A'
    park_address = address_locality+', '+ address_region
    park_zipcode = str(soup.find('span',class_='postal-code').string).strip()
    if park_zipcode is None:
        park_zipcode='N/A'
    park_phone = str(soup.find('span',class_='tel').string).strip()
    if park_phone is None:
        park_phone = 'N/A'
    park_site = NationalSite(park_category,park_name,park_address,park_zipcode,park_phone)
    
    return park_site

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    response = make_html_request_using_cache(state_url,CACHE_DICT)
    soup= BeautifulSoup(response,'html.parser')
    baseurl='https://www.nps.gov'
    state_site_list=[]

    state_site_info = soup.find('ul',id='list_parks').find_all('div',class_='col-md-9 col-sm-9 col-xs-12 table-cell list_left')
    for state_site in state_site_info:
        state_site_path = state_site.find('a')['href']
        state_site_url= baseurl+state_site_path
        state_site_instance= get_site_instance(state_site_url)
        state_site_list.append(state_site_instance)
    
    return state_site_list

def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    origin = site_object.zipcode
    params = {'key':MAPAPI_KEY,'origin':origin,'radius':10,'units':'m','maxMatches':10,'ambiguities':'ignore','outFormat':'json'}
    results = make_request_with_cache('http://www.mapquestapi.com/search/v2/radius',params=params)
    return results

def nearby_places_formatted(results):
    '''Format the returned value from get_nearby_places(site_object)

    Parameters
    ----------
    results: dict
        a converted API return from MapQuest API 
    
    Returns
    -------
    list
        a list of (up to 10) nearby places
    '''   
    nearby_places_list = []
    for result in results['searchResults']:
        field = result['fields']
        name = field.get('name')
        address = field.get('address') or 'no address'
        category = field.get('group_sic_code_name') or 'no category'
        city= field.get('city') or 'no city'
        nearby_places_list.append(f'- {name} ({category}): {address} {city}')
    return nearby_places_list


if __name__ == "__main__":
    state_input = input('Enter a state name (e.g. Michigan,michigan) or \"exit\": ').lower()
    if state_input=='exit':
        exit()
    else:
        while state_input !='exit':
            CACHE_DICT=open_cache()
            state_url=build_state_url_dict()
            if state_input.isalpha() and state_input in state_url.keys():
                state_site_instance= get_sites_for_state(state_url[state_input])
                state_instance_info=[]
                for instance in state_site_instance:
                    state_instance_info.append(instance.info())
                print(f'--------------------------------------------\nList of national sites in {state_input}\n--------------------------------------------')
                for index, state_instance in enumerate(state_instance_info,1):
                    print(f'[{index}] {state_instance}')
                
                detail_input = input('Choose the number for detail search or \"exit\" or \"back\": ').lower()
                while detail_input.isnumeric():   
                    if int(detail_input) in range(1,len(state_instance_info)+1):
                        instance = state_site_instance[int(detail_input)-1]
                        nearby_places = nearby_places_formatted(get_nearby_places(instance))
                        print(f'--------------------------------------------\nPlace near {instance.name}\n--------------------------------------------')
                        for place in nearby_places:
                            print(place)
                        detail_input = input('Choose the number for detail search or \"exit\" or \"back\": ').lower()
                        
                    else:
                        print('[Error] Enter proper number')
                        detail_input = input('Choose the number for detail search or \"exit\" or \"back\": ').lower()
                if detail_input == 'back':
                    state_input = input('Enter a state name (e.g. Michigan,michigan) or \"exit\": ').lower() 
                else:
                    exit() 
            else:
                print('[Error] Enter proper state name')
                state_input = input('Enter a state name (e.g. Michigan,michigan) or \"exit\": ').lower()
        else: 
            exit()




