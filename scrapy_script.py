# -*- coding: utf-8 -*-
import scrapy
import re
import json
import requests
from lxml import html
import idna
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError
from time import sleep
import random
import pickle
# from slitherlib.slither import Snake
import random

idna.idnadata.codepoint_classes['PVALID'] = tuple(
    sorted(list(idna.idnadata.codepoint_classes['PVALID']) + [0x5f0000005f])
)

class TestSpider(scrapy.Spider):
    name = 'test'
    allowed_domains = ['houzz.in']
    # start_urls = ['https://www.houzz.com/professionals/general-contractor']
    start_urls=['https://www.houzz.com/professionals/architects']
    # start_urls=['https://www.houzz.com/professionals/home-builders']
    # start_urls=['https://www.houzz.com/professionals/artist-and-artisan']
    category='Design-Build-Firms'
    # # start_urls=['https://www.houzz.in/professionals/searchDirectory?topicId=26721&query=Design-Build+Firms&location=india&distance=0&sort=4']
    pages = iter([_ for _ in range(15, 100,15)])
    # i = 0
    # proxy_pool=['139.59.62.255:8080','139.59.53.105:8080','223.31.117.243:80','139.59.61.229:8080']
    # req_proxy=''
    
    def list2str(self, info):
        s = ""
        for i in info:
            s += i.replace(",", "") + " , "
        return s

    def retrieve_nested_value(self,mapping,key_of_interest):
        mappings = [mapping]
        while mappings:
            mapping = mappings.pop()
            try:
                items = mapping.items()
            except AttributeError:
                # we didn't store a mapping earlier on so just skip that value
                continue

            for key, value in items:
                if key == key_of_interest:
    #                 yield value
                    
                    return value
                else:
                    # type of the value will be checked in the next loop
                    mappings.append(value)

     # def start_requests(self):
     #    test=feather.read_dataframe('design_links')

     #   return [ scrapy.http.Request(url = _) for _ in test.design_links ]

    # snake = Snake()
    # ip_addresses = snake.ips
    # user_agents = snake.uas
    # proxy=""
    def parse(self, response):
         # profile = response.xpath("//a[@data-compid='more']/@href").extract()
        # yield({'profile':profile})
        proxy=""
        p=response.xpath("//ul[@class='hz-pro-search-results mb0']//li")
        for plink in p:
            profile=plink.xpath(".//a[@itemprop='url']/@href").extract_first()
            
            # req=scrapy.http.Request(profile, callback=self.page_parse,dont_filter=True)
            # self.proxy=random.choice(self.ip_addresses)
            # req.meta['proxy']=self.proxy
            # yield req
            # sleep(1)

            yield scrapy.http.Request(profile, callback=self.page_parse,dont_filter=True)

        next_url = self.start_urls[0] + "/p/" + str(next(self.pages))

        # try:
        #     next_url="https://www.houzz.in"+response.xpath('//a[@class="hz-pagination-link hz-pagination-link--next"]//@href').extract_first()
        #     yield scrapy.http.Request(next_url,dont_filter=True)
        # except:
        #     next_url=""
        # try:
        #     next_url=self.start_urls[0]+'&p='+str(next(self.pages))
        # except:
        #     next_url="http://google.com"

        # self.i += 1
        # req1=scrapy.http.Request(next_url,dont_filter=True)
        # req1.meta['proxy']=self.proxy
        # yield req1
        yield scrapy.http.Request(next_url,dont_filter=True)

    def page_parse(self, response):

        ss = response.xpath("//script[@type='application/ld+json']/text()").extract() #ld+
        # file=open('data','wb')
        # pickle.dump(ss,file)
        # file.close()


        # res=self.retrieve_nested_value(mapping=ss,key_of_interest='pageDescriptionFooter')
        # res=res[res.find('{'):-res[::-1].find('}')]
        # res=res[:res.find(r',\n        "description":')]
        # ss=json.loads(res+'}')
        ss = json.loads(ss[0])[0]

        try:
            postalCode = ss['address']['postalCode']
        except:
            postalCode = ""

        try:
            streetAddress = ss['address']['streetAddress']
        except:
            streetAddress = ""

        try:
            url = ss['@id']
        except:
            url = ""

        try:
            country = ss['address']['addressCountry']
        except:
            country =" "
        try:
            city = ss['address']['addressLocality']
        except:
            city =" "

        try:
            state = ss['address']['addressRegion']
        except:
            state = " "

        company_name = ss['name']

        try:
            contact = self.list2str(info=response.xpath(
                "//div[contains(text(),'Contact Info:')]//following-sibling::div/text()").getall())
            contact=contact.replace(" , ","")
        except:
            contact =""

        try:    
            contact_address = self.list2str(info=response.xpath(
                "//div[contains(text(),'Contact Info:')]//following-sibling::div//span/text()").getall())
        except:
            contact_address=""

        try:   
            contact_city = response.xpath(
                "//div[contains(text(),'Contact Info:')]//following-sibling::div//a/text()").get()
        except:
            contact_city=""

        if contact_city is None:
            contact_city=""

        full_address = contact_address + contact_city

        try:
            name_first = contact.split(" ")[0]
        except:
            name_first=""

        try:
            name_middle = self.list2str(info=contact.split(" ")[1:-1])
        except:
            name_middle= ""

        try:
            name_last = contact.split(" ")[-1]
        except:
            name_last=""


        try:
            website = ss['url']
        except:
            website=" "

        if website.find('.')==-1:
            website=""
        elif len(re.findall('http',website))>1:
            http_part=website[:website.find('/')+2]
            if website[4]==':':
                website=website.replace('http://',"")
            else:
                website=website.replace('https://',"")
            website=http_part+website

        # try:
        #     website=re.findall('.+\.[^/]+',website)[0]
        # except:
        #     website=website

        # try:
        #     regex = r"(https://|http://)\w+\.\w+"
        #     website=re.match(regex,website).gropu()
        # except:
        #     website=website

        try:
            phone = ss['telephone']
            phone=str(re.sub('[^0-9+()]',"",phone))
        except:
            phone=" "

            
        email=" "
        try:
            pro_info=response.xpath("//span[@class='profile-meta__block hidden']/text()").extract()
            email= self.list2str(info=response.xpath("//span[@class='profile-meta__block hidden']/text()").re(r"[.a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+"))
        except:
            pro_info=""
            email=" "
        
        try:
            license_number=self.list2str(info=response.xpath("//div[contains(text(),'Number')]//following-sibling::div/text()").extract())
        except:
            license_number=""

        try:
            typical_job_cost=self.list2str(info=response.xpath("//div[contains(text(),'Typical')]//following-sibling::div/text()").extract())
        except:
            typical_job_cost=""

        
        if not re.search('[0-9]+',typical_job_cost):
            typical_job_cost=""
        else:
            typical_job_cost = str(typical_job_cost)


        try:
            review_value = ss['aggregateRating']['ratingValue']
        except:
            review_value = '0'

        try:
            review_count = ss['aggregateRating']['reviewCount']
        except:
            review_count = '0'

        awards = response.xpath(
            "//div[contains(text(),'Award')]//following-sibling::div//img/@alt | div[contains(text(),'Awards')]//following-sibling::div//img/@alt").extract()
        award_count = len(awards)
        awards_list = self.list2str(info=awards)

        badge = response.xpath(
            "//div[contains(text(),'Badge')]//following-sibling::div//img/@alt | div[contains(text(),'Badges')]//following-sibling::div//img/@alt").extract()
        badge_count = len(badge)
        badge_list = self.list2str(info=badge)

        affi = response.xpath(
            "//div[contains(text(),'Affiliation')]//following-sibling::div//img/@alt | div[contains(text(),'Affiliations')]//following-sibling::div//img/@alt").extract()
        affi_count = len(affi)
        affi_list = self.list2str(info=affi)

        try:
            followers=response.xpath("//div[@class='follow-stats']//em/text()").extract()[0]
        except:
            followers=''

        try:
            following=response.xpath("//div[@class='follow-stats']//em/text()").extract()[1]
        except:
            following=''


        alts = response.xpath(
            "//div[@class='text-center']//img/@alt").extract()
        links = response.xpath(
            "//div[@class='text-center']//a/@href").extract()

        ext_link = {
                    'Facebook':'',
                    'Twitter':'',
                    'Youtube':'',
                    'Instagram':'',
                    'Linkedin':'',
                    'Pinterest':''    
                    }


        if email is not None:
            if email.find('@')==-1: 
                try:
                    email=re.findall(r"[.a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",website)
                    email=self.list2str(info=email)
                except:
                    email=' '


        for _ in range(len(alts)):
            name = alts[_]
            
            offset=2
            if followers=="":
                offset-=1
            if following=="":
                offset-=1
            
            link=links[_+offset]

            ext_link[name.split("Find me on ")[1].replace(" ","")] = link
        #     print(f'{name.split("Find me on ")[1]} => {link}')


        web_link={
                'Facebook':' ',
                    'Twitter':' ',
                    'Youtube':' ',
                    'Instagram':' ',
                    'Linkedin':' ',
                    'Pinterest':' '
        }

        
        url_status=''
        if email.find('@')==-1:
            url_status='404'
        else:
            url_status='Opened and Listed'

        data= {
              'Houzz Primary Category':self.category,
              'Houzz Company Name': company_name,
              'Houzz URL': url,
              'Houzz Phone Number': phone,
              'Houzz Website' : website,
              'Houzz - Full Address': full_address,
              'Houzz - Street': streetAddress,
              'Houzz - City': city,
              'Houzz - State': state,
              'Houzz - Postal Code/Pin code': postalCode,
              'Houzz - Country': country,
              'Houzz - Data Under "Professional Information"': pro_info,
              'Houzz-License Number': license_number,
              'Houzz - Awards':str(award_count) + " => " + awards_list,
              'Houzz - Badges':str(badge_count) + " => " + badge_list,
              'Houzz - Affiliations': str(affi_count) + " " + affi_list,
              'Houzz - Number of Reviews': review_count,
              'Houzz - Review Rating': review_value,
              'Houzz - Followers': followers,
              'Houzz - Following': following,
              'Houzz - Typical Job Costs': typical_job_cost,
              'Houzz - Contact': contact,
              'Houzz - Contact First Name': name_first,
              'Houzz - Contact Middle Name': name_middle,
              'Houzz - Contact Last Name': name_last,
              'Houzz - Facebook':ext_link['Facebook'],
              'Houzz - Instagram':ext_link['Instagram'],
              'Houzz - Twitter':ext_link['Twitter'],
              'Houzz - Linkedin':ext_link['Linkedin'],
              'Houzz - Youtube':ext_link['Youtube'],
              'Houzz - Pinterest':ext_link['Pinterest'],
              'Website Searched': website,
              'email on Website' : email,
              'Mobile/Cellphone on Website':phone,
              'Website - Facebook' : web_link['Facebook'],
              'Website - Instagram' : web_link['Instagram'],
              'Website - Twitter' : web_link['Twitter'],
              'Website - Linkedin' : web_link['Linkedin'],
              'Website - Youtube' : web_link['Youtube'],
              'Website - Pinterest' : web_link['Pinterest'],
              'url_status':url_status
              }

        if email.find('@')==-1:
            if website.find('.')!=-1:
                if website.find('facebook')==-1:
                    req=scrapy.http.Request(website,callback=self.success,meta=data,errback=lambda failure , item=data: self.on_error(failure,item),dont_filter=True)
                    req.meta['download_timeout']=20
                    yield req# yield scrapy.http.Request(website,callback=self.success,meta=data,errback=self.on_error,dont_filter=True)
                else:
                    yield scrapy.http.Request(website,callback=self.web_facebook,meta=data,errback=lambda failure , item=data: self.on_error(failure,item),dont_filter=True)
            else:
                yield data
        else:
            response.meta['url_status']=' Opened and Listed'
            yield data

    def success(self,response):
        
        web_link={
        'Facebook':' ',
        'Twitter':' ',
        'Youtube':' ',
        'Instagram':' ',
        'Linkedin':' ',
        'Pinterest':' '
        }
        

        try:
            web_link['Facebook']=response.xpath("//*[contains(@href,'facebook.com')]/@href").extract_first()
        except:
            web_link['Facebook']=""
            

        try:
            web_link['Instagram']=response.xpath("//*[contains(@href,'insta')]/@href").extract_first()
        except:
            web_link['Instagram']=""
            

        try:
            web_link['Linkedin']=response.xpath("//*[contains(@href,'linked')]/@href").extract_first()
        except:
            web_link['Linkedin']=""
            

        try:
            web_link['Twitter']=response.xpath("//*[contains(@href,'twitter')]/@href").extract_first()
        except:
            web_link['Twitter']=""
            

        try:
            web_link['Youtube']=response.xpath("//*[contains(@href,'youtube')]/@href").extract_first()
        except:
            web_link['Youtube']=""
            

        try:
            web_link['Pinterest']=response.xpath("//*[contains(@href,'pinterest')]/@href").extract_first()
        except:
            web_link['Pinterest']=""
            

        
       
        email= self.list2str(info=response.xpath("//text()").re(r"[.a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+"))

        k=re.finditer(r"[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+\.(?!(jpg|png))",email)
        mails=[]
        for _ in k:
            s=_.start()
            e=_.end()
            temp=(email[s:e+4])
            #mail_set.add(mail[s:e+4])
            if temp not in mails:
                mails.append(temp)
        email=self.list2str(info=mails)
        
        if email is not None:
            if email.find('@')==-1:
                try:
                   # email=response.xpath("//*[contains(@href,'@')]/@href  | //*[contains(text(),'@')]/@href").extract_first()
                    email=response.xpath("//*[contains(@href,'@')]/@href  | //*[contains(text(),'@')]/@href").extract()
                    email1=response.xpath("//*[contains(@href,'@')]/text()  | //*[contains(text(),'@')]/text()").extract()
                    email.extend(email1)
                    
                    email_refined=[]
                    for i,e in enumerate(email):
                        try:
                            email_refined.append(re.findall("[.a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",e)[0])
                        except:
                            pass

                    email=self.list2str(info=email_refined)
                except:
                    email=' '

        if email is not None:        
            if email.find('@')==-1:
                protected=None
                try:
                    protected=response.xpath("//*[contains(@href,'email') and contains(@href,'protect')]//@href").extract_first()
                    email=protected+'@'
                except:
                    email=' '
                    protected = None
                if protected is not None:
                    response.meta['url_status']='email protected'

        # if email is not None:
        #     if email=="":
        #         try:
        #             email=response.xpath(+"//a[contains(@href,'mail')]/@href").extract_first()
        #         except:
        #             pass

        

        # phone=self.list2str(info=response.xpath("//text()").re("[0-9]{1,3}[-\s]{0,1}[0-9-\s]{10,16}"))

        # regex=re.compile(r'[\n\r\t,]')
        # phone=regex.sub("",phone)

        if response.meta.get('email on Website').find('@')==-1 and email.find('@')!=-1 and email is not None:
            response.meta['email on Website'] = email

        response.meta['Mobile/Cellphone on Website'] = ""

        response.meta['Website - Facebook']=web_link['Facebook']
        response.meta['Website - Instagram'] = web_link['Instagram']
        response.meta['Website - Twitter'] = web_link['Twitter']
        response.meta['Website - Linkedin'] = web_link['Linkedin']
        response.meta['Website - Youtube'] = web_link['Youtube']
        response.meta['Website - Pinterest'] = web_link['Pinterest']

        if email is not None:
            if email.find('@')==-1:
                try:
                    # contactus=response.xpath("//a[contains(@href,'ontact') or contains(text(),'ontact')]/@href").extract_first()
                    # contactus=response.urljoin(contactus)
                    # yield scrapy.http.Request(contactus,callback=self.contactus_page,meta=response.meta,errback=lambda failure , item=response.meta: self.on_error(failure,item))
                    
                    contactus=response.xpath("//a[contains(@href,'ontact')]//@href | //a[contains(text(),'ontact')]//@href").extract()
                    contact=[]
                    for _ in contactus:
                        c=response.urljoin(_)
                        if re.search(r'(?<=\w\/)[\/\w\-\.]+$',c):
                            contact.append(c)

                    contact=list(set(contact))

                    # # for c in contact:
                    if contact and contact is not None:
                        yield scrapy.http.Request(contact[0],callback=self.contactus_page,meta=response.meta,errback=lambda failure , item=response.meta: self.on_error(failure,item),dont_filter=True)
                    else:
                        response.meta['url_status']=' Opened and Not Listed'
                        yield response.meta
                except:
                    response.meta['url_status']=' Opened and Not Listed'
                    yield response.meta
            else:
                response.meta['url_status']=' Opened and Listed'
                yield response.meta
        else:
            try:
                # contactus=response.xpath("//a[contains(@href,'ontact') or contains(text(),'ontact')]/@href").extract_first()
                # contactus=response.urljoin(contactus)
                # yield scrapy.http.Request(contactus,callback=self.contactus_page,meta=response.meta,errback=lambda failure , item=response.meta: self.on_error(failure,item))
                
                contactus=response.xpath("//a[contains(@href,'ontact')]//@href | //a[contains(text(),'ontact')]//@href").extract()
                contact=[]
                for _ in contactus:
                    c=response.urljoin(_)
                    if re.search(r'(?<=\w\/)[\/\w\-\.]+$',c):
                        contact.append(c)

                contact=list(set(contact))

                # # for c in contact:
                if contact and contact is not None:
                    yield scrapy.http.Request(contact[0],callback=self.contactus_page,meta=response.meta,errback=lambda failure , item=response.meta: self.on_error(failure,item),dont_filter=True)
                else:
                    response.meta['url_status']=' Opened and Not Listed'
                    yield response.meta
            except:
                response.meta['url_status']=' Opened and Not Listed'
                yield response.meta

    def contactus_page(self,response):
        

        email= self.list2str(info=response.xpath("//text()").re(r"[.a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+"))

        k=re.finditer(r"[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+\.(?!(jpg|png))",email)
        mails=[]
        for _ in k:
            s=_.start()
            e=_.end()
            temp=(email[s:e+4])
            #mail_set.add(mail[s:e+4])
            if temp not in mails:
                mails.append(temp)
        email=self.list2str(info=mails)
        
        if email is not None:        
            if email.find('@')==-1:
                try:
                    # email=response.xpath("//*[contains(@href,'@')]/@href  | //*[contains(text(),'@')]/@href").extract_first()
                    email=response.xpath("//*[contains(@href,'@')]/@href  | //*[contains(text(),'@')]/@href").extract()
                    email1=response.xpath("//*[contains(@href,'@')]/text()  | //*[contains(text(),'@')]/text()").extract()
                    email.extend(email1)
                    
                    email_refined=[]
                    for i,e in enumerate(email):
                        try:
                            email_refined.append(re.findall("[.a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",e)[0])
                        except:
                            pass

                    email=self.list2str(info=email_refined)
                except:
                    email=' ' 


        if email is not None:
            if email.find('@')==-1:
                protected=None
                try:
                    protected=response.xpath("//*[contains(@href,'email') and contains(@href,'protect')]//@href").extract_first()
                    email=protected+'@'
                except:
                    email=' '
                    protected = None
                if protected is not None:
                    response.meta['url_status']='email protected'
        # if email is not None:
        #     if email=="":
        #         try:
        #             email=response.xpath("//a[contains(@href,'mail')]/@href").extract_first()
        #         except:
        #             pass

        # phone=self.list2str(info=response.xpath("//text()").re("[0-9]{1,3}[-\s]{0,1}[0-9-\s]{10,16}"))

        # regex=re.compile(r'[\n\r\t,]')
        # phone=regex.sub("",phone)
        if response.meta.get('email on Website').find('@')==-1:# and response.meta.get('url_status')!='email protected':
            response.meta['email on Website'] = email

        if response.meta.get('url_status')!='email protected':
            if email.find('@')!=-1:
                 response.meta['url_status']=' Opened and Listed'
            elif str(response.status)>'350':
                 response.meta['url_status']=' 404'
            else:
                response.meta['url_status']=' Opened and not Listed'

        response.meta['Mobile/Cellphone on Website'] = " "
        yield response.meta



    def errback_httpbin(self, failure):
            # log all errback failures,
            # in case you want to do something special for some errors,
            # you may need the failure's type
            self.logger.error(repr(failure))

            #if isinstance(failure.value, HttpError):
            if failure.check(HttpError):
                # you can get the response
                response = failure.value.response
                self.logger.error('HttpError on %s', response.url)

            #elif isinstance(failure.value, DNSLookupError):
            elif failure.check(DNSLookupError):
                # this is the original request
                request = failure.request
                self.logger.error('DNSLookupError on %s', request.url)

            #elif isinstance(failure.value, TimeoutError):
            elif failure.check(TimeoutError):
                request = failure.request
                self.logger.error('TimeoutError on %s', request.url)


    def on_error(self,failure,item):
        # item['url_status']='404'
        # yield item
        failure.request.meta['url_status']='404'
        yield failure.request.meta

    def web_facebook(self,response):
        try:
            about=response.xpath("//a[contains(@href,'bout')]/@href | //a[contains(text(),'bout')]/@href").extract_first()
            if about.find('https://www.facebook.com/')==-1:
                about="https://www.facebook.com/"+about
            yield scrapy.http.Request(about,callback=self.about_facebook,meta=response.meta,errback=lambda failure , item=response.meta: self.on_error(failure,item),dont_filter=True)
        except:
            yield response.meta


    def about_facebook(self,response):
       

        email=response.xpath("//a[contains(@href,'mail')]/div/text()").extract_first()

        if email.find('@')!=-1:
            
            try:
                details=response.xpath("//div[@class='_50f4']/text()").extract()
            except:
                details=''

            phone=""
            try:
                # if details[0].find('Call')!=-1:
                #     phone=details[0]

                for d in details:
                    if d.find("Call")!=-1:
                        phone=str(d)
                    else:
                        pass
            except:
                phone=""

            website=""
            try:
                # if details[2].find("http")!=-1:
                #     website=details[2]

                for d in details:
                    if d.find("http")!=-1:
                        website=d
                    else:
                        pass
            except:
                website=""

            try:
                if details[1].find('@')!=-1 and email=="":
                    email=details[1]
            except:
                pass

            if phone:
                phone=str(re.sub('[^0-9]',"",phone))
            response.meta['email on Website'] = email
            response.meta['Mobile/Cellphone on Website'] = phone
            response.meta['Website Searched'] = website

        if email.find('@')==-1:
            try:
                email=response.xpath("//*[contains(@href,'@')]/text() | //*[contains(text(),'@')]/text()").extract_first()
                email=re.findall("[.a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",email)
                email=self.list2str(info=email)
            except:
                pass

        if email.find('@')!=-1:
            response.meta['url_status']='Opened and Listed'
        else:
            response.meta['url_status']='Opened and Not Listed'

        

        yield response.meta


