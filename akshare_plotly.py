import akshare as ak
from   datetime import datetime, timedelta,date
import pandas as pd
import plotly.graph_objects as go
from   plotly.subplots import make_subplots
import re
import random
import os,shutil
import  sxtwl

Gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
Zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


gua_list = ["乾","坤","屯","蒙","需","讼","师","比","小畜","履","泰","否","同人","大有","谦","豫","随","蛊","临","观",
"噬嗑","贲","剥","复","无妄","大畜","颐","大过","坎","离","咸","恒","遁","大壮","晋","明夷","家人","睽",
"蹇","解","损","益","夬","姤","萃","升","困","井","革","鼎","震","艮","渐","归妹","丰","旅","巽","兑","涣",
"节","中孚","小过","既济","未济"]

def isGua(string1):  
    if string1.strip in gua_list:
        return True
    else:
        return False

def getGuaFromTitle(string):
    index1=string.find("之")
    if index1>=0:
        name1=string[index1-1:index1]
        name2=string[index1+1:index1+2]
        if name1 not in gua_list:
            name1=string[index1-2:index1]
        if name2 not in gua_list:
            name2=string[index1+1:index1+3]
        if name1 in gua_list  and name2 in gua_list:
            return name1+"之"+name2
        else:
            return "NULL"
    index2=string.find("静卦")
    if index2>0:
        name3=string[index2-1:index2]
        if name3  not in gua_list:
            name3=string[index2-2:index2]
        if name3 in gua_list:
            return name3+"静卦"
        else:
            return "NULL"
    return "NULL"
        

def getGuaName(contents):   #给扫描信息用
    re1=r'[天|地|火|水|雷|风|泽|山]{2}[^\x00-\xff]{1,2}|乾为天|震为雷|坎为水|兑为泽|巽为风|离为火|艮为山|坤为地'
    result=re.findall(re1,contents)
    #print(result)
    length=len(result)
    if length==0:
        return "NULL"  #这个图片没有卦存在
    for i in range(length):
        result[i]=result[i].strip()
        result[i]=re.sub("\W","",result[i])
        if '为' in result[i]:
            result[i]=result[i][0]
        else:
            result[i]=result[i][2:]
    if  length==1  or  result[0]==result[1]:
        text1=result[0]+'静卦'
    else:
        text1=result[0]+'之'+result[1]
        #百度OCR经常把夬识别成夫等等
    return text1.replace("夫","夬").replace("夹","夬").replace("顾","颐").replace("通","遁").replace("之之","之")
    #下一步排盘还是要增加卦的有效性稽查

def extractGuaName(title_content):
    guaName=getGuaFromTitle(title_content)
    if guaName=="NULL":
        guaName=getGuaName(title_content)
    return guaName

def get_trading_date():# 获取市场的交易时间
    trade_date = ak.tool_trade_date_hist_sina()['trade_date']
    trade_date = [d.strftime("%Y-%m-%d") for d in trade_date]
    return trade_date

def insertDizhi(x):
    list=['亥','子','丑','寅','卯','辰','巳','午','未','申','酉','戌']
    return list[x]

def  insertDizhiMonth(x):
    list1=['丑','寅','卯','辰','巳','午','未','申','酉','戌','亥','子']
    return list1[x-1]

def candleline(stock, startday, endday, labelday ,period="daily" ):
    # print("candleline begin, stock=:", stock)
    #formatted_date = datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
    if stock=="sh000001" or stock=="999999":   #上证指数
        data=ak.index_zh_a_hist("000001", period, start_date=startday, end_date=endday)
    elif  stock=="399006" or stock=="399005":   #index of shanghai
        data=ak.index_zh_a_hist(stock, period, start_date=startday, end_date=endday)
    elif stock.startswith("5") or stock.startswith("1") :  #ETF 
        data = ak.fund_etf_hist_em(stock, period, start_date=startday, end_date=endday)
    else:     #now is stock name
        data=ak.stock_zh_a_hist(stock, period, start_date=startday, end_date=endday )
    #data=ak.stock_zh_a_hist(symbol=stock, period="daily", start_date=startday, end_date=endday)
    stockname=findname_stock(stock)
    data = data.rename(columns = {'日期':'date', '开盘':'open', '收盘':'close', '最高':'high', '最低':'low', '成交量':'volume'})
    if data.empty: 
        print("这个股票已退市")
        return "alert.jpg"
    dt_all = pd.date_range(start=data['date'].iloc[0],end=data['date'].iloc[-1])
    dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
    trade_date=get_trading_date()
    dt_breaks = list(set(dt_all) - set(trade_date))   
    # Create subplots and mention plot grid size
    # 计算每天的地支，形成列表
    data['date']=pd.to_datetime(data['date'])
    data.set_index('date', inplace=True) 
    markday= datetime.strptime(labelday, "%Y%m%d").strftime("%Y-%m-%d")
    markday=pd.to_datetime(markday)
    if markday in data.index:
        pos= data.loc[markday, 'high']
    else:
        next_date = data.index[data.index > markday]
        if not next_date.empty:
            pos= data.loc[next_date[0], 'high'] # Ret
            markday=next_date[0]
    print(markday,pos)
    maxhigh=data['high'].max()
    minlow=data['low'].min()
    #print(maxhigh)
    #print(type(maxhigh))
    amp=(maxhigh-minlow)/minlow
    #to be used when adjust the scale of display dizhi and day
    if period=="daily":  #daily k line
       # data['day']=data['date'].dt.day
        data['day'] = data.index.strftime('%d').str.lstrip('0')
        origin=date(1990,12,19)
        day000=pd.to_datetime(origin)  
        data['days']=(data.index-day000).days
        data['days']=(data['days']-5)%12
        #print(data['days'])
        dizhi=data['days'].apply(insertDizhi) 
        period_chinese="日线"
    else:   #monthly k line
        #data['day']=data['date'].dt.month
        data['day'] = data.index.strftime('%m').str.lstrip('0')
       # print(data['day'])
        #data['day']=data['day'].astype(int)
        dizhi=data['day'].astype(int).apply(insertDizhiMonth) 
        period_chinese="月线"
    posDizhi=1-amp/12
    posDay=posDizhi-amp/12
    fig = go.Figure(data=[go.Candlestick(x=data.index, 
                            open=data["open"], high=data["high"],low=data["low"], close=data["close"], 
                            increasing_line_color= 'red', decreasing_line_color= 'green',
                            increasing_fillcolor='red', decreasing_fillcolor='green') ]
                   )                               
    fig.add_trace(go.Scatter(x=data.index,y=data.low*posDizhi,mode="text",name="地支",text=dizhi,textfont=dict(size=10,color="black"))
                 )
    fig.add_trace(go.Scatter(x=data.index,y=data.low*posDay,mode="text",name="日期",text=data['day'],textfont=dict(size=10,color="blue"))
                  )
    fig.add_annotation(x=markday, y=pos,xref='x',yref='y', text="", 
                       xanchor='right',yanchor='bottom',showarrow=True, arrowhead=1 , arrowsize=1, arrowwidth=2
                     )
    fig.update_layout(title_text=stock+stockname+"-"+period_chinese, title_x=0.2,title_y=0.99,title_font_color="black",title_font_size=12,
        showlegend=False, xaxis_rangeslider_visible=False, plot_bgcolor='white',  paper_bgcolor= 'white',width=400,height=300,
        xaxis = dict( showgrid = True, showticklabels = True,gridcolor='lightgrey' ),
        yaxis = dict( showgrid = True, showticklabels = True,gridcolor='lightgrey', ),
        margin=dict(l=20, r=10, t=10, b=30)
        )
    # Do not show OHLC's rangeslider plot 
    # 去除休市的日期，保持连续
    fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])
    fig.write_image("temp.jpg")
    #fig.show()  
    #print("drawing temp.jpg is ok")
    return "temp.jpg"

def drawDailyLine(secNum,dateOriginStr,time_period=30):
    #sec = '600166'    originStr='2022-11-10'      becuase the database is this format
    day0=datetime.strptime(dateOriginStr,"%Y-%m-%d").date()
    day1=day0-timedelta(days=5)
    day2=day0+timedelta(days=time_period)
    start=day1.strftime("%Y%m%d")
    end=day2.strftime("%Y%m%d")
    mark=datetime.strptime(dateOriginStr, "%Y-%m-%d").strftime("%Y%m%d")
    tempfile=candleline(stock=secNum,startday=start,endday=end, labelday=mark, period="daily")
    return tempfile
# 2024-7-5 修改这个函数，即将取消savefolder
def drawMonthLine(secNum,dateOriginStr):
    day0=datetime.strptime(dateOriginStr,"%Y-%m-%d").date()
    day1=day0-timedelta(days=100)
    day2=day0+timedelta(days=400)
    start=day1.strftime("%Y%m%d")
    end=day2.strftime("%Y%m%d")
    mark=datetime.strptime(dateOriginStr, "%Y-%m-%d").strftime("%Y%m%d")
    tempfile=candleline(stock=secNum,startday=start,endday=end, labelday=mark, period="monthly")
    return tempfile

def findname_stock(codestr):  #csv 文件中有股票和ETF名单，包括大盘与创业板代号
    df=pd.read_csv("e:/stock6yao/data/stock_and_etf.csv",dtype={0:"string",1:"string"})
    stocks = df.loc[df['code'] == codestr, 'name']
    if  stocks.empty:
        name="NULL"
    else:
        name=stocks.values[0] 
    return name

def findcode_stock(namestr):
    df=pd.read_csv("e:/stock6yao/data/stock_and_etf.csv",dtype={0:"string",1:"string"})
    stock_code = df.loc[df['name'].str.contains(namestr), 'code']
    if  stock_code.empty:
        code="NULL"
    else:
        code=stock_code.values[0]
    return code
    
def extractStockName(contents):
    code="NULL"
    name="NULL"
    re2=r'sh000001|000001.XSHG|大盘|上证|深成指|综指|沪深|沪市|沪指|股市'
    stockFind=re.findall(re2,contents)
    if stockFind:
        code="sh000001"
        name="上证指数"
        return code,name
    re0=r'创业板指|399006'
    stockFind=re.findall(re0, contents)
    if stockFind:
        code="399006"
        name="创业板"
        return code, name
    re1=r'中小板|399005'
    stockFind=re.findall(re1, contents)
    if stockFind:
        code="399005"
        name="中小板"
        return code, name
    re3=r'(?<![a-zA-Z])\d{6}(?![a-zA-Z])(?!\.)'
    stockFind=re.findall(re3,contents)
    #cleaned_stock_codes = [code for code in stock_codes if not any(re.search(code, link) for link in re.findall(r'img\d+\.jpg', sample_text))]
    if stockFind:
        re_img=r'images.+jpg|images.+.jpeg|images.+png'
        images=re.findall(re_img,contents)
        if len(images)>0:
            for imglink in images:
                if stockFind[0] in imglink:
                    return "NULL","NULL"
        code= stockFind[0]
        name=findname_stock(code)
        return code, name

    stock_df=pd.read_csv("e:/stock6yao/data/stock_and_etf.csv",dtype={0:"string",1:"string"})
    for stock_name in stock_df['name']:
        stock_name1=stock_name.replace("ST","").replace("*","")
        if  contents.find(stock_name1)>-1:
            #print("股票名字为:"+stock_name)
            stock_code=findcode_stock(stock_name1)
            return stock_code,stock_name
    return code,name

def getSubject(contents):
    #用了（）显得简洁，但是后面要拼接
    #reSub1=r'(求测内容|占问|男测|主题|起卦钥语|占事)(:|：)\s?.*'
    #reSub2=r'.*?(走势|行情|涨跌|一周|下周|短线|长线|中线|个月|趋势|财运)'
    reSub1=r'求测内容[:：]\s?.*|占[事问][:：]\s?.*|男测[:：]\s?.*|主题[:：]\s?.*|起卦钥语[:：]\s?.*|预测策项.*|占问事宜.*'
    reSub2=r'.*走势|.*行情|.*涨跌|.*一周|.*下周|.*短线|.*长线|.*中线|.*个月|.*趋势|.*财运|.*如何'
    subjectList1=re.findall(reSub1,contents)
    if len(subjectList1)>0:
        rightSubject=subjectList1[0].replace("占问","").replace("事宜","").replace("占事","").replace("男测","").replace("主题","").replace("占类","").replace("问","").replace(":","").replace("：","")
        rightSubject=rightSubject.replace("起卦钥语","").replace("求测内容","")
        rightSubject=rightSubject.lstrip()
        if len(rightSubject)>25:  #限制长度
            rightSubject=rightSubject[0:30]
        finalsub=rightSubject.replace("\xa0","").replace("\xad","-")
        return finalsub
    subjectList2=re.findall(reSub2,contents)
    if len(subjectList2)>0:
            finalsub=subjectList2[0].lstrip()
            if len(finalsub)>30:
                finalsub=finalsub[:30]
            return finalsub
    else:   #什么规则也不好用，就用第一行文字
        temp=contents[0:30].lstrip()
        temp=temp.split("\n")[0]
        finalsub=temp.replace("\xa0","").replace("\xad","-")
        if "image" in finalsub or finalsub=="":
            return "NULL"
        return finalsub

def isSubjectValid(title):
    string="行情_走势_今天_明天_本月_个月_年卦_全年_上证_大盘_涨跌_月底_周_线_涨_跌"
    list=string.split("_")
    for item in list:
        if title.find(item)>0:
            return True
    return False

    
def getDate(contents):
        re1=r'\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{1,2}-\d{1,2}|\d{4}/\d{1,2}/\d{1,2}'
        day=re.findall(re1,contents)
        #print(day)
        if len(day)==0:
            #date=getDateFromGanzi(contents)
            #return date
            return "NULL"
        else:
            daystr=day[0]
        try:
            if "年" in daystr:
                day0=datetime.strptime(daystr,"%Y年%m月%d日").date()
            elif  "/" in daystr:
                day0=datetime.strptime(daystr,"%Y/%m/%d").date()
            elif "-" in daystr:
                day0=datetime.strptime(daystr,"%Y-%m-%d").date()
        except ValueError:
            daystr=daystr[0:-1]
            return daystr
        normalDateStr=day0.strftime("%Y-%m-%d")
        return normalDateStr

def getDateOcr(contents):
    re1=r'\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{1,2}-\d{1,2}|\d{4}/\d{1,2}/\d{1,2}'
    day=re.findall(re1,contents)
    state=0
    if len(day)==0:
        date=getDateFromGanzi(contents)
        return date
    else:
        daystr=day[0]
    try:
        if "年" in daystr:
            day0=datetime.strptime(daystr,"%Y年%m月%d日").date()
        elif  "/" in daystr:
            day0=datetime.strptime(daystr,"%Y/%m/%d").date()
        elif "-" in daystr:
            day0=datetime.strptime(daystr,"%Y-%m-%d").date()
            state=3
    except ValueError:
        daystr=daystr[0:-1]
        if "年" in daystr:
            day0=datetime.strptime(daystr,"%Y年%m月%d日").date()
        elif  "/" in daystr:
            day0=datetime.strptime(daystr,"%Y/%m/%d").date()
        elif "-" in daystr:
            day0=datetime.strptime(daystr,"%Y-%m-%d").date()
    normalDateStr=day0.strftime("%Y-%m-%d")
    #print("Old Baidu:",normalDateStr)
    if state==3:  #百度识别问题，经常把日与时混在一起。增加地支时间判读正确否
        re_dh=r'-\d{2,4}[:：]'
        re_gz= r'.*旬空'
        dh=re.findall (re_dh,contents)
        gz=re.findall (re_gz, contents)
        if len(dh)>0 and len(gz)>0:
            dhstr=dh[0].replace("-","").replace(":","").replace("：","")
            hour_dz=gz[0][-4:-3]
            if len(dhstr)==2:
                day=dhstr[0:1]
            elif len(dhstr)==4:
                day=dhstr[0:2]
            else:
                hourstr=dhstr[1:]
                #index=Zhi.index(hour_dz)
                index=getZhiNum(hour_dz)
                zhinum=index*2
                if int(hourstr)==zhinum-1 or int(hourstr)==zhinum:
                    print("OK, that is OK")
                    day=dhstr[0]
                else:
                    hourstr=dhstr[2]
                    day=dhstr[0:2]
            h_index=normalDateStr.rindex("-")
            newstring=normalDateStr[0:h_index]+"-"+day
            normalDateStr=newstring
    #print("DATE by OCR: ", normalDateStr)
    return normalDateStr

def getZhiNum(str):
   #key_index = [key for key in Zhi_dic if Zhi_dic[key]==str]
   zhi_dic={0:"子", 1:"丑", 2:"寅", 3:"卯", 4:"辰", 5:"巳己已", 6:"午", 7:"未", 8:"申", 9:"酉", 10:"戌", 11:"亥"}
   for key,value in zhi_dic.items():
    if str in value:
        return key

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

def getDateFromGanzi(cont):
    re1=r'干.*时'
    strlist=re.findall(re1,cont)
    if len(strlist)==0:
        return "NULL"
    else:
        str=strlist[0]
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
            

if  __name__=='__main__':
    # code could be sh000001, 399006, 152919 like etf or pure stock
    file1=drawDailyLine("600028","2023-1-20")
    dst="C:/Users/wangy/Desktop/"+file1  
    shutil.copy(file1, dst)
    #print("desktop has a file named temp.jpg")
    #pic=candleline("002028", "20240601","20240729","20240710", period="daily" )