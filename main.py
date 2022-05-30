import subprocess
import csv
import pandas as pd
import numpy as np
import urllib.request as request
import json
#print('Welcome to Sdkak, a dependency manager')
inputcsv=pd.read_csv('input.csv')  
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
URL=[]
for u in urlist:
    URL.append(url1+u+'main/package.json')
print(URL)
def returnjson(repURL):
    with request.urlopen(repURL) as response:
        if response.getcode() == 200:
            source = response.read()
            data = json.loads(source)
        else:
            print('404 error')
    return data['dependencies']
print(returnjson(URL[1]))
#print(n[0])
#print(r)
try:
    while True:
        cmdin=input('>>>')
        listofcmd=cmdin.split(' ')
        p1 = subprocess.Popen(listofcmd, stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,shell=True)
        out1, err = p1.communicate()
        print('-------------')
        print(out1.decode('utf-8'))
except KeyboardInterrupt:
    print('CLI exited')
