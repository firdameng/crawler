
# -*- coding: utf-8 -*-

import threading            #多线程
import json                 #解析json
import os                   #输出文件
import mongo_cache

from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit
from time import ctime,time      #测试时间
from downloader import Downloader  

PAGE_SIZE=20                      #每个json返回图片src数目


def set_query_parameter(url,param_name,param_value):
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))
    

#线程的任务
def get_imgs_src(json_url,group_no,step,down_callback,write_back_filename):

    print '%s is dowdloading....\n' %(threading.currentThread().getName())
    
    start=group_no*PAGE_SIZE*step  #组号x页大小x组间隔=起始地址
    end=start+step*PAGE_SIZE
    images=set()
    while start < end:
        json_data=down_callback(set_query_parameter(json_url,'start',start))
        try:
            ajax=json.loads(json_data)
        except ValueError as e:
            print e
            ajax=None
        else:
            for img in ajax['images']:
                images.add(img['src'].replace('thumb','photo'))
            start+=PAGE_SIZE
        if ajax is None:
            break
    with open(write_back_filename,'a') as f:    #注意这里不能覆盖
        f.write('\n'.join(images))

'''
线程调度
'''
def threads_crawl(threads_count,page_count,douban_img_url,search_name):
    json_url=douban_img_url.format(q=search_name,limit=PAGE_SIZE,start=0)
    down_callback=Downloader(cache=mongo_cache.MongoCache())
    write_back_filename=os.getcwd()+'\\'+'dd'+'.txt'
    step=page_count/threads_count
    print '%s is crawling...'%(threading.currentThread().getName())
    threads=[]
    for group_no in range(threads_count):
        t=threading.Thread(target=get_imgs_src,args=(json_url,group_no,step,down_callback,write_back_filename))
        threads.append(t)
    return threads    
    
'''
测试多线程抓取
'''
def main():
    print 'start:%s' % ctime()
    s=time()
    douban_img_url='https://www.douban.com/j/search_photo?q={q}&limit={limit}&start={start}'
    search_name='李冰冰'
    threads_count=20
    page_count=20
    threads=threads_crawl(threads_count,page_count,douban_img_url,search_name)
    for thread in threads:
        thread.start()         #这里才开始运行
    
    for thread in threads:
        thread.join()
        
    print 'end:%s' % ctime() 
    print  'cost:',time()-s
    
    
    
main()
   
   
        