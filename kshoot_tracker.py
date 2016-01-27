import os
import sys
import ntpath
from os.path import join as pjoin
import shutil
import subprocess
import codecs
import re
import datetime

html_prelude = """
<html>
    <head>
        <meta charset="utf-8" />
        <style type="text/css">
            body {{
                background: #000;
                color: #FFF;
                font-family: Helvetica Neue,Helvetica,sans-serif;
            }}
            table {{
                border-collapse: collapse;
            }}
            table, th, td {{
                border: 1px solid white;
            }}
            tr.played {{
                background: #440;
            }}
            tr.passed {{
                background: #040;
            }}
            tr.uc {{
                background: #404;
            }}
            tr.puc {{
                background: #400;
            }}
        </style>
    </head>
    <body>
        Generated on {} using Klazen's K-Shoot Tracker Tool!
        <table>
            <tr><th>Difficulty</th><th>Level</th><th>Score</th><th>Title</th><th>Folder</th><th>C</th></tr>
            <tr>
""".format(datetime.date.today())

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
        o_file = "output.html"
    
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
                                                percent = int(data[8])
                                                is_uc = (data[12]=="1")
                                                is_puc = (data[13]=="1")
                            entries.append((title,cur_group,lvl,diff,score,percent,is_uc,is_puc))
                            break
                    print()
    print("all songs analyzed, printing results:")
    with codecs.open(o_file,"w",encoding='utf-8') as of:
        of.write(html_prelude)
        sorted_entries = sorted(entries,key=lambda t: (t[2],t[0]),reverse=True)
        for entry in sorted_entries:
            #of.write(u"{:>9} {:>2} [{:0>8}] {}   ({})".format(entry[3],entry[2],entry[4],entry[0],entry[1]))
            class_text = ""
            score = entry[4]
            percent = entry[5]
            is_uc = entry[6]
            is_puc = entry[7]
            clear_text = ""
            if score>0:
                if percent<70:
                    class_text=" class='played' "
                else:
                    if is_puc:
                        class_text=" class='puc' "
                        clear_text="PUC"
                    elif is_uc:
                        class_text=" class='uc' "
                        clear_text="UC"
                    else:
                        class_text=" class='passed' "
                        clear_text="C"
            of.write(u"<tr"+class_text+u"><td>{}</td><td>{}</td><td>{:0>8}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(entry[3],entry[2],entry[4],entry[0],entry[1],clear_text))
        of.write("</tr></body></html>")
        print("process complete!")
if __name__ == "__main__":
    main()