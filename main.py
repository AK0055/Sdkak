import subprocess
from urllib.error import HTTPError
import pandas as pd
import numpy as np
import urllib.request as request
import json
import re
#print('Welcome to Sdkak, a dependency manager')
pvlist=[]
URL=[]
package=[]
version=[]
version_satisfied=[]
repourlfalse=[]
inputcsv=None
def returnjson(repURL,pname):
    try:
        with request.urlopen(repURL) as response:
            if response.getcode() == 200:
                source = response.read()
                data = json.loads(source)
                #print(data['dependencies'])
                if data['dependencies'].__contains__(pname):
                    print('dep')
                    return data['dependencies']
                elif data['devDependencies'].__contains__(pname):
                    print('dev')
                    return data['devDependencies']
            else:
                print('404 error')
    except HTTPError:
        print('404 error')
def returnvalidurl(repURL):
    try:
        status_code = request.urlopen(repURL).getcode()
        website_is_up = status_code == 200
        return website_is_up
    except HTTPError:
        print('404 error')
def readcsv(filename):
    global URL,inputcsv
    inputcsv=pd.read_csv(filename)  
    print(inputcsv)
    name=inputcsv['name']
    n = np.array(name)
    rep=inputcsv['repo']
    r = np.array(rep)
    urlist=[]
    url1='https://raw.githubusercontent.com/'
    for repi in r:
        print(type(repi))
        urlist.append(repi.replace("https://github.com/", ""))
    print(urlist)
    for u in urlist:
        temp=url1+u+'main/package.json'
        temp2=url1+u+'master/package.json'
        print(temp)
        print(temp2)
        print(URL)
        if returnvalidurl(temp):
            print('valid-main')
            URL.append(temp)
        elif returnvalidurl(temp2):
            print('valid-master')
            URL.append(temp2)
        
def versioncomp(v1,v2):
    for i in range(len(v1)):
      if v1[i]>v2[i]:
         return 1
      elif v2[i]>v1[i]:
         return -1
    return 0
def chkdep(package):
    global URL
    global pvlist
    for u in URL:
        data=returnjson(u,package[0])
        pname=package[0]
        pver=package[1]
        datapv=data[pname]
        
        if re.search("^\^", datapv):
            datapv=datapv.replace("^","")
        elif re.search("^~", datapv):
            datapv=datapv.replace("~","")
        print(datapv)
        pvlist.append(datapv)
    versionchecker(pver)
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
    print(version_satisfied)
    inputcsv['version']=version
    inputcsv['version_satisfied']=version_satisfied
    print(inputcsv.head())
    #print(verlist)
    #print(inverlist)

def cmd2funcinput(cin):
    x = re.search("^sdkak -i [a-z]*[A-Z]*[0-9]*\.csv [a-z]*[A-Z]*@{1}\d*\.\d*.\d*$", cin)
    return x
def cmd2funcupdate(cin):
    x = re.search("^sdkak -u [a-z]*[A-Z]*\.csv [a-z]*[A-Z]*@{1}\d*\.\d*.\d*$", cin)
    return x
#print(n[0])
#print(r)
try:
    while True:
        cmdin=input('>>>')
        if cmd2funcinput(cmdin):
            listofcmd=cmdin.split(' ')
            print(listofcmd)
            readcsv(listofcmd[2])
            package=listofcmd[3].split('@')
            chkdep(package)
        elif cmd2funcupdate(cmdin):
            print(inputcsv)
            repourlfalse=inputcsv[['repo','version_satisfied']].query('version_satisfied == "False"')['repo']
            repourlist=np.array(repourlfalse)
            print(repourlfalse)
        """ listofcmd=cmdin.split(' ')
        p1 = subprocess.Popen(listofcmd, stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,shell=True)
        out1, err = p1.communicate()
        print('-------------')
        print(out1.decode('utf-8')) """
except KeyboardInterrupt:
    print('CLI exited')
