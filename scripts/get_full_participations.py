# coding: utf-8
from bs4 import BeautifulSoup
import requests
import re
import io, json, csv
import time, datetime
import collections
import sys

__doc__ ='''
Restructuration de la BDD de la consultation:

Un participant:
* a voté sur x articles
* a fait x modifications sur x articles
* a proposé x articles
* a proposé x sources pour x articles
* a émis x arguments pour x articles

Un article est composé
* d'un texte
* d'un titre
* d'un lien
* d'un auteur
* d'une date
* est issu d'une proposition ou non (citoyen ou gouvernement)
il est caractérisé par 
* x votes pour x participants
* x modifications par x participants
* x arguments pour x participants
* x sources pour x participants

A recouper avec les données opinions de la version de etalab
'''
def clean_text(text):
    return re.sub("\n|\t|\s\s", "", text.strip())
def define_propositions(liste):
    '''' listes articles proposés par le participant
    [
    {   
        "id": source-13094
        "source_link": #lien relatif à la source
        "source_title": #titre de la source
        "category": #type de source
        "texte": #description
        "votes": signalé comme pertinent
    },
    ]
    '''
    modifications = []
    for n in liste.find_all("li"):
        modification = {}
        modification["id"] = n.get("data-pie-id")
        modification["votes"] = {i:n.get(i) for i in ["data-mitige", "data-nok","data-ok"]}
        article = n.find_all("a")[-1]
        modification["article_link"] = unicode((article.get("href")).encode("utf-8"))
        modification["article_title"] = unicode(clean_text(article.text)).encode("utf-8")
        stats = n.find("p", {"class":"opinion__votes"})
        stats = [(n.getText()).split(" ") for n in stats.find_all("span") if n.get("class") is None]
        modification["stats"] = {v[1]: v[0] for v in stats}
        modifications.append(modification)
    return modifications
    
def define_sources(liste):
    '''' liste de sources pour un participant
    [
    {   
        "id": source-13094
        "source_link": #lien relatif à la source
        "source_title": #titre de la source
        "category": #type de source
        "texte": #description
        "votes": signalé comme pertinent
    },
    ]
    '''
    sources = []
    for n in liste.find_all("li"):
        source = {}
        source["id"] = unicode(n.get("id")).encode("utf-8")
        source["category"] = unicode(n.find("span", {"class": "label-info"}).text).encode("utf-8")
        source["source_title"] = unicode(n.find("a").text).encode("utf-8")
        source["source_link"] = unicode(n.find("a").get("href")).encode("utf-8")
        source["texte"] = unicode(clean_text(n.find("p",{"class": "excerpt"}).text)).encode("utf-8")
        source["votes"] = int(n.find("span",{"class":"nb-votes"}).text)
        sources.append(source)
    return sources
def define_votes(liste):
    '''' liste de votes pour un participant
    [
    {   
        "id": vote-13094
        "article_link": #lien relatif de l'article
        "article_title": #titre partiel de l'article
        "date": #format 'string' type %d %B %YYYY %H:%M
        "opinion": # -1 contre, 0 neutre, 1 pour
    },
    ]
    '''
    votes = []
    opinion = {"label-danger":-1,"label-warning": 0, "label-success": 1} 
    for n in liste.find_all("li"):
        vote = {}
        vote["id"] = n.get("id")
        article = n.find_all("a")[-1]
        vote["article_link"] = unicode((article.get("href")).encode("utf-8"))
        vote["article_title"] =unicode(clean_text(article.text)).encode("utf-8")
        vote["date"] = unicode((n.find("p", {"class":"opinion__date"}).text).encode("utf-8"))
        vote["opinion"] = unicode(opinion[n.find_all("span", {"class":"label"})[0].get("class")[-1]])
        votes.append(vote)
    return votes

def define_modifications(liste):
    ''' liste des modifications sur un article par participants
    appelées versions
    [{   
        "id:#id de version? ou id de l'article
        "article_link": # lein relatif à l'article
        "article_title": #titre partiel de l'article
        "stats": # -1 contre, 0 neutre, 1 pour
    },
    '''
    modifications = []
    for n in liste.find_all("li"):
        modification = {}
        modification["id"] = n.get("data-pie-id")
        modification["votes"] = {i:n.get(i) for i in ["data-mitige", "data-nok","data-ok"]}
        article = n.find_all("a")[-1]
        modification["article_link"] = unicode((article.get("href")).encode("utf-8"))
        modification["article_title"] = unicode(clean_text(article.text)).encode("utf-8")
        stats = n.find("p", {"class":"opinion__votes"})
        stats = [(n.getText()).split(" ") for n in stats.find_all("span") if n.get("class") is None]
        modification["stats"] = {v[1]: v[0] for v in stats}
        modifications.append(modification)
    return modifications
    
    
def define_arguments(liste):
    '''liste d'arguments pour un participant
    [
    {   
        "id": arg-1234
        "article_link": #
        "article_title": #titre partiel de l'article
        "texte"
        "date": #format 'string' type %d %B %YYYY %H:%M
        "vote": # -1 contre, 0 neutre, 1 pour
    },
    ]
    '''
    arguments = []
    for n in liste.find_all("li"):
        print n
        argument = {}
        argument["id"] = n.get("id")
        article = n.find_all("a")[-1]
        argument["article_link"] = unicode((article.get("href")).encode("utf-8"))
        argument["article_title"] =unicode(clean_text(article.text)).encode("utf-8")
        argument["date"] = unicode((n.find("p", {"class":"opinion__date"}).text).encode("utf-8"))
        argument["votes"]  = int(n.find("span",{"class":"opinion__votes-nb"}).text)
        arguments.append(argument)
    return arguments

def get_stats(tree):
    '''
    {
        u'modifications': 8, 
        u'votes': 2205, 
        u'sources': 68, 
        u'arguments': 97, 
        u'projets': 0, 
        u'propositions': 2, 
        u'commentaires': 0, 
        u'contributions': 175, #correspondent à toutes les actions sauf les votes
        u'projets participatifs': 0
    }
    '''
    profile_stats = tree.find("div",{"class":"profile__values"})
    stats_title = [clean_text(n.text).lower() for n in profile_stats.find_all("h2")]
    stats_values = [clean_text(n.text) for n in profile_stats.find_all("p")]
    user_stats = {k:int(v) for k,v in zip(stats_title, stats_values) if k not in ['projets participatifs', 'commentaires', 'projets']}
    return user_stats


    
def get_part(profile):
    '''détails des votes sur un article "votes"'''
    BASE_URL = "https://www.republique-numerique.fr"+profile
    user = None
    
    r = requests.get(BASE_URL)
    if r.status_code == 200:
        tree = BeautifulSoup(r.text)
        stats = get_stats(tree)
        user = {}
        for k, v in stats.items():
            if k == "contributions":
                user[k] = {"total": v}
            else:
                user[k] = {"nb": v}
            
        
        doc_index = ["propositions", "modifications","arguments", "sources", "projects", "commentaires", "votes"]
        html_struct = tree.find_all("div", {"class":"container--custom"})[1:]
        
        doc = {k:v for k,v in zip(doc_index, html_struct) if k in stats.keys()}
        
        if stats["contributions"] == 0:
            user["votes"]["votes"] = define_votes(doc["votes"])
            return user
        else:
            for k, v in doc.items():
                if stats[k] != 0:
                    func =  "define_"+k
                    user[k][k] = getattr(sys.modules[__name__], "define_%s" % k)(v)
                 
            print user
            return user
        
        
def store2mongodb(user):
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client['republique-numerique']
    users = db['users']
    return users.insert(user)

def readcsv(fname):
    with open(fname,'r') as f:
        reader = csv.reader(f, delimiter='\t')
        return [row for row in reader][1:]
def define_user():
    pass
def get_participations():
    #pour chaque utilisateur issu du CSV
    for row in readcsv("./data/participants.csv"):
        profile, name, nb_votes, nb_contributions = row
        if nb_contributions != "0":
            userid = re.sub("/profile/", "", profile)
            
            with open("./data/users/"+userid+".json", "w") as f:
                data = {userid:get_part(profile)}
                f.write(json.dumps(data, sort_keys=True, indent=4))
            
        else:
            continue
        
def get_one_participations(profile = "/profile/gouvernement"):
    userid = re.sub("/profile/", "", profile)    
    with open("./data/users/"+userid+".json", "w") as f:
        data = {userid:get_part(profile)}
        f.write(json.dumps(data, sort_keys=True, indent=4))

    
if __name__=="__main__":
    
    get_participations(profile = "/profile/gouvernement")
    #get_gouv_participations()
