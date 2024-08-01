import re,os
import akshare_plotly as akPlot
reSub1=r'(求测内容|占问|男测|主题|起卦钥语|占事)(:|：)?\s?(.*)'
re3=r'(?<![a-zA-Z])\d{6}(?![a-zA-Z])(?!\.)'
#matches=re.findall(reSub1,cont)
#if matches:
#    s=""
#    for match in matches[0]:
#        s=s+match
#    print(s)
#stock=re.findall(re3,cont)
#print(stock)
def repairBadPost(file):
    with open(file,'r',encoding='utf-8') as f:
        cont=f.read()
    newcont=re.sub(r'<br>=+<br>',"*****\n",cont)
    list=["青龙","白虎","朱雀","勾陈","螣蛇","玄武","旬","占","干","公历","六神"]
    for item in list:
        newcont=newcont.replace(item,"\n"+item)
    with open(file,'w',encoding='utf-8') as f:
        f.write(newcont)
    print("file corrected!")

def soManyBlank(dir):
    i=0
    for file in os.listdir(dir):
        i=i+1
        if file.endswith(".md"):
            filefull=dir+file
            with open(filefull,"r",encoding="utf-8") as f:
                cont=f.read()
            #num=cont.count("\n")
            newcont=re.sub(r'\n{2}',"\n",cont)
            with open(filefull,"w",encoding="utf-8") as f:
                f.write(newcont)
            print(i)

def html_to_md(dir):
    i=0
    for file in os.listdir(dir):
        i=i+1
        if file.endswith(".md"):
            filefull=dir+file
            with open(filefull,"r",encoding="utf-8") as f:
                cont=f.read()
            #num=cont.count("\n")
            newcont=re.sub(r'<.*>'," ",cont)
            newcont=newcont.replace("&nbsp;"," ")
            newcont=re.sub(r'\n{2}',"\n",newcont)
            print(newcont)
            list=["青龙","白虎","朱雀","勾陈","螣蛇","玄武","旬","占","干","公历","六神"]
            for item in list:
                newcont=newcont.replace(item,"\n"+item)
            #print(newcont)
            ok=input("OK! continue:")
            if ok=="o" or ok=="k":
                with open(filefull,"w",encoding="utf-8") as f:
                    f.write(newcont)
                #newname=dir+file.replace(".html",".md")
                #os.rename(filefull,newname)
                print(i)

def seperateTotalFile(file):
    dir=os.path.dirname(file)
    print(dir)
    with open(file,'r',encoding='utf-8') as f:
        content=f.read()
    content=content.replace("<br>","")
    i=0
    contList=content.split("*****")
    for cont in contList:
        subject=akPlot.getSubject(cont)
        guaName=akPlot.getGuaName(cont)
        subFile=dir+"/"+f'无名氏_{guaName}_{subject}.md'
        with open(subFile,'w',encoding='utf-8') as f:
            f.write(cont)
        print(i,"name=",subFile)
        #print(cont)
        i=i+1
        #if i>5:
        #    break
       


CURRENT_DIR="C:/youdaoMD/汇总案例/"

if __name__=='__main__':
    file="C:/youdaoMD/汇总案例/汇总卦1.md"
    seperateTotalFile(file)
    #repairBadPost(file)


