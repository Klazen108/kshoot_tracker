import os
import sys
import ntpath
from os.path import join as pjoin
import shutil
import subprocess
import codecs
import re

#import gmk_analysis module
#sys.path.insert(0, 'GMKResourceAnalyzer')
#import gmk_analysis

#function child_dirs
##Returns all child directories in the parent directory
#param parent_path: the directory to scan
def child_dirs(parent_path):
    return [d for d in os.listdir(parent_path) if os.path.isdir(pjoin(parent_path,d))]

#function child_files
##Returns all child filenames in the parent directory
#param parent_path: the directory to scan
def child_files(parent_path):
    return [f for f in os.listdir(parent_path) if os.path.isfile(pjoin(parent_path,f))]

#gets the leaf node name of the path, or in other words, the filename or the directory name
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def main():
    #get project file path and ensure it exists
    found = False
    if len(sys.argv)>1:
        ksh_dir = sys.argv[1]
    else:
        ksh_dir = input('Enter the project folder: ')
    
    if not os.path.exists(ksh_dir):
        print('Folder '+ksh_dir+' doesn\'t exist! Please try again.')
        sys.exit(-1)
    
    entries = []
    
    songs_dir = pjoin(ksh_dir,'songs')
    score_dir = pjoin(ksh_dir,'score')
    for cur_group in child_dirs(songs_dir):
        for cur_folder in child_dirs(pjoin(songs_dir,cur_group)):
            print("song: "+cur_group+"/"+cur_folder)
            ksh_files = (f for f in child_files(pjoin(songs_dir,cur_group,cur_folder)) if f.endswith(".ksh"))
            for file in ksh_files:
                #print("found: "+cur_group+"/"+cur_folder+"/"+file)
                with codecs.open(pjoin(songs_dir,cur_group,cur_folder,file),encoding='utf-8') as f:
                    diff = ""
                    lvl = 0
                    title = ""
                    score = 0
                    for line in f.readlines():
                        if (line.startswith("difficulty=")):
                            diff = line.split('=')[1].replace("\n","").replace("\r","")
                        elif (line.startswith("level=")):
                            lvl = int(line.split('=')[1].replace("\n","").replace("\r",""))
                        elif ("title=" in line):
                            title = line.split('=')[1].replace("\n","").replace("\r","")
                        if diff and lvl and title:
                            print('{:>2} {} '.format(lvl,diff),end="")
                            score_file = pjoin(score_dir,"PLAYER",cur_group,cur_folder,file.replace("ksh","ksc"))
                            if os.path.exists(score_file):
                                with codecs.open(score_file,encoding='utf-8') as scf:
                                    for scline in scf.readlines():
                                        if scline.rstrip():
                                            m = re.search(r"on=(\d+),",scline)
                                            if m:
                                                print (m.groups()[0],end="")
                                                score = int(m.groups()[0])
                                            #else:
                                            #    print("no score".format(score_file),end="")
                            #else:
                            #    print("no score".format(score_file),end="")
                            entries.append((title,cur_group,lvl,diff,score))
                            break
                    print()
    print("all songs analyzed, printing results:")
    sorted_entries = sorted(entries,key=lambda t: (t[2],t[0]),reverse=True)
    for entry in sorted_entries:
        print(u"{:>9} {:>2} [{:0>8}] {}   ({})".format(entry[3],entry[2],entry[4],entry[0],entry[1]))
if __name__ == "__main__":
    main()