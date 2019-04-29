import os

path = 'E:\定期更新文件夹10.7\腾讯新闻'
for i in os.listdir(path):
    subpath = path + '\\' + i
    os.chdir(subpath)
    for j in os.listdir(subpath):
        tail = os.path.splitext(j)[1]
        if tail == '.csv':
            os.remove(j)
