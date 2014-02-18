'''
Created on Feb 18, 2014

@author: rick
'''

import shutil
import csv
import sys
import os
import re
import fnmatch
import numpy as np
import pylab as P
import matplotlib.pyplot as plt
from collections import Counter
from subprocess import Popen, PIPE

import Tkinter, tkFileDialog
root = Tkinter.Tk()
root.withdraw()


encoding_cmd_strings = {
'prep': '~/../../opt/local/bin/ffmpeg -i {0} -ac 1 -ar 16000 {1}',
'merge': '~/../../opt/local/bin/ffmpeg -i {0} -i {1} -filter_complex amerge {2}',
'sync': './vamp-simple-host match-vamp-plugin.dylib:match {0} 3 -o {1}'
}

def ffmpeg_prep(source, target, encoding):
    """Uses a shell call to ffmpeg to convert a video
    to the desired encoding"""
    print 'Prep started'
    # Popen calls the ffmpeg process, and collects the standard out/error
    p = Popen(encoding_cmd_strings[encoding].format(source, target),stdout=PIPE,stderr=PIPE,shell=True)
    stdout, stderr = p.communicate(input=None)
    return stdout, stderr


def ffmpeg_merge(source1, source2, target, encoding):
    """Uses a shell call to ffmpeg to convert a video
    to the desired encoding"""
    print 'Merge started'
    # Popen calls the ffmpeg process, and collects the standard out/error
    p = Popen(encoding_cmd_strings[encoding].format(source1, source2, target),stdout=PIPE,stderr=PIPE,shell=True)
    stdout, stderr = p.communicate(input=None)
    return stdout, stderr


def vamp_sync(source, target, encoding):
    """Uses a shell call to ffmpeg to convert a video
    to the desired encoding"""
    print 'Vamp sync started'
    # Popen calls the ffmpeg process, and collects the standard out/error
    p = Popen(encoding_cmd_strings[encoding].format(source, target),stdout=PIPE,stderr=PIPE,shell=True)
    stdout, stderr = p.communicate(input=None)
    return stdout, stderr


def findMode(data, flag):
    rawdata = np.genfromtxt(data,dtype='float',delimiter = ',',skiprows=0, skip_header=0, skip_footer=0, usecols=1,usemask=True, invalid_raise=False)

    print "Finding Sync Point"
    
    nData = []
    for el in rawdata:
        nData.append(el)
        
    syncData = Counter(nData)
    sync = syncData.most_common(1)
    if flag == "KM":
        return "Morae,"+str((sync[0])[0])+"\n"
    if flag == "KS":
        return "SMI,"+str((sync[0])[0])+"\n"



def syncPrep(directory):
    kinectInput = directory+'/input/kinect.wav'
    smiInput = directory+'/input/smi.avi'
    moraeInput = directory+'/input/morae.wmv'
    tempOutput = directory+'/temp/'
    
    if not os.path.exists(tempOutput):
        os.makedirs(tempOutput)
    
    ffmpeg_prep(kinectInput, tempOutput+'kinectMono.wav', 'prep')
    ffmpeg_prep(smiInput, tempOutput+'smiMono.wav', 'prep')
    ffmpeg_prep(moraeInput, tempOutput+'moraeMono.wav', 'prep')
     
    ffmpeg_merge(tempOutput+'kinectMono.wav', tempOutput+'smiMono.wav', tempOutput+'mergeKS.wav', 'merge')
    ffmpeg_merge(tempOutput+'kinectMono.wav', tempOutput+'moraeMono.wav', tempOutput+'mergeKM.wav', 'merge')
    ffmpeg_merge(tempOutput+'smiMono.wav', tempOutput+'moraeMono.wav', tempOutput+'mergeSM.wav', 'merge')
     
    vamp_sync(tempOutput+'mergeKS.wav', tempOutput+'KS.txt', 'sync')
    vamp_sync(tempOutput+'mergeKM.wav', tempOutput+'KM.txt', 'sync')
    vamp_sync(tempOutput+'mergeSM.wav', tempOutput+'SM.txt', 'sync')
    
    return tempOutput


def txt2csv(directory):
    tempdirectory = directory+'/temp'
    print "clean sync txt"
    for filename in (os.listdir(tempdirectory)):
        #print filename
        if fnmatch.fnmatch(filename, '*.txt'):
            filepath = os.path.join(tempdirectory, filename)
            savename = os.path.splitext(filepath)[0]+".csv"

            txt_file = r""+filepath+""
            csv_file = r""+savename+""
            
            in_txt = csv.reader(open(txt_file, "rb"), delimiter = ':')
            out_csv = csv.writer(open(csv_file, 'wb'))
            
            out_csv.writerows(in_txt)


directory = tkFileDialog.askdirectory()
tempdirectory = directory+'/temp'
syncPrep(directory)
header = "Data Stream, Sync Point (in seconds)\n"
writeHeader = True

txt2csv(directory)
outputData = []
outputData.append("Kinect,0\n")

syncsavename = directory+"/syncData.csv"
sync_file = r""+syncsavename+""
output = open(sync_file,'wb')
#print outputData

for csvfile in os.listdir(tempdirectory):
    #print csvfile
    if fnmatch.fnmatch(csvfile, 'KM.csv'):
        outputData.append(findMode(tempdirectory+'/'+csvfile, 'KM'))
    if fnmatch.fnmatch(csvfile, 'KS.csv'):
        outputData.append(findMode(tempdirectory+'/'+csvfile, 'KS'))

if writeHeader:
    output.write(header)
    writeHeader = False
for line in outputData:
    #print line
    output.write(line)
    
#danger this last line deletes the temp folder
shutil.rmtree(tempdirectory)

