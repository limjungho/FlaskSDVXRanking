import urllib.request
from time import sleep
imgurl = 'http://anzuinfo.me/images/track_img/'
savedir = 'static/img/Jacket/'
imgchrList = ['n','a','e','m','i','g','h','v']
for i in range(1448,1449):
    if i%20==0:
        print('Loading...'+str(i))
    for chr in imgchrList:
        urlcomp = imgurl+str(i).zfill(4)+chr+'.jpg'
        savedircomp = savedir+str(i).zfill(4)+chr+'.jpg'
        mem = urllib.request.urlopen(urlcomp).read()
        if mem[0] is 60:
            continue
        urllib.request.urlretrieve(urlcomp, savedircomp)
        sleep(0.02)
