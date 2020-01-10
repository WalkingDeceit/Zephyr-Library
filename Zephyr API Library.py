# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 11:08:40 2019

@author: Abhishek Nikkudala
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 15:45:14 2019

"""

import urllib2
import ast
import base64
import datetime
import json
import pandas as pd
from urllib2 import Request, urlopen
import webbrowser
import time
import os

class Error(Exception):
    pass

class InvalidTestCase(Error):
    pass

now = datetime.datetime.now()

hostname = None
headers = None
cookie = None

def cook():
      request = Request('https://'+hostname+'/flex/services/rest/v3/user/current',headers = headers)
   #print request.get_header('Authorization')
      response_body = urlopen(request)
      global cookie
      cookie = response_body.headers.get('Set-Cookie')

def authorization(username,password):

   base64string = base64.b64encode('%s:%s' % (username,password))
   global headers
   headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic '+base64string
        }


##_________________ASSIGN FUNCTIONS____________________##

def assign_testcase_to_phase(treeid,tctId,phaseid,tcrphaseid):
    values = json.dumps([{
    "treeid":treeid,
    "tctIds":[tctId],
    "isExclusion": True
    }])
    #check_server_status()                
    request = Request('https://'+hostname+'/flex/services/rest/v3/assignmenttree/'+str(phaseid)+'/assign/bytree/'+str(tcrphaseid)+'?includehierarchy=false', data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    #response_body = urlopen(request).read()
    urlopen(request).read()
    print '---------PHASE ASSIGN----------------'
    #print response_body
        
def assign_testcases_to_current_user(phaseId):
    #print phaseId
    values = """{}"""
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/assignmenttree/'+str(phaseId)+'/assign', data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    #response_body = urlopen(request).read()
    urlopen(request).read()
    print '---------USER ASSIGN----------------'
    #print response_body

def assign_testcases_to_anyone(tctId,phaseId):
    #check_server_status()
    values = json.dumps({'createRTSList': [{'tctId': tctId, 'testerId': -10, 'cyclePhaseId': phaseId}]})
    request = Request('https://'+hostname+'/flex/services/rest/v3/execution/modify', data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    #response_body = urlopen(request).read()
    urlopen(request).read()
    #print response_body
    print '---------USER ASSIGN--------------'
        

##__________ CHECK FUNCTIONS ______________##
def check_cycle(name,release_id):
    #print 'check_cycle'+name
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/cycle/all')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    #print response_body
    response_body= json.loads(response_body)
    for l in range(0,len(response_body)):
        data = response_body[l]
        if data['name']==name and data['releaseId']==release_id:
            return 1
    return 0

def check_node(name,release_id):
    #print 'check_node'+name
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcasetree')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    #print response_body
    response_body = json.loads(response_body)
    for l in range(0,len(response_body)):
        data = response_body[l]
        if data['name']==name and data['releaseId']==release_id:
            return 1    
    return 0
    
def check_phase(phaseName,releaseId):
    #print 'check_phase'+phaseName
    #check_server_status()
    response_body = get_cycles_for_release(releaseId)
    phase_list = []
    for i in range(0,len(response_body)):
        if response_body[i]['name'] == 'Zephyr Framework':
            for j in range(0,len(response_body[i]['cyclePhases'])):
                phase_list.append(response_body[i]['cyclePhases'][j]['id'])
    
    
    
    if len(phase_list) == 0:
        return False
    for i in range(0,len(phase_list)):
        #check_server_status()
        request = Request('https://'+hostname+'/flex/services/rest/v3/assignmenttree/'+str(phase_list[i]))
        request.add_header('cookie', cookie)
        request.add_header('Content-Type', 'application/json')
        response_body = urlopen(request).read()
        response_body = json.loads(response_body)
        if phaseName == response_body['name']:
            return True
    return False

def check_server_status():
    try:
       request = Request('https://'+hostname+'/flex/services/rest/v3/user/current',headers = headers)
       request.add_header('cookie',cookie)
       #response = urllib2.urlopen(req2).read()
       urlopen(request).read()
    except:
       url = 'https://'+hostname+'/flex/html5/login'
       webbrowser.open(url)
       time.sleep(10)
       browserExe = "iexplore.exe"
       os.system("taskkill /f /im "+browserExe)
       print 'Server refreshed at '+str(time.asctime())
       
def check_testcase(testcaseName, projectId):
    response_body = get_all_testcases_for_project(projectId)
    for item in range(0,len(response_body['results'])):
        if response_body['results'][item]['testcase']['name'] == testcaseName:
            return True
    return False
    

##_____________ CALCULATE ____________________ ##
def calculate_Assignments_For_Release(releaseId):
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/cycle/assignments/'+str(releaseId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    return response_body    

##_____________ CREATE ____________________ ##

#"data": get_data_teststep(SourceDB,SourceTable,TargetDB,TargetTable,SourceSystem,TargetSystem),
def create_count_teststep(testcase,SourceDB,SourceTable,TargetDB,TargetTable,SourceSystem,TargetSystem):
    values =json.dumps({
            "steps": [
                    {
                            "orderId" : 1,
                            "step": "step",
                            "data": str(get_teststep_data(SourceDB,SourceTable,TargetDB,TargetTable,SourceSystem,TargetSystem)),
                            "result":"result" 
                        }
                    ]
            })
    #check_server_status()
    URL='https://'+hostname+'/flex/services/rest/v3/testcase/'+str(testcase.phaseTctId)+'/teststep/'+str(testcase.tctId)+'/'+str(testcase.projectId)
    #URL='https://capgemini1111.zephyrdemo.com/flex/services/rest/latest/testcase/26/teststep/30/1'
    request = Request(URL,data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    #print '---------Test STEP----------------'
    #response_body = urlopen(request).read()
    urlopen(request).read()
    #print response_body

def create_teststep_new(testcase,values):
    URL='https://'+hostname+'/flex/services/rest/v3/testcase/'+str(testcase.phaseTctId)+'/teststep/'+str(testcase.tctId)+'/'+str(testcase.projectId)
    #check_server_status()
    #URL='https://capgemini1111.zephyrdemo.com/flex/services/rest/latest/testcase/26/teststep/30/1'
    request = Request(URL,data = values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    #print '---------Test STEP----------------'
    #response_body = urlopen(request).read()
    urlopen(request).read()
    #print response_body
    
def create_count_teststep_data(source,target,source_system,target_system):
    values =json.dumps({
            "steps": [
                    {
                            "orderId" : 1,
                            "step": "Source System",
                            "data": source_system,
                            "result":"Result" 
                        },
                        {
                            "orderId" : 2,
                            "step": "Source Table",
                            "data": source,  
                            "result":"Result" 
                        },    
                        {
                            "orderId" : 3,
                            "step": "Target System",
                            "data": target_system,
                            "result":"Result" 
                        },
                        {
                            "orderId" : 4,
                            "step": "Target Table",
                            "data": target,
                            "result":"Result" 
                        },
                        {
                            "orderId" : 5,
                            "step": "Count rows in Source and Target Tables",
                            "data": "Rows of "+source+"="+"Rows of "+target,
                            "result":"Same number of rows." 
                        }
                    ]
            })
    return values
    
def create_compare_teststep_data(src_sql,tgt_sql,source_system,target_system):
    values =json.dumps({
            "steps": [
                    {
                            "orderId" : 1,
                            "step": "Source system",
                            "data": source_system,
                            "result":"Result" 
                        },
                        {
                            "orderId" : 2,
                            "step": "Source Table",
                            "data": src_sql,  
                            "result":"Result" 
                        },    
                        {
                            "orderId" : 3,
                            "step": "Target system",
                            "data": target_system,
                            "result":"Result" 
                        },
                        {
                            "orderId" : 4,
                            "step": "Target Table",
                            "data": tgt_sql,
                            "result":"Result" 
                        },
                        {
                            "orderId" : 5,
                            "step": "Compare Source and Target Tables",
                            "data": "Rows of "+src_sql+"="+"Rows of "+tgt_sql,
                            "result":"Similar rows." 
                        }
                    ]
            })
    return values

def create_notnull_teststep_data(system,column,table):
    values =json.dumps({
            "steps": [
                    {
                            "orderId" : 1,
                            "step": "Source system",
                            "data": system,
                            "result":"Result" 
                        },
                        {
                            "orderId" : 2,
                            "step": "Source Table",
                            "data": table,  
                            "result":"Result" 
                        },
                        {
                            "orderId" : 3,
                            "step": "Column",
                            "data": column,  
                            "result":"Result" 
                        },
                        {
                            "orderId" : 4,
                            "step": "Check Not Null Rows",
                            "data": "Column to be checked : "+column,
                            "result":"Result" 
                        }
                    ]
            })
    return values

def create_duplicate_teststep_data(system,columnlist,table):
    values =json.dumps({
            "steps": [
                    {
                            "orderId" : 1,
                            "step": "Source Details",
                            "data": system,  
                            "result":"Result" 
                        },
                        {
                            "orderId" : 2,
                            "step": "Source Table",
                            "data": table,  
                            "result":"Result" 
                        },
                        {
                            "orderId" : 3,
                            "step": "Columnlist",
                            "data": columnlist,  
                            "result":"Result" 
                        },
                        {
                            "orderId" : 4,
                            "step": "Check duplicates",
                            "data": "Column list : "+columnlist,
                            "result":"Result" 
                        }
                    ]
            })
    return values
   
def create_cycle(releaseId):
    values = json.dumps({ 
                "name": "Zephyr Framework", 
                "cycleStartDate": str(now.month)+'/'+str(now.day)+'/'+str(now.year), 
                "cycleEndDate": "12/31/2019", 
                "status": 0, 
                "releaseId": releaseId
                })
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/cycle',data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    print '---------Test Cycle----------------'
    #print response_body
    return response_body['id']

def create_phase(cycleId,name):
    values =json.dumps({
    "phaseStartDate" : str(now.month)+'/'+str(now.day)+'/'+str(now.year),
    "phaseEndDate" : str(now.month)+'/'+str(now.day)+'/'+str(now.year),
    "freeForm" : True,
    "name" : name,
    "cycleId" : cycleId
    })
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/cycle/'+str(cycleId)+'/phase', data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    print '---------Test Phase----------------'
    #print response_body
    response_body = json.loads(response_body)
    return response_body['id'],response_body['tcrCatalogTreeId']

def create_node(name,releaseId):
    values = json.dumps({
        "name": name,
        "type": "Phase",
        "releaseId": releaseId
        })
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcasetree', data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    print '---------Test NODE----------------'
    #print response_body
    response_body= json.loads(response_body)
    return response_body['id']

def create_modules(parentId,releaseId):
    #check_server_status()
    values = json.dumps({"name": "Count", "description": "", "type": "Module", "releaseId": releaseId})
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcasetree?parentid='+str(parentId+1), data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    #response_body = urlopen(request).read()
    urlopen(request).read()
    #check_server_status()
    values = json.dumps({"name": "NotNULL", "description": "", "type": "Module", "releaseId": releaseId})
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcasetree?parentid='+str(parentId+2), data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    #response_body = urlopen(request).read()
    urlopen(request).read()
    #check_server_status()
    values = json.dumps({"name": "Compare", "description": "", "type": "Module", "releaseId": releaseId})
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcasetree?parentid='+str(parentId+3), data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    #response_body = urlopen(request).read()
    urlopen(request).read()
    #check_server_status()
    values = json.dumps({"name": "Duplicates", "description": "", "type": "Module", "releaseId": releaseId})
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcasetree?parentid='+str(parentId+4), data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    #response_body = urlopen(request).read()
    urlopen(request).read()
    #print response_body

def create_dictionary_of_dataframes(testCases):
    columns = ['execute','source_system','source','target_system','target','executionId','testerId']
    df1 = pd.DataFrame(columns = columns)
    columns = ['execute','system','table','columnlist','executionId','testerId']
    df2 = pd.DataFrame(columns = columns)
    columns = ['execute','system','table','column','executionId','testerId']
    df3 = pd.DataFrame(columns = columns)
    columns = ['execute','source_system','src_sql','target_system','tgt_sql','executionId','testerId']
    df4 = pd.DataFrame(columns = columns)
    data = {
            'CountModule' : df1,
            'DuplicateCheckModule' : df2,
            'NotnullModule' : df3,
            'CompareModule' : df4
    }
    for item in testCases:
       try:
           if item == 'CountModule':
              for i in range(0,len(testCases[item])):
                 source_system,source,target_system,target = get_count_teststep_data(testCases[item][i])
                       #print srSystem,tgtSystem,source,target
                 data['CountModule'].loc[i] = [testCases[item][i].executeStatus,source_system,source,target_system,target,testCases[item][i].executionId,testCases[item][i].testerId]
           if item == 'NotnullModule' :
              for i in range(0,len(testCases[item])):
                 system,table,column = get_notnull_teststep_data(testCases[item][i])
                       #print srSystem,tgtSystem,source,target
                 data['NotnullModule'].loc[i] = [testCases[item][i].executeStatus,system,table,column,testCases[item][i].executionId,testCases[item][i].testerId]
           if item == 'DuplicateCheckModule' :
              for i in range(0,len(testCases[item])):
                 system,table,columnlist = get_duplicate_teststep_data(testCases[item][i])
                       #print srSystem,tgtSystem,source,target
                 data['DuplicateCheckModule'].loc[i] = [testCases[item][i].executeStatus,system,table,columnlist,testCases[item][i].executionId,testCases[item][i].testerId]
           if item == 'CompareModule' :         
              for i in range(0,len(testCases[item])):
                 source_system,src_sql,target_system,tgt_sql = get_compare_teststep_data(testCases[item][i])
                       #print srSystem,tgtSystem,source,target
                 data['CompareModule'].loc[i] = [testCases[item][i].executeStatus,source_system,src_sql,target_system,tgt_sql,testCases[item][i].executionId,testCases[item][i].testerId]
       except InvalidTestCase:
           print ',Module : '+item
    return data

##_____________DELETE FUNCTIONS_______________##
    
def delete_frozen_testcases(phaseId,tcrTestcaseId):
    values = json.dumps({"ids":[tcrTestcaseId]})
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/execution/'+str(phaseId)+'/testcase', data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    request.get_method = lambda: 'DELETE'
    response_body = urlopen(request).read()
    return response_body


##_____________GET FUNCTIONS_______________##

def get_all_testcases_for_project(projectId):    
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase?zqlquery=projectid='+str(projectId)+'&pagesize=1000')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    return json.loads(response_body)

def getTestcasesForNode(nodeId,releaseId):
    pageSize = getCountOfTestcasesByPhasesIds(nodeId,releaseId)
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase/tree/'+str(nodeId)+'?pagesize='+str(pageSize))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    #print json.loads(response_body)
    return json.loads(response_body)

def get_teststep(phaseTctId):
    URL='https://'+hostname+'/flex/services/rest/v3/testcase/'+str(phaseTctId)+'/teststep'
    #check_server_status()
    request = Request(URL)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    try:
       return json.loads(response_body)
    except ValueError:
       raise InvalidTestCase
      
def get_count_teststep_data(testcase):
   try:
      response_body = get_teststep(testcase.phaseTctId)
      source_system =  response_body['steps'][0]['data']
      source =  response_body['steps'][1]['data']
      target_system =  response_body['steps'][2]['data']
      target =  response_body['steps'][3]['data']
      return source_system,source,target_system,target
   except InvalidTestCase:
      print 'Invalid Data for '+testcase.name
      raise InvalidTestCase
        
def get_compare_teststep_data(testcase):
    try:
       response_body = get_teststep(testcase.phaseTctId)
       source_system =  response_body['steps'][0]['data']
       src_sql =  response_body['steps'][1]['data']
       target_system =  response_body['steps'][2]['data']
       tgt_sql =  response_body['steps'][3]['data']
       return source_system,src_sql,target_system,tgt_sql
    except InvalidTestCase:
       print 'Invalid Data for '+testcase.name
       raise InvalidTestCase
    
def get_notnull_teststep_data(testcase):
    try:
       response_body = get_teststep(testcase.phaseTctId)
       system =  response_body['steps'][0]['data']
       table =  response_body['steps'][1]['data']
       column =  response_body['steps'][2]['data']
       return system,table,column
    except InvalidTestCase:
       print 'Invalid Data for '+testcase.name
       raise InvalidTestCase
    
def get_duplicate_teststep_data(testcase):
    try:
       response_body = get_teststep(testcase.phaseTctId)
       system =  response_body['steps'][0]['data']
       table =  response_body['steps'][1]['data']
       columnlist =  response_body['steps'][2]['data']
       return system,table,columnlist
    except InvalidTestCase:
       print 'Invalid Data for '+testcase.name
       raise InvalidTestCase
    
def get_phase_details(phaseName,releaseId):
    response_body = get_cycles_for_release(releaseId)
    phase_list = []
    '''phase_list = get_phases_of_zephyr_cycle(response_body)
    print phase_list
    '''
    for i in range(0,len(response_body)):
        if response_body[i]['name'] == 'Zephyr Framework':
            for j in range(0,len(response_body[i]['cyclePhases'])):
                phase_list.append(response_body[i]['cyclePhases'][j]['id'])
    
    for i in range(0,len(phase_list)):
        #check_server_status()
        request = Request('https://'+hostname+'/flex/services/rest/v3/assignmenttree/'+str(phase_list[i]))
        request.add_header('cookie', cookie)
        request.add_header('Content-Type', 'application/json')
        response_body = urlopen(request).read()
        response_body = json.loads(response_body)
        if phaseName == response_body['name']:
            return phase_list[i],response_body['id']
    return ( 0 , 0 )
    

'''XXXXXX---------OUR FIRST FUNCTION--------XXXXXX'''

def get_details(name,url):
    #check_server_status()
    request = Request(url)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    cont = json.loads(response_body)
  
    for k in cont:
        if name == k['name']:
            return k['id']

'''XXXXXX-----------------------------------XXXXXX'''
        
def get_tcr_details(name,rid,url):
    #check_server_status()
    request = Request(url)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    cont = json.loads(response_body)
  
    for k in cont:
        if name == k['name'] and rid == k['releaseId']:
            return k['id']

def get_teststep_data(SourceDB,SourceTable,TargetDB,TargetTable,SourceSystem,TargetSystem):
            data = {
                    "src_system": SourceSystem,
                    "tgt_system": TargetTable,
                    "source": SourceDB+'.'+SourceTable,
                    "target": TargetDB+'.'+TargetTable
                    }
            #print data
            return data

def get_project_id(name):
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/latest/project/')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    '''response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    for k in response_body:
        if name == k['name']:
            return k['id']
    '''
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    for k in response_body:
        if name == k['name']:
            return k['id']
    string = "Invalid '"+name,            
    raise InvalidTestCase,string

def get_release_id(name,projectId):
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/latest/release/project/'+str(projectId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    for k in response_body:
        if name == k['name']:
            return k['id']
    string = 'Invalid '+name,            
    raise InvalidTestCase,string
         
def get_tcrCatalogId(project_name,release_name,node_name):
    project_id = get_details(project_name,'https://'+hostname+'/flex/services/rest/v3/project/')
    release_id = get_details(release_name,'https://'+hostname+'/flex/services/rest/v3/release/project/'+str(project_id))
    tcr_id = get_tcr_details(node_name,release_id,'https://'+hostname+'/flex/services/rest/v3/testcasetree')
    return tcr_id

def getTestcaseNames(response_body):
    names= []
    for i in range(0,len(response_body['results'])):
        names.append(response_body['results'][i]['testcase']['name'])
    return names

def get_execution_details(testcaseId):
    print '-----------Execution ----------------'
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/execution?pagesize=1000')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    #print response_body
    response_body= json.loads(response_body)
    return response_body
    '''for l in range(0,len(response_body['results'])):
        data = response_body['results'][l]
        #print data
        if testcaseId == data['tcrTreeTestcase']['testcase']['testcaseId']:
            #print data['id'],data['testerId']
            return data['id'],data['testerId']
    return 0,0     '''
    
def get_step_data(module,testcaseVersionId):
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase/'+str(testcaseVersionId)+'/teststep')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    #print response_body
    response_body = json.loads(response_body)
    response_body = response_body['steps'][0]['data']
    #response_body = json.loads(response_body)
    st= response_body.encode('ascii','ignore')
    response_body = ast.literal_eval(st)
    if module == 'count':
        return response_body['tgt_system'].encode('ascii','ignore'),response_body['src_system'].encode('ascii','ignore'),response_body['source'].encode('ascii','ignore'),response_body['target'].encode('ascii','ignore')
    if module == 'notnull':
        return response_body['system'].encode('ascii','ignore'),response_body['column'].encode('ascii','ignore'),response_body['table'].encode('ascii','ignore')
    if module == 'duplicate' :
        return response_body['columnlist'].encode('ascii','ignore'),response_body['system'].encode('ascii','ignore'),response_body['table'].encode('ascii','ignore')
    if module == 'compare' :
        return response_body['system'].encode('ascii','ignore'),response_body['src_sql'].encode('ascii','ignore'),response_body['tgt_sql'].encode('ascii','ignore')

def get_status_id(status):
    if status == 'True':
        return 1
    elif status == 'Execution Failed':
        return 10
    else:
        return 2
     
def getPlanningGridTcts(tcrphaseId):
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase/planning/'+str(tcrphaseId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    return response_body
   
   
def get_execution_tct_id(testcaseId,tcrphaseId):
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase/planning/'+str(tcrphaseId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    #response_body = getPlanningGridTcts(tcrphaseId)
    for data in range(0,len(response_body['results'])):
        if response_body['results'][data]['testcase']['testcaseId']==testcaseId:
            return response_body['results'][data]['tct']['id']
    
def get_cycle_id(name,releaseId):
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/cycle/all')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    #print response_body
    response_body = json.loads(response_body)
    for i in range(0,len(response_body)):
        if releaseId == response_body[i]['releaseId'] and name == response_body[i]['name']:
            return response_body[i]['id']
    
def get_all_project_details():
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/project')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    return json.loads(response_body)

def get_all_release_for_project(projectId):
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/release/project/'+str(projectId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    return json.loads(response_body)

def get_cycles_for_release(releaseId):
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/cycle/release/'+str(releaseId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    #print response_body
    return json.loads(response_body)
    
def get_phases_of_zephyr_cycle(response_body):
    phaseIds = []
    print 'lg'
    for i in range(0,len(response_body)):
        if response_body[i]['name'] == 'Zephyr Framework':
            for j in range(0,len(response_body[i]['cyclePhases'])):
                phaseIds.append(response_body[i]['cyclePhases'][j]['tcrCatalogTreeId'])
    return phaseIds

def getTCRCatalogTreeNodes():
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcasetree')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    return json.loads(response_body)

def getZephyrNodesId(responseBody,releaseId):
    testRepNodeIds = []
    for i in range(0,len(responseBody)):
        if responseBody[i]['releaseId'] == releaseId:
            if responseBody[i]['name'] == 'CountModule' or responseBody[i]['name'] == 'CompareModule' or responseBody[i]['name'] == 'NotnullModule' or responseBody[i]['name'] == 'DuplicateCheckModule':
                testRepNodeIds.append(responseBody[i]['id'])
    return testRepNodeIds

def get_phase_testcasetree_details(tcrPhaseId,releaseId):
    pageSize = getCountOfTestcasesByPhase(tcrPhaseId,releaseId)
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase/planning/'+str(tcrPhaseId)+'?pagesize='+str(pageSize))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    return json.loads(response_body)

def get_Node(phaseId):
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcasetree/'+str(phaseId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    return json.loads(response_body)

def getCountOfTestcasesByPhase(tcrCatalogTreeId,releaseId):
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase/count?tcrcatalogtreeid='+str(tcrCatalogTreeId)+'&releaseid='+str(releaseId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    return response_body

def getCountOfTestcasesByPhasesIds(treeId,releaseId):
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase/count/ids?treeids='+str(treeId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    if len(response_body) > 0:
        return response_body[0]['testcaseCount']
    else :
        return 0
#________ UPDATE FUNCTIONS __________________##

def update_testcase_status(executionId,statusId,testerId):
    values="""{}"""
    #check_server_status()
    request = Request('https://'+hostname+'/flex/services/rest/v3/execution/'+str(executionId)+'?status='+str(statusId)+'&testerid='+str(testerId),data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    request.get_method = lambda: 'PUT'
    #response_body = urlopen(request).read()
    urlopen(request).read()

def update_testcase_execution_notes(executionId,testerId,notes):
    values = json.dumps({"notes" : notes})
    request = Request('https://'+hostname+'/flex/services/rest/v3/execution/'+str(executionId)+'?testerid='+str(testerId),data=values,headers = headers)
    request.get_method = lambda: 'PUT'
    urlopen(request).read()