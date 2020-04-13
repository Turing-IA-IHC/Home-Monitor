"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly recognizersmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Module to generate components and more.
"""

__version__ = "1.0.0"

import sys, getopt
import os.path
import shutil

def help():
    print('Correct way to use commander depends of command')
    print('\n --- To start system use start (s) and components start value --- ')
    print('     like: s value')
    print('     Values:')
    print('         components = 0  # Message no one component')
    print('         components = 1  # Only pool')
    print('         components = 2  # Only load controller')
    print('         components = 3  # Pool + load controller')
    print('         components = 4  # Only Recognizers')
    print('         components = 5  # Pool + Recognizers')
    print('         components = 6  # Load controller + Recognizers')
    print('         components = 7  # Pool + Load controller + Recognizers')
    print('         components = 8  # Only Adnormal events')
    print('         components = 15 # All components')
    print("     Example: 'hm s 9' to load data pool and the analyzers.")
    print('\n --- To create new component use generator (g) --- ')
    print('     like: g type name ')
    print('     Types:')
    print('         c|controller: To cerate a new Controller component')
    print('         r|recognizer: To cerate a new Recognizer component')
    print('         a|analyzer: To cerate a new Analizer component')
    print('         n|channel: To cerate a new Channel component')
    print("     Example: 'hm g r humanFall' this will generate a Recognizer component named 'humanFallRecognizer' and place it in Recognizers folder.")

def startSystem(components:int, vars):
    """ Start Home-Monitor systems """
    sys.path.insert(0, './Core/')
    from main import main as mainHM
    mainHM(components , vars)

def createComponent(me_type, me_name):
    path = os.path.normpath(me_type + "s" + "/" + me_name)
    if not os.path.exists(path):
        # Folder and files creation
        base = os.path.normpath("Templates/New" + me_type)
        shutil.copytree(base, path)
        oriName = os.path.normpath(path + "/New" + me_type + ".py")
        newName = os.path.normpath(path + "/" + me_name + ".py")
        os.rename(oriName, newName)
        # Replace into files
        with open(newName,'r') as file:
            filedata = file.read()
            filedata = filedata.replace('New' + me_type, me_name)
        with open(newName,'w') as file:
            file.write(filedata)

        with open(os.path.normpath(path + "/config.yaml"),'r') as file:
            filedata = file.read()
            filedata = filedata.replace('New' + me_type, me_name)
        with open(os.path.normpath(path + "/config.yaml"),'w') as file:
            file.write(filedata)

        if me_type == 'Recognizer':
            oriName = os.path.normpath(path + "/training/01_train_New" + me_type + ".py")
            newName = os.path.normpath(path + "/training/01_train_" + me_name + ".py")        
            os.rename(oriName, newName)
            oriName = os.path.normpath(path + "/training/02_test_New" + me_type + ".py")
            newName = os.path.normpath(path + "/training/02_test_" + me_name + ".py")
            os.rename(oriName, newName)
            
        print('Component {} created successfully in {}s folder'.format(me_name, me_type))
    else:
        print('Already exists a componet with same name')

def main(argv):

    if len(argv) == 0:
        help()
        sys.exit(0)

    if argv[0] in ['-h', 'h', '--help', 'help']:
        help()
        sys.exit(0)

    if argv[0] in ['-s', 's', '--start', 'start']:
        startSystem(int(argv[1]), argv[2:])
        sys.exit(0)

    if argv[0] in ['-g', 'g', '--generate', 'generate']:
        if len(argv) < 3:
            print ('Bad command args use -h to get help')
            sys.exit(2)
        ME_TYPE = ''
        if argv[1] in ['-c', 'c', '--controller', 'controller']:
            ME_TYPE = 'Controller'
        elif argv[1] in ['-r', 'r', '--recognizer', 'recognizer']:
            ME_TYPE = 'Recognizer'
        elif argv[1] in ['-a', 'a', '--analyzer', 'analyzer']:
            ME_TYPE = 'Analyzer'
        elif argv[1] in ['-n', 'n', '--channel', 'channel']:
            ME_TYPE = 'Channel'
        else:
            print ('Bad command args use -h to get help')
            sys.exit(2)

        ME_NAME = argv[2] + ME_TYPE
        createComponent(ME_TYPE, ME_NAME)
        sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])