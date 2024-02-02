#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import requests
import pandas as pd
import pysftp 
import config
import base64
import requests
from urllib.request import urlretrieve as retrieve



class API_creds:

    base_url = 'https://connectivity.ottocap.com'
    
    num_of_creds = 0
    
    def __init__(self, client_secret, client_id):
        self.client_secret = client_secret
        self.client_id = client_id
        
        API_creds.num_of_creds += 1
        
    def encodeCredentials(self):
        client_credential_string = self.client_id + ':' + self.client_secret
        encoded_credentials = base64.b64encode(client_credential_string.encode('utf-8'))
        encoded_credential_string = str(encoded_credentials, 'utf-8')
        
        return('Basic ' + encoded_credential_string)
    
    
    def get_access_token(self):
    
        s = requests.Session()

        url_ext = '/authenticate/token/'

        url = API_creds.base_url+url_ext
        
        payload = {
        'username' : config.otto_email,
        'password' : config.otto_pass,
        "grant_type": "password"
            }

        headers = {
            'authorization': self.encodeCredentials(),
            'Content-Type' : 'application/x-www-form-urlencoded'
        }

        r = s.post(url, headers = headers, data = payload)
        tok = r.json()['access_token']
        return(tok)
        return(r)

#Instantiate API Creds class at otto variable 
otto = API_creds(config.client_secret, config.client_ID)
tok = otto.get_access_token()

# --------------------------------------------------with token established, go & grab unique inventory string------------

def getInventory(tok):
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Authorization': 'Bearer ' + tok    
    }
    
    response = requests.get('https://ottocap.com/api/s/download_inventory', headers= headers)
    link = response.json()['file']        
    return(link)


link = getInventory(tok)

# -------------------------------------------------make a request to the link & save as 'df' in local directory----------

def retrieve_send():
    #takes hardcoded url, and saves as ottocap_inventory.csv in local dir
    retrieve(link, 'ottocap_inventory.csv')
    
    df = pd.read_csv('ottocap_inventory.csv')
    df2 = df[['sku_parent', 'sku_no', 'name', 'color', 'size','instock', 'CA', 'TX', 'GA']].copy()
    
    return(df2)
    
df = retrieve_send()
df.to_csv('otto_inv.csv', index = False)

# ----------------------------------------------- send otto inventory to remote server------

Hostname = '165.22.33.209'
Username = 'root'
Password = ''
sftpPort = 22

# ignore hosts check
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None


with pysftp.Connection(host=Hostname, port=sftpPort, username=Username, password=Password, cnopts = cnopts) as sftp:
    print('Connection established')
    
    remotepath = '/var/www/html/admin/ottoexcelfile/otto_inv.csv'
    localpath = 'otto_inv.csv'
    sftp.put(localpath, remotepath)