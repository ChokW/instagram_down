# !/usr/bin/env python
# coding=utf-8

import requests
import urllib2
import os
import json
import Queue
import threading
proxies = {
  "http": "http://127.0.0.1:8118",
  "https": "http://127.0.0.1:8118",
}
headers={
    "User-Agent":"Instagram 7.18.1 (iPhone4,1; iPhone OS 9_2_1; zh_CN; zh-Hans-CN; scale=2.00; 640x960) AppleWebKit/420+"
}
cookies={
    "sessionid":"IGSCbbe13cd4b8784956b05bf1310a190863e086f8ce42b354ffb2689505725c7aa5%3ArqXy2rfViM7sjuP61p143tvm21W04qJq%3A%7B%22_token_ver%22%3A2%2C%22_auth_user_id%22%3A2897867765%2C%22_token%22%3A%222897867765%3ANzLZt8rUOzDpd0yknw4xryMpOHlPEDoZ%3Ab05b8641d360e0045ddc89748ea2032316ca0e62d9fff06adfa7eb47445323d9%22%2C%22asns%22%3A%7B%22107.182.189.89%22%3A8100%2C%22time%22%3A1458576698%7D%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22last_refreshed%22%3A1458576698.682646%2C%22_platform%22%3A0%7D"
}
params={
    "rank_token":"2897867765_C27D9282-A859-45EF-8905-15CC20FF1067"
}
# Chrome console _sharedData.entry_data.ProfilePage[0].user.id
instagram_id="50804348"  # Download instagram user id
downpath=""
s = requests.Session()
def instagram_post():
    r = s.get("https://i.instagram.com/api/v1/feed/user/"+str(instagram_id),params=params,cookies=cookies,headers=headers,proxies=proxies)
    if(r.status_code == 200):
        return r.json()
    else:
        return None
def downimg(imgurl):
    filename = os.path.basename(imgurl)
    r = requests.get(imgurl,proxies=proxies)
    with open(downpath+filename, "wb") as code:
        code.write(r.content)
    print  imgurl
class ThreadDown(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self._queue = queue
    def run(self):
        while True:
            msg = self._queue.get()
            if isinstance(msg, str) and msg == 'quit':
                break
            downimg(msg)
        print 'ThreadDownBye byes!'

def build_worker_pool_img(queue, size):
    workers = []
    for _ in range(size):
        worker = ThreadDown(queue)
        worker.start()
        workers.append(worker)
    return workers
if __name__ == "__main__":
    downpath = '~/instagram/user/'+instagram_id+'/'  # Download path
    if os.path.exists(downpath):
        pass
    else:
        os.makedirs(downpath)
    index=0
    imgqueue = Queue.Queue()
    img_worker_threads = build_worker_pool_img(imgqueue,10)
    while True:
        index=index+1
        print "当前下载第"+str(index)+"页"
        retobj = instagram_post()
        items = retobj["items"]
        if(index == 200):
            break
        if(len(items)==0):
            break
        for item in items:
            max_id = item["id"]
            imgurl = item["image_versions"][0]["url"].replace('/s640x640/','/').replace('/s320x320/','/').replace('/s150x150/','/')
            imgqueue.put(imgurl)
        params["max_id"]=max_id
    for worker in img_worker_threads:
        imgqueue.put('quit')
    for worker in img_worker_threads:
        worker.join()
    print "图片下载成功"
