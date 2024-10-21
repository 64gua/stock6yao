# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 13:43:24 2024

@author: Robert
"""
import datetime
import os,re,shutil, csv
import akshare_plotly as akPlot


def test_os_function():
    #pdf_file_path = "C:/youdaoPDF/uiaudsf/iojaiodfs/大壮之泰test.pdf"
    dir="C:/youdaoMD/易经测市"
    os.chdir(dir)
    for file in os.listdir(dir):
        filename,ext=os.path.splitext(file)
        if ext=="":
            print(file)
            newfile=file+".html"
            os.rename(file,newfile)
    #filename, ext = os.path.splitext(file1)
    #file=os.path.basename(file1)
    #print(filename,"ext", ext, "file", file)

    #file2=os.path.split(pdf_file_path)[-1]
    #print("split name:",file2)
    #above 2 are same
    #list=os.path.split(pdf_file_path)
    #dir=os.path.dirname(pdf_file_path)
    
    #filename, ext = os.path.splitext(pdf_file_path)
    #mdFolder="c:/youdaoMD/易经测市/测股卦例v3"
    #image1="./images/demo.jpg"
    #image2="../images/demo.jpg"
    #filepath1=os.path.join(mdFolder,image1)
    #filepath2=os.path.join(mdFolder,image2)
    #print(filepath1)
    
    #print(filepath2)
    #os.makedirs(mdFolder, exist_ok=True)
    #os.makedirs(mdFolder+"/images", exist_ok=True)
    #os.makedirs(mdFolder+"/tests", exist_ok=True)
 
def filenames_no_ext(targetDir):
    list=[]
    for file in os.listdir(targetDir):
       # if file.endswith(".md") or file.endswith(".pdf") or file.endswith(".note")
       if file.endswith(".pdf") :
            name=os.path.splitext(file)[0]
            list.append(name)
    return list

def similar():
    mddir="c:/youdaoMD/BBS/images/"
    oldfiles=os.listdir(mddir)
    newfile="sh000001_2010-12-29_D.jpg"
    posnew=newfile.rindex("_")
    for file in oldfiles:
        posold=file.rindex("_")
        if file[0:posold] == newfile[0:posnew] and file != newfile:
            print(file,file[:posold])
            print(newfile,newfile[:posnew])
            # Delete the old picture
            #os.remove(os.path.join(folder_path, file))
            print(f"to be Deleted {file}")


def if_it_diff(folder_samll,folder_big,tempdir):
    purename_small = filenames_no_ext(folder_samll)
    #print(purename_small)
    purename_big = filenames_no_ext(folder_big)
    i=0
    for file_small in purename_small: 
        if file_small not in purename_big:
            print("differt numbers: ", i)
            i+=1
            file_diff=folder_samll+"/"+file_small+".md"
            mddst=tempdir+"/"+file_small+".md"
           # copy those jpg files within md 
            with open(file_diff, 'r',encoding="utf-8") as file:
                file_content=file.read()
                r1=r'images.+.[png|jpg|jpeg|gif]'
                images=re.findall(r1, file_content)
                #print(i, images)
                for imagefile in images:
                    fullimage=dir_a+"/"+imagefile
                    imagedst=tempdir+"/"+imagefile
                    #print(i,file_diff,imagefile)
                    shutil.copy(fullimage, imagedst)
            #copy md file to tempdir
            shutil.copy(file_diff,mddst)
                    

def if_it_same(folder_samll,folder_big,tempdir):
    purename_small = filenames_no_ext(folder_samll)
    purename_big = filenames_no_ext(folder_big)
    purename_big=os.listdir(folder_big)
    i=0
    for file_small in purename_small: 
        if file_small not in purename_big:
            print("same numbers: ", i)
            i+=1
            file_same=folder_samll+"/"+file_small+".md"
            print(i, file_small)
            if i>20:
                return

def if_it_same_list(list_file,folder_big):
    # if txt file, use f.readline()
    list_small=[]
    with open(list_file, newline='',encoding="utf-8") as f:
        reader=csv.reader(f)
        for row in reader:
            name=row[0][:-4]
            list_small.append(name)
    files_big=[]
    for file in os.listdir(folder_big):
       # if file.endswith(".md") or file.endswith(".pdf") or file.endswith(".note")
       if file.endswith(".pdf") :
            name=os.path.splitext(file)[0]
            files_big.append(name)
    size2=len(files_big)
    print("big is:", len(files_big))
    same_list=[]
    diff_list=[]
    i=0
    for small in list_small: 
        i=i+1
        findstate=0
        j=0
        for big in files_big:
            j+=1
            #if  files_big[j].find(file_small)!=-1 :
            if small in big: 
                findstate=1
                same_list.append(small)
                break
            else:
                continue
        if findstate==0:
            diff_list.append(small)
            print("******,different*****:",small)
    print("CSV has files :",len(list_small))
    print("相同文件数目:", len(same_list))
    print("不同文件数目：",len(diff_list))
   # print("differt files is :",diff_list )

def is_name_exist(filename,folder_big="c:/youdaoPDF/418down/易经测市/测股卦例/"):
    #folder_big default="c:/youdaoPDF/418down/易经测市/测股卦例/"
    filesmall=filename.replace(".pdf","")
    files_big=[]
    for file in os.listdir(folder_big):
       if file.endswith(".pdf") :
            name=os.path.splitext(file)[0]
            files_big.append(name)
    print("big folder has files number:", len(files_big))
    state=0
    for big in files_big:
        if filesmall in big:
            state=1
            break
    return state
    
def changeName(path):
    os.chdir(path)
    i=0
    for filename in os.listdir(path):
        i=i+1
        if ".note" in filename:
            newfilename=filename.replace(".note","v2.md")
        #print(newfilename)
            os.rename(filename,newfilename)
            print(i,filename, newfilename)
    print("OK! finished! ")

def find_md_only_pics(dir):  #有些文件只有图片，需要找出来处理，再进数据库
    print("curent dir:",os.getcwd())
    i=0
    for oldfile in os.listdir(dir):
        if oldfile.endswith(".md"):
            oldfile=CURRENT_DIR+oldfile
            with open(oldfile, 'r', encoding="utf-8") as f:
                cont=f.read()
            totallen=len(cont)
            re1=r'images.+jpg|images.+.jpeg|images.+png'
            images=re.findall(re1,cont)
            len_ims=0
            if images:
                for imgname in images:
                    len_ims+=len(imgname)
                if totallen<len_ims+13:
                    #print(totallen,"vs", len_ims)
                    #print(imgname,len(imgname))
                    print(oldfile,i," only pics")
                    i+=1
                    oldfile_basename=os.path.basename(oldfile)
                    newfile=CURRENT_DIR+"ST"+oldfile_basename
                    os.rename(oldfile, newfile)
                    print("this file renamed to :", newfile)
    print("all the files has been changed ok!")

def find_md_only_pics_2(dir):  #有些文件只有图片，需要找出来处理，再进数据库
    print("curent dir:",os.getcwd())
    i=0
    for oldfile in os.listdir(dir):
        if oldfile.endswith(".md"):
            oldfile=CURRENT_DIR+oldfile
            with open(oldfile, 'r', encoding="utf-8") as f:
                cont=f.read()
            if cont.find("妻财")==-1 and cont.find("旬空")==-1:
                print(i, oldfile)
                oldfile_basename=os.path.basename(oldfile)
                newfile=CURRENT_DIR+"PT"+oldfile_basename
                os.rename(oldfile, newfile)
                print(i, "  renamed to :", newfile)
                i=i+1
    print("all the files has been renamed ok!")

def batchChangeContent(path):
    for file_name in os.listdir(path):
        if file_name.endswith('.md'):
            file_name=path+"/"+file_name
            with open(file_name,'r',encoding='utf-8') as file:
                file_content=file.read()
            new_content=file_content.replace("c:/youdaoMD/测股卦例v3/","")
            #print(new_content)
            with open(file_name,'w',encoding='utf-8') as file:
                file.write(new_content)
            print(f'{file_name}文件替换完成。' )
    print("all the works done......")

    
def create_html_table(rows):
        html = "<table>"
        for row in rows:
            html += "<tr>"
            for cell in row:
                html += "<td> {} </td>".format(cell)
            html += "</tr>"
        html += "</table>"
        return html
    
def add_csv_with_sz(file,newfile):
    with open(file, newline='',encoding="utf-8") as f:
        reader=csv.reader(f)
        for row in reader:
            code=row[0]
            newcode="sz"+code
            name=row[1]
            list=[newcode,name]
            with open(newfile, 'a', newline='',encoding="utf-8" ) as csvfile:
                writer=csv.writer(csvfile)
                writer.writerow(list)

def replaceMdInfo(dir):
    #os.chdir(dir)
    i=0
    for file in os.listdir(dir):
        file=dir+"/"+file
        if file.endswith(".md"):
            with open(file, 'r',encoding="utf-8") as f:
                cont=f.read()
            index=cont.find(".md")
            if index>=0:
                mdinfo=cont[0:index+3]
                #newcont=cont.replace(mdinfo,"")
                #with open(file,"w",encoding="utf-8") as f:
                #    f.write(newcont)
                print(i,file)
                i=i+1
    print("everything is finished")

def replace_blank(dir):
    os.chdir(dir)
    for file in os.listdir(dir):
        if file.startswith("nulldate_"):
            with open(file,'r',encoding="utf-8") as f:
                cont=f.read()
            num=cont.count("\n")
            if num>25:
                print(dir+"/"+file)
            newcont=cont.replace("\n","")
            with open(file,'w',encoding="utf-8") as f:
                f.write(newcont)
            newfilename=file.replace("nulldate_","DateOK_")
            os.rename(file,newfilename)
            print("rename:", file,newfilename )
    print("OK!")

def findFileChanged(dir):  #文件一部分转换成功，还有没成功的，区分开来。
    os.chdir(dir)
    print("OK1")
    i=0
    for file in os.listdir(dir):
        if file.startswith("D"):
            #file_path=CURRENT_DIR+file
            filesta=os.stat(file)
            current_date=datetime.datetime.fromtimestamp(filesta.st_mtime)
            date_string = current_date.strftime('%Y-%m-%d %H:%M:%S')
            if date_string[0:10]!="2024-07-24":
                i=i+1
                newfile=file.replace("D","K")
                os.rename(file,newfile)
                print("rename is OK!")

def moveJpgDown(dir):
    os.chdir(dir)
    i=0
    for file in os.listdir(dir):
        if file.endswith(".png"):
            i+=1
            mdfile=file.replace(".png",".md")
            with open(mdfile,'w',encoding="utf-8") as f:
                mdlink=f"![](images/{file})"
                f.write(mdlink)
            new_file_path="images/"+file
            os.rename(file,new_file_path)
            print(i, "move to images")
    print("finished!")

CURRENT_DIR="D:/Markdown/易经测市"

if __name__ == "__main__":
    #list_file="c:/youdaoPDF/pdf_csv/part5_treated_v1_file_list.csv"
    #dir_big="C:/youdaoPDF/418down/易经测市/测股卦例/"
   # dir=CURRENT_DIR
    #replaceMdInfo(dir)
    #getInfofromMdtoCsv(dir)
    changeName(CURRENT_DIR)
    #file1="C:/youdaoMD/测股卦例v3/nulldate_家人之蛊_大通燃气一个月走势_兄化财&财化父&子化父_.md"
    #replace_blank(dir)
    #test_os_function()

