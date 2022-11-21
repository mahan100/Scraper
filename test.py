import codecs
import io

proxy_list=[]
with open(r'C:\Users\Mehdi\Desktop\Project\scraping\digikala_scraping\proxy-list.txt',encoding='utf8')as p:
    read=p.read()
print(len(proxy_list))