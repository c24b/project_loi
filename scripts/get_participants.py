# coding: utf-8
from bs4 import BeautifulSoup
import requests
import re
import io, json, csv
import time, datetime
def clean_text(text):
    return re.sub("\n|\t|\s\s", "", text.strip())

def get_all_participants(fname):
    #participants = []
    with open(fname, 'w') as f:
        writer = csv.writer(f, delimiter="\t")
        fieldnames = ["userpage", "username", "votes_nb", "contributions_nb"]
        writer.writerow(fieldnames)
        for x in range(1,1335):
            URL = "https://www.republique-numerique.fr/projects/projet-de-loi-numerique/participants/"+str(x)
            r = requests.get(URL)
            tree = BeautifulSoup(r.text)
            for n in tree.find_all("div",{"class":"media-body"}):
                user_link = n.find("a").get("href")
                user_name = n.find("a").text
                try:
                    stats = re.sub("\n|\t|\r", "", n.find("span",{"class":"excerpt"}).text).encode("utf-8")
                    stats = re.sub("\s\s\s", "", stats).strip().split(" ")
                    contributions,votes= stats[0], stats[4]
                    
                except AttributeError:
                    votes, contributions = 0, 0
                writer.writerow([user_link.encode("utf-8"), user_name.encode("utf-8"), str(votes), str(contributions)])
                #participants.append({"link":user_link, "username":user_name, "votes":votes, "contributions":contributions})
    return

def get_propositions_details(profile="/profile/constancedequatrebarbes"):
    '''détails des propositions i.e nouveaux articles "opinions"'''
    profile_url = "https://www.republique-numerique.fr"+profile+"/opinions"
    r = requests.get(profile_url)
    tree = BeautifulSoup(r.text)
    votes = []
    votes_list = tree.find("ul", {"class":"media-list"})
    for n in votes_list.find_all("div",{"class":"opinion__data"}):
        vote = {}
        article = n.find_all("a")[-1]
        
        vote["article_link"] = unicode((article.get("href")).encode("utf-8"))
        vote["article_title"] = unicode((clean_text(article.text)).encode("utf-8"))
        stats = n.find("p", {"class":"opinion__votes"})
        stats = [(n.getText()).split(" ") for n in stats.find_all("span") if n.get("class") is None]
        vote["stats"] = {v[1]: v[0] for v in stats}
    
        
        votes.append(vote)
    return votes

def get_modifications_details(profile="/profile/constancedequatrebarbes"):
    '''détails des modifications i.e changement dans le texte de loi "versions"'''
    profile_url = "https://www.republique-numerique.fr"+profile+"/versions"
    r = requests.get(profile_url)
    tree = BeautifulSoup(r.text)
    votes = []
    votes_list = tree.find("ul", {"class":"media-list"})
    for n in votes_list.find_all("div",{"class":"opinion__data"}):
        vote = {}
        article = n.find_all("a")[-1]
        
        vote["article_link"] = unicode((article.get("href")).encode("utf-8"))
        vote["article_title"] = unicode(clean_text((article.text).encode("utf-8")))
        stats = n.find("p", {"class":"opinion__votes"})
        stats = [(n.getText()).split(" ") for n in stats.find_all("span") if n.get("class") is None]
        vote["stats"] = {v[1]: v[0] for v in stats}
    
        
        votes.append(vote)
    return votes
    
def get_votes_details(profile):
    '''détails des votes sur un article "votes"'''
    opinion = {"label-danger":-1,"label-warning": 0, "label-success": 1} 
    profile_url = "https://www.republique-numerique.fr"+profile+"/votes"
    r = requests.get(profile_url)
    tree = BeautifulSoup(r.text)
    votes_list = tree.find("ul", {"class":"media-list"})
    votes = []
    try:
        for n in votes_list.find_all("div",{"class":"opinion__data"}):
            vote = {}
            article = n.find_all("a")[-1]
            vote["article_link"] = unicode((article.get("href")).encode("utf-8"))
            vote["article_title"] = unicode((clean_text(article.text)).encode("utf-8"))
            vote["date"] = unicode((n.find("p", {"class":"opinion__date"}).text).encode("utf-8"))
            vote["vote"] = unicode(opinion[n.find_all("span", {"class":"label"})[0].get("class")[-1]])
            votes.append(vote)
    except:
        #de temps en temps le chargement est trop rapide et il ne trouve pas la classe opinion__data
        #on recharge donc 1 seule fois
        #dans ce cas si l'erreur persite pour pour gérer les erreurs renvoie une liste vide
        #attention ici le profil du gouvernement n'est pas filtré alors même qu'il apparait à de multiples reprises
        r = requests.get(profile_url)
        tree = BeautifulSoup(r.text)
        votes_list = tree.find("ul", {"class":"media-list"})
        votes = []
        try:
            for n in votes_list.find_all("div",{"class":"opinion__data"}):
                vote = {}
                article = n.find_all("a")[-1]
                vote["article_link"] = unicode((article.get("href")).encode("utf-8"))
                vote["article_title"] = unicode((article.text).encode("utf-8"))
                vote["date"] = unicode((n.find("p", {"class":"opinion__date"}).text).encode("utf-8"))
                vote["vote"] = unicode(opinion[n.find_all("span", {"class":"label"})[0].get("class")[-1]])
                votes.append(vote)
        except:    
            pass
    return votes

def store2mongodb(user):
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client['republique-numerique']
    users = db['users']
    return users.insert(user)
    

def full_votes_x_participants(fin):
    with open(fin, 'r') as f:
        
        reader = csv.reader(f, delimiter="\t")
        users ={"users":[]}
        for i, row in enumerate(reader):
            profile, name, nb_votes, nb_contributions = row
            if i == 0:
                continue
            elif row[0] != "/profile/gouvernement":
                user = re.sub("/profile/", "", row[0])
                fout = os.path.join("./data", user+".json")
                with io.open(fout, 'w', encoding='utf-8') as fo:
                #store2mongodb({"user":user.encode("utf-8"), "votes": votes})                
                    u = { user.encode("utf-8"):
                            {"user_info":  
                                {"userid": unicode(user.encode("utf-8")), 
                                "username":unicode(name.encode("utf-8")), 
                                "user_link": unicode(("https://www.republique-numerique.fr"+profile).encode("utf-8"))
                                },
                            "user_votes":
                                {"votes": get_votes_details(row[0]), 
                                "contribution": get_contrib_details(row[0]), 
                                "nb_votes":int(nb_votes), 
                                "nb_contributions":int(nb_contributions)
                                }
                            }
                        }
                    print u
                    fo.write(unicode(json.dumps(u,sort_keys=True,indent=4, ensure_ascii=False)))
                
            else:
                continue
            
            
    return users["users"]
    
if __name__=="__main__":
    # ecrire le fichier de participants (CSV)
    #~ write2csv(data, "/data/participants.csv")
    #ecrire le détails des votes par participants
    #full_votes_x_participants("./data/votesxparticipants2.json", "./data/participants.csv")
    print get_modifications_details("/profile/constancedequatrebarbes")
    
