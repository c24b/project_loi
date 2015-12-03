import requests
from bs4 import BeautifulSoup
import re

def clean_text(data):
    return re.sub('\n|\r|\t|\s\s', "", data.strip())

def describe_section(data):
    try:
        return clean_text(data.contents[0].string), clean_text(re.sub(":", "", data.contents[1].string))
    except IndexError:
        return clean_text(data.contents[0].string), None
    
def dsc_sections(data):
    ref = [n.strong.getText() for n in data if n.strong is not None] 
    subt = [(n.getText()).split(":")[-1] for n in data if n.strong is not None]
    return [{"reference":x, "soustitre": y}  for x,y in zip(ref,subt)]


def extract(url="https://www.republique-numerique.fr/pages/projet-de-loi-pour-une-republique-numerique"):
    r = requests.get("https://www.republique-numerique.fr/pages/projet-de-loi-pour-une-republique-numerique")
    proposition = {}
    if r.status_code == 200:
        #structure
        soup = BeautifulSoup(r.text)
        #~ proposition["titres"] = dsc_sections(soup.find_all("h1"))
        #~ proposition["chapitres"] = dsc_sections(soup.find_all("h2"))
        #~ proposition["sections"] = dsc_sections(soup.find_all("h3"))
        #~ proposition["articles"] = dsc_sections(soup.find_all("h4"))
        
        articles =[]
        jsondata = {}
        
        art_nb = 1                
        for h in soup.find_all("h4"):
            if h.strong is not None:
            
                article = clean_text(" ".join([n.getText() for n in h.next_siblings if n.name == "p"]))
                art = clean_text(h.strong.text), clean_text(h.contents[2].string)
                
                #print h.text
                
                sect = [describe_section(n) for n in h.previous_siblings if n.name == "h3"][0]
                chap = [describe_section(n) for n in h.previous_siblings if n.name == "h2"][0]
                titr = [describe_section(n) for n in h.previous_siblings if n.name == "h1"][0]
                
                
                    
                jsondata[art_nb] = {"article_nb":art[0], 
                                    "article_subtitle": art[1], 
                                    "titre_nb":titr[0], 
                                    "titre_subtitle": titr[1],
                                    "chapter_nb":chap[0], 
                                    "chapter_subtitle": chap[1], 
                                    "section_nb":sect[0], 
                                    "section_subtitle": sect[1],
                                    "article_text": article}
                art_nb = art_nb+ 1
        return jsondata
def write2json(data, fname = "proposition.json"):
    import io, json
    with io.open(fname, 'w', encoding='utf-8') as f:
        f.write(unicode(json.dumps(proposition, ensure_ascii=False)))

def write2csv(data, fname="proposition.csv"):
    import io, csv
    fieldnames = [n.encode("utf-8") for n in data[1].keys()]
    
    with open(fname, 'w') as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(fieldnames)
        for row in data.values():
            
            row = [n.encode("utf-8") if n is not None else "None" for n in row.values()]
            writer.writerow(row)
        
if __name__ == "__main__":
    proposition = extract()
    #write2csv(proposition)
    #write2json(proposition)
    
