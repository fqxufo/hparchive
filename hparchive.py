# coding=utf-8
from requests_html import HTMLSession
from tqdm import tqdm
from urllib.parse import quote_from_bytes
import os
import time
import re
import sys
import webbrowser


if not os.path.exists('./hparchive'):
    os.makedirs('./hparchive')

favlist = {}
useragent = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Safari/605.1.15'}
hpsession = HTMLSession()
hpsession.headers.update(useragent)


def userlogin():
    '''用户登录'''
    questionids = {
    '0':'无安全提问',
    '1':'母亲的名字',
    '2':'爷爷的名字',
    '3':'父亲出生的城市',
    '4':'您其中一位老师的名字',
    '5':'您个人计算机的型号',
    '6':'您最喜欢的餐馆名称',
    '7':'驾驶执照的最后四位数字',
    }
    usernameinput = input('用户名： ')
    pwdinput = input('密码: ')
    username = quote_from_bytes(usernameinput.encode('gbk'))
    pwd = quote_from_bytes(pwdinput.encode('gbk'))
    data = {'username': username, 'password': pwd}
    print('按数字选择安全提问,没有就直接回车或者选择0')
    for question in questionids:
        print(question,':  ',questionids[question])
    questionid = '0'
    while True:
        questionidinput = input('按数字选择安全提问:')
        if questionidinput == '':
            break
        if (questionidinput in ['0','1','2','3','4','5','6','7']):
            questionid = questionidinput
            break

    
    print('安全提问: ',questionids[questionid])
    if (questionid != '0'):
        answerinput = input('输入安全提问答案:')
        answer = quote_from_bytes(answerinput.encode('gbk'))
        data['answer'] = answer
        data['questionid'] = questionid
    
    print(data)
    loginurl = 'https://www.hi-pda.com/forum/logging.php?action=login&loginsubmit=yes&inajax=1'
    result = hpsession.post(loginurl, data=data)
    resultgbk = result.content.decode('gbk')
    if '密码错误次数过多' in resultgbk:
        print('错误次数过多,请15分钟后再试,建议使用浏览器登录查看详情')
        time.sleep(3)
        webbrowser.open('https://www.hi-pda.com/forum/index.php')
        sys.exit(0)
    
    if '可以尝试' in resultgbk:
        print(resultgbk)
        time.sleep(2)
        sys.exit(0)
    




def getfav(page=1):
    '''从页面获取收藏帖子标题及tid，确定总收藏页数maxpagenum'''
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



def genTOC():
    '''生成目录HTML文件'''
    tocs = ''
    for i in favlist:
        tocs = tocs + '<a href="./hparchive/' + str(i) +'-1.html" target="_blank">' + favlist[i] + '</a><br>' + '\n'
    
    with open('fav.html','w') as f:
        f.write(tocs) 
        


def savethread(tid,page=1):
    '''下载tid对应的帖子html,如果是多页的帖子会自动连续下载,直到
    页面里找不到下一页按钮时停止'''
    rawurl = 'https://www.hi-pda.com/forum/viewthread.php?tid='
    if (page == 1):
        
        threadurl = rawurl + str(tid)
    
    else:
        threadurl = rawurl + str(tid) + '&extra=&page=' + str(page)


    
    r = hpsession.get(threadurl)
    r1 = r'viewthread.php\?tid=' + tid + r'&amp;extra=&amp;page=(\d+)'  #页码按钮的链接的正则,分组1是指向的页码
    r2 = tid + r'-\1.html'   #替换成tid-页码.html的形式,即指向本地的html文件
    modhtml = re.sub(r1,r2,r.html.html)
    if (r.status_code != 200):
        print(favlist[tid])
    with open('./hparchive/' + str(tid) + '-' + str(page) + '.html','w',encoding='gb18030') as f:
        #直接使用utf-8会乱码,全部转换utf-8可能会有兼容问题,所以还是保持原编码不变,因为gbk在某些特殊字符会报错,使用gb18030
        f.write(modhtml)
    
    hasnextpage = r.html.find('a.next')
    time.sleep(0.1)
    if (len(hasnextpage) > 1 ):
        savethread(tid,page=page+1)

    



def work():
    userlogin()
    maxpagenum = getfav(page=1)
    if maxpagenum > 1:
        for i in range(2, maxpagenum + 1):
            getfav(page=i)
    print('一共' + str(len(favlist)) + '个收藏贴')
    genTOC()
    for tid in tqdm(favlist):
        savethread(tid)
        time.sleep(0.3)


if __name__ == "__main__":
    work()



