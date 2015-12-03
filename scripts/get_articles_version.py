# coding: utf-8
import os
import json, csv
import re
from collections import defaultdict
import requests
from bs4 import BeautifulSoup as bs

def get_articles():
    votes = []
    with open("./full_participants.json") as f:
        data = json.load(f)
        for k in  data.values():
            for user in k:
                for n in  user.values():
                    proposition = n["propositions"]
                    #print proposition
                    if proposition["nb"] != 0:
                        for n in proposition["propositions"]:
                            votes.append([n["id"],n["article_link"]])
    return votes
def find_votants():
    votes = []
    with open("./full_participants.json") as f:
        data = json.load(f)
        for k in  data.values():
            for user in k:
                for n in  user.values():
                    proposition = n["votes"]
                    #print proposition
                    if proposition["nb"] != 0:
                        for n in proposition["propositions"]:
                            votes.append([n["id"],n["article_link"]])
    return votes
    
def extract_articles():
    '''ecrire le détail de chaque article donnés par l'API'''
    votes = get_articles()
    OPINION_URL = "https://www.republique-numerique.fr/api/opinions/"
    with open("./proposition.csv", "r") as f:
        writer = csv.DictReader(f, delimiter="\t")
        for n in sorted(votes):
            url = OPINION_URL+n[0]
            r = requests.get(url)
            
            if r.status_code == 200:
            #~ 
                #~ r = requests.get(url)
                data = r.json()
                with open("./data/articles/"+n[0]+".json", "w") as f:
                    f.write(unicode(json.dumps(data, sort_keys=True, indent=4)))
            else:
                print n[0]
                
def define_articles_list():
    '''definir chaque article avec son id et son auteur, son texte, sa section, etc...'''
    import os
    articles = []
    article_path = "./data/articles/"
    for f in os.listdir(article_path):
        file_path = os.path.join(article_path, f)
        with open(file_path, "r") as fi:
            #print file_path
            article = {}
            
            data = json.load(fi)
            
            #print  data["opinion"].keys()
            art = data["opinion"]
            article["author"] = art["author"]["uniqueId"]
            #del art["votes"]
            #print art.keys()
            #[u'updated_at', u'connections', u'sources', u'arguments_count', u'versions_count', u'connections_count', u'votes_total', u'id', u'author', u'has_user_reported', u'_links', u'arguments', u'answer', u'type', u'body', u'ranking', u'user_vote', u'sources_count', u'votes_ok', u'step', u'link', u'appendices', u'is_trashed', u'isContribuable', u'created_at', u'title', u'modals', u'votes_mitige', u'arguments_yes_count', u'arguments_no_count', u'votes_nok']
            
            
            
            try:
                article["explication"] = bs(art["appendices"][0]["body"]).text
            except:
                article["explication"] = None
            article["created_at"] = art["created_at"]
            article["updated_at"] = art["updated_at"]
            article["text"] = bs(art["body"]).text
            article["title"] = bs(art["title"]).text
            article["id"] = art["id"]
            article["url"] =  art["_links"]["show"]
            article["chapitre"] = art["_links"]["type"].split("/")[-1]
            article["section_nb"] = art["type"]["title"]
            article["section_title"] = art["type"]["subtitle"]
            article['votes_total'] = art['votes_total']
            article["versions_count"] = art["versions_count"]
            article["sources_count"] = art["sources_count"] 
            if article["sources_count"] > 0:
                article["sources"] = []
                for n in art["sources"]:
                    s = {"author": n["author"]["uniqueId"],"text":bs(n["body"]).text, "title":bs(n["title"]).text, "source_link": n["_links"]["edit"]}
                    for k,v in n.items(): 
                        if k in ["category", "created_at", "updated_at", "id", "link", "votes_count"]:
                            s[k] = v
                    article["sources"].append(s)
            else:
                article["sources"] = []
            article["arguments_count"] = art["arguments_count"]
            if article["arguments_count"] > 0:
                article["arguments"] = []
                for n in art["arguments"]:
                    s = {"author": n["author"]["uniqueId"],"text":bs(n["body"]).text, "argument_link": n["_links"]["show"]}
                    for k,v in n.items(): 
                        if k in ["category", "created_at", "updated_at", "id", "type","votes_count"]:
                            s[k] = v
                    article["arguments"].append(s)
            else:
                article["arguments"] = []
            article["step"] = art["step"]
            articles.append(article)
    with open('./data/full_articles.json', 'w') as f:
        f.write(unicode(json.dumps({"articles":articles}, indent=4, sort_keys=True)))

def article_details():
    with open('./data/full_articles.json', 'r') as f:
        a = json.load(f)
        for article in a["articles"]:
            
            uid = article["url"]
            article_id = article["id"]
            
            #print article.keys()
            if article["votes_total"] > 0:
                article["votes"] = []
                #par participants
                with open('./data/full_participants.json', 'r') as f:
                    u = json.load(f)
                    for user in u["participants"]:
                        username = user.keys()[0]
                        
                        
                        if user[username]["votes"]["nb"] > 0:
                            
                            
                            user_votes = user[username]["votes"]["votes"]
                            for vote in user_votes:
                                candidate_url = "http://www.republique-numerique.fr"+vote["article_link"]
                            
                                if uid == candidate_url:
                                    vote = {"user":username, "date":vote["date"], "opinion":vote["opinion"], "id":vote["id"]}
                                    article["votes"].append(vote)
                            
                                #print +n["article_link"], n["article_id"]
                        
                    #~ #[u'modifications', u'votes', u'sources', u'arguments', u'propositions', u'contributions']
                    #~ for n in user.values():
                        #~ #print n.keys()
                        #~ 
                        #~ if n["votes"]["nb"] > 0:
            else:
                article["votes"] = []
                
            with open("./data/articles_view/"+str(article_id)+".json", 'w') as f:
                f.write(unicode(json.dumps(article, indent=4)))

#article_details()                
def get_versions():
    
    import os
    articles = []
    article_path = "./data/articles_view/"
    
    for f in os.listdir(article_path):
        file_path = os.path.join(article_path, f)
        version_path = os.path.join("./data/history/", f)
        print version_path
        with open(file_path, "r") as fi:
            #print file_path
            article = {}
            data = json.load(fi)
            
            versions_url = "https://www.republique-numerique.fr/api/opinions/%s/versions" %(str(data["id"]))
            #posibilité de récuperer le détail de chaque version jusqu'à 1410
            r = requests.get(versions_url)
            v = r.json()
            
            versions = []
            
            data["version_count"] = len(v["versions"])
            data["versions"] = []
            if data["version_count"] == 0:
                continue
            else:
                #print version_count
                
                for n in v["versions"]:
                    history = {}
                    for k, v in n.items():
                        if k in ["created_at","updated_at", u'votes_ok', u'votes_mitige', u'arguments_yes_count', u'arguments_count', u'votes_total', u'arguments_no_count', 'votes_nok']:
                           history[k] = v
                    data["versions"].append(history)
            
            with open(version_path, "w") as fo:
                fo.write(unicode(json.dumps(data, indent=4)))
    

def get_history(data):
    data["history"] = []
    
    #~ if len(data["versions"]) > 0:        
    print data["id"],len(data["versions"])
    
    for vid in range(2, 1411):
        version_url = "https://www.republique-numerique.fr/api/opinions/%s/versions/%s" %(str(data["id"]), str(vid))
        r = requests.get(version_url)
        #print r
        if r.status_code == 200:
            v = r.json()["version"]
            data["history"].append(v)
        
    data["history_count"] = len(data["history"])
    print data["history_count"]
    return data
                #~ print v["body"], 
                #~ print "*****"
                #~ print v["parent"]["body"]
                
def get_versions():
    article_path = "./full_articles.json"
    v_path = "./data/full_versions/"
    with open(article_path, "r") as fi:
        data = json.load(fi)["articles"]
        for article in data:
            data2 = get_history(article)
            file_out = str(article["id"])+".json"
            version_path = os.path.join(v_path, file_out)
            with open(version_path, "w") as fo:
                fo.write(unicode(json.dumps(data2, indent=4)))
            
get_versions()
