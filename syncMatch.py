
'''
Created on Jan 24, 2014
 
@author: rick
'''
 
import csv
import os
import shutil
import fnmatch
import numpy as np
import pylab
from collections import Counter
import Tkinter, tkFileDialog
from subprocess import Popen, PIPE

root = Tkinter.Tk()
root.withdraw()


vamp_cmd_strings = {
'prep': '~/../../opt/local/bin/ffmpeg -i {0} -ac 1 -ar 16000 {1}',
'merge': '~/../../opt/local/bin/ffmpeg -i {0} -i {1} -filter_complex amerge {2}',
'sync': '/Users/danilogr/Projects/syncmatch/vamp/./vamp-simple-host match-vamp-plugin.dylib:match {0} 3 -o {1}' #hardcoding location of vamp files
}


def ffmpeg_prep(source, target, encoding):
    """Uses a shell call to ffmpeg to convert a video
    to the desired encoding"""
    print 'Prep started'
    # Popen calls the ffmpeg process, and collects the standard out/error
    p = Popen(vamp_cmd_strings[encoding].format(source, target), stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate(input=None)
    print 'Prep complete'
    return stdout, stderr


def ffmpeg_merge(source1, source2, target, encoding):
    """Uses a shell call to ffmpeg to convert a video
    to the desired encoding"""
    print 'Merge started'
    # Popen calls the ffmpeg process, and collects the standard out/error
    p = Popen(vamp_cmd_strings[encoding].format(source1, source2, target), stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate(input=None)
    print 'Merge complete'
    return stdout, stderr


def vamp_sync(source, target, encoding):
    """Uses a shell call to ffmpeg to convert a video
    to the desired encoding"""
    print 'Vamp sync started'
    # Popen calls the ffmpeg process, and collects the standard out/error
    p = Popen(vamp_cmd_strings[encoding].format(source, target), stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate(input=None)
    print 'Vamp sync complete'
    return stdout, stderr


def findMode(data):
    rawdata = np.genfromtxt(data,dtype='float', delimiter = ',', skiprows=0, skip_header=0, skip_footer=0, usecols=1, usemask=True, invalid_raise=False)
    pylab.figure()
    pylab.hist(rawdata, 250, histtype='stepfilled')
    pylab.savefig(os.path.join(os.path.dirname(os.path.dirname(data)), 'histo.png'))
    print "Finding Sync Point"
    
    nData = []
    for el in rawdata:
        nData.append(el)
        
    syncData = Counter(nData)
    sync = syncData.most_common(1)
    return "Merge,"+str((sync[0])[0])+"\n"
    
    
def syncPrep(video1, video2):
    tempOutput = os.path.join(os.path.dirname(video1), "temp")
    
    if not os.path.exists(tempOutput):
        os.makedirs(tempOutput)
    
    print ffmpeg_prep(video1, os.path.join(tempOutput,'v1.wav'), 'prep')
    print ffmpeg_prep(video2, os.path.join(tempOutput,'v2.wav'), 'prep')
    
    print ffmpeg_merge(os.path.join(tempOutput,'v1.wav'), os.path.join(tempOutput,'v2.wav'), os.path.join(tempOutput,'merge.wav'), 'merge')

    print vamp_sync(os.path.join(tempOutput,'merge.wav'), os.path.join(tempOutput,'merge.txt'), 'sync')

    return tempOutput


def syncTxt2csv(tempdirectory):
    for filename in (os.listdir(tempdirectory)):
        #print filename
        if fnmatch.fnmatch(filename, '*.txt'):
            filepath = os.path.join(tempdirectory, filename)
            savename = os.path.splitext(filepath)[0]+".csv"

            txt_file = r""+filepath+""
            csv_file = r""+savename+""
            
            with open(txt_file, 'rb') as in_txt, open(csv_file, 'wb') as out_csv:
                inReader = csv.reader(in_txt, delimiter = ':')
                outWriter = csv.writer(out_csv)
                
                for row in inReader:
                    outWriter.writerow(row)
            
            in_txt.close()
            out_csv.close()


def syncMatch(video1, video2):
    tempSyncDir = syncPrep(video1, video2)
    syncTxt2csv(tempSyncDir)
    syncHeader = "Data Stream, Sync Point (in seconds)\n"
    writeSyncHeader = True
    syncOutputData = []
    
    syncsavename = os.path.join(os.path.dirname(video1), "syncData.csv")
    sync_file = r""+syncsavename+""
    with open(sync_file, 'wb') as syncOutput:
        syncWriter = csv.writer(syncOutput)
        for csvfile in os.listdir(tempSyncDir):
            #print csvfile
            if fnmatch.fnmatch(csvfile, 'merge.csv'):
                syncOutputData.append(findMode(os.path.join(tempSyncDir,csvfile)))
        
        if writeSyncHeader:
            syncWriter.writerow(syncHeader.split(','))
            writeSyncHeader = False
        
        syncRows = list(syncOutputData)
        for el in syncRows:
            syncWriter.writerow(el.split(','))
    
    syncOutput.close()
    
    #danger this last line deletes the temp folder
    shutil.rmtree(tempSyncDir)
    
    print "Synchronization Complete"


if __name__ == "__main__":
    video1 = tkFileDialog.askopenfilename()
    video2 = tkFileDialog.askopenfilename()	
    root.destroy()
    syncMatch(video1, video2)
