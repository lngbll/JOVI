import os, time


paths = []
def all_count(path):
    nums = 0
    def count(_path):
        nonlocal nums
        if  os.path.isdir(_path):
            for i in os.listdir(_path):
                os.chdir(_path)
                sub_path = os.path.join(_path,i)
                count(sub_path)
        else:
            with open(_path, 'r', encoding='utf-8') as f:
                articles = len(f.readlines())
                nums += articles
        return nums

    os.chdir(path)
    all_nums = dict()
    zs = 0
    for i in os.listdir(path):
        _i = i.rstrip('.txt')
        complete_path = os.path.join(path,i)
        all_nums[_i] = count(complete_path)
        zs += all_nums[_i]
        nums = 0
    all_nums['总数'] = zs
    return all_nums



if __name__=='__main__':
    date = time.strftime('%m-%d',time.localtime())
    path = 'e:\\定期更新{}'.format(date)
    os.chdir(path)
    for _path in os.listdir(path):
        sub_path = os.path.join(path,_path)
        print(all_count(sub_path))