# hparchive
导出hipda'我的收藏'/'我的发帖'
需要python 3.6+
依赖以下几个python库：
- [requests-html](https://github.com/kennethreitz/requests-html)
- [tqdm](https://github.com/tqdm/tqdm)

直接 `pip install requests-html` 即可，会自动安装其他需要的库

运行方法 `python hparchive.py (-fav,-mypost)`

`python hparchive.py` 及 `python hparchive -fav` 会在脚本目录生成fav.html及hparchive文件夹，fav.html即是包含所有收藏贴链接的目录

`python hparchive.py -mypost` 会在脚本目录生成mypost.html及hparchive文件夹，mypost.html即是包含所有"我的发贴"链接的目录

第二个参数加 --print 可以下载打印版网页,速度更快,但是只有前两页内容,不完整
例如: `python hparchive.py -fav --print`


