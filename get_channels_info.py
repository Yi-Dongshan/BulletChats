# -*- coding = utf-8 -*- 
# @Time : 2022/3/25 10:38 
# @Author : 易东山
# @File : get_bulletchat_of_channel.py
# @Software: PyCharm


import os
import pprint
import requests
import json
import pandas as pd


def get_channel_info(type_id):
    # 用于存储该类频道的所有频道信息
    channel_info_list = []
    # 循环判断信息
    has_more = True
    offset: int = 0
    # 获取该类频道的所有频道信息
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.62',
    }
    while has_more:

        type_url = 'https://api.bilibili.com/x/web-interface/web/channel/category/channel_arc/list?id={0}&offset={1}' \
            .format(type_id, offset)
        # time.sleep(0.1)
        type_res = requests.get(url=type_url, headers=headers, timeout=5)
        json_type_res = json.loads(type_res.text)
        # pprint.pprint(json_type_res['data'])

        # 删除无用数据，获取有用数据
        if json_type_res['data']['archive_channels']:
            for i in range(0, 6):
                try:
                    temp = json_type_res['data']['archive_channels'][i]
                    del temp['archives']
                    del temp['background']
                    del temp['cover']
                    del temp['theme_color']
                    channel_info_list.append(json_type_res['data']['archive_channels'][i])
                except:
                    pass

        # 更新信息，用来判断是否进行下一页的数据获取
        has_more = json_type_res['data']['has_more']
        offset = json_type_res['data']['offset']

    return channel_info_list


def get_all_channels_info(filepath='./频道信息.xlsx'):
    # 获取频道分类情况
    type_info_url = 'https://api.bilibili.com/x/web-interface/web/channel/category/list'
    type_info_response = requests.get(url=type_info_url, timeout=5)
    type_info_res_json = json.loads(type_info_response.text)
    type_info_list = type_info_res_json['data']['categories']
    # print(type_info_list)

    # 保存频道分类情况(可选)
    type_info_df = pd.DataFrame(type_info_list)
    type_info_df.rename(columns={'name': '类型',
                                 'channel_count': '频道数'},
                        inplace=True)
    with pd.ExcelWriter(path=filepath, mode='w', engine='openpyxl') as writer:
        type_info_df.to_excel(writer, sheet_name='频道分类情况')
    print('频道分类情况已保存！')

    # 遍历所有分类(2+22个), 获取各类频道的所有频道信息
    for i in range(0, 24):
        # 类信息：类id, 类名, 该类的频道数
        type_id = type_info_list[i]['id']
        type_name = type_info_list[i]['name']
        channel_count_of_type = int(type_info_list[i]['channel_count'])
        # 获取频道信息
        print('id:{} \"{}\"类的频道信息 正在获取中···'.format(type_id, type_name), end='')
        channel_info_list = get_channel_info(type_id)
        # 判断是否获取到该类的全部频道
        if len(channel_info_list) == channel_count_of_type:
            print('\rid:{} \"{}\"类的频道信息 已全部获取！'.format(type_id, type_name))
        else:
            print('\rERROR: id:{} \"{}\"类的频道信息 未全部获取,缺少 {} 个频道的频道信息！'
                  .format(type_id, type_name, channel_count_of_type - len(channel_info_list)))

        # 转换为 pd.DataFrame
        channel_info_list_df = pd.DataFrame(channel_info_list)
        # 修改标题行名称
        channel_info_list_df.rename(columns={'name': '频道名称',
                             'subscribed_count': '订阅数',
                             'archive_count': '总视频数',
                             'featured_count': '精选视频数', },
                    inplace=True)
        # 保存该类频道的频道信息, 至excel的指定sheet
        if not os.path.exists(filepath):  # 判断是否存在文件夹如果不存在则创建为文件夹
            with pd.ExcelWriter(path=filepath, mode='w', engine='openpyxl') as writer:
                channel_info_list_df.to_excel(writer, sheet_name='{0}-{1}'.format(type_id, type_name))
            print('id:{} \"{}\"类的频道信息 已保存！'.format(type_id, type_name))
        else:
            with pd.ExcelWriter(path=filepath, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
                channel_info_list_df.to_excel(writer, sheet_name='{0}-{1}'.format(type_id, type_name))
            print('id:{} \"{}\"类的频道信息 已保存！'.format(type_id, type_name))
        print('-'*30)


if __name__ == '__main__':
    # savepath = './频道信息.xlsx'  # 或者用绝对路径, 但需注意判断是否存在路径, 还有字符转义  'D:\\Bullet Chat Test\\频道信息.xlsx'
    # get_all_channels_info(savepath)

    # test: 输出某类的所有频道信息
    subchannels_list = get_channel_info(100)       # 100 代表"热门"类频道
    pprint.pprint(subchannels_list)
