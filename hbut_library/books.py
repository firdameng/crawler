# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urlparse import urlsplit,parse_qs,urlunsplit
from urllib import urlencode,unquote
import re
import time
import eventlet
from eventlet.green import urllib2

import book_csver 

book_url = 'http://202.114.181.8:8080/newbook/newbook_cls_book.php?\
back_days=180&\
loca_code=ALL&\
cls=I&\
s_doctype=ALL&\
clsname=%E6%96%87%E5%AD%A6&\
page=1'

# book_url = 'http://202.114.181.8:8080/newbook/newbook_cls_book.php?\
# back_days=180&\
# loca_code=ALL&\
# cls=TP3&\
# s_doctype=ALL&\
# clsname=%E8%AE%A1%E7%AE%97%E6%8A%80%E6%9C%AF%E3%80%81%E8%AE%A1%E7%AE%97%E6%9C%BA%E6%8A%80%E6%9C%AF&\
# page=1'

lend_avl_url = 'http://202.114.181.8:8080/opac/ajax_lend_avl.php'

item_url = 'http://202.114.181.8:8080/opac/ajax_item.php'

def update_query_parameter(url, querys):
    '''
    url - 待更新的查询url
    querys - 待更新或添加的查询键值对字典
    '''
    scheme, netloc, path, query, fragment = urlsplit(url)
    query_params = parse_qs(query)
    for t in querys.iteritems():
        query_params[t[0]] = t[1]
    new_query_string = urlencode(query_params, doseq=True)
    return urlunsplit((scheme, netloc, path, new_query_string, fragment))  
  
def parse_author_str(author_str):
    '假定str不为空'
    book_author_nationality = ''
    book_author = ''
    for s in author_str.split(','):  # 小写的逗号
        # 去除首尾空白
        s = s.strip()
        # 如果存在（作者国籍），则提取出来
        t = re.findall(r'\(.*\)',s)
        if t:
            book_author_nationality += ',' + t[0][1:-1]
        
        t = re.search(r' +',s)
        if t:
            book_author += ',' + s[t.span()[1]:]
        else:
            book_author += ',' + s  # 无国籍时，直接赋值作者名            
    
    # 修正不带作者国籍的情况
    # if not book_author_nationality:
        # if re.search(r'[a-zA-Z]+',book_author):
            # book_author_nationality = '中'

    book_author_nationality = book_author_nationality[1:] if book_author_nationality else u'中'
    book_author = book_author[1:]
    return book_author_nationality,book_author
  
def task(url): 
    try:
        html = urllib2.urlopen(url).read()
        soup = BeautifulSoup(html, 'html.parser')
        list_books_div = soup.find_all('div',class_ = 'list_books')
        list_books = []
    except Exception as e:
            print "%s , could not fetch url :%s" % (e,url)
            return []
            
    for book in list_books_div:
        book_id = book.find('span').get('id')[5:]
        book_name = book.find('a').string
        book_index = book.find('h3').contents[-1]
        book_aut_pre_year = book.find('p').contents[-1].strip().split('  ')
        
        # 拆分作者国籍，和作者名
        book_author_str = book_aut_pre_year[0].strip()
        book_author_nationality, book_author= parse_author_str(book_author_str)
        
        book_press = ''
        book_publication_date = ''
        if len(book_aut_pre_year) > 1:
            book_press = book_aut_pre_year[1].split(' ')[0]
            book_publication_date = book_aut_pre_year[1].split(' ')[1]

        # 构造请求馆藏量
        timestamp = int(round(time.time() * 1000))
        querys = {
        'marc_no':book_id,
        'time':str(timestamp)
        }
        remain_num_url = update_query_parameter(lend_avl_url,querys)
        
        try:
            book_remain_str = urllib2.urlopen(remain_num_url).read().strip().decode('utf-8')
            book_remain_num = re.findall(r'\d+/\d*',book_remain_str)[0].split('/')
            if not book_remain_num[1]:
                book_remain_num[1] = '0'
            book_remain = book_remain_num[0]
            book_avl = book_remain_num[1]
            print book_remain_num
        except Exception as e:
            book_remain = ''
            book_avl = ''
            print "%s , could not fetch remain_num_url :%s" % (e,remain_num_url)
        
        # 获取图书馆藏地
        book_place_querys = {'marc_no':book_id}
        book_place_url = update_query_parameter(item_url,book_place_querys)
        try:
            book_place_html = urllib2.urlopen(book_place_url).read()
            pure_bph = book_place_html.replace('</span>','')
            table_html = BeautifulSoup(pure_bph, 'html.parser')
            trs = table_html.find_all('tr',class_ = 'whitetext')
            book_valid_place = ''
            for tr in trs:
                if tr.find('font'):         # 改藏书地可借书
                    book_valid_place += ',' + tr.find_all('td',width = '25%')\
                    [0].contents[-1].strip()
            book_valid_place = ','.join(list(set(book_valid_place[1:].split(','))))
            print book_valid_place
        except Exception as e:
            book_valid_place = ''
            print "%s , could not fetch book_place_url: %s" % (e,book_place_url)
        
        list_books.append(
        {
            'book_id':book_id,
            'book_name':book_name,
            'book_index':book_index,
            'book_author_nationality':book_author_nationality,
            'book_author':book_author,
            'book_press':book_press,
            'book_publication_date':book_publication_date,
            'book_remain':book_remain,
            'book_avl':book_avl,
            'book_valid_place':book_valid_place
        })
    return list_books

if __name__ == "__main__": 
    
    # 创建待爬取的书籍页面URL
    urls = []
    all_pages = 192         # 根据待爬取类别下多少页人为设置
    for i in range(1,all_pages):
        urls.append(update_query_parameter(book_url, {'page':str(i)}))
        
    # 从URL提取结果数据集文件名
    scheme, netloc, path, query, fragment = urlsplit(book_url)
    query_params = parse_qs(query)
    filename = query_params['cls'][0] + '_' + \
            unquote(query_params['clsname'][0]).decode('utf8')  + '_' +\
            query_params['back_days'][0] + '.csv'

    # 首先写入csv列名,the csv module doesn't support unicode,
    header = ['Id','书名', '索引号', '国家','作者','出版社','年份', '馆藏', '可借','馆藏地']
    book_csver.write_csv_header(filename,header)
    
    # 构造绿色线程池
    pool = eventlet.GreenPool()
    
    step = 20
    for i in range(0,all_pages,step):
        books = pool.imap(task, urls[i:i + step])
        for book_list in books:
            book_csver.write_csv_books(filename,book_list,pattern = 'ab')
        time.sleep(15)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
