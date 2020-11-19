# -*- coding: utf-8 -*-
import os
import sys
import struct
import requests
import re
try:
    from ctypes import windll, create_string_buffer
except ImportError:
    pass

STD_OUTPUT_HANDLE = -11

header = {
    #'accept': 'text/html,application/xhtml+xml,application/xml',
    #'User - Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
}

ucolors = {
    'red': 31,
    'green': 32,
    'cyan': 36,
    'yellow': 33,
    'blue': 34,
    'default': 37
}

wcolors = {
    'green': 0xa,
    'cyan': 0xb,
    'red': 0xc,
    'yellow': 0xe,
    'blue': 0x1,
    'default': 0x7,
}
def calcSize(len):
    if len < 1024:
        return str(len)+'B'
    elif len < 1024*1024:
        return str(len//1024)+'KB'
    elif len < 1024*1024*1024:
        return str((len//1024)//1024)+'MB'
    return str(len//(1024*1024*1024))+'GB'

def rmakedirs(path):
    path = os.path.dirname(path)
    if path and not os.path.exists(path):
        os.makedirs(path)
    return

def set_color(color='default'):
    stdout_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    windll.kernel32.SetConsoleTextAttribute(stdout_handle, wcolors[color])

def cprint(s,color='default'):
    if sys.platform.startswith('win'):
        set_color(color)
        print('{}'.format(s))
        set_color('default')
    else:
        print('\033[1;{}m{}\033[0m'.format(ucolors[color], str(s)))
    return

def dFile(url,path):
    r = requests.get(url,headers=header)
    with open(path+url.split('/')[-1],'wb+') as f:
        for chunk in r.iter_content(chunk_size=512*1024):
            if chunk:
                f.write(chunk)
    return
            

def rdir(url,path):
    r = requests.get(url,headers=header)
    if '<title>Index of' in r.text:
        urls = re.findall('href="(.*?)"',r.text)
        for u in urls:
            if '/' in u:
                u = u.split('/')[0]
                if u != '.' and u != '..':
                    rmakedirs(path+u)
                rdir(url+u+'/',path+u+'/')
            else:
                dFile(url+u,path+u)
    elif r.status_code == 200:
        dFile(url,path)
    else:
        cprint('[-] Download failed. HTTP 403 Forbidden','yellow')
    return