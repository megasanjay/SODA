# -*- coding: utf-8 -*-

# python module for Software for Organizing Data Automatically (SODA)

from os import listdir, stat, makedirs, mkdir
from os.path import isdir, isfile, join, splitext, getmtime, basename, normpath, exists, expanduser
import pandas as pd
from pandas import DataFrame
from time import strftime, localtime
from shutil import copy2
from blackfynn import Blackfynn
from configparser import ConfigParser
import threading
from glob import glob

### Global variables
curateprogress = ' '
curatestatus = ' '
curateprintstatus = ' '

userpath = expanduser("~")
configpath = join(userpath, '.blackfynn', 'config.ini')
submitdataprogress = ' '
submitdatastatus = ' '
submitprintstatus = ' '

### FEATURE #1: SPARC dataset organizer
# Organize dataset
def savefileorganization(table, pathsavefileorganization):
    # tablepd = pd.read_html(table)[0]
    # tablepd.to_excel("test.xlsx")
    try:
        # soup = BeautifulSoup(table, 'lxml')
        # f = open("dict.txt","w")
        # f.write(soup)
        # f.close()
        return table
    except Exception as e:
        raise e

### FEATURE #2: SPARC metadata generator

# Generate manifest.xlsx file in each subfolder of the dataset
# Automaticall fill out filename, timestamp (last modified), and file type info
def curatedataset(pathdataset, createnewstatus, pathnewdataset, \
        manifeststatus, submissionstatus, pathsubmission, datasetdescriptionstatus, pathdescription, \
        subjectsstatus, pathsubjects, samplesstatus, pathsamples):

    global curateprogress
    global curatestatus
    global curateprintstatus
    curateprogress = ' '
    curatestatus = ''
    curateprintstatus = ' '
    error = ''
    c = 0

    if not isdir(pathdataset):
        curatestatus = 'Done'
        error = error + 'Error: Please select a valid dataset folder\n'
        c += 1

    if createnewstatus:
        if not isdir(pathnewdataset):
            curatestatus = 'Done'
            error = error + 'Error: Please select a valid folder for new dataset\n'
            c += 1

    if submissionstatus:
        if not isfile(pathsubmission):
            curatestatus = 'Done'
            error = error + 'Error: Select valid path for submission file\n'
            c += 1
        # Adding check for correct file name
        if splitext(basename(pathsubmission))[0] != 'submission':
            curatestatus = 'Done'
            error = error + 'Error: Select valid name for submission file\n'
            c += 1

    if datasetdescriptionstatus:
        if not isfile(pathdescription):
            curatestatus = 'Done'
            error = error + 'Error: Select valid path for dataset description file\n'
            c += 1
        # Adding check for correct file name
        if splitext(basename(pathdescription))[0] != 'dataset_description':
            curatestatus = 'Done'
            error = error + 'Error: Select valid name for dataset_description file\n'
            c += 1

    if subjectsstatus:
        if not isfile(pathsubjects):
            curatestatus = 'Done'
            error = error + 'Error: Select valid path for subjects file\n'
            c += 1
        # Adding check for correct file name
        if splitext(basename(pathsubjects))[0] != 'subjects':
            curatestatus = 'Done'
            error = error + 'Error: Select valid name for subjects file\n'
            c += 1

    if samplesstatus:
        if not isfile(pathsamples):
            curatestatus = 'Done'
            error = error + 'Error: Select valid path for samples file\n'
            c += 1
        # Adding check for correct file name
        if splitext(basename(pathsamples))[0] != 'samples':
            curatestatus = 'Done'
            error = error + 'Error: Select valid name for samples file\n'
            c += 1

    if c > 0:
        error = error+'\nTerminating ..'
        raise Exception(error)
        return
    #get list of file in pathnewdataset
    # see if any of submission, dataset_description, subjects, samples exist
    # Show error 'File xxx already exists at target location: either delete or select "None" in the SODA interface'
    if not createnewstatus:
        c = 0
        error = ''
        for i in glob(pathdataset + '\*'):
            if i == join(pathdataset, 'submission.xlsx') and submissionstatus:
                error = error + 'submission file already present\n'
                c += 1
            if i == join(pathdataset, 'dataset_description.xlsx') and datasetdescriptionstatus:
                error = error + 'dataset_description file already present\n'
                c += 1
            if i == join(pathdataset, 'samples.xlsx') and samplesstatus:
                error = error + 'samples file already present\n'
                c += 1
            if i == join(pathdataset, 'subjects.xlsx') and subjectsstatus:
                error = error + 'subjects file already present\n'
                c += 1

        if c > 0:
            error = error + 'Either delete or select "None" in the SODA interface\n\n'
            error = error + 'Terminating ..'
            curatestatus = 'Done'
            raise Exception(error)
            return

    try:
        curateprogress = 'Started'
        curateprintstatus = 'Curating'
        if createnewstatus:
            topath = createdataset(pathdataset, pathnewdataset)
            curateprogress = curateprogress + ', ,' + 'New dataset created'
            pathdataset = topath
        else:
            curateprogress = curateprogress + ', ,' + "New dataset not requested"

        if manifeststatus:
            createmanifest(pathdataset)
            curateprogress = curateprogress + ', ,' + 'Manifest created'
        else:
            curateprogress = curateprogress + ', ,' + 'Manifest not requested'

        if submissionstatus:
            copyfile(pathsubmission, pathdataset)
            curateprogress = curateprogress + ', ,' + 'Submission file created' + pathnewdataset
        else:
            curateprogress = curateprogress + ', ,' + 'Submission file not requested'

        if datasetdescriptionstatus:
            copyfile(pathdescription, pathdataset)
            curateprogress = curateprogress + ', ,' + 'Dataset description file created'
        else:
            curateprogress = curateprogress + ', ,' + 'Dataset description file not requested'

        if subjectsstatus:
            copyfile(pathsubjects, pathdataset)
            curateprogress = curateprogress + ', ,' + 'Subjects file created'
        else:
            curateprogress = curateprogress + ', ,' + 'Subjects file not requested'

        if samplesstatus:
            copyfile(pathsamples, pathdataset)
            curateprogress = curateprogress + ', ,' + 'Samples file created'
        else:
            curateprogress = curateprogress + ', ,' + 'Samples file not requested'

        curateprogress = curateprogress + ', ,' + 'Success: COMPLETED!'
        curatestatus = 'Done'

    except Exception as e:
        curatestatus = 'Done'
        raise e


def curatedatasetprogress():
    global curateprogress
    global curatestatus
    global curateprintstatus
    return (curateprogress, curatestatus, curateprintstatus)

def createmanifest(datasetpath):
    # Get the names of all the subfolder in the dataset
    folders = [folder for folder in listdir(datasetpath) if
               isdir(join(datasetpath, folder))]

    # In each subfolder, generate a manifest file
    for folder in folders:
        # Initialize dataframe where manifest info will be stored
        df = DataFrame(columns=['filename', 'timestamp', 'description',
                                'file type', 'Additional Metadata…'])
        # Get list of files/folders in the the folde#
        # Remove manifest file from the list if already exists
        folderpath = join(datasetpath, folder)
        allfiles = listdir(folderpath)
        if 'manifest.xlsx' in allfiles:
            allfiles.remove('manifest.xlsx')

        # Populate manifest dataframe
        filename = []
        timestamp = []
        filetype = []
        for file in allfiles:
            filepath = join(folderpath, file)
            filename.append(splitext(file)[0])
            lastmodtime = getmtime(filepath)
            timestamp.append(strftime('%Y-%m-%d %H:%M:%S',
                                      localtime(lastmodtime)))
            if isdir(filepath):
                filetype.append('folder')
            else:
                fileextension = splitext(file)[1]
                if not fileextension:  #if empty (happens for Readme files)
                    fileextension = 'None'
                filetype.append(fileextension)

        df['filename'] = filename
        df['timestamp'] = timestamp
        df['file type'] = filetype

        # Save manifest as Excel sheet
        manifestfile = join(folderpath, 'manifest.xlsx')
        df.to_excel(manifestfile, index=None, header=True)


def createdataset(frompath, topath):
    datasetfoldername = basename(normpath(frompath))
    topath = join(topath, datasetfoldername)
    topath = return_new_path(topath)
    copytree(frompath, topath)
    return topath

def return_new_path(topath):
    """
    This function checks if the folder already exists and in such cases, appends the name with (2) or (3) etc.
    """
    if exists(topath):
        for i in range(2, 20001):
            if not exists(topath + ' (' + str(i) + ')'):
                return topath + ' (' + str(i) + ')'

def copytree(src, dst, symlinks=False, ignore=None):
    if not exists(dst):
        makedirs(dst)
    for item in listdir(src):
        s = join(src, item)
        d = join(dst, item)
        if isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not exists(d) or stat(s).st_mtime - stat(d).st_mtime > 1:
                copy2(s, d)

def copyfile(src, dst):
    copy2(src, dst)



#createdataset(r'C:\Users\Bhavesh\Desktop\test_dataset', r'C:\Users\Bhavesh\Desktop\new_dataset')

# Generate master manifest.xlsx file in the main dataset folder

# Save project information required for submission.xlsx
# in an Excel file


# Save investigator profile required for dataset_description.xlsx
# in an Excel file


# Generate new submission.xlsx based on existing one


# Generate new dataset_description.xlsx based on existing one


# Convert Excel to csv


# Convert Excel to json


### FEATURE #4: SODA Blackfynn interface
# Log in to Blackfynn
def bfaddaccount(keyname, key, secret):
    error, c = '', 0
    keyname = keyname.strip()
    if (not keyname) or (not key) or (not secret):
        raise Exception('Error: Please enter valid keyname, key, and/or secret')

    if (keyname.isspace()) or (key.isspace()) or (secret.isspace()):
        raise Exception('Error: Please enter valid keyname, key, and/or secret')

    bfpath = join(userpath, '.blackfynn')
    #Load existing or create new config file
    config = ConfigParser()
    if exists(configpath):
        config.read(configpath)
        if config.has_section(keyname):
            raise Exception('Error: Key name already exists')
    else:
        if not exists(bfpath):
            mkdir(bfpath)
        if not exists(join(bfpath, 'cache')):
            mkdir(join(bfpath, 'cache'))

    #Add new account
    config.add_section(keyname)
    config.set(keyname, 'api_token', key)
    config.set(keyname, 'api_secret', secret)

    with open(configpath, 'w') as configfile:
        config.write(configfile)

    #Check key and secret are valid, if not delete account from config
    try:
        bf = Blackfynn(keyname)
        with open(configpath, 'w') as configfile:
            config.write(configfile)
        return 'Sucesss: added account ' + str(bf)
    except:
        bfdeleteaccount(keyname)
        raise Exception('Authentication Error: please check that key name, key, and secret are entered properly')

def bfdeleteaccount(keyname):
    config = ConfigParser()
    config.read(configpath)
    config.remove_section(keyname)
    with open(configpath, 'w') as configfile:
        config.write(configfile)

def bfaccountlist():
    accountlist = ['Select']
    if exists(configpath):
        config = ConfigParser()
        config.read(configpath)
        accountname = config.sections()
        accountnamenoglobal = [n for n in accountname if n != "global"]
        if accountnamenoglobal:
            for n in accountnamenoglobal:
                try:
                    bfn = Blackfynn(n)
                    accountlist.append(n)
                except:
                    print('removing', n)
                    config.remove_section(n)
            with open(configpath, 'w') as configfile:
                config.write(configfile)

    return accountlist

# Visualize existing dataset in the selected account
def bfdatasetaccount(accountname):
    try:
        bf = Blackfynn(accountname)
        dataset_list = ['Select dataset']
        for ds in bf.datasets():
            dataset_list.append(ds.name)
        return dataset_list
    except Exception as e:
        raise e

# Add new empty dataset folder
def bfnewdatasetfolder(datasetname, accountname):
    error, c = '', 0
    datasetname = datasetname.strip()
    if (not datasetname):
        error = error + 'Error: Please enter valid dataset folder name'
        c += 1

    if (datasetname.isspace()):
        error = error + 'Error: Please enter valid dataset folder name'
        c += 1

    try:
        bf = Blackfynn(accountname)
    except Exception as e:
        error = error + 'Error: Please select a valid Blackfynn account'
        c += 1

    dataset_list = []
    for ds in bf.datasets():
        dataset_list.append(ds.name)
    if datasetname in dataset_list:
        error = error + 'Error: Dataset folder name already exists'
        c += 1
    else:
        bf.create_dataset(datasetname)
    if c>0:
        raise Exception(error)

# Submit dataset to selected account
def bfsubmitdataset(accountname, bfdataset, pathdataset):
    global submitdataprogress
    global submitdatastatus
    global submitprintstatus
    submitdataprogress = ' '
    submitdatastatus = ' '
    submitprintstatus = ' '
    error, c = '', 0

    try:
        bf = Blackfynn(accountname)
    except Exception as e:
        submitdatastatus = 'Done'
        error = error + 'Error: Please select a valid Blackfynn account'
        c += 1

    try:
        myds = bf.get_dataset(bfdataset)
    except Exception as e:
        submitdatastatus = 'Done'
        error = error + 'Error: Please select a valid Blackfynn dataset'
        c += 1

    if not isdir(pathdataset):
        #if not isdir(pathdataset):
        submitdatastatus = 'Done'
        error = error + 'Error: Please select a valid local dataset folder'
        c += 1
    if c>0:
        raise Exception(error)

    try:
        def calluploadfolder():
            global submitdataprogress
            global submitdatastatus
            submitdataprogress = "Started uploading to dataset %s \n" %(bfdataset)
            myds = bf.get_dataset(bfdataset)
            myfolder = myds.name
            mypath = pathdataset
            upload_structured_file(myds, mypath, myfolder)
            submitdataprogress = submitdataprogress + ', ,' + "Success: dataset and associated files have been uploaded"
            submitdatastatus = 'Done'

        submitprintstatus = 'Uploading'
        t = threading.Thread(target=calluploadfolder)
        t.start()
    except Exception as e:
        submitdatastatus = 'Done'
        raise e


def upload_structured_file(myds, mypath, myfolder):
    global submitdataprogress
    global submitdatastatus

    mypath = join(mypath)
    for f in listdir(mypath):
        if isfile(join(mypath, f)):
            submitdataprogress = submitdataprogress + ', ,' + "Uploading " + f + " in " + myfolder
            filepath = join(mypath, f)
            myds.upload(filepath)
            submitdataprogress = submitdataprogress + ',' + " uploaded"
        else:
            submitdataprogress = submitdataprogress + ', ,' +"Creating folder " + f
            mybffolder = myds.create_collection(f)
            myfolderpath = join(mypath, f)
            upload_structured_file(mybffolder, myfolderpath, f)

def submitdatasetprogress():
    global submitdataprogress
    global submitdatastatus
    global submitprintstatus
    return (submitdataprogress, submitdatastatus, submitprintstatus)

# Share dataset with Curation Team