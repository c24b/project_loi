#/usr/bin/python2.7 env
#coding: utf-8
#from pattern.fr import ngrams
import re
from pattern.fr import sentiment
import json, csv
from pprint import pprint
from pattern.vector import stem, PORTER, LEMMA, count
import unicodedata
from collections import Counter, OrderedDict, defaultdict

import string
from unidecode import unidecode
words = []

    
def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def clean_body(words):
    clean_words = []
    for n in words:
        n8 = unidecode(unicode(n, "utf-8"))
        nA = n8.encode("ascii")
        #print(n)
        clean_words.append(strip_accents(u"%s" %nA))
    return clean_words

def top_words(words_list):
    return Counter(words_list)
       
i = 0
articles = defaultdict(list)
#import pdb; pdb.set_trace()
mood = {}
for row in csv.reader(open("/home/c24b/projets/loinumerique/df_datacamp_plain.csv", 'r')):
    
    id, body, vote_counts, author, dtype, article, created_at, url_auteur, url_arg = row
    
    if i == 0:
        header = row
        
    else:
        
        for c in string.punctuation:
            body = body.replace(c,' ')
        for c in string.whitespace:
            body = body.replace(c,' ')
        for c in ["'"]:
            body = body.replace(c,' ')
        words = clean_body([n.lower() for n in body.split(" ")])
        comment = " ".join(words)
        
        polarity, subjectivity = sentiment(comment)
        vote = (polarity+subjectivity)
        subjectivity = subjectivity+1.0000001
        polarity = polarity*subjectivity
        
        try:
            mood[polarity].append(row)
        except:
            mood[polarity] = [row]
        #.append(comment)
        
        #print  polarity,"\t\t", comment[:50],"\t\t", len(comment[:50]),"\t\t"
        #print stem(s, stemmer=PORTER)
        words.extend(words)

    i =+ 1


#flop10 = sorted(mood.items())[:10]
#top10 = sorted(mood.items())[::-10]

#~ j = json.loads(mood)
#~ 
#~ open("results.json", "w").write(json.dumps(j))

for k,v in mood.items():
    #print str(k)+";"+";".join(v[0])
    print ("%s;%s"%(";".join(v[0]), k))

    # (";").join(v)
    
        

    

#~ 
# with open('./data-utf8.json') as f:    
#~ data  = json.loads(open('./data4.py', "r").read())
#~ 
#~ 
#~ 
#~ i = 0
#~ for id,v in data.items():
    #~ # for k, b in v.items():
    #~ for n in v["opinion"]["arguments"]:
        #~ comment = (n["body"]).encode("utf-8")
        #~ comment = re.sub('[^\w|^\s]', "", comment)
        #~ s = Sentence(parse(comment))
        #~ print stem(s, stemmer=PORTER)
        #~ print count(s, stemmer=LEMMA)
        #~ print count(s, stemmer=PORTER)
        #~ #print(s parse(lemmata=True) .)
    #~ i += 1
    #~ if i == 10:
        #~ break

