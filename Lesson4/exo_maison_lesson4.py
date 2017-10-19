
# coding: utf-8

# In[20]:


import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from itertools import chain
from multiprocessing import Pool, TimeoutError
import numpy as np


# In[2]:


urlArgus = "https://www.lacentrale.fr/cote-voitures-renault-zoe--2012-.html"

regions = ["ile_de_france", "provence_alpes_cote_d_azur", "aquitaine"]

urlLeboncoin = "https://www.leboncoin.fr/voitures/offres/"

# In[5]:


def getSoupFromURL(url, method='get', data={}):

    if method == 'get':
        res = requests.get(url)
    elif method == 'post':
        res = requests.post(url, data=data)
    else:
        return None

    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup
    else:
        return None


# In[3]:


def getUrlArgus():
    urlArgusList = []
    for annee in range(2012,2018):
        urlArgusList.append("https://www.lacentrale.fr/cote-voitures-renault-zoe--" + str(annee) + "-.html")
    return urlArgusList


# In[4]:


def getArgusLinks(urlArgus):
    soupArgus = getSoupFromURL(urlArgus)
    a = soupArgus.find_all("div", class_ = "listingResultLine auto")
    linksArgus = ["https://www.lacentrale.fr/" + a[i].a['href'] for i in range(len(a))]
    return linksArgus


# In[6]:


def getUrlList():
    urlList = []
    for region in regions:
        siteSoup = getSoupFromURL("https://www.leboncoin.fr/voitures/offres/" + region + "/?th=1&q=renault%20zo%E9")
        numberOfPages = int(siteSoup.find_all("a", class_ = "element page")[-1].text.strip())
        for page in range(1,numberOfPages+1):
            urlList.append(urlLeboncoin + region + "/?o=" + str(page) + "&q=renault%20zo%E9")
    return urlList

# In[9]:

# récuperer la liste de tous les renault zoe
def getLinks(url):
    soup = getSoupFromURL(url)
    subsoup = soup.find_all("a", class_= "list_item clearfix trackable")
    linkList = ["http:" + car['href'] for car in subsoup]
    return linkList


# In[7]:


def getVersion(soup):

    regexLife = "[Ll]{1}[iI]{1}[fF]{1}[eE]{1}"
    regexZen = "[zZ][eE][nN]"
    regexIntens = "[Ii][Nn][Tt][Ee][Nn][Ss]"

    description = soup.find("p", itemprop = "description").text.strip()

    if re.search(regexLife, description):
        version = "Life"
    elif re.search(regexZen, description):
        version = "Zen"
    elif re.search(regexIntens, description):
        version = "Intens"
    else:
        version = "Inconnu"
    return version


# In[8]:


def sellerType(soup):

    if soup.find("span", class_ = "ispro"):
        seller = "Professionel"
    else :
        seller = "Particulier"

    return seller


# In[10]:


def getNumber(soup):

    regexTelNumber = '(0[1-9](?P<sep>[-. ]?)(?:\d{2}(?P=sep)){3}\d{2})'
    description = soup.find("p", itemprop = "description").text.strip()
    num = re.search(regexTelNumber, description)

    if num :
        number = num.group(0).replace(" ", "").replace("-", "").replace(".", "")
        return number
    else :
        return "Numéro Inconnu"


# In[11]:


def getInfos(carLink):

    carSoup = getSoupFromURL(carLink)

    price = int(carSoup.find_all("span", class_= "value")[0].text.strip().replace("\xa0€", "").replace(" ", ""))

    year = int(carSoup.find_all("span", class_= "value")[4].text.strip())

    kilometrage = int(carSoup.find_all("span", class_= "value")[5].text.strip().replace("KM", "").replace(" ", ""))

    version = getVersion(carSoup)

    telephonNumber = getNumber(carSoup)

    seller = sellerType(carSoup)

    return version, year,  kilometrage, price, telephonNumber, seller


# In[12]:


def getArgusEstimatedPrice(argusLink):
    soupArg = getSoupFromURL(argusLink)
    estimatedPrice = int(soupArg.find("span", class_ = "jsRefinedQuot").text.strip().replace(" ", ""))
    return estimatedPrice


# In[78]:


get_ipython().run_cell_magic('time', '', '\n# Scrapping des estimations du prix des Argus\nargusUrls = getUrlArgus()\nyear = [2012, 2013, 2014, 2015, 2016, 2017]\n\nintensPrice = list(map(lambda x :  getArgusEstimatedPrice(getArgusLinks(x)[0]), argusUrls))\nlifePrice = list(map(lambda x :  getArgusEstimatedPrice(getArgusLinks(x)[2]), argusUrls))\nzenPrice = list(map(lambda x :  getArgusEstimatedPrice(getArgusLinks(x)[4]), argusUrls))')


# In[79]:


# Création d'une Dataframe avec les estimations des prix en fonction de l'année et du modèle
d = {"Intens" : intensPrice, 'Life': lifePrice, 'Zen': zenPrice}
dfEstimatedPrice = pd.DataFrame(d, index = year)

dfEstimatedPrice["Inconnu"] = round(dfEstimatedPrice.mean(axis = 1),0)
dfEstimatedPrice


# In[47]:


get_ipython().run_cell_magic('time', '', '# Multithreading\npool = Pool(processes=10)\n\nurlList = getUrlList()\n\nfinalList = []\ncarsLinks = []\n\ncarsLinks = pool.map(getLinks, urlList)\ncarsLinks = list(chain.from_iterable(carsLinks))\n\n# Création de liste avec chaque ligne comprenant les infos sur chaque voiture\ncompleteList = pool.map(getInfos, carsLinks)')


# In[97]:


# Création d'un DataFrame comprenant les infos du boncoin sur les voitures
df = pd.DataFrame(completeList, columns = ["version", "year",  "kilometrage", "price", "telephon_number", "seller"])
df.head()


# In[98]:


df["EstimatedPrice"] = np.nan
dftest = df[["year", "version"]].values


# In[104]:


get_ipython().run_cell_magic('time', '', 'for i in range(len(dftest)):\n    if dftest[i][0] in year :\n        df["EstimatedPrice"][i] = dfEstimatedPrice.loc[dftest[i][0], dftest[i][1]]    ')


# In[105]:


df.head()


# In[106]:


df.to_csv(path_or_buf = "/Users/robinchampseix/Desktop/Telecom/MS_Big_Data/Kit_Data_Science/renaultZoe.csv", sep='\t')
