import  sxtwl
import akshare_plotly as akPlot
import os,re

Gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
Zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def getGZ(gzStr):
    tg = -1
    dz = -1
    for i, v in enumerate(Gan):
        if gzStr[0]  == v:
            tg = i
            break
    for i, v in enumerate(Zhi):
        if  gzStr[1] == v:
            dz = i
            break
    return sxtwl.GZ(tg, dz)

def reverseDay(str):
    yearindex=str.find("年")
    year=str[yearindex-2:yearindex]
    monthindex=str.find("月")
    month =str[monthindex-2:monthindex]
    dayindex=str.find("日")
    day=str[dayindex-2:dayindex]
    hourindex=str.find("时")
    hour=str[hourindex-2:hourindex]
    list=[year,month,day,hour]
    #print(list)
    jds = sxtwl.siZhu2Year(getGZ(year), getGZ(month), getGZ(day), getGZ(hour), 1970, 2029)
    for jd in jds:
        t = sxtwl.JD2DD(jd )
        #print("符合条件的时间:%d-%d-%d %d:%d:%d"%(t.Y, t.M, t.D, t.h, t.m, round(t.s)))
        result=f'{t.Y}-{t.M}-{t.D}'
        #print(result)
        return result
        
def example():
# 四注反查 分别传的是年天干，月天干，日天干，时天干， 开始查询年，结束查询年  返回满足条件的儒略日数
    jds = sxtwl.siZhu2Year(getGZ('壬子'), getGZ('丁未'), getGZ('辛酉'), getGZ('己丑'), 1900, 2029)
    for jd in jds:
        t = sxtwl.JD2DD(jd )
        print("符合条件的时间:%d-%d-%d %d:%d:%d"%(t.Y, t.M, t.D, t.h, t.m, round(t.s)))

def findDate(dir):
    os.chdir(dir)
    i=0
    for file in os.listdir(dir):
        if file.startswith("DateOK"):
            i=i+1
            with open(file,'r',encoding="utf-8") as f:
                cont=f.read()
            day=akPlot.getDate(cont)
            if day=="NULL":
                print(i, file)
                re1=r'干.*时'
                result=re.findall(re1,cont)
                if len(result)==0:
                        print("no date-->:", dir+"/"+file)
                else:
                    day=reverseDay(result[0])
                    oldstr=result[0]
                    newstr=oldstr+"   "+day
                    print(newstr)
                    newcont=cont.replace(oldstr,newstr)
                    with open(file,"w",encoding="utf-8") as f:
                        f.write(newcont)
                    newfilename=file.replace("DateOK_","OK")
                    os.rename(file,newfilename)
            else:
                newfilename=file.replace("DateOK_","OK")
                os.rename(file,newfilename)


if __name__ == "__main__":
    teststr="  壬子年    丁未月   辛酉日     己丑时 "
    #day=reverseDay(teststr)
    #print(day)
    dir="C:/youdaoMD/测股卦例v3"
    findDate(dir)