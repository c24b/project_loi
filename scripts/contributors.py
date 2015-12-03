import io
import json
import re
from bs4 import BeautifulSoup
from os import listdir
from os.path import join

def define_user(user):
    
    #[u'username', u'displayName', u'media', u'vip', u'isAdmin', u'_links', u'uniqueId']
    return {'username': user["username"], "user_displayName": user["displayName"], "user_id": user["uniqueId"], "user_profile": user['_links']["profile"]}

def read_json_file(fname="read_example.json"):
    '''methode simple pour lire un fichier json en python'''
    with open(fname, 'r') as f:
        return json.load(f)

def write2json(data, fname = "write_example.json"):
    '''methode simple pour ecrire un fichier json en python'''
    with io.open(fname, 'w', encoding='utf-8') as f:
        f.write(unicode(json.dumps(data, ensure_ascii=False)))
        
def understand():
    
def extract_votes():
    mypath = "./opinions-republique-numerique/"
    data_f = []
    for n in listdir(mypath):
        if n != ".git":
            mp2 = join(mypath,n)
            fullpath = join(mp2,"opinion.json")
            data = read_json_file(fullpath)
            row = {}
            
            #titre de l'article
            row["titre"] = BeautifulSoup(data["opinion"]["title"]).get_text()
            row["texte"] = re.sub("\n|\r|\t", "", BeautifulSoup(data["opinion"]["body"]).getText())
            row["nb_votes"], row["votes_pour"], row["votes_contre"], row["votes_neutre"] =  data["opinion"]["votes_total"], data["opinion"]['votes_ok'],data["opinion"]["votes_nok"], data["opinion"]['votes_mitige']
            row["argument_users"] = [define_user(n["user"]) for n in data["opinion"]["votes"]]
            row["nb_users"] = len(row["argument_users"])
            row["author"] = define_user(data["opinion"]["author"])
            row["date"] = data["opinion"]['updated_at']
            row["arguments_nb"],row["arguments_pour"], row["arguments_contre"] = data["opinion"]["arguments_count"], data["opinion"]['arguments_yes_count'], data["opinion"]['arguments_no_count']
            data_f.append(row)
    return data_f
    
def json2csv(data):
    '''convert for csv'''
    for row in data:
        for k, v in row.items():
            if k.startswith("arguments") or k.startswith("votes"):
                row[k] = str(v).encode("utf-8")
            elif k == "argument_users":
                row[k] = ("***".join([v1["user_id"] for v1 in v])).encode("utf-8")
                #row[k] = v["user_id"].encode("utf-8")
            elif k == "author":
                row[k] = str(v["user_id"]).encode("utf-8")
            elif v is None:
                row[k] = "".encode("utf-8")
            elif type(v) == int:
                try:
                    row[k] = str(row[k]).encode("utf-8")
                except:
                    print k
            else:
                try:
                    row[k] = row[k].encode("utf-8")
                except:
                    print k
    return data

def write2csv(data, fname="./data/votes.csv"):
    import io, csv
    fieldnames = [n.encode("utf-8") for n in data[1].keys()]
    
    with open(fname, 'w') as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(fieldnames)
        for row in data:
            writer.writerow(row.values())
            
if __name__ == "__main__":
    data_f = extract_votes()
    #write2json(data_f, "./data/votes.json")
    data = json2csv(data_f)
    write2csv(data_f)


    
