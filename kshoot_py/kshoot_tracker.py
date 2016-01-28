import os
import sys
import ntpath
from os.path import join as pjoin
import shutil
import subprocess
import codecs
import re
import datetime
import json

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


def main():
    #get project file path and ensure it exists
    found = False
    if len(sys.argv)>1:
        ksh_dir = sys.argv[1]
    else:
        ksh_dir = input('Enter the project folder: ')
    if len(sys.argv)>2:
        o_file = sys.argv[2]
    else:
        o_file = "output.json"
    
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
                    percent = 0
                    is_uc = 0
                    is_puc = 0
                    rank = ""
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
                                            data = scline.split(",")
                                            m = re.search(r"on=(\d+)",data[5])
                                            if m:
                                                print (m.groups()[0],end="")
                                                score = int(m.groups()[0])
                                                rank = int(data[7])
                                                if   (rank==5): rank="AAA"
                                                elif (rank==4): rank="AA"
                                                elif (rank==3): rank="A"
                                                elif (rank==2): rank="B"
                                                elif (rank==1): rank="C"
                                                else:           rank="D"
                                                percent = int(data[8])
                                                is_uc = (data[12]=="1")
                                                is_puc = (data[13]=="1")
                            entries.append({"title":title,"group":cur_group,"level":lvl,"diff":diff,"score":score,"rank":rank,"percent":percent,"uc":is_uc,"puc":is_puc})
                            break
                    print()
    print("all songs analyzed, printing results:")
    with codecs.open(o_file,"w",encoding='utf-8') as of:
        sorted_entries = sorted(entries,key=lambda t: (t["level"],t["title"]),reverse=True)
        of.write(json.dumps(sorted_entries))
        print("process complete!")
if __name__ == "__main__":
    main()