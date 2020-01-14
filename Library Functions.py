"""
Custom Library in python for Integrating Zephyr with user interfaces.
Version : Zephyr 6.5
Last Updated : Jan 12, 2019
Author : Abhishek Yadav, Johanan Abhishek
ENJOY!
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

def getCook():
      request = Request('https://'+hostname+'/flex/services/rest/v3/user/current',headers = headers)
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
    
    request = Request('https://'+hostname+'/flex/services/rest/v3/assignmenttree/'+str(phaseid)+'/assign/bytree/'+str(tcrphaseid)+'?includehierarchy=false', data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    urlopen(request).read()
    
        
def assign_testcases_to_current_user(phaseId):
    values = """{}"""
    request = Request('https://'+hostname+'/flex/services/rest/v3/assignmenttree/'+str(phaseId)+'/assign', data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    urlopen(request).read()

def assign_testcases_to_anyone(tctId,phaseId):
    values = json.dumps({'createRTSList': [{'tctId': tctId, 'testerId': 1, 'cyclePhaseId': phaseId}]})
    request = Request('https://'+hostname+'/flex/services/rest/v3/execution/modify', data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    urlopen(request).read()
        

##__________ CHECK FUNCTIONS ______________##
def check_cycle(name,release_id):
    request = Request('https://'+hostname+'/flex/services/rest/v3/cycle/all')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body= json.loads(response_body)
    for l in range(0,len(response_body)):
        data = response_body[l]
        if data['name']==name and data['releaseId']==release_id:
            return 1
    return 0

def check_node(name,release_id):
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcasetree')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    for l in range(0,len(response_body)):
        data = response_body[l]
        if data['name']==name and data['releaseId']==release_id:
            return 1    
    return 0
    
def check_phase(phaseName,releaseId):
    response_body = get_cycles_for_release(releaseId)
    phase_list = []
    for i in range(0,len(response_body)):
        if response_body[i]['name'] == 'Zephyr Framework':
            for j in range(0,len(response_body[i]['cyclePhases'])):
                phase_list.append(response_body[i]['cyclePhases'][j]['id'])  
    
    if len(phase_list) == 0:
        return False
    for i in range(0,len(phase_list)):
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
       urlopen(request).read()
    except:
       url = 'https://'+hostname+'/flex/html5/login'
       webbrowser.open(url)
       time.sleep(10)
       browserExe = "iexplore.exe"
       os.system("taskkill /f /im "+browserExe)
       
def check_testcase(testcaseName, projectId):
    response_body = get_all_testcases_for_project(projectId)
    for item in range(0,len(response_body['results'])):
        if response_body['results'][item]['testcase']['name'] == testcaseName:
            return True
    return False
    

##_____________ CALCULATE ____________________ ##
def calculate_Assignments_For_Release(releaseId):
    request = Request('https://'+hostname+'/flex/services/rest/v3/cycle/assignments/'+str(releaseId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    return response_body    

##_____________ CREATE ____________________ ##

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
    URL='https://'+hostname+'/flex/services/rest/v3/testcase/'+str(testcase.phaseTctId)+'/teststep/'+str(testcase.tctId)+'/'+str(testcase.projectId)
    request = Request(URL,data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    urlopen(request).read()

def create_teststep(testcase,values):
    URL='https://'+hostname+'/flex/services/rest/v3/testcase/'+str(testcase.phaseTctId)+'/teststep/detail/'+str(testcase.tctId)    
    request = Request(URL,data = json.dumps(values[0]))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response = json.loads(urlopen(request).read())
    id = int(response['id'])
    
    for i in range(1,len(values)):
        values[i]['id']=id
        values[i]['tcId'] = testcase.testcaseId
        values[i]['tctId'] = testcase.tctId
        request = Request(URL,data = json.dumps(values[i]))
        request.add_header('cookie', cookie)
        request.add_header('Content-Type', 'application/json')
        response = urlopen(request).read()            
           
def create_cycle(releaseId):
    values = json.dumps({ 
                "name": "Zephyr Framework", 
                "cycleStartDate": str(now.month)+'/'+str(now.day)+'/'+str(now.year), 
                "cycleEndDate": "12/31/2020", 
                "status": 0, 
                "releaseId": releaseId
                })
    
    request = Request('https://'+hostname+'/flex/services/rest/v3/cycle',data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    return response_body['id']

def create_phase(cycleId,name):
    values =json.dumps({
    "phaseStartDate" : str(now.month)+'/'+str(now.day)+'/'+str(now.year),
    "phaseEndDate" : str(now.month)+'/'+str(now.day)+'/'+str(now.year),
    "freeForm" : True,
    "name" : name,
    "cycleId" : cycleId
    })
    
    request = Request('https://'+hostname+'/flex/services/rest/v3/cycle/'+str(cycleId)+'/phase', data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    return response_body['id'],response_body['tcrCatalogTreeId']

def create_node(name,releaseId):
    values = json.dumps({
        "name": name,
        "type": "Phase",
        "releaseId": releaseId
        })
    
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcasetree', data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body= json.loads(response_body)
    return response_body['id']

def create_modules(parentId,releaseId):
    values = json.dumps({"name": "Count", "description": "", "type": "Module", "releaseId": releaseId})
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcasetree?parentid='+str(parentId+1), data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    
    urlopen(request).read()
    values = json.dumps({"name": "NotNULL", "description": "", "type": "Module", "releaseId": releaseId})
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcasetree?parentid='+str(parentId+2), data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    urlopen(request).read()
    
    values = json.dumps({"name": "Compare", "description": "", "type": "Module", "releaseId": releaseId})
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcasetree?parentid='+str(parentId+3), data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    urlopen(request).read()
    
    values = json.dumps({"name": "Duplicates", "description": "", "type": "Module", "releaseId": releaseId})
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcasetree?parentid='+str(parentId+4), data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    urlopen(request).read()

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
    request = Request('https://'+hostname+'/flex/services/rest/v3/execution/'+str(phaseId)+'/testcase', data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    request.get_method = lambda: 'DELETE'
    response_body = urlopen(request).read()
    return response_body


##_____________GET FUNCTIONS_______________##

def get_all_testcases_for_project(projectId):    
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase?zqlquery=projectid='+str(projectId)+'&pagesize=1000')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    return json.loads(response_body)

def getTestcasesForNode(nodeId,releaseId):
    pageSize = getCountOfTestcasesByPhasesIds(nodeId,releaseId)
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase/tree/'+str(nodeId)+'?pagesize='+str(pageSize))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    #print json.loads(response_body)
    return json.loads(response_body)

def get_teststep(phaseTctId):
    URL='https://'+hostname+'/flex/services/rest/v3/testcase/'+str(phaseTctId)+'/teststep'
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
       raise InvalidTestCase
    
def get_notnull_teststep_data(testcase):
    try:
       response_body = get_teststep(testcase.phaseTctId)
       system =  response_body['steps'][0]['data']
       table =  response_body['steps'][1]['data']
       column =  response_body['steps'][2]['data']
       return system,table,column
    except InvalidTestCase:
       raise InvalidTestCase
    
def get_duplicate_teststep_data(testcase):
    try:
       response_body = get_teststep(testcase.phaseTctId)
       system =  response_body['steps'][0]['data']
       table =  response_body['steps'][1]['data']
       columnlist =  response_body['steps'][2]['data']
       return system,table,columnlist
    except InvalidTestCase:
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
        request = Request('https://'+hostname+'/flex/services/rest/v3/assignmenttree/'+str(phase_list[i]))
        request.add_header('cookie', cookie)
        request.add_header('Content-Type', 'application/json')
        response_body = urlopen(request).read()
        response_body = json.loads(response_body)
        if phaseName == response_body['name']:
            return phase_list[i],response_body['id']
    return ( 0 , 0 )
    

def get_details(name,url):
    request = Request(url)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    cont = json.loads(response_body)
  
    for k in cont:
        if name == k['name']:
            return k['id']
        
def get_tcr_details(name,rid,url):
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
    request = Request('https://'+hostname+'/flex/services/rest/latest/project/')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    for k in response_body:
        if name == k['name']:
            return k['id']
    string = "Invalid '"+name,            
    raise InvalidTestCase,string

def get_release_id(name,projectId):
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
    request = Request('https://'+hostname+'/flex/services/rest/v3/execution?pagesize=1000')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body= json.loads(response_body)
    return response_body
    
def get_step_data(module,testcaseVersionId):
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase/'+str(testcaseVersionId)+'/teststep')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    response_body = response_body['steps'][0]['data']
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
    
def getPlanningGridTcts(tcrphaseId):
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase/planning/'+str(tcrphaseId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    return response_body
   
def get_execution_tct_id(testcaseId,tcrphaseId):
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase/planning/'+str(tcrphaseId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    for data in range(0,len(response_body['results'])):
        if response_body['results'][data]['testcase']['testcaseId']==testcaseId:
            return response_body['results'][data]['tct']['id']
    
def get_cycle_id(name,releaseId):
    request = Request('https://'+hostname+'/flex/services/rest/v3/cycle/all')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    for i in range(0,len(response_body)):
        if releaseId == response_body[i]['releaseId'] and name == response_body[i]['name']:
            return response_body[i]['id']
    
def get_all_project_details():
    request = Request('https://'+hostname+'/flex/services/rest/v3/project')
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    return json.loads(response_body)

def get_all_release_for_project(projectId):
    request = Request('https://'+hostname+'/flex/services/rest/v3/release/project/'+str(projectId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    return json.loads(response_body)

def get_cycles_for_release(releaseId):
    request = Request('https://'+hostname+'/flex/services/rest/v3/cycle/release/'+str(releaseId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    return json.loads(response_body)
    
def get_phases_of_zephyr_cycle(response_body):
    phaseIds = []
    for i in range(0,len(response_body)):
        if response_body[i]['name'] == 'Zephyr Framework':
            for j in range(0,len(response_body[i]['cyclePhases'])):
                phaseIds.append(response_body[i]['cyclePhases'][j]['tcrCatalogTreeId'])
    return phaseIds

def getTCRCatalogTreeNodes():
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
    
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase/planning/'+str(tcrPhaseId)+'?pagesize='+str(pageSize))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    return json.loads(response_body)

def get_Node(phaseId):
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcasetree/'+str(phaseId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    return json.loads(response_body)

def getCountOfTestcasesByPhase(tcrCatalogTreeId,releaseId):
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase/count?tcrcatalogtreeid='+str(tcrCatalogTreeId)+'&releaseid='+str(releaseId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    return response_body

def getCountOfTestcasesByPhasesIds(treeId,releaseId):
    request = Request('https://'+hostname+'/flex/services/rest/v3/testcase/count/ids?treeids='+str(treeId))
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    response_body = urlopen(request).read()
    response_body = json.loads(response_body)
    if len(response_body) > 0:
        return response_body[0]['testcaseCount']
    else :
        return 0
    
#_________________UPDATE FUNCTIONS __________________##

def update_testcase_status(executionId,statusId,testerId):
    values="""{}"""
    request = Request('https://'+hostname+'/flex/services/rest/v3/execution/'+str(executionId)+'?status='+str(statusId)+'&testerid='+str(testerId)+'&allExecutions=false&includeanyoneuser=true',data=values)
    request.add_header('cookie', cookie)
    request.add_header('Content-Type', 'application/json')
    request.get_method = lambda: 'PUT'
    urlopen(request).read()

def update_testcase_execution_notes(executionId,testerId,notes):
    values = json.dumps({"notes" : notes})
    request = Request('https://'+hostname+'/flex/services/rest/v3/execution/'+str(executionId)+'?testerid='+str(testerId),data=values,headers = headers)
    request.get_method = lambda: 'PUT'
    urlopen(request).read()
