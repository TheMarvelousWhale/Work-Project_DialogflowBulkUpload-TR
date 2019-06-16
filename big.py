# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 21:54:29 2019

@author: hoang
"""

'''
This is the most ambitious code so far

Dependencies:
parent.json - template for parent json
child.json - template for child json 
usersays_en.json - template for training phrases json
The agent folder - specified as source
Its dependency dest
The QnVarTemplate excel for different variation in training phrase for parent. We use 00 as placeholder for the Tutorial Room number
The main file with 4 columns - qn, ns,lhs, lhn in that order. Within each column the info must follow the same format.

There is something I would like to talk about the parent.json and child.json
We need to assign a random ID to the parent json and then this ID gonna be used to the parentID and rootParentID of the child json
parent and child json both has webhooks enabled
child json has the entities @NTU_location annotated
Format wise, parent json has 2 custom payload, one with a link and one with 2 buttons

'''
####################################################################################
import re,json,uuid,shutil 
import pandas as pd
from copy import deepcopy
from pprint import pprint #debug purpose and print json in a readable manner
###################################################################################
def createID():
    """
    To create a random ID for parent. Use ID to link later on for children json
    """
    temp = uuid.uuid4().hex
    return temp[0:8] +'-'+temp[8:12] +'-'+temp[12:16]+'-'+temp[16:20]+'-'+temp[20:]
####################################################################################
    '''
    Copy the json template into a python dictionary template
    '''
with open(r'parent.json') as f:
    parent_template_question = json.loads(f.read())

with open(r'child.json') as f:
    child_template_question = json.loads(f.read())
    
with open(r'usersays_en_v2.json') as f:
    payload_template = json.loads(f.read())
    
with open(r'usersays_en_v1.json') as f:
    simplepayload_template = json.loads(f.read())

source = './Lyon_template/'
dest = './Lyon_template - Copy/'

shutil.copytree(source,dest) #make a copy of the template folder
####################################################################################
    
#Global Variables
qnVarTemp = pd.read_excel("QnVarTemplate.xlsx")    
main = pd.read_excel("TRTR.xlsx")



def create_parent(msg,url,TRnum):
    '''
    create a copy the json (actually is a python dict) from the boilerplate
    return the json for writing into a file later on
    
    '''
    n = TRnum #use n for shorter typing
    pq_copy=deepcopy(parent_template_question) #make a copy
    pq_copy["id"] = createID() #assign random ID
    pq_copy["name"] = f'Freshmen.Facts.Lifestyle.Location.TR-{TRnum}' #IntentName
    context = re.sub('\.','',pq_copy["name"]) #Remove the full stops from name to form a context
    pq_copy["responses"][0]["affectedContexts"][0]["name"] = f'{context}-followup' #set in output context
    pq_copy["responses"][0]["messages"][0]["payload"]["message"] = f'TR+{TRnum} is at {msg}' 
    #link for the link button
    pq_copy["responses"][0]["messages"][0]["payload"]["metadata"]["payload"][0]["url"] = url 
    #text on the link button for the first payload
    pq_copy["responses"][0]["messages"][0]["payload"]["metadata"]["payload"][0]["name"] = f'Direction to TR+{TRnum}'
    #message to the second payload
    pq_copy["responses"][0]["messages"][1]["payload"]["message"] = f'Alternatively TR+{n} can also mean LHS-TR+{n} (the Hive) or LHN-TR+{n} (the Arc). Click on the respective buttons to know more about the location'
    #text button on the first button of the second payload
    pq_copy["responses"][0]["messages"][1]["payload"]["metadata"]["payload"][0]["title"] = f'LHS-TR+{TRnum}'
    pq_copy["responses"][0]["messages"][1]["payload"]["metadata"]["payload"][0]["message"] = f'I would like to know about the location of LHS-TR+{TRnum}'
    pq_copy["responses"][0]["messages"][1]["payload"]["metadata"]["payload"][1]["title"] = f'LHN-TR+{TRnum}'
    pq_copy["responses"][0]["messages"][1]["payload"]["metadata"]["payload"][1]["message"] = f'I would like to know about the location of LHN-TR+{TRnum}'
    return pq_copy 

def create_parent_trainphrases(TRnum):
    load = deepcopy(payload_template)
    for i in range(len(load)):
        try:
            #this is the annotated one
            t = load[i]['data'][1]['text']
            n = re.sub('00',str(TRnum),t)
            load[i]['data'][1]['text'] = n
        except:
            #this is the not annotated one
            t = load[i]["data"][0]["text"]
            n = re.sub('00',str(TRnum),t)
            load[i]['data'][0]['text'] = n
    return load


def create_child(childnum,TRnum,parent,msg,url): #childnum is LHS or LHN
    cq = deepcopy(child_template_question)
    cq["parentId"] = parent["id"]
    cq["rootParentId"] = parent["id"]
    cq["name"] = f'Freshmen.Facts.Lifestyle.Location.TR-{TRnum}-{childnum}-TR+{TRnum}'
    cq["contexts"][0] =  parent["responses"][0]["affectedContexts"][0]["name"]
    cq["responses"][0]["messages"][0]["payload"]["message"] = f'TR+{TRnum} is at {msg}'
    cq["responses"][0]["messages"][0]["payload"]["metadata"]["payload"][0]["url"] = url
    cq["responses"][0]["messages"][0]["payload"]["metadata"]["payload"][0]["name"] = f'Direction to {childnum}-TR+{TRnum}'
    cq["events"][0]["name"] = f'{childnum}TR{TRnum}'
    return cq

def create_child_trainphrases(childnum,TRnum,parent):
    temp = deepcopy(simplepayload_template)
    i = 0
    if childnum == "LHN":
        i = 1
    temp[0]['data'][0]['text'] = parent["responses"][0]["messages"][1]["payload"]["metadata"]["payload"][i]["message"]
    return temp


##############################################################################################

#murl = f'http://maps.ntu.edu.sg/m?q=tutorial%20room%20%2B%20{TRnum}&fs=m'
#lhsurl = f'http://maps.ntu.edu.sg/m?q=tutorial%20room%20%2B%20{TRnum}%20-%20lhn&fs=m'
#lhnurl = f'http://maps.ntu.edu.sg/m?q=tutorial%20room%20%2B%20{TRnum}%20-%20lhs&fs=m'

p0 = r'(.*) is located at (.*).You may want to do a search at (.*) to locate the respective tutorial rooms'
#p1 = r'(.*) is located at (.*).You may want to do a search at (.*) locate the respective tutorial rooms'

 
for rownum in range(len(main.index)):
    '''
    The general idea is loop through each row of the excel
    for the first col value, extract the TR number
    for the second col value, extract the info , clean if it needs to , then pass into the function for parent
    for the third col value, do the same, pass into function to create LHS
    for the fourth, same same for LHN
    p - parent, p_u - parent's usersays
    c1 - child one LHS
    c2 - child two LHN
    '''
    row = main.iloc[rownum,:] #take one row one
    TRnum = re.findall('\d+',row[0])[0] #find the TR number
    ns = re.findall(p0,row[1])[0] #use re to extract all the thing all
    p = create_parent(ns[1],ns[2],TRnum) #pass the info to the functionc
    p_u = create_parent_trainphrases(TRnum)
    lhsStr = row[2] #Clean up the string
    newlhsStr = re.sub('\u200b','',lhsStr)
    lhs = re.findall(p0,newlhsStr)[0]
    c1 = create_child("LHS",TRnum,p,lhs[1],lhs[2])
    c1_u = create_child_trainphrases("LHS",TRnum,p)
    lhnStr = row[3]
    newlhnStr = re.sub('\u200b','',lhnStr)
    lhn = re.findall(p0,newlhnStr)[0]
    c2 = create_child("LHN",TRnum,p,lhn[1],lhn[2])
    c2_u = create_child_trainphrases("LHN",TRnum,p)
    print(rownum)
    
    #write the new json into the intent folder of the copy of the template folder
    with open(f'{dest}intents/TR{TRnum}_parent.json','w') as f:
                f.write(json.dumps(p))
    with open(f'{dest}intents/TR{TRnum}_parent_usersays_en.json','w') as f:
                f.write(json.dumps(p_u))
    with open(f'{dest}intents/TR{TRnum}_LHS.json','w') as f:
                f.write(json.dumps(c1))
    with open(f'{dest}intents/TR{TRnum}_LHS_usersays_en.json','w') as f:
                f.write(json.dumps(c1_u))
    with open(f'{dest}intents/TR{TRnum}_LHN.json','w') as f:
                f.write(json.dumps(c2))
    with open(f'{dest}intents/TR{TRnum}_LHN_usersays_en.json','w') as f:
                f.write(json.dumps(c2_u))
    
    

#ZIP AND GO
shutil.make_archive("New Intents", 'zip', dest)
shutil.rmtree(dest)    
    
    
    
    
    
    
    
    
    
    
    
