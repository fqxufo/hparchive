# coding=utf-8
from requests_html import HTMLSession
from tqdm import tqdm
import os
import time


if not os.path.exists('./hparchive'):
    os.makedirs('./hparchive')


username = input('用户名： ')
pwd = input('密码: ')

data = {'username': username, 'password': pwd}

useragent = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Safari/605.1.15'}
hpsession = HTMLSession()
hpsession.headers.update(useragent)

loginurl = 'https://www.hi-pda.com/forum/logging.php?action=login&loginsubmit=yes&inajax=1'
hpsession.post(loginurl, data=data)

favlist = {}


# 从页面获取收藏帖子标题及tid，确定总收藏页数maxpagenum
def getfav(page=1):
    if (page == 1):
        favurl = 'https://www.hi-pda.com/forum/my.php?item=favorites&type=thread'
    else:
        favurl = 'https://www.hi-pda.com/forum/my.php?item=favorites&type=thread&page=' + \
            str(page)

    fav = hpsession.get(favurl)
    tbodysel = '#wrap > div.main > div > div.threadlist.datalist > form > table > tbody'

    tbody = fav.html.find(tbodysel, first=True)
    favas = tbody.find('tr > th > a')

    for a in favas:
        tid = a.attrs['href'].split('tid=')[1].split('&')[0]
        favlist[tid] = a.text

    if (page == 1):
        maxpagesel = '#wrap > div.main > div > div.threadlist.datalist > form > table > tbody > tr:nth-child(76) > td:nth-child(3) > div > a:nth-last-child(2)'
        maxpageanchor = fav.html.find(maxpagesel, first=True)
        if (maxpageanchor == None):
            maxpage = 1
        else:
            maxpage = int(maxpageanchor.text.split('page=')[0])
        return maxpage


# 下载tid对应的帖子html
def savethread(tid):
    rawurl = 'https://www.hi-pda.com/forum/viewthread.php?tid='
    threadurl = rawurl + str(tid)
    r = hpsession.get(threadurl)
    if (r.status_code != 200):
        print(favlist[tid])
    with open('./hparchive/' + str(tid) + '.html','wb') as f:
        f.write(r.content)



maxpagenum = getfav(page=1)

if maxpagenum > 1:
    for i in range(2, maxpagenum + 1):
        getfav(page=i)



print('一共' + str(len(favlist)) + '个收藏贴')

for tid in tqdm(favlist):
    savethread(tid)
    time.sleep(0.5)