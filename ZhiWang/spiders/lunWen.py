# -*- coding: utf-8 -*-
import scrapy
import json
import time
from scrapy import Request
from ZhiWang import items

class LunwenSpider(scrapy.Spider):
    name = 'lunWen'
    allowed_domains = ['vpn.lzufe.edu.cn']

    def __init__(self):
        super().__init__()
        # 因为这个TWFID是通过软件获取的，所以是无法通过爬虫获取的，这里暂时没有什么好的解决方案，
        # 这里的方法是先登陆上软件，然后打开浏览器登陆一次，然后通过抓包手动获取里面的值
        self.cookies = {
            'AppCount': '1',
            'AppEnabled': '0',
            'EA_port': '54530',
            'haveLogin': '1',
            'IpEnabled': '0',
            'is_reminded': '1',
            'language': 'zh_CN',
            'LoginMode': '2',
            'remoteAppCount': '0',
            'scacheUseable': '0',
            'TWFID': '1002f7569c020015',
            'UsingDkey': '0',
            'webonly': '0',
            'websvr_cookie': '%zd'
        }

    def start_requests(self):
        """
        获取登陆后的cookie
        url必须在程序启动时通过手动抓包获取
        """
        yield scrapy.FormRequest(
            url="https://vpn.lzufe.edu.cn:8444/por/shortcut.csp?type=cs&destUrl=service.csp&id=1002f7569c020015&language=zh_CN&is_reminded=1&ea_port=54530",
            callback=self.parse_page,
        )

    def parse_page(self, response):
        """
        pagename	ASP.brief_default_result_aspx
        isinEn	1
        dbPrefix	SCDB
        dbCatalog	中国学术文献网络出版总库
        ConfigFile	SCDBINDEX.xml
        research	off
        t	1557235673377
        keyValue	食物
        S	1
        sorttype	

        """
        # print(response.text)
        url = "https://vpn.lzufe.edu.cn:8444/web/1/http/0/kns.cnki.net/kns/brief/brief.aspx?" \
              "pagename=ASP.brief_default_result_aspx&" \
              "isinEn=1&" \
              "dbPrefix=SCDB&" \
              "dbCatalog=中国学术文献网络出版总库&" \
              "ConfigFile=SCDBINDEX.xml&" \
              "research=off&" \
              "t="+ str(int(time.time() * 1000)) + "&" \
              "keyValue=美术&" \
              "sorttype"
        print(url)
        # url = "https://vpn.lzufe.edu.cn:8444/web/1/http/0/kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&isinEn=1&dbPrefix=SCDB&dbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&research=off&t=1557238267340&keyValue=%E9%A3%9F%E7%89%A9&S=1&sorttype"
        yield Request(
            url=url,
            cookies=self.cookies,
            callback=self.parse_detail,
        )

    def parse_detail(self, response):
        # print(response.text)
        index = 0
        for each in response.xpath('//a[@class="fz14"]'):
            title = each.xpath('./text()').extract()[0]
            paper_link = "https://vpn.lzufe.edu.cn:8444" + each.xpath('./@href').extract()[0]
            print(paper_link, title, sep="\n")
            """
            https://vpn.lzufe.edu.cn:8444/web/1/http/1/nvsm.cnki.net/kns/detail/detail.aspx?QueryID=16&CurRec=1&recid=&FileName=GXQG20190507000&DbName=CAPJDAY&DbCode=CJFQ&yx=Y&pr=&URLID=45.1385.TS.20190507.0955.002
            https://vpn.lzufe.edu.cn:8444/web/1/http/1/nvsm.cnki.net/kns/detail/detail.aspx?QueryID=16&CurRec=1&recid=&FileName=GXQG20190507000&DbName=CAPJDAY&DbCode=CJFQ&yx=Y&pr=&URLID=45.1385.TS.20190507.0955.002
            https://vpn.lzufe.edu.cn:8444/web/1/http/1/kns.cnki.net/KCMS/detail/45.1385.TS.20190507.0955.002.html?uid=WEEvREcwSlJHSldRa1FhdkJkVG1BSEJZaXlPU3cveWtHUTZMQnJlWmZRND0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!&v=MDIxNjBidVpxRmk3bVVMekFJRlk9SWpYYWFiRzRIOWpNcW85Q1pPc1BZdzlNem1SbjZqNTdUM2ZscVdNMENMTDdSN3Fl
            """
            yield scrapy.FormRequest(paper_link,cookies=self.cookies,callback=self.get_paper)
            if index>=1:
                break
            index+=1

    def get_paper(self, response):
        print(response.url)
        item = items.ZhiwangItem()
        caj_down = "https://vpn.lzufe.edu.cn:8444"+response.xpath('//div[@id="DownLoadParts"]/a[@id="cajDown"]/@href').extract()[0]
        pdf_down = "https://vpn.lzufe.edu.cn:8444"+response.xpath('//div[@id="DownLoadParts"]/a[@id="pdfDown"]/@href').extract()[0]
        item['caj_down'] = caj_down
        item['pdf_down'] = pdf_down
        print("caj_down:",caj_down)
        print("pdf_down:",pdf_down)
        # 将解析好的下载地址，交送给管道进行下载并保存
        yield item