import requests
import threadpool
import time
import os
import re
from lxml import etree
from lxml.html import tostring

class ScrapDemo():
    next_page_url=""    #下一页的URL
    page_num=1  #当前页
    detail_url_list=0 #详情页面URL地址list
    deepth=0 #设置抓取的深度
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36"
    }
    fileNum=0
    def __init__(self,url):
        self.scrapyIndex(url)

    def threadIndex(self,urllist): #开启线程池
        if len(urllist) == 0:
            print("请输入需要爬取的地址")
            return False
        ScrapDemo.detail_url_list=len(urllist)
        pool=threadpool.ThreadPool(len(urllist))
        requests=threadpool.makeRequests(self.detailScray,urllist)
        for req in requests:
            pool.putRequest(req)
            time.sleep(1)
        pool.wait()

    def detailScray(self,url): #抓取数据
        if not url == "":
            url='http://xiaohua.zol.com.cn/{}'.format(url)
            res=requests.get(url,headers=ScrapDemo.headers)
            html=res.text
            element=etree.HTML(html)
            divEle=element.xpath("//div[@class='article-text']")[0]
            self.downloadText(divEle)

    def downloadText(self,ele): #保存到txt文件
        clist = ele.xpath("p/text()")
        for index in range(len(clist)):
            '''
                正则表达式：过滤空格或换行符
            '''
            clist[index]=re.sub(r'(\t|\r)+','',clist[index])
        content="".join(clist)
        basedir=os.path.dirname(__file__)
        filePath=os.path.join(basedir)
        filename="xiaohua{0}-{1}.txt".format(ScrapDemo.deepth,str(ScrapDemo.fileNum))
        file=os.path.join(filePath,"..","file",filename)
        try:
            f=open(file,"w")
            f.write(content)
            print("下载success!")
            if ScrapDemo.fileNum == (ScrapDemo.detail_url_list - 1):
                print("下载完成")
                if not ScrapDemo.next_page_url == "" and ScrapDemo.deepth < 10:
                    self.scrapyIndex(ScrapDemo.next_page_url)

        except Exception as err:
            print("Error:%s" % str(err))

        ScrapDemo.fileNum=ScrapDemo.fileNum+1

    def scrapyIndex(self,url): #基本抓取
        if not url == "":
            ScrapDemo.fileNum=0
            ScrapDemo.deepth=ScrapDemo.deepth+1
            print("开启第{0}页抓取".format(ScrapDemo.page_num))
            res=requests.get(url,headers=ScrapDemo.headers)
            html=res.text
            element=etree.HTML(html)
            a_urllist=element.xpath("//a[@class='all-read']/@href")
            next_page=element.xpath("//a[@class='page-next']/@href")
            if not len(next_page) == 0:
                ScrapDemo.next_page_url='http://xiaohua.zol.com.cn/{}'.format(next_page[0])
                ScrapDemo.page_num=ScrapDemo.page_num+1

            self.threadIndex(a_urllist[:2])