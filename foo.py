import mne
import matplotlib.pyplot as plt
import numpy as np
import h5py
import os
import tqdm
import sys
import pdb
import math
import bottleneck as bn

from util import *

"""
TODO
 - Get the conversion data from HDF5 files (why first dataset doesn't have it?)
 - Implement sliding window
"""

SAMPLE_RATE_HZ = 24414.0625 # in Hz
NUM_CHANNELS = 96
global num_samples

def OpenHDF5Data(filename,header=''):
    print("\n Opening file {}.\n".format(filename))
    current_file = h5py.File(filename,'r')
    #print("Ck: What does data look like?"); pdb.set_trace() # check the filename stuff!
    data = current_file['acquisition']['timeseries']['broadband']['data']
    t = current_file['acquisition']['timeseries']['broadband']['timestamps']
    #pdb.set_trace()
    return t,data

def downsampleData(t,data,factor,sample_rate=SAMPLE_RATE_HZ):
    print("\n Downsampling ECoG Data....\n")
    return mne.filter.resample(t,down=factor),mne.filter.resample(data,down=factor,axis=0)
     # this might crash because of how f*cking big the data is this is
                        # the only thing I enjoy please don't take this away from me

def preprocessECoGData(t,data,sample_rate=SAMPLE_RATE_HZ):
    # probably would do some filtering and stuff
    print("\n Preprocessing ECoG Data...\n")
    t_ds,data_ds = downsampleData(t,data,8)
    return t_ds,data_ds 

def preprocessXYData(t,data,sample_rate,nbins=1):
    pass

def getBinFromData(t,data,binSize,binNum):
    print("\n Binning data...\n")

    if (binSize*binNum + binSize) > (num_samples): # we're at the end, chunk may be small
        remainderSize = ((binSize*binNum + binSize) - (num_samples)) - 1 # might be off by one
        dcut = data[h5py.MultiBlockSlice(start=binSize*binNum,count=remainderSize)]
    else:
        dcut = data[h5py.MultiBlockSlice(start=binSize*binNum,count=binSize)]
    # reshape / buffer by binsize
    return t,dcut

def getBasicStats(t,bindata):
    # data format kxnxt (#bins x #chans x time)
    print("\nRunning basic stats (stddev, variance)....\n")

    std = numpy.std(bindata)
    variance = numpy.var(bindata)
    return std,variance

def getSlidingWindowStats(t,data,windowSize):
    bn.move_var(a,windowSize)

    return 

def showHDF5Headers(filename):
    print("\n Retrieving headers.. {}.\n".format(filename))
    current_file = h5py.File(filename,'r')
    return list(current_file.keys())

def printIntro():
    print("\n\n****************************************** \n Neural Stablity & Variability Analysis \n****************************************** \n\n")

def getValidFoldersAndNames():
    cwd = os.getcwd()
    data_folder = os.path.join(cwd,"data/")
    data_folder_dirs = [os.path.join(data_folder,datadir) for datadir in os.listdir(data_folder) if os.path.isdir(os.path.join(data_folder,datadir))]
    valid_data_dirs = []
    valid_folder_names = []
    # only get valid folders (those with at least one .nwb file)
    for folder in data_folder_dirs:
        files = os.listdir(folder)
        valid = True
        for file_ in files:
            if file_[-4:] != '.nwb':
                valid = False
                break
        if valid:
            valid_data_dirs.append(folder)
            valid_folder_names.append(os.path.split(folder)[1])

    return valid_data_dirs,valid_folder_names

if __name__ == "__main__":
    printIntro()
    folderdirs,foldernames = getValidFoldersAndNames()
    selected_foldername = listRequest(foldernames,"Data Folder")
    selected_folderdir = folderdirs[foldernames.index(selected_foldername)]
    files_to_analyze = [os.path.join(selected_folderdir,file_) for file_ in os.listdir(selected_folderdir)]

    # get type of data
    '''
    dclasses = ['Raw Data (units)','Transformed Data (uV)']
    '''

    # get analysis type
    atypes = ['Sliding','Binned']
    selected_atype = listRequest(atypes,"Analysis Type")

    # get bin size from user
    bin_percentage = 0
    while not bin_percentage: # get bin num for user
        nbins_input = input("Enter percent of data for windowsize (1-99): ")
        input_int = readIntFromStr(nbins_input,1,99)
        if input_int:
            bin_percentage = input_int # minimum 1 bin

    for filename in files_to_analyze: # run through each file
        # would like for this to be threaded
        pdb.set_trace
        t,data = OpenHDF5Data(filename)
        t,cleanedData = preprocessECoGData(t,data)
        num_samples = np.shape(cleanedData)[0]
        binSize = int((bin_percentage/100.0) * num_samples) # size per bin in samples
        nBins = math.ceil(num_samples / binSize)
        # bin and get stats
        if selected_atype == 'Binned':
            for bin_i in range(nBins):
                t,bindata = getBinFromData(t,cleanedData,binSize,bin_i)
                std,var = runBasicStats(t,bindata)
                stds.append(std); variances.append(var)
        elif selected_atype == 'Sliding':
            for i in range(num_samples):
                stds,variances = getSlidingWindowStats(t,cleanedData,binSize)
                
        # Plot some stuff
        plt.figure()
        plt.plot(np.arange(nbins)+1,stds)
        plt.title("Standard Deviation Over Time (Window Size = {} seconds)".format(binSize/SAMPLE_RATE_HZ))
        plt.xlabel("Seconds or something")
        plt.ylabel("Some kind of electrode recording data.")