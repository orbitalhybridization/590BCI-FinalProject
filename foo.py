import mne
import matplotlib.pyplot as plt
import numpy as np
import h5py
import os
import tqdm
import sys
import pdb
import math

"""
TODO
 - Get the conversion data from HDF5 files (why first dataset doesn't have it?)
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
    return t,data

def preprocessECoGData(t,data,sample_rate=SAMPLE_RATE_HZ):
    # probably would do some filtering and stuff
    print("\n Preprocessing ECoG Data...\n")
    return t,data

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

def showHDF5Headers(filename):
    print("\n Retrieving headers.. {}.\n".format(filename))
    current_file = h5py.File(filename,'r')
    return list(current_file.keys())

def readIntFromStr(str_input,min=1,max=-1):
    try:
        int_check = int(str_input)
        if int_check < min:
            if int_check > max and (max != -1):
                raise ValueError("\nInvalid number '{}' must be integer greater than {} and less than {}".format(nbins_input,min,max))
            else:
                raise ValueError("\nInvalid number '{}' must be integer greater than {}.".format(nbins_input,min))
        else:
            return int_check

    except Exception as e:
        pdb.set_trace()
        print("\nInvalid number '{}' (must be an integer)".format(str_input)) 
        print("Returned error: {}".format(e))

    return -1 # error

def printIntro():
    print("\n\n****************************************** \n Neural Stablity & Variability Analysis \n****************************************** \n\n")

if __name__ == "__main__":
    printIntro()
    files_to_analyze = []
    while not files_to_analyze: # populate files
        ans = input("Use all files in current folder (y/n)? ")
        if ans == "Y" or (ans == "y"):
            cwd = os.getcwd()
            files_to_analyze = [os.path.join(cwd,subdf) for subdf in os.listdir(cwd) if subdf[-4:] == '.nwb']
            #print("Ck: if pathing is correct\n"); pdb.set_trace()
        elif ans == "N" or (ans == "n"):
            print("No isn't really an option yet. Try Y to analyze or q to quit.\n")
        elif ans == "q" or (ans == 'Q'):
            print("Quitting program.\n")
            sys.exit()
        else:
            print("Please answer Y/N, or 'q' to quit.\n")

    # get header from user
    '''
    headers = showHDF5Headers(files_to_analyze[0])
    header = ''
    while not header:
        # show header options
        headers_request = "Header options\n-------------------"
        headers_list_formatted = ["\t [{num}] {name}\n" for num+1,name in enumerate(headers)]
        headers_list_formatted = ''.join(list_headers)
        print(headers_request + headers_list)
        print("--------------------------------------")
        # get user input for header
        header_input = input("\nPlease type index of header to use:")
        header_i = readIntFromStr(header_input,1,len(headers_list)) # input only indices of available headers
        if header_i:
            header = headers[header_i-1] # header will be one-off since list starts at 1
    '''

    # get bin size from user
    bin_percentage = 0
    while not bin_percentage: # get bin num for user
        nbins_input = input("Enter percent of data per bin (1-99): ")
        input_int = readIntFromStr(nbins_input,1,99)
        if input_int:
            bin_percentage = input_int # minimum 1 bin

    for filename in files_to_analyze: # run through each file
        # would like for this to be threaded
        t,data = OpenHDF5Data(filename)
        t,cleanedData = preprocessECoGData(t,data)
        num_samples = np.shape(cleanedData)[0]
        binSize = (bin_percentage/100.0) * num_samples # size per bin in samples
        nBins = math.ceil(num_samples / float(binSize))
        stds = []
        variances = []
        # bin and get stats
        for bin_i in range(nBins):
            t,bindata = getBinFromData(t,cleanedData,binSize,bin_i)
            std,var = runBasicStats(t,bindata)
            stds.append(std); variances.append(var)
        # Plot some stuff
        plt.figure()
        plt.plot(np.arange(nbins)+1,stds)
        plt.title("Standard Deviation Over Time (Bin Size = {} seconds)".format(binSize/SAMPLE_RATE_HZ))
        plt.xlabel("Seconds or something")
        plt.ylabel("Some kind of electrode recording data.")