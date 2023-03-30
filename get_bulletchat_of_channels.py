# -*- coding = utf-8 -*- 
# @Time : 2022/3/26 9:21 
# @Author : 易东山
# @File : get_bulletchat_of_channels.py 
# @Software: PyCharm

import random
import os
import requests
import json
import pandas as pd
import numpy as np
from retrying import retry
from pprint import pprint
import get_bulletchat



def excel2list(filepath, sheet=3):

    # 读取Excel文件
    df = pd.read_excel(io=filepath,
                       sheet_name=sheet,    # 工作表的选取
                       usecols='B:C',   # 只读取 B:C 列
                       nrows=3,)        # 读取前3行
    # print(list(df))
    # 替换Excel表格内的空单元格，否则在下一步处理中将会报错
    df.fillna("", inplace=True)

    df_list = []
    for i in df.index.values:
        # loc为按列名索引 loc 为按位置索引，使用的是 [[行号], [列名]]
        df_line = df.loc[i, ['id', '频道名称']].to_dict()
        # 将每一行转换成字典后添加到列表
        df_list.append(df_line)

    return df_list


@retry(stop_max_attempt_number=5, wait_fixed=2000)
def get_videos_info_by_channel(channel_id, year='2021'):
    videos_info_list = []

    # offset = ''     # channel_url的参数
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.62',
    }
    channel_url = 'https://api.bilibili.com/x/web-interface/web/channel/featured/list' \
                  '?channel_id={0}&filter_type={1}&offset=&page_size=30'\
        .format(channel_id, year)
    channel_response = requests.get(channel_url, headers=headers, timeout=5)
    channel_response_json = json.loads(channel_response.text)

    videos_info_list.extend(channel_response_json['data']['list'])

    return videos_info_list


def get_bulletchat_of_channels(channels_info_path: str, bulletchat_path_prefix: str):
    # 获取所有类名, 共22个(不包括"热门"和"全部")
    df = pd.read_excel(channels_info_path, sheet_name=None)
    sheet_name_list = list(df)
    del sheet_name_list[0:3]

    # 在每个类(sheet)中分别读取前3个频道的信息 (共22*3=66个)
    channels_list = []
    for i in range(3, 25):
        excel2list(channels_info_path, i)
        channels_list.extend(excel2list(channels_info_path, i))

    # 遍历这66个频道
    video_num = 0           # 计数君(视频数)
    for num in range(60, 66):

        # 频道类型, 频道信息, 保存路径
        type_num = num//3
        type_id_name = sheet_name_list[type_num]
        channel_id = channels_list[num]['id']
        channel_name = channels_list[num]['频道名称']
        bulletchat_path_suffix = '{0}\\{1}-{2}\\'.format(type_id_name, channel_id, channel_name)
        bulletchat_path = bulletchat_path_prefix + bulletchat_path_suffix

        # 控制台输出信息
        print('#' * 80)
        print('【频道】:  {0}  {1}-{2}'.format(type_id_name, channel_id, channel_name))

        # 创建弹幕保存路径
        bulletchat_folder = os.path.exists(bulletchat_path)
        if not bulletchat_folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(bulletchat_path)

        # 遍历所有频道, 获取视频bvid (数据中还包含其他视频信息)
        videos_list = get_videos_info_by_channel(channel_id)

        # 获取视频弹幕(每个频道只获取b个视频)
        for i in range(0, 3):
            if video_num >= 46:
                bvid = videos_list[random.randint(1, 5)]['bvid']
                title = videos_list[random.randint(1, 5)]['name']
            else:
                bvid = videos_list[i]['bvid']
                title = videos_list[i]['name']

            video_num += 1      # 计数君(视频数)
            print('-'*80)
            print('No.{}'.format(video_num))
            print('【BV号】:', bvid)

            bulletchat_file = bulletchat_path + '{}.csv'.format(bvid)
            # bulletchat_dd_file = bulletchat_path + '{}-dd.csv'.format(bvid)

            bulletchat_flag = os.path.exists(bulletchat_file)
            if not bulletchat_flag:  # 判断是否存在文件, 如果不存在则爬取弹幕
                get_bulletchat.get_dm_and_info_of_1video(bvid, bulletchat_path)
            else:
                print('【视频】:{}    的弹幕文件已存在.'.format(title))
    pass


if __name__ == '__main__':

    # 遍历频道, 爬取弹幕
    channels_info_path = './频道信息-排序版.xlsx'
    bulletchat_savepath = 'D:\\Bullet Chat\\弹幕\\'
    get_bulletchat_of_channels(channels_info_path, bulletchat_savepath)

    # # test 1:输入频道id, 获取频道的视频信息
    # pprint(get_videos_info_by_channel('9222'))

