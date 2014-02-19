
'''
Created on Jan 24, 2014
 
@author: rick
'''
 
import csv
import sys
import os
import re
import shutil
import string
import fnmatch
import numpy as np
import pylab as P
from collections import Counter
import subprocess as sp
from decimal import Decimal
import Tkinter, tkFileDialog
from subprocess import Popen, PIPE

root = Tkinter.Tk()
root.withdraw()

encoding_cmd_strings = {
'mp4': '~/../../opt/local/bin/ffmpeg -i {0} -y -acodec libfaac -vcodec mpeg4 {1}'
}


vamp_cmd_strings = {
'prep': '~/../../opt/local/bin/ffmpeg -i {0} -ac 1 -ar 16000 {1}',
'merge': '~/../../opt/local/bin/ffmpeg -i {0} -i {1} -filter_complex amerge {2}',
'sync': 'vamp/./vamp-simple-host match-vamp-plugin.dylib:match {0} 3 -o {1}'
}

def ffmpeg_prep(source, target, encoding):
    """Uses a shell call to ffmpeg to convert a video
    to the desired encoding"""
    print 'Prep started'
    # Popen calls the ffmpeg process, and collects the standard out/error
    p = Popen(vamp_cmd_strings[encoding].format(source, target),stdout=PIPE,stderr=PIPE,shell=True)
    stdout, stderr = p.communicate(input=None)
    return stdout, stderr


def ffmpeg_merge(source1, source2, target, encoding):
    """Uses a shell call to ffmpeg to convert a video
    to the desired encoding"""
    print 'Merge started'
    # Popen calls the ffmpeg process, and collects the standard out/error
    p = Popen(vamp_cmd_strings[encoding].format(source1, source2, target),stdout=PIPE,stderr=PIPE,shell=True)
    stdout, stderr = p.communicate(input=None)
    return stdout, stderr


def vamp_sync(source, target, encoding):
    """Uses a shell call to ffmpeg to convert a video
    to the desired encoding"""
    print 'Vamp sync started'
    # Popen calls the ffmpeg process, and collects the standard out/error
    p = Popen(vamp_cmd_strings[encoding].format(source, target),stdout=PIPE,stderr=PIPE,shell=True)
    stdout, stderr = p.communicate(input=None)
    return stdout, stderr


def findMode(data, flag):
    rawdata = np.genfromtxt(data,dtype='float',delimiter = ',',skiprows=0, skip_header=0, skip_footer=0, usecols=1,usemask=True, invalid_raise=False)
    P.figure()
    if flag == "KM":
        P.title("Kinect/Morae")
    if flag == "KS":
        P.title("Kinect/SMI")
    
    P.hist(rawdata, 250, histtype='stepfilled')
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
    
    
def syncPrep(kinectInput, smiInput, moraeInput):
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


def syncTxt2csv(tempdirectory):
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


def main():
    directory = tkFileDialog.askdirectory()
    root.destroy()
    
    for dirContents in os.listdir(directory):
        #print dirContents
        if dirContents == 'Kinect':
            kinectDirectory = directory+'/Kinect'
            for filename in os.listdir(kinectDirectory):
                if fnmatch.fnmatch(filename, '*.wav'):
                    kinectAudioFile = os.path.join(kinectDirectory, filename)
                    
                    
        if dirContents == 'Morae':
            moraeDirectory = directory+'/Morae'
            for filename in os.listdir(moraeDirectory):
                if fnmatch.fnmatch(filename, '*.mp4'):
                    moraeVideoFile = os.path.join(moraeDirectory, filename)
                        
        if dirContents == 'SMI':
            smiDirectory = directory+'/SMI'
            for filename in os.listdir(smiDirectory):
                if fnmatch.fnmatch(filename, '*.mp4'):
                    smiVideoFile = os.path.join(smiDirectory, filename)
    
    return directory, kinectAudioFile, smiVideoFile, moraeVideoFile


def syncMatch(kinectAudio, smiVideo, moraeVideo):
    tempSyncDir = syncPrep(kinectAudio, smiVideo, moraeVideo)
    syncTxt2csv(tempSyncDir)
    syncHeader = "Data Stream, Sync Point (in seconds)\n"
    writeSyncHeader = True
    syncOutputData = []
    syncOutputData.append("Kinect,0\n")
    
    syncsavename = directory+"/syncData.csv"
    sync_file = r""+syncsavename+""
    syncOutput = open(sync_file,'wb')
    
    for csvfile in os.listdir(tempSyncDir):
        #print csvfile
        if fnmatch.fnmatch(csvfile, 'KM.csv'):
            syncOutputData.append(findMode(tempSyncDir+'/'+csvfile, 'KM'))
        if fnmatch.fnmatch(csvfile, 'KS.csv'):
            syncOutputData.append(findMode(tempSyncDir+'/'+csvfile, 'KS'))
    
    if writeSyncHeader:
        syncOutput.write(syncHeader)
        writeSyncHeader = False
    for line in syncOutputData:
        #print line
        syncOutput.write(line)
    
    syncOutput.close()
    
    #danger this last line deletes the temp folder
    shutil.rmtree(tempSyncDir)
    
    print "Synchronization Complete"



histoFlag = True


directory, kinectAudioFile, smiVideoFile, moraeVideoFile = main()

syncMatch(kinectAudioFile, smiVideoFile, moraeVideoFile)
if histoFlag:
    P.show()
