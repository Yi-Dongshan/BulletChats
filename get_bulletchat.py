# -*- coding = utf-8 -*-
# @Time : 2022/3/4 21:31
# @Author : 易东山
# @File :
# @Software: PyCharm


import os
import csv
import pprint
import time
from datetime import datetime, timedelta  # 用于日期的表示和计算
import json
import re
import requests
from dm_pb2 import DmSegMobileReply
from google.protobuf.json_format import MessageToJson
from retrying import retry
from random import uniform, randint, choice

headers = {
    # 此处需要cookie
    }

def timestamp_to_date(time_stamp, format_string="%Y-%m-%d %H:%M:%S"):
    # 将10位时间戳转换为时间字符串，默认为1970-01-01 00:00:00格式
    time_array = time.localtime(time_stamp)
    str_date = time.strftime(format_string, time_array)
    return str_date


def get_month_list(mon_1, mon_2):
    # 函数功能：获取两个月份间的所有月份
    # 输入：两个月份（字符串格式'%Y-%m'）
    # 返回：一个列表，其中包含这两个日期之间的所有月份（字符串格式'%Y-%m'）
    mon_list = []  # 形参加个后缀_0避免内外变量重名
    mon_1 = datetime.strptime(mon_1, "%Y-%m")  # 字符串2datetime
    mon_2 = datetime.strptime(mon_2, "%Y-%m")

    mon_2 += timedelta(weeks=4)  # 加一个月，约等于加4周，避免函数返回的列表中缺了mon_2
    while mon_1 <= mon_2:  # 构建日期列表
        date_str = mon_1.strftime("%Y-%m")
        mon_list.append(date_str)
        mon_1 += timedelta(weeks=4)
    mon_list = list(set(mon_list))  # 将列表转换为集合，直接删除重复元素,再转为列表
    mon_list.sort(reverse=False)  # 上一步列表去重可能会打乱顺序，需要恢复为升序
    return mon_list


def get_day_list(oid_gdl, begin_mon):  # 局部变量，加了个函数缩写的后缀

    now_y_m = str(datetime.date(datetime.now()))[0:7]  # 当前月份（字符串格式"%Y-%m"）
    m_list = get_month_list(begin_mon, now_y_m)  # 列表，包含从视频发布到现在之间的所有月份，列表元素格式为'%Y-%m'
    day_list = []  # 列表，存储某视频有弹幕的日期，该列表元素格式为'%Y-%m-%d'

    print('视频的存在弹幕日期列表正在获取中……', end='')
    for y_m in m_list:
        Q = requests.get('https://api.bilibili.com/x/v2/dm/history/index?type=1&oid=' + oid_gdl + '&month=' + y_m,
                         headers=headers)
        if re.findall('("data":null)', Q.text) == ['"data":null']:
            # print('oid:' + oid_gdl + '视频在' + y_m + '无弹幕')
            time.sleep(0.1)
        else:
            day_list += json.loads(''.join(Q.text))['data']
            # print('oid:' + oid_gdl + '视频在' + y_m + '中存在弹幕的日期已获取')
    print('\r视频的存在弹幕日期列表已获取！')

    day_list.reverse()       # 返回逆序日期, 逆序后: 索引越大, 日期离现在越远
    return day_list


@retry(stop_max_attempt_number=5, wait_fixed=2000)
def get_info_by_bvid(bvid):

    url = 'https://api.bilibili.com/x/web-interface/view?bvid=' + bvid
    info = {}  # 用来存储单个视频的信息，<class 'dict'>
    info['get_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    response = requests.get(url=url, headers=headers, timeout=5)
    json_res = json.loads(response.text)

    info['title'] = json_res['data']['title']           # 1  标题     <class 'str'>
    info['url'] = 'https://www.bilibili.com/video/' + json_res['data']['bvid']  # 2  链接     <class 'str'>
    info['cid'] = json_res['data']['cid']               # 3  cid        <class 'int'>
    info['pubdate'] = timestamp_to_date(json_res['data']['pubdate'])  # 4  发布日期（'%Y-%m-%d %H:%M:%S'）  <class 'str'>
    info['duration'] = json_res['data']['duration']     # 5  时长（单位：s）<class 'int'>
    info['jianjie'] = json_res['data']['desc']          # 6  简介      <class 'str'>
    info['up'] = json_res['data']['owner']['name']      # 7  up主     <class 'str'>
    info['view'] = json_res['data']['stat']['view']     # 8  播放量    <class 'int'>
    info['danmu'] = json_res['data']['stat']['danmaku']  # 9  弹幕数量   <class 'int'>
    info['like'] = json_res['data']['stat']['like']     # 10  点赞量    <class 'int'>
    # info['dislike'] = json_res['data']['stat']['dislike']       #  点踩量(？不确定）    <class 'int'>
    info['coin'] = json_res['data']['stat']['coin']     # 11 投币量    <class 'int'>
    info['favorite'] = json_res['data']['stat']['favorite']  # 12 收藏量    <class 'int'>
    info['his_rank'] = json_res['data']['stat']['his_rank']  # 13 历史排名(全站排行榜最高**名)   <class 'int'>
    info['reply'] = json_res['data']['stat']['reply']  # 14 评论量    <class 'int'>
    info['share'] = json_res['data']['stat']['share']  # 15 分享量    <class 'int'>

    print('【获取时间】:', info['get_time'])
    print('【视频标题】:', info['title'])
    print('【发布日期】:', info['pubdate'])
    print('【弹幕数量】:', info['danmu'])
    print('【视频cid】:', info['cid'])

    return info


@retry(stop_max_attempt_number=5, wait_fixed=2000)
def get_history_dm_of_1day(oid, date):
    url_history = 'https://api.bilibili.com/x/v2/dm/web/history/seg.so?type=1&oid=' + str(oid) + '&date=' + date

    resp = requests.get(url_history, headers=headers, timeout=5)

    # 数据格式转码
    DM = DmSegMobileReply()  # <class 'dm_pb2.DmSegMobileReply'>
    DM.ParseFromString(resp.content)
    bchat = json.loads(MessageToJson(DM))['elems']  # <class 'list'>，列表元素是字典，每个字典均包含一条弹幕的多个信息

    # # 只获取当日的弹幕（原因：某日的历史弹幕中，可能混有其它日期的弹幕）
    # day_bchat = []
    # for item in bchat:
    #     if timestamp_to_date(int(item['ctime']))[0:10] == str(date):
    #         day_bchat.append(item)

    # 弹幕信息处理
    for item in bchat:
        try:
            del item['fontsize']
        except:
            pass
        try:
            del item['color']
        except:
            pass
        try:
            del item['idStr']
        except:
            pass
        try:
            del item['mode']
        except:
            pass
        try:
            del item['pool']
        except:
            pass
        try:
            del item['action']
        except:
            pass

        item['id'] = item['id'] + '\t'  # 在excel中，rowID会用科学计数法保存，数据会丢失低2位（记事本打开的话,不处理也不会有该问题）
        item['ctime'] = timestamp_to_date(int(item['ctime']))  # 弹幕时间戳转换为时间，格式如'2022-02-03 18:09:57'

    return bchat


def get_dm_and_info_of_1video(video_bvid: str, filepath='./'):

    # 获取视频信息
    info_list = []          # 存储单个/多个视频的信息
    info = get_info_by_bvid(video_bvid)
    info_list.append(info)
    cid = info['cid']       # 视频的oid和cid一致  <class 'int'>
    title = info['title']
    danmu = info['danmu']

    # 创建文件保存路径
    folder = os.path.exists(filepath)
    if not folder:                  # 判断是否存在文件夹, 如果不存在则创建为文件夹
        os.makedirs(filepath)
    info_filename = '视频信息'        # 视频信息的文件名
    danmu_filename = video_bvid     # 弹幕的文件名 (title中可能有非法字符，故使用bvid)

    # 保存视频信息
    info_header = ['title', 'url', 'cid', 'pubdate', 'duration', 'jianjie', 'up', 'view', 'danmu',
                   'like', 'coin', 'favorite', 'his_rank', 'reply', 'share', 'get_time']
    with open(file='{0}{1}.csv'.format(filepath, info_filename), mode='a+', newline='', encoding='utf-8') as f_1:
        writer = csv.DictWriter(f_1, fieldnames=info_header)  # 提前预览列名，当下面代码写入数据时，会将其一一对应
        with open(file='{0}{1}.csv'.format(filepath, info_filename), mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            if not [row for row in reader]:
                writer.writeheader()  # 写入列名
                writer.writerows(info_list)  # 写入数据
            else:
                writer.writerows(info_list)  # 写入数据
    print('视频信息已保存！！！\n【视频信息保存路径】：{0}{1}.csv'.format(filepath, info_filename))

    # 保存弹幕keys
    bullet_chat_header = ['id', 'progress', 'midHash', 'content', 'ctime', 'weight']
    with open(file='{0}{1}.csv'.format(filepath, danmu_filename), mode='a', newline='', encoding='utf-8') as f_2:
        writer = csv.DictWriter(f_2, fieldnames=bullet_chat_header)  # 提前预览列名，当下面代码写入数据时，会将其一一对应。
        writer.writeheader()  # 写入列名

    # 获取弹幕
    video_mon = info['pubdate'][0:7]  # 视频发布日期的年月份
    day_list = get_day_list(str(cid), video_mon)
    print('【存在弹幕天数】: {}'.format(len(day_list)))
    print('开始获取历史弹幕……')
    num_bulletchat: int = 0
    num_day: int = 0

    # 爬取弹幕
    # for day in day_list:
    day = day_list[0]
    while True:

        # 在控制台输出爬取进度
        print('\r【爬取进度】: 【当前弹幕条数】: {0}/{1}    【已获取天数】: {2}/{3}    【当前时间】: {5}    正在获取 {4} 的弹幕……'
              .format(num_bulletchat, danmu,  num_day, len(day_list), day, str(datetime.time(datetime.now()))),
              flush=True, end='')

        # 用来存储单个视频的弹幕
        bullet_chat_list = []

        # 获取弹幕
        temp = get_history_dm_of_1day(cid, day)
        bullet_chat_list.extend(temp)

        # sleep
        time.sleep(round(uniform(1, 2.5), 2))  # 休息一段时间，时间长短是(a, b)范围内的带有一位小数的随机数
        # 保存弹幕
        with open(file='{0}{1}.csv'.format(filepath, danmu_filename), mode='a', newline='', encoding='utf-8') as f_2:

            writer = csv.DictWriter(f_2, fieldnames=bullet_chat_header)  # 提前预览列名，当下面代码写入数据时，会将其一一对应
            writer.writerows(bullet_chat_list)

        # 弹幕和日期计数
        num_bulletchat += len(bullet_chat_list)
        num_day = day_list.index(day) + 1

        # 如果爬到最后一天,就退出循环
        if day == day_list[-1]:
            break
        else:
            # 否则更新参数day, 继续爬
            next_day = temp[-1]['ctime'][0:10]      # "某天"的历史弹幕中, 最后一条弹幕的日期
            if day == next_day:     # 如果这天的历史弹幕里, 全部是这一天的, 下一次就爬下一个日期的
                next_day_index = day_list.index(next_day) + 1
                day = day_list[next_day_index]
            else:                   # 否则, 下一次就爬最后一条的那一天的 (会造成重复)
                day = next_day

    # 输出最后一次爬取的情况
    print('\r【爬取进度】: 【当前弹幕条数】: {0}/{1}    【已获取天数】: {2}/{3}    【完成时间】:{4}'
          .format(num_bulletchat, danmu, num_day, len(day_list), str(datetime.time(datetime.now()))))
    print('所有弹幕已保存！！！   【弹幕保存路径】：{0}{1}.csv'.format(filepath, danmu_filename))
    print('-'*80)

    pass


if __name__ == '__main__':

    """
        获取单个视频的弹幕
        BV号                标题           发布日期
        BV1EP4y1j7kV       S11全球总决赛    21-11-06
        BV1YK4y1o7Gt
    """
    bvid = input("请输入视频BV号：")
    save_path = 'D:\\Bullet Chat\\弹幕\\16-综艺\\4346-脱口秀\\'
    get_dm_and_info_of_1video(bvid, save_path)

