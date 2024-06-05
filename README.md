# BulletChats

## 简介
BulletChats 是一个用于爬取哔哩哔哩（Bilibili）视频弹幕的爬虫程序。

## 弹幕定义
根据哔哩哔哩公司2021年3月在香港交易所发布的全球发行技术术语词汇表，**弹幕**（Dan Mu）被定义为像子弹一样在屏幕上飞过的评论。

## 技术要求
为了运行本项目，需要安装 **google.protobuf**。这是一个用于序列化结构化数据的库，可以在这里找到安装指南：[protobuf GitHub页面](https://github.com/protocolbuffers/protobuf)。

## 安装
1. 克隆仓库到本地机器
   
   ```git clone https://github.com/Yi-Dongshan/BulletChats.git```
3. 进入项目目录

   ```cd BulletChats```
5. 安装必要的依赖

   ```pip install -r requirements.txt```
7. 安装google.protobuf库

   访问 protobuf GitHub页面 以获取安装指南。

## 使用方法
在安装完所有依赖项后，您可以按照以下步骤使用BulletChats爬取弹幕：
1. 运行爬虫脚本
2. 根据提示输入视频的相关信息，如BV号等。

## 注意事项
- 请确保遵守哔哩哔哩的使用条款和隐私政策。
- 爬虫使用应遵循合理频率，避免对哔哩哔哩服务器造成不必要的负担。

## 贡献
如果您有任何改进建议或发现了问题，欢迎提交Pull Request或创建Issue。

## 许可
本项目采用**GPL**许可证。
