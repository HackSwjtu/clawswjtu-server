# clawswjtu-server
查询交大最新讲座信息和学术竞赛信息的微信小程序的后端程序
##爬虫端
讲座信息爬取的页面主要为两个：
1. http://www.swjtu.edu.cn/jsp/activity.jsp?page=1&siteId=12163&catalogPath=-12163-12259-&selectDay=&searchType=month&address=&keyword=&hdType=
2. http://dean.swjtu.edu.cn/servlet/LectureAction?Action=LectureMore&SelectType=Month

竞赛通知爬取的页面：TODO

爬虫框架使用Pyspider, Pyspider的项目，任务和结果都使用数据库进行存储，消息队列使用redis存储

运行方式: `pyspider -c config.json`

##服务端
由于微信小程序需要使用api来获得json数据，使用flask来制作api,　使用sqlalchemy做数据池连接，目前可用的api有两个：
1. /lecture/lastweek : 获取一周内的讲座信息
2. /lecture/search?keyword={} : 根据关键词进行讲座标题的模糊搜索

部署：nginx+supervisor+flask


