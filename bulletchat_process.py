# -*- coding = utf-8 -*- 
# @Time : 2022/3/29 21:47 
# @Author : 易东山
# @File : get_path_of_files.py 
# @Software: PyCharm


import os
import re
import pandas as pd
from pprint import pprint


# 获取指定文件夹下的所有文件路径(Ⅰ)
def listdir(path, list_name):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            listdir(file_path, list_name)
        else:
            list_name.append(file_path)
    pass


# 获取指定文件夹下的所有文件路径(Ⅱ)
def listdir_2(path):
    path = os.path.join(path=path)
    path_list = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            path_list += [os.path.join(dirpath, filename)]
    return path_list


# 弹幕去重
def bulletchat_drop_duplicates(filepath: str):
    # 读取弹幕文件
    bc_df = pd.read_csv(filepath_or_buffer=filepath, engine='python')
    # 计数1：去重前弹幕数
    num_before_drop = len(bc_df)
    # 去重
    bc_df.drop_duplicates(subset=['id'], keep='first', inplace=True)
    # 计数2：去重后弹幕数
    num_after_drop = len(bc_df)
    # 重置行索引
    bc_df.reset_index(drop=True, inplace=True)
    # 提取表头
    headers = list(bc_df.columns)
    # 删掉多余的行索引
    right_headers = ['id', 'progress', 'midHash', 'content', 'ctime', 'weight']
    for column in headers:
        if column not in right_headers:
            bc_df.drop(columns=column, inplace=True)
    # 保存至原文件
    bc_df.to_csv(path_or_buf=filepath, index=True, header=True)
    print('\r去重完成, 去重后前弹幕数: {}/{}'.format(num_after_drop, num_before_drop))
    pass


# 弹幕数据 -> 弹幕内容
def bc_info_2_bc_content_only(file_pathname: str, save_pathname: str):

    # 读取弹幕文件
    df = pd.read_csv(filepath_or_buffer=file_pathname, engine='python')

    # 提取表头
    headers = list(df.columns)
    # pprint(headers)

    # 删除除 'content' 以外的弹幕信息
    for column in headers:
        if column != 'content':
            df.drop(columns=column, inplace=True)

    # 检查输出路径是否存在, 不存在则创建路径
    save_path = save_pathname[:-16]
    folder = os.path.exists(save_path)
    if not folder:
        os.makedirs(save_path)

    # 保存 'content' 至指定文件夹
    df.to_csv(save_pathname, index=False, header=None)    # index=False 不保存行索引; header=None 不保存表头
    print('弹幕content已保存\n【弹幕content文件路径】：', save_pathname)


# 计数
def count_words(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            contents = f.read()
    except FileNotFoundError:
        return f"The file {filename} doesn't exit. Please check!"
    except UnicodeDecodeError:
        return f"Please rencode the file with utf-8 format."

    # 消去每条弹幕之间的换行符
    words_list = contents.split('\n')
    # 计数：弹幕总条数, 弹幕总字符数(包括空格)
    bc_num = len(words_list)-1
    char_num = 0
    # 遍历每条弹幕, 计数
    for words in words_list:
        char_num += len(words)
    # 列表存放计数结果
    num_count = [bc_num, char_num]
    # print(num_count)
    return num_count


if __name__ == '__main__':

    filepath = 'D:\\Bullet Chat\\弹幕\\'  # 文件夹路径

    # 获取指定文件夹下的所有文件路径 (方法2)
    file_pathname_list = listdir_2(path=filepath)
    # print(file_pathname_list)
    print('总文件数量：', len(file_pathname_list))  # 166个

    # 筛选出弹幕文件('BVxxxxxxxxxx.csv')和视频信息文件('视频信息.csv')的文件路径
    bcfile_pathname_list = []  # 存储弹幕文件的路径
    infofile_pathname_list = []  # 存储'视频信息.csv'的路径
    for file_pathname in file_pathname_list:
        # 正则表达式匹配
        bcfile_name = re.findall(pattern=r'(BV.*?\.csv)', string=file_pathname)
        infofile_name = re.findall(pattern=r'(.*?视频信息.csv)', string=file_pathname)
        if bcfile_name:
            bcfile_pathname_list.append(file_pathname)
        elif infofile_name:
            infofile_pathname_list.append(file_pathname)

    # 输出文件数目信息
    print('视频信息文件数量：', len(infofile_pathname_list))        # 66个  (22类型 * 3个频道 = 66)
    print('弹幕文件数量：', len(bcfile_pathname_list))             # 231个  ( 298-66-1 = 231 )
    pprint(bcfile_pathname_list)

    # 设置(但不创建)弹幕 'content' 的文件路径('D:\\···\\BVxxxxxxxxxx.txt')
    bccontent_pathname_list = []
    for bcfile_pathname in bcfile_pathname_list:
        bcfile_pathname = 'D:\\Bullet Chat\\弹幕-纯享版\\' + bcfile_pathname[18:-4] + '.txt'
        bccontent_pathname_list.append(bcfile_pathname)

    # 计数：所有视频的弹幕总条数, 及总字符数
    total_bc_num = 0
    total_char_num = 0

    bc_sta = []         # 弹幕统计数据

    # 批量处理弹幕文件: 去重, 提取弹幕内容, 计数 (可自由选择搭配)
    for i in range(0, len(bcfile_pathname_list)):
        # 弹幕文件路径 和 弹幕 'content' 文件路径
        bcfile_pathname = bcfile_pathname_list[i]
        bccontent_pathname = bccontent_pathname_list[i]
        # 输出序号 和 弹幕文件名
        print('-'*70)
        print(f'No.{i+1}')
        print('【弹幕文件路径】：', bcfile_pathname)

        # # 去重
        # bulletchat_drop_duplicates(filepath=bcfile_pathname)
        # # 筛选出弹幕内容, 保存至指定文件夹
        # bc_info_2_bc_content_only(file_pathname=bcfile_pathname, save_pathname=bccontent_pathname)

        # 弹幕条数和字符数统计
        bc_num = count_words(bccontent_pathname)[0]
        char_num = count_words(bccontent_pathname)[1]


        # 输出统计数据
        print('【弹幕数】：{} 条'.format(bc_num))
        print('【字符数】：{} 个'.format(char_num))

        bc_sta.append({'频道类型': bcfile_pathname.split('\\')[-3],
                        '频道': bcfile_pathname.split('\\')[-2],
                        'BV': bcfile_pathname[-16:-4],
                        '弹幕条数': bc_num,
                        '弹幕字符数': char_num})

        # 更新全局统计数据
        total_bc_num += bc_num
        total_char_num += char_num

    # 输出： 视频总数  弹幕条数  总字符数
    print('-'*70)
    print('【视频总数】：{} 个'.format(len(bcfile_pathname_list)))
    print('【弹幕总数】：{} 条'.format(total_bc_num))
    print('【字符总数】：{} 个'.format(total_char_num))

    # 保存统计数据至文件
    bc_sta_df = pd.DataFrame(bc_sta)
    bc_sta_df.to_csv(path_or_buf=filepath + '统计数据.csv', index=True, header=True)

    # 批量处理视频信息文件:
    info_df = pd.DataFrame()
    for i in range(0, len(infofile_pathname_list)):
        infofile_pathname = infofile_pathname_list[i]
        info_df_i = pd.read_csv(filepath_or_buffer=infofile_pathname, engine='python')
        info_df = pd.concat([info_df, info_df_i], ignore_index=True)
    info_df.to_csv(path_or_buf=filepath + '视频信息汇总.csv', index=True, header=True)

    """
    待完成:
    1. re找出所有 '视频信息.csv'      √
    2. 读取 '视频信息.csv'           √
    3. 匹配 统计信息 与 原有的视频信息
    4. 更新原有的 '视频信息.csv'
    5. 重定向输出统计信息至文件
    """

    """
    5. 重定向输出统计信息至文件
    import sys
    f = open('a.log', 'a')
    sys.stdout = f
    sys.stderr = f		# redirect std err, if necessary
    f.close()
    """