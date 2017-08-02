# -*- coding: utf-8 -*-

import csv

def _init_():
    ''''''

def write_csv_header(filename,header):
    with open(filename, 'wb') as csvfile:
        bookswriter = csv.writer(csvfile)
        bookswriter.writerow(header)
        
def write_csv_books(filename,books,pattern = 'wb'):
    '''
    filename - 待写入的csv文件名,
    header - csv文件列名,
    books - book字典数据列表
    '''
    with open(filename, pattern) as csvfile:
        bookswriter = csv.writer(csvfile)
        bookrows = []
        for book in books:
            bookrows.append(
            [
            book['book_id'].encode('utf-8'),\
            book['book_name'].encode('utf-8'),
            book['book_index'].encode('utf-8'),\
            book['book_author_nationality'].encode('utf-8'),\
            book['book_author'].encode('utf-8'),\
            book['book_press'].encode('utf-8'),\
            book['book_publication_date'].encode('utf-8'),\
            book['book_remain'].encode('utf-8'),\
            book['book_avl'].encode('utf-8'),\
            book['book_valid_place'].encode('utf-8')
            ]
            )
        bookswriter.writerows(bookrows)
