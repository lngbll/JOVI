import os
from openpyxl import load_workbook
import time
from Jovi_longlasttime.tools.count import all_count

date = time.strftime('%m-%d',time.localtime())
path = 'e:\\数据统计03-25.xlsx'
dir = 'e:\定期更新{}'.format(date)

os.chdir('E:\\')
book = load_workbook(filename=path)





def count_web(path):
   return all_count(path)


def read_and_write(sheet_name,article_nums):
    sheet = book.get_sheet_by_name(sheet_name)
    keys = list(article_nums.keys())
    keys.reverse()
    values = list(article_nums.values())
    values.reverse()
    sheet.append(['日期']+keys)
    sheet.append([date]+values)
    return

def main():
    for subdir in os.listdir(dir):
        new_path = os.path.join(dir,subdir)
        count = count_web(new_path)
        read_and_write(subdir,count)
    book.save(path)

if __name__=='__main__':
    main()

