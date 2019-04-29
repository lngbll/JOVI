# def get_cp_as():
#     f1 = open("C:\\Users\\luyuwei\\Desktop\\今日头条\\t.js", 'r')
#     js = f1.read()
#     ctx = execjs.compile(js)
import execjs


def get_js():
    f = open(r"E:\Jovi_longlasttime\Jovi_longlasttime\signature.js", 'r', encoding='UTF-8')  ##打开JS文件
    line = f.readline()
    htmlstr = ''
    while line:
        htmlstr += line
        line = f.readline()
    ctx = execjs.compile(htmlstr)
    return ctx.call('get_as_cp_signature')
