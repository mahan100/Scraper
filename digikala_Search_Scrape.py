from multiprocessing.connection import wait
from socket import timeout
from time import sleep
import requests
import json
import pandas
import argparse
import numpy as np
import concurrent.futures

class scrape:
    def __init__(self,search,items):
        self.items=items
        self.proxy_available=[]
        self.url=f'https://api.digikala.com/v1/search/?q={search}&page='
        self.header={
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'en-US,en;q=0.5',
            'Connection':'keep-alive',
            'Host':'api.digikala.com',
            'Sec-Fetch-Dest':'document',
            'Sec-Fetch-Mode':'navigate',
            'Sec-Fetch-Site':'none',
            'Sec-Fetch-User':'?1',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'      
        }        
    def send_request(self,page):
        try:
          sleep(2)          
        #   response=requests.request('GET',self.url+f'{page}',headers=self.header,proxies={'http':proxy,'https':proxy},timeout=3)
          response=requests.request('GET',self.url+f'{page}',headers=self.header)
        except NameError as e:
            print(f'connecrion failed....\n{e}')
        
        print(f'page {page} recieved successfully.......' if response.status_code else f'page {page} failed......')
        return response.json()
        
    def get_data(self):
        end_page=np.ceil(self.items/20)
        end_item=self.items-(end_page-1)*20
        page=1
        data=self.send_request(page)
        data_final=[]
        index=20
        while len(data['data']['products'])!=0:
            max_len=len(data['data']['products'])
            if page==end_page:
                index=end_item if end_item<max_len else max_len
            # print(f'number of items in page = {page} = {max_len} and max_len={max_len} and end_item={end_item}')
            for i in range(0,int(index)):
                    title=data['data']['products'][i]['title_fa']
                    product_url='https://www.digikala.com/'+data['data']['products'][i]['url']['uri']
                    category=data['data']['products'][i]['data_layer']['category']
                    image_url=data['data']['products'][i]['images']['main']['url'][0]
                    rating=data['data']['products'][i]['rating']['rate']
                    price=data['data']['products'][i]['default_variant']['price']['selling_price']
                    columns=['title','product_url','category','image_url','rating','price']
                    values=[title,product_url,category,image_url,rating,price]
                    zipped=zip(columns,values)
                    dictionary=dict(zipped)
                    data_final.append(dictionary)
               
            page+=1
            if page>end_page:
                print(f'total rows = {len(data_final)}')
                break
            else:  
                data=self.send_request(page)
     
    
        df=pandas.DataFrame(data_final,columns=['title','product_url','category','image_url','rating','price'])    
        # print(df)
        return df
        
        
    def save_fulldata_json(self):
        result=self.send_request()
        with open('data.json', 'w', encoding='utf8') as json_file:
             json.dump(result,json_file, ensure_ascii=False)   
        print('jason fulldata stored in csv file successfully.....')          
    
    def save_csv(self):
        df=self.get_data()
        df.to_csv('file_csv.csv',sep=',',encoding='utf-8')
        print('data stored in csv file successfully.....')        
   
    @classmethod
    def start(cls,search,items):
        words=[]
        # for i in search.split():
        #     words.append(i)
        #     words.append('+')
        # search=''.join(words[:-1])
        return cls(search,items)

    def proxy(self):
        proxy_list=[]
        with open(r'C:\Users\Mehdi\Desktop\Project\proxy_list4.txt',encoding='utf-8')as p:
            for row in p:
                proxy_list.append(row.strip())                
            #print(proxy_list)         
        with concurrent.futures.ThreadPoolExecutor(max_workers=10)as c:
            c.map(self.proxy_check_request,proxy_list)
            c.shutdown(wait=True)
            self.proxy_selection()
          
          
    def proxy_selection(self):
        print(f'you are in proxy_selection-----------------------------\n {self.proxy_available}')
             
    def proxy_check_request(self,proxy):
       
       try:    
           check=requests.get('https://www.google.com',proxies={'http':proxy,'https':proxy},timeout=3)    
           if check.ok:
               print(f'proxy {proxy} is availble| \n')
               self.proxy_available.append(proxy) 
       except:
           
           print(f'proxy {proxy} was failed \n')   
                
    def arg_parse():
        parser = argparse.ArgumentParser(description='''*********************** digikala data extraction 
                                         search field **********************''')
        parser.add_argument('search', help='enter the name of prodcut ----example---> [mobile]')
        parser.add_argument('items', help='enter number of prodcuts  ----example---> [22]')
        args = parser.parse_args()
        search=args.search
        items=int(args.items)
        print(f'your produc name is {search} for {items} items')
        d=scrape.start(search=search,items=items)
        d.save_csv()

if __name__=='__main__':
    d=scrape.start(search="گوشی+موبایل",items=30)
    # d.save_csv()
    d.proxy()
