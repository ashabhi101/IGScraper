import pandas as pd, numpy as np, json, time, urllib, json, os, codecs, re
from bs4 import BeautifulSoup as BS
from itertools import chain
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
class ig_scraper(object):
    def __init__(self, chromepath ='C://Program Files/chromedriver.exe', creds = 'creds.json', fpath = '../Data/'):
        self.driver = webdriver.Chrome(chromepath)
        with open(creds, 'r') as f:
            creds = json.loads(f.read())
        self.un = creds.get('un')
        self.pw = creds.get('pw')
        self.fpath = fpath
        self.piclinks_profile = set()
    def reset_links(self):
        self.piclinks_profile = set()
    def quit_driver(self):
        try:
            self.driver.quit()
        except:
            pass
    def restart_driver(self):
        try:
            self.quit_driver()
        except:
            pass
        self.__init__()
    def get_page(self, url):
        self.driver.get(url)
    def quit(self):
        try:
            self.driver.quit()
        except:
            pass
    def log_in(self):
        self.get_page('https://www.instagram.com/accounts/login')
        time.sleep(2)
        bs = BS(self.driver.page_source)
        cl = bs.find_all('input', {'name':'username'})[0].get('class')
        self.driver.find_elements_by_class_name(cl[0])[0].clear()
        self.driver.find_elements_by_class_name(cl[0])[0].send_keys(self.un)
        self.driver.find_elements_by_class_name(cl[0])[1].clear()
        self.driver.find_elements_by_class_name(cl[0])[1].send_keys(self.pw)
        li = [b for b in bs.find_all('button') if 'log in' in b.text.lower()][0].get('class')
        clicked = False
        for l in li:
            els = self.driver.find_elements_by_class_name(l)
            if len(els)==1:
                clicked = True
                els[0].click()                
                break
        if not clicked:
            self.driver.find_elements_by_class_name(li[0]).click()
    def get_user(self, username):
        url = 'https://www.instagram.com/{}'.format(username)
        self.get_page(url)
    def scroll_page(self, sleep = 2, maxiters = 1000, reset_links = True):
        if reset_links:
            self.reset_links()
        lenOfPage = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        iters = 0
        maxiters = maxiters
        sc,bs = self.get_pagesource()
        self.piclinks_profile = self.piclinks_profile.union(set(self.get_piclinks_profile()))
        while match==False:
            bs = BS(self.driver.page_source)
            try:
                b = [b for b in bs.find_all('button') if 'show more posts from' in b.text.lower()][0]
                cl = b.get('class')[0]
                self.driver.find_element_by_class_name(cl).click()
            except:
                pass
            lastCount = lenOfPage
            time.sleep(sleep)
            lenOfPage = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            if lastCount==lenOfPage:
                match=True
            iters += 1
            sc,bs = self.get_pagesource()
            self.piclinks_profile = self.piclinks_profile.union(set(self.get_piclinks_profile()))
            if iters>= maxiters:
                break
    def get_pagesource(self):
        self.sc = self.driver.page_source
        self.bs = BS(self.sc)
        return self.sc, self.bs
    def get_piclinks_profile(self):
        hrefs = self.bs.find_all('a')
        piclinks_profile = [h.get('href') for h in hrefs if '/p/' in h.get('href')]
        return piclinks_profile
    def get_photos(self, fpath = '../Data/', metadata = True):
        iters = 0
        maxiters = 11
        piclink = ''
        if metadata:
            try:
                url = self.driver.current_url
                fname = re.findall('/p/([^/]+)',url)[0]
                j = self.get_meta_data(fname,fpath=fpath+'metadata/')
                
                short = j.get('entry_data').get('PostPage')[0].get('graphql').get('shortcode_media')
                # If multiple images in post
                if 'sidecar' in short.get('__typename').lower():
                    for sht in short.get('edge_sidecar_to_children').get('edges'):
                        node = sht.get('node')
                        if 'video' in node.get('__typename').lower():
                            piclink = node.get('video_url')
                            piclink = piclink.replace('&amp;', '&')
                            pname = re.findall('/[^?^/]+mp4',piclink)[0].replace('/', '')
                        else:
                            piclink = node.get('display_url')
                            piclink = piclink.replace('&amp;', '&')
                            pname = re.findall('/[^?^/]+jpg',piclink)[0].replace('/', '')
                        urllib.request.urlretrieve(piclink, '{}{}'.format(fpath,pname))
                        
                else:
                    if 'video' in short.get('__typename').lower():
                        piclink = short.get('video_url')
                        piclink = piclink.replace('&amp;', '&')
                        pname = re.findall('/[^?^/]+mp4',piclink)[0].replace('/', '')
                    else:
                        piclink = short.get('display_url')
                        piclink = piclink.replace('&amp;', '&')
                        pname = re.findall('/[^?^/]+jpg',piclink)[0].replace('/', '')
                    urllib.request.urlretrieve(piclink, '{}{}'.format(fpath,pname))
                metadatafail = False
            except:
                metadatafail = True
                pass
        else:
            metadatafail = True
        if (metadata is False)|metadatafail:
            while iters<maxiters:
                fname = None
                bs = BS(self.driver.page_source)
                try:
                    st = [l for l in bs.find_all('video', {'class':'tWeCl'})][0]
                    piclink = st.get('src').replace('&amp;', '&')
                except:
                    st = [l for l in bs.find_all('img', {'class':'FFVAD'})][0]
                    st = str(st)
                    imglinks = [[l for l in s.split() if 'https://' in l] for s in st.split(',')]
                    imglinks = list(chain(*imglinks))
                    piclink = imglinks[-1]
                    piclink = piclink.replace('&amp;', '&')
                
                try:
                    fname = re.findall('/[^?^/]+jpg',piclink)[0].replace('/', '')
                except:
                    fname = re.findall('/[^?^/]+mp4',piclink)[0].replace('/', '')
                urllib.request.urlretrieve(piclink, '{}{}'.format(fpath,fname))
                try:
                    self.driver.find_element_by_class_name('coreSpriteRightChevron').click()
                except:
                    break
                
                time.sleep(2)
                iters +=1

    def get_all_photos(self, sleep = 2, fpath = '../Data/'):
        for l in self.piclinks_profile:
            try:
                self.get_page('https://www.instagram.com/{}'.format(l))
                time.sleep(sleep)
                self.get_photos(fpath=fpath)
            except:
                pass

    def get_meta_data(self, fname,fpath = '../Data/'):
        """
        In progress
        Parse JSON data from post page

        """
        try:
            os.listdir(fpath)
        except:
            os.mkdir(fpath)

        sc = self.driver.page_source
        try:
            j = [s for s in BS(sc).find_all('script') if 'platform' in str(s)][0].text
            j = json.loads(re.findall('\{.*\}', j)[0])
        except:
            scr = re.findall('window._sharedData = (\{"config":\{"csrf_token":.*\})', sc)[0]
            j = json.loads(re.findall('\{.*\}', scr)[0])
            # j = json.loads(scr[:scr.find('<')-1])

        with codecs.open(fpath+fname+'.json', 'w', encoding = 'utf-8') as f:
            f.write(json.dumps(j))
        return j
# C:\Users\yangy\Dropbox\Photos\misc\igscraper

