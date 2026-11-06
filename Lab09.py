from pathlib import Path
import os
import json
from random import randint
import re
import sys

BOOKS_DIR = Path(__file__).parent / 'books'

HOW_MANY_BOOK = 3
LINE = 128
PAGE = 64
pages = {}
page_number=0
line_window = {}
line_number = 0
char_window = []

def clean_line(line):
    return line.strip().replace( '-', '' ) + ' '  # Adding a space instead of a newline.

def process_books(*paths):
    for path in paths:
        #print(f'Reading {path}')
        read_book( path )
        #print(f'{len(pages)}, {len(pages[1])}, {pages[len(pages)]}')

def read_book(file_path):
    global char_window
    with open(file_path, 'r', encoding='utf-8-sig') as fp:
        for line in fp:
            line = clean_line(line)
            if line.strip():
                for c in line:
                    process_char(c)

    if len(char_window) > 0:
        add_line()
    if len(line_window) > 0:
        add_page()


def process_char(char):
    global char_window
    char_window.append(char)
    if len(char_window) == LINE:
        add_line()


def add_line():
    global char_window, line_number
    line_number += 1
    process_page( ''.join(char_window), line_number )
    char_window.clear()


def process_page(line, line_num):
    global line_window, pages, page_number
    line_window[line_num] = line
    if len(line_window) == PAGE:
        add_page()


def add_page():
    global line_number, line_window, pages, page_number
    page_number += 1
    pages[page_number] = dict(line_window)
    line_window.clear()
    line_number = 0

def generate_code_book():
    global pages
    code_book = {}
    for page, lines in pages.items():
        for num, line in lines.items():
            for pos, char in enumerate(line):
                code_book.setdefault(char, []).append(f'{page}-{num}-{pos}')
    return code_book


def save(file_path, book):
    with open(file_path, 'w') as fp:
        # json.dump(book, fp, indent=4)
        json.dump(book, fp)


def reset_state():
    global pages, page_number, line_window, line_number, char_window
    pages = {}
    page_number = 0
    line_window = {}
    line_number = 0
    char_window = []


def load(file_path, *key_books, reverse=False):
    if not os.path.exists(file_path):
        reset_state()
        process_books(*key_books)
        book = pages if reverse else generate_code_book()
        save(file_path, book)
    with open(file_path, 'r') as fp:
        return json.load(fp)

def encrypt(code_book, message):
    cipher_text = []
    for char in message:
        index = randint(0, len(code_book[char]) - 1)
        cipher_text.append(code_book[char].pop(index))
    return '-'.join(cipher_text)

def decrypt(rev_code_book, ciphertext):
    plaintext = []
    for cc in re.findall(r'\d+-\d+-\d+', ciphertext):
        page, line, char = cc.split('-')
        plaintext.append(
            rev_code_book[page][line][int(char)])
    return ''.join(plaintext)


def main_menu():
    print("""1). Encrypt
2). Decrypt
3). Quit
""");
    return int(input("Make a selection [1,2,3]: "))


def main():
    key_books = (
        "books/Gulliver's Travels.txt",
        "books/shakespeare.txt",
        "books/Tess of the d'Urbervilles.txt",
        "books/great gatsby.txt",
    )
    code_book_path = 'code_books/book2.json'
    rev_code_book_path = 'code_books/book2_r.json'
    while True:
        try:
            choice = main_menu()
            match (choice):
                case 1:
                    code_book = load(code_book_path, *key_books)
                    message = input("Please enter your secret message: ")
                    print(encrypt(code_book, message))
                    continue;
                case 2:
                    rev_code_book = load(rev_code_book_path, *key_books, reverse=True)
                    message = input("Please enter your cipher text: ")
                    print(decrypt(rev_code_book, message))
                    continue;
                case 3:
                    sys.exit(0)
        except ValueError as ve:
            print("Improper selection.")

if __name__ == '__main__':
    main()


#process_books(BOOKS_DIR / 'great gatsby.txt',BOOKS_DIR / "Tess of the d'Urbervilles.txt",)
#cb = generate_code_book()
#save('./code_books/book1.json', cb)
#message = input("Type your secret message: ")
#print(
    #encrypt(load('./code_books/book1.json', BOOKS_DIR / 'great gatsby.txt',BOOKS_DIR / "Tess of the d'Urbervilles.txt"), message))

#ciphertext = '69-25-52-47-28-62-13-49-34-80-51-22-108-58-25-7-57-45-96-16-76-54-63-11-83-12-114-53-21-39-136-28-52-97-21-74-108-13-75-42-43-50-58-36-52'
#print(
    #decrypt(
#load('./code_books/book1._r.json', BOOKS_DIR / 'great gatsby.txt',BOOKS_DIR / "Tess of the d'Urbervilles.txt", reverse=True)
    #,ciphertext)
#)
