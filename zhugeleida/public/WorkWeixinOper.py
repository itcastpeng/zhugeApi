# 企业微信api操作

import redis
import requests
import json


class WorkWeixinOper():
    def __init__(self, corpid, corpsecret, redis_access_token_name):
        """
        初始化
        :param corpid: 企业ID
        :param corpsecret: 应用的凭证密钥
        :param redis_access_token_name: 存放在redis中的access_token对应key的名称
        """
        self.corpid = corpid  # 企业ID
        self.corpsecret = corpsecret  # 应用的凭证密钥
        self.access_token = ''  # 企业access_token
        self.redis_access_token_name = redis_access_token_name  # 存放在redis中的access_token对应key的名称
        self.redis = redis.StrictRedis(host='redis_host', port=6379, db=8, decode_responses=True)

        self.get_access_token()

        print(self.access_token)

    # 获取 access_token
    def get_access_token(self):
        self.access_token = self.redis.get(self.redis_access_token_name)
        if not self.access_token:  # 如果access_token不存在，则重新获取
            api_url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}".format(
                corpid=self.corpid,
                corpsecret=self.corpsecret,
            )

            ret = requests.get(api_url)
            self.access_token = ret.json().get('access_token')
            self.redis.set(self.redis_access_token_name, self.access_token, 7000)

    # 发送文本消息
    def send_message(self, agentid, msg, touser=None, toparty=None, totag=None):
        api_url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}".format(
            access_token=self.access_token
        )
        print('msg---------msg----------msg-------msg-------msg----> ', type(msg), msg, json.dumps(msg))
        post_data = {
            # "touser": "UserID1|UserID2|UserID3",
            # "toparty": "PartyID1|PartyID2",
            # "totag": "TagID1 | TagID2",
            "msgtype": "text",
            "agentid": agentid,
            "text": {
                "content": msg
            },
        }

        if touser:
            post_data['touser'] = touser
        if toparty:
            post_data['toparty'] = toparty
        if totag:
            post_data['totag'] = totag

        ret = requests.post(url=api_url, data=bytes(json.dumps(post_data, ensure_ascii=False), encoding='utf-8'))
        print(ret.text)


if __name__ == '__main__':
    corpid = 'wx81159f52aff62388'  # 企业ID
    corpsecret = 'dGWYuaTTLi6ojhPYG1_mqp9GCMTyLkl2uwmsNkjsSjw'  # 应用的凭证密钥
    redis_access_token_name = "access_token_send_msg"  # 存放在redis中的access_token对应key的名称
    obj = WorkWeixinOper(corpid, corpsecret, redis_access_token_name)
    username = '赵欣鹏'
    url = 'http://api.zhugeyingxiao.com/zhugeleida/public/myself_tools/approval_audit'
    msg = """【审核用户】：{username}\n【点击链接】：{url}\n """.format(
        username=username,
        url=url,
    )
    obj.send_message(
        agentid=1000005,
        # msg="""小程序名称：诸葛雷达\n审核状态：审核通过\n备注：审核通过""",
        msg=msg,
        touser="1531464629357"
    )


