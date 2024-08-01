import sys,re,os
import requests
CONFIGS = {
     "url": "https://sm.ms/api/v2/upload",
     "authorization": "KWHgboKXa4gI2xx1vGsnKYw7sQ45Ij8Y",
 }
 
def upload_image(image_path):
    print(image_path)
    headers = {"Authorization": CONFIGS.get("authorization")}
    files = {"smfile": open(image_path, "rb")}
    response = requests.post(CONFIGS.get("url"), files = files, headers = headers).json()
    return response["data"]["url"]

def upload_markdown(mdfile_path):
    with open(mdfile_path,'r',encoding='utf-8') as f:
        content=f.read()
    re1=r'\(.*jpg\)|\(.*jpeg\)|\(.*png\)'
    images=re.findall(re1,content)
    for item in images:
        item=item.replace("(","").replace(")","")
        itempath=os.path.dirname(mdfile_path)+"/"+item
        print(itempath)
        newjpg=upload_image(itempath)
        print(newjpg)
        content=content.replace(item,newjpg)
    with open(mdfile_path,'w',encoding="utf-8") as f:
        f.write(content)
    print("OK!")


def main(argv):
     args = iter(argv)
     next(args)
     for image_path in args:
         print(upload_image(image_path))

if  __name__=='__main__':
    #file="C:/youdaoMD/BBS/images/000503_2008-01-15_D.jpg"
    mdfile="C:/youdaoMD/BBS/晋静卦_002173_2015-07-31_9162.md"
    #url=upload_image(file)
    #print(url)
    upload_markdown(mdfile)

