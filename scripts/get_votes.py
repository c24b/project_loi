# coding: utf-8
from bs4 import BeautifulSoup
import io, json, csv
import time, datetime
import requests
from bs4 import BeautifulSoup
import re

def read_json_file(fname="read_example.json", fnameout="full_participants.json"):
    '''methode simple pour lire un fichier json en python'''
    with open(fname, 'r') as f:
        with open(fnameout, 'w') as fout:
            fout.write(f.read()+"}}")
        #return json.load(f, encoding="utf-8")
        
def get_votes(fname):
    '''détails des votes pour chaque article de loi'''
    with open(fname, 'r') as f:
        data = f.read()[0:500]
    for n in data.split(":"):
        print n
        
    return 
    
if __name__=="__main__":
    get_votes("./data/votesxparticipants_clean.json")
    
    
