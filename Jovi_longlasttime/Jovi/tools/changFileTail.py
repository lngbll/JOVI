# os.chdir('e:\定期更新文件夹')
import os

os.chdir('E:\定时更新文件夹\大搜狐网')
file1 = os.listdir(".")

for i in file1:
    # print(i)
    # os.chdir('.\%s'%i)
    # print(os.getcwd())
    file2 = os.listdir('.\%s' % i)
    for j in file2:
        # os.chdir('.\%s'%j)
        # print(os.getcwd())
        file3 = os.listdir('.\%s\%s' % (i, j))

        for k in file3:
            portion = os.path.splitext(k)
            print(portion)
            # 如果后缀是.txt
            if portion[1] == ".csv":
                newname = portion[0] + '.txt'
                os.rename('.\%s\%s\%s' % (i, j, k), '.\%s\%s\%s' % (i, j, newname))
