import subprocess
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
inputcsv=None
def returnjson(repURL):
    with request.urlopen(repURL) as response:
        if response.getcode() == 200:
            source = response.read()
            data = json.loads(source)
        else:
            print('404 error')
    return data['dependencies']
def readcsv(filename):
    global URL,inputcsv
    inputcsv=pd.read_csv(filename)  
    #print(inputcsv)
    name=inputcsv['name']
    n = np.array(name)
    rep=inputcsv['repo']
    r = np.array(rep)
    urlist=[]
    url1='https://raw.githubusercontent.com/'
    for rep in r:
        urlist.append(rep.replace("https://github.com/", ""))
    print(urlist)
    for u in urlist:
        URL.append(url1+u+'main/package.json')
    print(URL)
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
        data=returnjson(u)
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
    x = re.search("^sdkak -i [a-z]*[A-Z]*\.csv [a-z]*[A-Z]*@{1}\d*\.\d*.\d*$", cin)
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
            

        """ listofcmd=cmdin.split(' ')
        p1 = subprocess.Popen(listofcmd, stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,shell=True)
        out1, err = p1.communicate()
        print('-------------')
        print(out1.decode('utf-8')) """
except KeyboardInterrupt:
    print('CLI exited')
