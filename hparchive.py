# coding=utf-8
from requests_html import HTMLSession
from tqdm import tqdm
import os
import time
import re
import sys
import hashlib


if not os.path.exists('./hparchive'):
    os.makedirs('./hparchive')

tidlist = {}
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
    username = usernameinput.encode('gbk')
    # pwd = hashlib.md5(pwdinput.encode('gbk')).hexdigest()
    pwd = pwdinput.encode('gbk')
    data = {'loginfield':'username','username': username, 'password': pwd}
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
        answer = answerinput.encode('gbk')
        data['questionid'] = questionid
        data['answer'] = answer
        
    
    # print(data)
    loginurl = 'https://www.hi-pda.com/forum/logging.php?action=login&loginsubmit=yes&inajax=1'
    result = hpsession.post(loginurl, data=data)
    # print(result.request.body)
    # print(result.request.headers)
    resultgbk = result.content.decode('gbk')
    # print(resultgbk)
    if '密码错误次数过多' in resultgbk:
        print('错误次数过多,请15分钟后再试,建议使用浏览器登录查看详情')
        sys.exit(0)
    
    if '可以尝试' in resultgbk:
        print(resultgbk)
        sys.exit(0)
    
    if '请填写安全提问以及正确的答案' in resultgbk or '选择错误' in resultgbk:
        print('没有填写安全提问或者答案不正确')
        sys.exit(0)



def getlist(page=1,listtype = '-fav'):
    '''从我的收藏/我的帖子页面获取帖子标题及tid'''
    baseurl = 'https://www.hi-pda.com/forum/my.php?item=favorites&type=thread'
    if (listtype == '-mypost'):
        baseurl = 'https://www.hi-pda.com/forum/my.php?item=threads'

    if (page == 1):
        listurl = baseurl
    else:
        listurl = baseurl + '&page=' + str(page)

    listpage = hpsession.get(listurl)
    # print(listurl)
    
    tbodysel = '#wrap > div.main > div > div.threadlist.datalist > form > table > tbody'
    if (listtype == '-mypost'):
        tbodysel = 'tbody'
    # print(listtype,tbodysel)
    

    tbody = listpage.html.find(tbodysel, first=True)
    listitem = tbody.find('tr > th > a')
    # print(tidlist)

    for a in listitem:
        tid = a.attrs['href'].split('tid=')[1].split('&')[0]
        tidlist[tid] = a.text
    nextpage = listpage.html.find('a.next')
    hasnextpage = len(nextpage) > 0
    time.sleep(0.1)
    if (hasnextpage):
        getlist(page=page+1,listtype=listtype)



def genTOC(listtype='-fav'):
    '''生成目录HTML文件'''
    filename = 'fav.html'
    if (listtype == '-mypost'):
        filename = 'mypost.html'
    tocs = ''
    for i in tidlist:
        tocs = tocs + '<a href="./hparchive/' + str(i) +'-1.html" target="_blank">' + tidlist[i] + '</a><br>' + '\n'
    
    with open(filename,'w',encoding='utf-8') as f:
        f.write(tocs) 
        


def savethread(tid,page=1,pagetype='norm'):
    '''下载tid对应的帖子html,如果是多页的帖子会自动连续下载,直到
    页面里找不到下一页按钮时停止'''
    rawurl = 'https://www.hi-pda.com/forum/viewthread.php?tid='

    if pagetype == '--print':
        printableurl = rawurl + str(tid) + '&action=printable'
        printr = hpsession.get(printableurl)
        with open('./hparchive/' + str(tid) + '-' + str(page) + '.html','w',encoding='gb18030') as f:
            f.write(printr.html.html)
        return 

    if (page == 1):
        
        threadurl = rawurl + str(tid)
    
    else:
        threadurl = rawurl + str(tid) + '&extra=&page=' + str(page)


    
    r = hpsession.get(threadurl)
    r1 = r'viewthread.php\?tid=' + tid + r'&amp;extra=&amp;page=(\d+)'  #页码按钮的链接的正则,分组1是指向的页码
    r2 = tid + r'-\1.html'   #替换成tid-页码.html的形式,即指向本地的html文件
    modhtml = re.sub(r1,r2,r.html.html)
    if (r.status_code != 200):
        print(tidlist[tid])
    with open('./hparchive/' + str(tid) + '-' + str(page) + '.html','w',encoding='gb18030') as f:
        #直接使用utf-8会乱码,全部转换utf-8可能会有兼容问题,所以还是保持原编码不变,因为gbk在某些特殊字符会报错,使用gb18030
        f.write(modhtml)
    
    nextpage = r.html.find('a.next')
    hasnextpage = len(nextpage) > 0
    time.sleep(0.1)
    if (hasnextpage ):
        savethread(tid,page=page+1)

    



def work():
    listtype = '-fav'
    pagetype = 'norm'
    helpmsg = '参数错误,-fav收藏帖,-mypost我的发帖,--print加载打印版网页(只有前两页内容，但是速度较快)'
    if (len(sys.argv) > 3):
        print ('参数错误,正确用法:python hparchive (-fav,-mypost,--print)')
        sys.exit(1)
    
    elif (len(sys.argv) == 3):
        listtype = sys.argv[1]
        pagetype = sys.argv[2]
        if listtype not in ['-fav','-mypost']:
            print(helpmsg)
            sys.exit(1) 
        elif pagetype != '--print':
            print(helpmsg)
            sys.exit(1)

    elif (len(sys.argv) == 2):
        listtype = sys.argv[1]
        if listtype not in ['-fav','-mypost']:
            print(helpmsg)
            sys.exit(1) 

    userlogin()
    getlist(page=1,listtype=listtype)
    print('一共' + str(len(tidlist)) + '个贴子')
    genTOC(listtype=listtype)

    is_windows = (os.name == 'nt') #判断系统类型，windows下进度条会有问题，设置ascii为True
    for tid in tqdm(tidlist,ascii=is_windows):
        savethread(tid,page=1,pagetype=pagetype)
        time.sleep(0.3)


if __name__ == "__main__":
    work()



