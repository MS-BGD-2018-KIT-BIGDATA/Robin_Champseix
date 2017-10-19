#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 17:52:21 2017

@author: robinchampseix
"""

import requests
from bs4 import BeautifulSoup


years = ["2010","2011","2012","2013"]

labels = ["TOTAL DES PRODUITS DE FONCTIONNEMENT = A","TOTAL DES CHARGES DE FONCTIONNEMENT = B","TOTAL DES RESSOURCES D'INVESTISSEMENT = C","TOTAL DES EMPLOIS D'INVESTISSEMENT = D"]

def getSoupFromUrl(url):
    
    res = requests.get(url)
    
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup
    else:
        return None

def getMoyenneStrate(Url,label):
    soup = getSoupFromUrl(Url)
    if soup:
        share = soup.find_all("td",string=label)[0]
        moyenneStrate = share.previous_sibling.previous_sibling.text.strip()
        return moyenneStrate

def getEurosParHabitants(Url,label):
    soup = getSoupFromUrl(Url)
    if soup:
        share = soup.find_all("td",string=label)[0]
        moyenneStrate = share.previous_sibling.previous_sibling.previous_sibling.previous_sibling.text.strip()
        return moyenneStrate

for year in years:
    
    url = 'http://alize2.finances.gouv.fr/communes/eneuro/detail.php?icom=056&dep=075&type=BPS&param=5&exercice=' + year
    
    getSoupFromUrl(url)
    
    for label in labels :
        moyenneStrate = getMoyenneStrate(url,label)
        eurosparlabel = getEurosParHabitants(url,label)
        moyennes = "La moyenne de la strate de " + year + " pour le " + label + " est " + moyenneStrate
        eurosparhab = "Les euros par habitant de " + year + " pour le " + label + " valent " + eurosparlabel
        print(moyennes)
        print(eurosparhab)

