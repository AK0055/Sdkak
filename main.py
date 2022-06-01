from urllib.error import HTTPError
import pandas as pd
import numpy as np
import urllib.request as request
import json
import re
import os
print('Welcome to SDKak, A Package Dependency Manager')
pvlist=[]
URL=[]
package=[]
version=[]
version_satisfied=[]
repourlfalse=[]
reponamefalse=[]
clonename=[]
inputcsv=None

#Returns dependency specified in command inside package.json given in the URL
def returnjson(repURL,pname):
    try:
        with request.urlopen(repURL) as response:
            if response.getcode() == 200:
                source = response.read()
                data = json.loads(source)
                if data['dependencies'].__contains__(pname):
                    #print('dep')
                    return data['dependencies']
                elif data['devDependencies'].__contains__(pname):
                    #print('dev')
                    return data['devDependencies']
            else:
                print('404 error')
    except HTTPError:
        print('404 error')

#Check if the URL is valid    
def returnvalidurl(repURL):
    try:
        status_code = request.urlopen(repURL).getcode()
        website_is_up = status_code == 200
        return website_is_up
    except HTTPError:
        print('404 error, trying alternate branch-master')

#Input CSV and fetch data rows, process URL to get JSON data
def read_process_csv(filename):
    global URL,inputcsv,clonename
    inputcsv=pd.read_csv(filename)  
    name=inputcsv['name']
    n = np.array(name)
    rep=inputcsv['repo']
    r = np.array(rep)
    urlist=[]
    #Create a RAW URL path from github repo URL to fetch JSON data
    url1='https://raw.githubusercontent.com/'
    for repi in r:
        clonename.append(repi.split('/')[4])
        urlist.append(repi.replace("https://github.com/", ""))
    inputcsv['clonename']=clonename
    for u in urlist:
        temp=url1+u+'main/package.json'
        temp2=url1+u+'master/package.json'
        if returnvalidurl(temp):
            print('valid branch-main')
            URL.append(temp)
        elif returnvalidurl(temp2):
            print('valid branch-master')
            URL.append(temp2)

#Function to compare two versions        
def versioncomp(v1,v2):
    for i in range(len(v1)):
      if v1[i]>v2[i]:
         return 1
      elif v2[i]>v1[i]:
         return -1
    return 0

#Function to process version numbers and compare from given URL
def chkdep(package):
    global URL
    global pvlist
    for u in URL:
        data=returnjson(u,package[0])
        pname=package[0]
        pver=package[1]
        datapv=data[pname]
        #remove dependency prefixes
        if re.search("^\^", datapv):
            datapv=datapv.replace("^","")
        elif re.search("^~", datapv):
            datapv=datapv.replace("~","")
        #print(datapv)
        pvlist.append(datapv)
    versionchecker(pver)\

#Compare version in remote and version specified by command
def versionchecker(pver):
    global version,version_satisfied,inputcsv
    for v in pvlist:
        verlist=v.split(".")
        inverlist=pver.split(".")
        verlist = [int(i) for i in verlist]
        inverlist = [int(i) for i in inverlist]
        flag=versioncomp(verlist,inverlist)
        version.append(v)
        if flag < 0:
            print ("version in github is smaller")
            version_satisfied.append('False')
        elif flag > 0:
            print ("version in github is larger")
            version_satisfied.append('True')
        else:
            print ("Both versions are equal")
            version_satisfied.append('True')
    inputcsv['version']=version
    inputcsv['version_satisfied']=version_satisfied
    print(inputcsv.head())
    
#Function syntax to initialise and get version matching status from a CSV
def cmd2funcinput(cin):
    x = re.search("^sdkak -i [a-z]*[A-Z]*[0-9]*\.csv [a-z]*[A-Z]*@{1}\d*\.\d*.\d*$", cin)
    return x
#Function syntax to update the version of the outdated version in remote origin and create PR
def cmd2funcupdate(cin):
    x = re.search("^sdkak -u [a-z]*[A-Z]*[0-9]*\.csv [a-z]*[A-Z]*@{1}\d*\.\d*.\d*$", cin)
    return x

#Function to clone the git repo from remote
def gitclone(repourlist,reponame):
    for r,n in zip(repourlist, reponame):
        os.system('git clone '+r)
        print(n+' has been cloned')

#Function to create branch, commit and push changes to remote
def gitbranch(n,url):
    replaced = '.git'
    url = url[:-1] + replaced
    print(url)
    os.chdir(n)
    print("Current working directory: {0}".format(os.getcwd()))
    os.system('git checkout -b '+n+'branch')
    os.system('git branch')
    os.system('git add .')
    os.system('git commit -m "Test: Modifying package.json"')
    os.system('git push '+url+' '+n+'branch')
    os.system('cd ..')

#Function to modify the package.json dependency version from commandline
def modifyjson(filepath,pname,pvalue):
    with open(filepath+'/package.json') as f:
        data = json.load(f)
        if data['dependencies'].__contains__(pname):
            print(filepath+' in dependencies')
            data['dependencies'][pname] = pvalue
            
        elif data['devDependencies'].__contains__(pname):
            print(filepath+' in devdependencies')
            data['devDependencies'][pname] = pvalue
            
        try:
            print('Package.JSON modified for '+filepath)
            json.dump(data, open(filepath+'/package.json','w'), indent = 4)
        except json.decoder.JSONDecodeError:
            print('Invalid json encoding')

# Driver
try:
    while True:
        cmdin=input('>>> ')
        #Initialise, fetch JSON and compare versions
        if cmd2funcinput(cmdin):
            listofcmd=cmdin.split(' ')
            read_process_csv(listofcmd[2])
            package=listofcmd[3].split('@')
            chkdep(package)
        #Clone repo, update outdated version to specified version, commit changes and create PR
        elif cmd2funcupdate(cmdin):
            listofcmd=cmdin.split(' ')
            package=listofcmd[3].split('@')
            repourlfalse=inputcsv[['repo','version_satisfied']].query('version_satisfied == "False"')['repo']
            reponamefalse=inputcsv[['name','repo','version_satisfied','clonename']].query('version_satisfied == "False"')['clonename']
            repourlist=np.array(repourlfalse)
            reponamelist=np.array(reponamefalse)
            gitclone(repourlist,reponamelist)
            for i,j in zip(reponamelist,repourlist):
                modifyjson(i,package[0],package[1])
                gitbranch(i,j)
                os.chdir('../')
                #gitcommitpush(i)
            
        listofcmd=[]
        pvlist=[]
        URL=[]
        package=[]
        version=[]
        version_satisfied=[]
        repourlfalse=[]
        reponamefalse=[]
        clonename=[]
        inputcsv=None
        print('Press Ctrl-C to exit')


        

except KeyboardInterrupt:
    print('CLI exited')
