
from publicFunc import account

import time
import requests
import json

token = '93b5f91eb56b8a4f8d96b7182920d68d'
# token = 'f20a5549cefd04ca6daa06eeb251ca36'
timestamp = str(int(time.time() * 1000))

get_data = {
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    # 'user_id': 1,
    'user_id': 1,



}

post_data = {

}

ip = 'http://127.0.0.1:8001'
# ip = 'http://192.168.100.20:8000'
# ip = 'http://api.zhugeyingxiao.com'




# url =  ip + '/zhugeleida/admin/help_doc'  # 获取产品的列表
# get_data['article_id'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)

# url =  ip + '/zhugeleida/admin/help_doc/add/0'  # 获取产品的列表
# post_data['title'] = '我是标题'
# post_data['content'] = '我是内容'
# ret = requests.post(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/help_doc/update/1'  # 获取产品的列表
# post_data['title'] = '我是标题xx'
# post_data['content'] = '我是内容xx'
# ret = requests.post(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/help_doc/delete/1'  # 获取产品的列表
#
# ret = requests.post(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/login'  # 获取产品的列表
# post_data['username'] = 'zhangcong'
# post_data['password'] = '123456'
#
# ret = requests.post(url, data = post_data ,params=get_data)

# url =  ip + '/zhugeleida/admin/modify_password'  # 获取产品的列表
# post_data['password1'] = '1234qwerQWERA'
# post_data['password2'] = '1234qwerQWER'
# ret = requests.post(url, data = post_data ,params=get_data)



# url =  ip + '/zhugeleida/admin/login_rules'  # 获取产品的列表
# ret = requests.get(url, data = post_data ,params=get_data)

######################### 小程序第三方授权 ############################

# url = ip + '/zhugeleida/admin/open_weixin/tongzhi'
# get_data['signature'] = '6b6913bd899e3a4ab761d7d385caa598f15b4d3b'
# get_data['timestamp'] = '1533708502'
# get_data['nonce'] = '1568674329'
# get_data['msg_signature'] = 'b9287c7d48aff83269b7e3ea528ab826e99a93d9'
#
# post_data['postdata'] = """
# 	<xml>
# 		<AppId><![CDATA[wx67e2fde0f694111c]]></AppId>
# 		<Encrypt><![CDATA[tf9Ck4zUGvL1s1QBIG3McN7BJhKpMzkCdFJYVR1QJdqcRO4v5Z2DmyFkuTQctoCYiFKNYjxMiK75BAepovmv5j+Ta188nsXXOsAqT17NRFZPif8/bcbqSMDOWBhkNVAS6DCoOrKkN+RMx3HLhkLp2A6lh+3jDpXvoeqbrhP4sWjwMzBzntGOdKnf/rIyODl5azXY29dwXrWDoqrrKAcOAxz38gjMFssDc8AYDcXFzxmLsSf14fYzzJj6WyKBLR23Jp/1spuCLDWcMnUE35T7gXCFaW/p1cQwtcwGGbqZlbI6cpQbFZNTKD83KVew+qGFFrdsJuErXORHU5B+H3Jx7R9o/+F+gvYssAGHEEVG8ZZKvP2VCti/4tN1j5BVuCgyAPki2UedFpDCRxSmXmK8WIIURx2DTnyu5+mqttgxg2ubKpsHFbTnpIAIBCIVYVbHisyx0k17vZma/BGlJfmgJg==]]></Encrypt>
# 	</xml>
# """

# ret = requests.post(url, params=get_data,data=post_data)


# url = ip + '/zhugeleida/admin/open_weixin/create_grant_url'  # 获取 关联第三方的二维码
# ret = requests.post(url, params=get_data,data=post_data)


######################### 【企业微信】三方服务商授权 #########################

# url = ip + '/zhugeleida/admin/open_qiyeweixin/create_grant_url'  # 获取 关联第三方的二维码
# ret = requests.post(url, params=get_data,data=post_data)
# #
# url = ip + '/zhugeleida/admin/open_qiyeweixin/set_session_info'  # 获取 关联第三方的二维码
# ret = requests.post(url, params=get_data,data=post_data)


# url = ip + '/zhugeleida/admin/xcx_auth_process'
# ret = requests.get(url, params=get_data,data=post_data)


# url = ip + "/zhugeleida/admin/xcx_auth_process/update/1" #
# post_data['authorization_appid'] = 'wxd306d71b02c5075e'
# ret = requests.post(url, params=get_data, data=post_data)


# url = ip + "/zhugeleida/admin/xcx_auth_process/update/xcx_get_authorizer_info"
# ret = requests.get(url, params=get_data)


# url = ip + '/zhugeleida/admin/open_qiyeweixin/third_fang_single_login'  #
# get_data['auth_code'] = 'CdpUdlQg3fLfi2-L6yzODsknfrCsMmIlOFpKEiQfslt5pTMLfEX2XquQESxfCTyBdZT1LwMNF4PIgGXsEpHoZ8kKqlu-iKlICMRgcjBRw0kclDg6y_FrGAw4JjWn2tpd'
# get_data['state'] = 'scan_code_web_login'
# ret = requests.get(url, params=get_data,data=post_data)


# url = ip + '/zhugeleida/admin/open_qiyeweixin/web_scan_authorize_qrcode'  #
# ret = requests.get(url, params=get_data,data=post_data)

# url = ip + '/zhugeleida/admin/jiChuSheZhi/myself_query_fafang_info'  #
# get_data['mch_billno'] =  '201812101344448436727' #  '201812051030494953312' # '201812051240434358450'
# get_data['company_id'] = 2
#
# ret = requests.get(url, params=get_data,data=post_data)






# url = ip + "/zhugeleida/admin/xcx_auth_process/update/3" #
# post_data['name'] = '测试小程序'
# post_data['head_img'] = 'xxx/yy.jpg'
# post_data['introduce'] = '不错的小程序哦'
# post_data['service_category'] = 'IT互联网'
# ret = requests.post(url, params=get_data, data=post_data)


# url = ip + "/zhugeleida/admin/dai_xcx/get_qrcode" #  获取体验小程序的体验二维码
# post_data['customer_id'] = 1
# ret = requests.post(url, params=get_data, data=post_data)


# url = ip + "/zhugeleida/admin/dai_xcx/submit_audit" #  获取体验小程序的体验二维码
# post_data['customer_id'] = 1
# ret = requests.post(url, params=get_data, data=post_data)



########################## 公众号 认证 ############################

# url = ip + '/zhugeleida/admin/gzh_auth_process'
# ret = requests.get(url, params=get_data,data=post_data)


# url = ip + '/zhugeleida/admin/gzh_auth_process/update/gzh_authorization_binding_xcx'
# get_data['company_id'] = 1
# get_data['appid'] = 'wxd306d71b02c5075e'
#
#
# ret = requests.post(url, params=get_data,data=post_data)






# url = ip + '/zhugeleida/admin/gzh_auth_process/update/query_already_bind_xcx'
# get_data['company_id'] = 1
#
#
#
# ret = requests.get(url, params=get_data,data=post_data)


############################## 公众号授权 #######################################
#
# url = ip + '/zhugeleida/admin/open_weixin_gongzhonghao/callback/wx84390d5be4304d80'  # 获取 关联第三方的二维码
# get_data['signature']= '4e59771150050f61a4830034fda6d9d1530128b4'
# get_data['timestamp']= '1545795939'
# get_data['nonce']= '1078398626'
# get_data['openid']= 'ob8Vy537Y0L0fHztITCKVjP9vf58'
# get_data['encrypt_type']= 'aes'
# get_data['msg_signature']= '18601dac3d3e69d6e7c47e70c8a7b6bcb134e029'
# post_data['xml'] = '<xml>\x0A    <ToUserName><![CDATA[gh_a8dc5e05049a]]></ToUserName>\x0A    <Encrypt><![CDATA[4YCLr9zMK2dB+kopMLXYojMBDrsEMKtqHY4ABT7p/Ffjea5+BamGG4upf4rfZZziyn3JSxVPpVroIYTNRdY0Yirk9j5fkHOJA3CWjjdk/ouVWSeI4hZhsHT0lLmORS/txiA6J2fmMxzx81CLnuEVC51eoU8eSi+XhshCzbzFOIYHf6YqpRjkb24xPLoKc696zvDdaYSytN/PUfEAeaR/Mk1uOyfuKhevxiH3uwj8qH2Caj9CTTSG8O0aebv6Dbao3Dcxx3/SO3j4a3IsF8735sM7KmopAwL/YnGxhwYAbxX8Kw3k2EnmBBHBFYYGGqaUTG/IreB9q42WxG4vtNskTxqX0yEnHpN8PtG+Yaa1otKq5YaO70dB1OhJ3cKivK0MpO36JGfT3QfYs6yFZYQymTEdfwIvJpwFUHeLCZQAhc0=]]></Encrypt>\x0A</xml>'
#
# ret = requests.post(url, params=get_data,data=post_data)



# url = ip + '/zhugeleida/admin/open_weixin_gongzhonghao/callback/wxa77213c591897a13?signature=29972dfe20da067eeaac10d6f46c5cf4f5e63608&timestamp=1545287108&nonce=11638010&openid=ob5mL1XQABqWWzvk308yArZVdB4M&encrypt_type=aes&msg_signature=acb092883c8a145f4d4fd3fb8305188407954e92'  # 获取 关联第三方的二维码
#
#
# post_data['xml'] = '<xml>\x0A    <ToUserName><![CDATA[gh_21c48bcaa193]]></ToUserName>\x0A    <Encrypt><![CDATA[1ISm89mMWffsJ8GXTpl4rtU7nYAT35L2+WofctxAiIH/9ximcXTaEBC4wVtQmljZVFQvePx/4GhDCa+Z6UAgocafmEVHF7VHyHGOVywAzLHci2Pu0zcHlsP23ZpaQyp10phxKbFIk7gTJJqtem3IhUmxw2D+4sbjYSFw1rgbS1wDt/3NHKanxUVubnz0TrA5ihEHv10MB9Ew0fR4xMP4L4mjtLYMReJeZ1fh8+3/ggSo0vN5jp4M9LqLESfzYW4xHBReUZt24xkyQ1JIxYRfobN/veWZhRALRUpQazoxmGhTbLbdGQRrrSmYCbsAtim7Eb7qbqAQMG1073sv6zhNaqe4kosWNlfzSSjzhAFb2qBxqSeNqERVw1g48fMf0lUkjSJ05+ObA5cr/RyXetQF2V05cQ4V0PQB8m6y3JThP4A=]]></Encrypt>\x0A</xml>'
#
#
# ret = requests.post(url, params=get_data,data=post_data)











# url = ip + '/zhugeleida/admin/open_weixin_gongzhonghao/create_grant_url'  # 获取 关联第三方的二维码
# ret = requests.post(url, params=get_data,data=post_data)


# url = ip + '/zhugeleida/admin/gzh_auth_process'
# ret = requests.get(url, params=get_data, data=post_data)


# url = ip + '/zhugeleida/admin/gzh_auth_process'
# ret = requests.get(url, params=get_data, data=post_data)



# url = ip + "/zhugeleida/admin/gzh_auth_process/update/app_id" #
# post_data['authorization_appid'] = 'wx6ba07e6ddcdc69b3'
# ret = requests.post(url, params=get_data, data=post_data)

######################## 公众号 #####################################

# url = ip + '/zhugeleida/gongzhonghao/create_gongzhonghao_auth_url/1'  # 获取 关联第三方的二维码
# ret = requests.get(url, params=get_data,data=post_data)







################################ 代小程序 发布 ####################################

# url = ip + "/zhugeleida/admin/dai_xcx/upload_code" # 第三方代小程序发布.审核
# post_data['app_ids_list'] = json.dumps([2])
# post_data['user_version'] = 'v1.0.5'
# post_data['template_id'] = 5
# post_data['user_desc'] = '诸葛雷达-营销_1.0.5'
# ret = requests.post(url, params=get_data, data=post_data)



# url = ip + "/zhugeleida/admin/dai_xcx/submit_audit" # 第三方代小程序发布
# post_data['app_ids_list'] = json.dumps([2])
# ret = requests.post(url, params=get_data, data=post_data)



# url = ip + "/zhugeleida/admin/dai_xcx/template_list"      #  获取模板
# ret = requests.get(url, params=get_data, data=post_data)


# url = ip + "/zhugeleida/admin/dai_xcx/get_latest_audit_status_and_release_code" #  定时任务
# ret = requests.get(url, params=get_data, data=post_data)



# url = ip + "/zhugeleida/admin/dai_xcx/get_latest_audit_status"     #  获取查询最新一次提交的审核状态
# ret = requests.get(url, params=get_data, data=post_data)


# url = ip + "/zhugeleida/admin/dai_xcx/relase_code"                 #  获取查询最新一次提交的审核状态
# post_data['app_ids_list'] = json.dumps([2])
# # post_data['auditid_list'] = ['427336758']
# ret = requests.post(url, params=get_data, data=post_data)



# url = ip + "/zhugeleida/admin/xcx_app"                  #  获取所有APP
# ret = requests.get(url, params=get_data, data=post_data)



# url = ip + "/zhugeleida/admin/dai_xcx/undocode_audit" # 第三方代小程序撤回
# post_data['app_ids_list'] = json.dumps([1])
# ret = requests.post(url, params=get_data, data=post_data)




###############################################################################################


# url = ip + '/zhugeleida/admin/home_page/acount_data' # 统计-名片状态+账号状态
# ret = requests.get(url, params=get_data)


# url = ip + '/zhugeleida/admin/home_page' # 统计-数据概览
# ret = requests.get(url, params=get_data)

# url = ip + '/zhugeleida/admin/home_page/line_info' # 统计-曲折图数据
# post_data['days'] = 7
# post_data['index_type'] = 1
# ret = requests.post(url, params=get_data,data=post_data)


#修改用户状态
# url = ip + '/zhugeleida/admin/user/update_status/1' # 更新用户的开启状态
# post_data['status'] = 1
# ret = requests.post(url, data=post_data,params=get_data)


#
# url = ip + '/zhugeleida/admin/admin_userprofile/switch_admin_user/2' # 更新用户的开启状态
# ret = requests.post(url, data=post_data,params=get_data)



# url = ip + '/zhugeleida/mycelery/bossLeida_acount_data_and_line_info/acount_data' # 统计-名片状态+账号状态
# get_data['company_id'] = 1
# ret = requests.get(url, params=get_data)


url = ip + '/zhugeleida/mycelery/bossLeida_acount_data_and_line_info/line_info' # 统计-名片状态+账号状态
get_data['company_id'] = 1
ret = requests.get(url, params=get_data)


#查询企业用户

# url = ip + '/zhugeleida/admin/user' # 更新用户的开启状态
# get_data['status'] = ''
# get_data['department'] = 1
# get_data['position'] = '拉'
# get_data['username'] = '张'
# ret = requests.get(url, data=post_data,params=get_data)




# url =  ip + '/zhugeleida/admin/product/product_list'  # 获取产品的列表
# get_data['product_type'] = 2
# # get_data['company_id'] = 4
# # get_data['product_name'] = '膜法'
# # get_data['status'] = 1  # # (1,'已上架') # (2,'已下架')
# ret = requests.get(url, data = post_data ,params=get_data)

# url =  ip + '/zhugeleida/admin/product/feedback_list'  # 获取产品的列表
# # get_data['status'] = 1
# # get_data['company_id'] = 1
#
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/product/product_single'  # 获取产品的列表
# get_data['product_id'] = 7
# get_data['product_type'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)


################################## 活管理设置 ###############################


# url =  ip + '/zhugeleida/admin/activity_manage/set_focus_get_redPacket'  # 获取产品的列表
# post_data['is_focus_get_redpacket'] = True
# post_data['focus_get_money'] = 1
# ret = requests.post(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/activity_manage/query_focus_get_redPacket'  # 获取产品的列表
# get_data['company_id'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)

#
# url =  ip + '/zhugeleida/admin/activity_manage/add/1'  # 获取产品的列表
# get_data['company_id'] = 1
# post_data['activity_name'] = '[抢话费互动]'
# post_data['activity_total_money'] = 10000
# post_data['activity_single_money'] = 2
# post_data['reach_forward_num'] = 5
# post_data['start_time'] ='2018-10-12 16:03'
# post_data['end_time'] = '2018-10-13 16:03'
# ret = requests.post(url, data = post_data ,params=get_data)

# url =  ip + '/zhugeleida/admin/activity_manage/update/1'  # 获取产品的列表
# get_data['company_id'] = 1
# post_data['article_id'] = 1
# post_data['activity_name'] = '[抢话费互动]'
# post_data['activity_total_money'] = 10000
# post_data['activity_single_money'] = 2
# post_data['reach_forward_num'] = 5
# post_data['start_time'] ='2018-10-12 16:03'
# post_data['end_time'] = '2018-10-13 16:03'
# ret = requests.post(url, data = post_data ,params=get_data)




# url =  ip + '/zhugeleida/admin/activity_manage/activity_list'  # 获取产品的列表
# get_data['company_id'] =1
# get_data['status'] = 2
# # get_data['activity_name'] = '想'
# # get_data['article_title'] = 'G'
#
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/activity_manage/change_artivity_status/1'  # 获取产品的列表
# post_data['status'] = 1
# ret = requests.post(url, data = post_data ,params=get_data)



# url =  ip + '/zhugeleida/admin/activity_manage/send_activity_redPacket'  # 获取产品的列表
# get_data['company_id'] = 1
# get_data['article_id'] = 2
# get_data['activity_id'] = 2
# get_data['status'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/activity_manage/query_total_xiaofei'  # 获取产品的列表
# get_data['company_id'] = 1
#
# ret = requests.get(url, data = post_data ,params=get_data)



# url =  ip + '/zhugeleida/admin/activity_manage/query_focus_gongzhonghao_customer'  # 获取产品的列表
# get_data['company_id'] = 1
# get_data['is_receive_redPacket'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/activity_manage/generate_focus_redPacket_excel'  # 获取产品的列表
# get_data['company_id'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)



# url =  ip + '/zhugeleida/admin/money_manage/generate_money_record_excel'  # 获取产品的列表
# get_data['company_id'] = 1
# # get_data['start_time'] = 1
# # get_data['start_time'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)
#
#
#
# url =  ip + '/zhugeleida/admin/money_manage/generate_money_record_excel'  # 获取产品的列表
# get_data['company_id'] = 1
# # get_data['start_time'] = 1
# # get_data['start_time'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/theOrder/generate_theOrder_excel/0'  # 获取产品的列表
# get_data['company_id'] = 1
# # get_data['start_time'] = 1
# # get_data['start_time'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)



# url =  ip + '/zhugeleida/admin/tuiKuanDingDan/generate_tuiKuan_Order_excel/0'  # 获取产品的列表
# get_data['company_id'] = 1
# # get_data['start_time'] = 1
# # get_data['start_time'] = 1
# ret = requests.get(url, data = post_data ,params=get_data)



##################################### 文章 + 文章标签 + 文章增删改查 ###############################


# url =  ip + '/zhugeleida/qiyeweixin/article/myarticle/1'  # 获取产品的列表
# # get_data['id'] = 1
# # get_data['status'] = 2
# # get_data['title'] = 'xx'
# # get_data['order'] = '-read_count'  # -forward_count  -create_date
# # get_data['tags_list'] = '[1]'
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/article/myarticle/1'  # 获取产品的列表
# ret = requests.get(url, data = post_data ,params=get_data)



# url =  ip + '/zhugeleida/admin/article/add/0'  # 获取产品的列表
# post_data['title'] = 'YYYYY'
# post_data['summary'] = 'BBBB'
# post_data['content'] = 'xx'
# post_data['cover_picture'] = 'xxxx.jpg'
#
# ret = requests.post(url, data = post_data ,params=get_data)



# url =  ip + '/zhugeleida/admin/article/update/9'  # 获取 二维码 产品的列表
# post_data['title'] = 'HHHHH'
# post_data['summary'] = 'CCCCC'
# post_data['content'] = 'NNNNN'
# post_data['cover_picture'] = 'xxxx.jpg'
# ret = requests.post(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/article/delete/10'  # 获取产品的列表
# ret = requests.post(url, data = post_data ,params=get_data)





# url =  ip + '/zhugeleida/admin/article_tag'  # 获取产品的列表
# ret = requests.get(url, data = post_data ,params=get_data)

# url =  ip + '/zhugeleida/admin/article_tag/add/0'  # 获取产品的列表
# post_data['tag_name'] = 'xxxx'
# ret = requests.post(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/article_tag/update/5'  # 获取产品的列表
# post_data['tag_name'] = 'TTTT'
# ret = requests.post(url, data = post_data ,params=get_data)

# url =  ip + '/zhugeleida/admin/article_tag/delete/5'  # 获取产品的列表
# ret = requests.post(url, data = post_data ,params=get_data)





# url =  ip + '/zhugeleida/gongzhonghao/article/myarticle/1'  # 获取产品的列表
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/article/climb_gzh_article_list'  # 获取产品的列表
# get_data['company_id'] = 1
# get_data['status'] = 0
#
# ret = requests.get(url, data = post_data ,params=get_data)


# url =  ip + '/zhugeleida/admin/article/sync_gzh_article'  # 获取产品的列表
# get_data['company_id'] = 2
# post_data['source_url'] = 'https://mp.weixin.qq.com/s/NpG9594hyKxMys3UL1SmNA'   # 'https://mp.weixin.qq.com/s/gOtmE8DH34xJtU8Eh5-w6w'  #'https://mp.weixin.qq.com/s?__biz=MzA5NzQxODgzNw==&mid=502885335&idx=1&sn=4b2c05ce119948494822f430a8a2b322&chksm=08ace0ed3fdb69fb4783142b29a10cf3bf9ed4447c809df5f439214f95d6eb21d11951c57bf5#rd'
# # post_data['media_id_list'] =  json.dumps(['ivcZrCjmhDznUrwcjIReRPoDiI2Fke3LVhHU7hNXTXE'])  #json.dumps(['ivcZrCjmhDznUrwcjIReRKw072mb7eq1Kn9MNz7oAxA'])
# ret = requests.post(url, data=post_data ,params=get_data)



# url =  ip + '/zhugeleida/mycelery/batchget_article_material'  # 获取产品的列表
# get_data['company_id'] = 1
# ret = requests.get(url, data=post_data ,params=get_data)



#############################################################################################

## z支付平台

# url =  ip + '/zhugeleida/admin/money_manage/money_record_list'  # 获取产品的列表
# get_data['company_id'] = 1
# # get_data['type'] = 3
# ret = requests.get(url, data=post_data ,params=get_data)


# url = 'http://api.zhugeyingxiao.com/zhugeleida/public/myself_tools/monitor_send_gzh_template_msg' # 分页 聊天信息记录
#
# get_data['title'] = '标题'
# get_data['content'] = '具体内容'
# get_data['remark'] = '备注'
#
# ret = requests.get(url, params=get_data)


# url = 'http://api.zhugeyingxiao.com/zhugeleida/mycelery/common_send_gzh_template_msg' # 分页 聊天信息记录
# # get_data['data'] = json.dumps({'user_id': 55, 'customer_id' : 854})
# get_data['company_id'] = 1
# get_data['customer_id'] = 854
#
# get_data['type'] = 'gongzhonghao_template_tishi' # 固定类型
# get_data['title'] = '标题'
# get_data['content'] = '具体内容'
# get_data['remark'] = '备注'
#
# ret = requests.get(url, data=post_data ,params=get_data)


# import random
#
# max_single_money = 1
# min_single_money = 0.3
# rand_num = random.uniform(max_single_money, min_single_money)
#
# focus_get_money = round(rand_num, 2)
# print('focus_get_money----->>',focus_get_money)
#
# url = ip +   '/zhugeleida/mycelery/record_money_process' # 分页 聊天信息记录
# get_data['type'] = 3
# get_data['user_id'] = 55
# get_data['customer_id'] = 852
# get_data['company_id'] = 1
# get_data['transaction_amount'] = float(focus_get_money) #int(float(0.4800))
# get_data['source'] = 2
#
# ret = requests.get(url, data=post_data ,params=get_data)




# url =  ip + '/zhugeleida/admin/company/recharge_amount/1'  # 获取产品的列表
#
# post_data['recharge_amount'] = 100
#
# ret = requests.post(url, data=post_data ,params=get_data)



# url =  ip + '/zhugeleida/admin/company/revoke_amount/1'  # 获取产品的列表
#
# post_data['revoke_amount'] = 22
#
# ret = requests.post(url, data=post_data ,params=get_data)





##########################################################################################




# url = ip + '/zhugeleida/admin/product/change_status/3' # 更新产品的状态
# post_data['status'] = 3
# ret = requests.post(url, data=post_data,params=get_data)

# url = ip + '/zhugeleida/admin/product/delete/11' # 更新产品的状态
#
# ret = requests.post(url, data=post_data,params=get_data)



# url = ip + '/zhugeleida/admin/product/add/0' # 添加产品
# post_data['name'] = 'jajjaj'
# post_data['price'] = 111
# post_data['price'] = 'naifad'
# post_data['product_type'] = 1
# content =  {
# 	'cover_data': [{
# 		'type': 'picture_url',
# 		'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_1.png', 'statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_2.png']
# 	}],
# 	'article_data': [{
# 			'type': 'title',
# 			'data': ['xx我是标题1']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_1.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_2.png']
# 		},
# 		{
# 			'type': 'title',
# 			'data': ['我是标题2']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_3.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容3']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_4.png']
# 		}
# 	]
# }
# post_data['content'] = json.dumps(content)
# ret = requests.post(url, data=post_data,params=get_data)




# url = ip + '/zhugeleida/admin/product/update/13' # 修改产品
# post_data['name'] = '发的发生的'
# post_data['price'] = 111
# post_data['price'] = 'naifad'
# post_data['product_type'] = 1
#
# content =  {
# 	'cover_data': [{
# 		'type': 'picture_url',
# 		'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_1.png', 'statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_2.png']
# 	}],
# 	'article_data': [{
# 			'type': 'title',
# 			'data': ['xx我是标题1']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_1.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_2.png']
# 		},
# 		{
# 			'type': 'title',
# 			'data': ['我是标题2']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_3.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容3']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_4.png']
# 		}
# 	]
# }
# post_data['content'] = json.dumps(content)
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip + '/zhugeleida/admin/product/change_feedback_status/1' # 更新产品的状态
# post_data['status'] = 2
# ret = requests.post(url, data=post_data,params=get_data)

#
# url = ip + '/zhugeleida/admin/product/recommend_index/7' # 更新推荐指数的状态
# post_data['index'] = 2
# ret = requests.post(url, data=post_data,params=get_data)





########################### 公司管理 + 秘钥管理 #########################################

# url = ip +  '/zhugeleida/admin/company/author_status'   # 验证通过
# get_data['company_id'] = 1
# ret = requests.get(url, data=post_data,params=get_data)

# url = ip +  '/zhugeleida/admin/company'   # 验证通过
# get_data['id']=1
# ret = requests.get(url, data=post_data,params=get_data)


# url = ip +  '/zhugeleida/admin/company/add_company/0'   # 后台增加公司
# post_data['name'] = '大麦公司'
# post_data['charging_start_time'] = '2018-08-01'
# post_data['open_length_time'] = 2
# post_data['mingpian_available_num'] = 5
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip +  '/zhugeleida/admin/company/update_company/1'   # 后台增加用户
# post_data['name'] = '大麦公司11'
# post_data['charging_start_time'] = '2018-09-01'
# post_data['open_length_time'] = 4
# post_data['mingpian_available_num'] = 10
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip +  '/zhugeleida/admin/company/update_agent/1'   # 后台增加用户
# post_data['name'] = 'AI雷达'
# post_data['app_type'] = 1
# post_data['agent_id'] = 1000002
# post_data['app_secret'] = '48m2h1e2DRcA55yfKqHa083UpbJy-30u30ypy4zPr8E'
# ret = requests.post(url, data=post_data,params=get_data)




# url = ip +  '/zhugeleida/admin/company/update_tongxunlu/1'   # 后台增加用户
# post_data['corp_id'] = 'wx81159f52aff62388'
# post_data['tongxunlu_secret'] = '-pkF6u6vdXRbapZNb-fdQc16DXBhGCgDmyfa0OUuOgk'
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip +  '/zhugeleida/admin/company/edit_service_setting'   # 验证通过
# post_data['type'] = 1  #  (1, '第三方企业微信'), (2, '第三方公众号'), (3, '第三方小程序')
#
# post_data['config'] = json.dumps({
#     'leida': {
#         'sToken': '5lokfwWTqHXnb58VCV',
#         'sEncodingAESKey': 'ee2taRqANMUsH7JIhlSWIj4oeGAJG08qLCAXNf6HCxt',
#         'sCorpID': 'wx5d26a7a856b22bec', #SuiteID
#     },
#     'boss': {
#         'sToken': '22LlaSyBP',
#         'sEncodingAESKey': 'NceYHABKQh3ir5yRrLqXumUJh3fifgS3WUldQua94be',
#         'sCorpID': 'wx36c67dd53366b6f0',
#     },
#     'address_book': {
#         'sToken': '8sCAJ3YuU6EfYWxI',
#         'sEncodingAESKey': '3gSz92t8espUQgbXembgcDk3e6Hrs9SpJf34zQ8lqEj',
#         'sCorpID': 'wx1cbe3089128fda03',
#     },
#     'general_parm': {
#         'sEncodingAESKey': 'HwX3RsMfMx9O4KBTqzwk9UMJ9pjNGbjE7PTyPaK7Gyxu4Z_G0ypv9iXT97A3EFDt',
#         'sCorpID': 'wx81159f52aff62388',
#     },
#     'domain_urls': {
#         'leida_http_url': 'http://zhugeleida.zhugeyingxiao.com'  #可信域名
#     }
# })

# post_data['type'] = 2  #  (1, '第三方企业微信'), (2, '第三方公众号'), (3, '第三方小程序')
# post_data['config'] = json.dumps( {
#     'app_id' : 'wx6ba07e6ddcdc69b3',  # 公众号 AppID
#     'app_secret' : '0bbed534062ceca2ec25133abe1eecba',   # 公众号 AppSecret
#     'token' :'R8Iqi0yMamrgO5BYwsODpgSYjsbseoXg',         # 消息校验Token
#     'encodingAESKey' : 'iBCKEEYaVCsY5bSkksxiV5hZtBrFNPTQ2e3efsDC143',  #消息加解密Key
#     'authorization_url' : 'http://zhugeleida.zhugeyingxiao.com',       #登录授权的发起页域名
#     'api_url' : 'http://api.zhugeyingxiao.com'                         # 接口域名
# })


# post_data['type'] = 3  #  (1, '第三方企业微信'), (2, '第三方公众号'), (3, '第三方小程序')
# post_data['config'] = json.dumps( {
#     'app_id' : 'wx6ba07e6ddcdc69b3',  # 公众号 AppID
#     'app_secret' : '0bbed534062ceca2ec25133abe1eecba',   # 公众号 AppSecret
#     'token' :'R8Iqi0yMamrgO5BYwsODpgSYjsbseoXg',         # 消息校验Token
#     'encodingAESKey' : 'iBCKEEYaVCsY5bSkksxiV5hZtBrFNPTQ2e3efsDC143',  #消息加解密Key
#     'authorization_url' : 'http://zhugeleida.zhugeyingxiao.com',       #登录授权的发起页域名
#     'api_url' : 'http://api.zhugeyingxiao.com'                         # 接口域名
# })
# ret = requests.post(url, data=post_data,params=get_data)



# url = ip +  '/zhugeleida/admin/company/query_service_settings'   # 验证通过
# # get_data['type'] = 1
#
# ret = requests.get(url, data=post_data,params=get_data)


















############################# 修改用户状态 ####################################

# url = ip +  '/zhugeleida/admin/user/add/0'   # 后台增加用户
# post_data['username'] = '我是你爸爸15'
# post_data['password'] = '123456xx'
# post_data['role_id'] = 1
# post_data['position'] = '运维TTT'
# post_data['department_id'] = '[]'
# post_data['company_id'] = 1
# post_data['phone'] = 13256718366
# post_data['mingpian_phone'] = 13966463395
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip +  '/zhugeleida/admin/admin_userprofile/add/0'   # 后台增加用户
# post_data['login_user'] = 'fsdfsa'
# post_data['username'] = 'sdfsadf'
# post_data['password'] = '123456'
# post_data['role_id'] = 1
# post_data['position'] = '运维TTT'
# # post_data['department_id'] = '[]'
# post_data['company_id'] = 1
# #post_data['phone'] = 13256718366
# #post_data['mingpian_phone'] = 13966463395
# ret = requests.post(url, data=post_data,params=get_data)




# url = ip +  '/zhugeleida/admin/admin_userprofile/update/3'   # 后台增加用户
# post_data['login_user'] = '34vvvv'
# post_data['username'] = 'v55544'
# post_data['password'] = 'qwert'
# post_data['role_id'] = 1
# post_data['position'] = 'fff'
# # post_data['department_id'] = '[]'
# post_data['company_id'] = 1
# #post_data['phone'] = 13256718366
# #post_data['mingpian_phone'] = 13966463395
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip +  '/zhugeleida/admin/admin_userprofile/delete/4'   # 后台增加用户
# ret = requests.post(url, data=post_data,params=get_data)

# url = ip + '/zhugeleida/admin/admin_userprofile'    #后台用户展示嗯嗯。
# ret = requests.get(url, params=get_data)



# url = ip +  '/zhugeleida/admin/user/create_small_program_qr_code/0'   # 后台增加用户
# post_data['user_id'] = 128
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip +  '/zhugeleida/admin/user/sync_user_tongxunlu/5'   # 后台增加用户
# ret = requests.post(url, data=post_data,params=get_data)


#######################################################################


# url = ip +  '/zhugeleida/admin/user/create_scan_code/0'   # 生成 扫描的用户二维码
# ret = requests.get(url, data=post_data,params=get_data)

# url = ip +  '/zhugeleida/admin/user/scan_code_to_add_user/0'   # 生成 扫描的用户二维码
# post_data['username'] = '李大爷'
# post_data['position'] = '喂驴的'
# post_data['wechat'] = '44944'
# post_data['wechat_phone'] = '13290563972'
# post_data['mingpian_phone'] = '13290563972'
# post_data['department_id'] = json.dumps([1,2])
#
# ret = requests.post(url, data=post_data,params=get_data)



# url = ip + '/zhugeleida/admin/user'    #后台用户展示嗯嗯。
# get_data['type'] = 'temp_user'
# ret = requests.get(url, params=get_data)

# url = ip +  '/zhugeleida/admin/user/update/3'   # 后台增加用户
# get_data['type'] = 'temp_user'
# post_data['username'] = 'v55544'
# post_data['position'] = '呵呵呵呵'
#
# post_data['company_id'] = 1
# post_data['wechat'] = 13256718366
# post_data['wechat_phone'] = 13256718366
# post_data['mingpian_phone'] = 13966463395
# post_data['department_id'] = json.dumps([2,3])
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip +  '/zhugeleida/admin/user/delete/3'   # 后台增加用户
# get_data['type'] = 'temp_user'
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip +  '/zhugeleida/admin/user/approval_storage_user_info/0'   # 后台增加用户
# post_data['user_id_list'] = json.dumps([1])
#
# ret = requests.post(url, data=post_data,params=get_data)




##############################################################################

# url = ip + '/zhugeleida/admin/article/add/0' # 添加产品
# post_data['title'] = 'jajjaj'
# post_data['summary'] = '摘要'
# post_data['cover_picture'] = 'statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_1.png'
# content =  {
# 	'cover_data': [{
# 		'type': 'picture_url',
# 		'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_1.png', 'statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_2.png']
# 	}],
# 	'article_data': [{
# 			'type': 'title',
# 			'data': ['xx我是标题1']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_1.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_2.png']
# 		},
# 		{
# 			'type': 'title',
# 			'data': ['我是标题2']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_3.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容3']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_4.png']
# 		}
# 	]
# }
# post_data['content'] = json.dumps(content)
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip +  '/zhugeleida/admin/article/delete/3'   # 删除文章
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip + '/zhugeleida/admin/article/update/9' # 添加产品
# post_data['title'] = 'xxxxx'
# post_data['summary'] = 'sss摘要'
# post_data['cover_picture'] = 'statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_1.png'
# content =  {
# 	'cover_data': [{
# 		'type': 'picture_url',
# 		'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_1.png', 'statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_2.png']
# 	}],
# 	'article_data': [{
# 			'type': 'title',
# 			'data': ['xx我是标题1']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_1.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_2.png']
# 		},
# 		{
# 			'type': 'title',
# 			'data': ['我是标题2']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_3.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容3']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_4.png']
# 		}
# 	]
# }
# post_data['content'] = json.dumps(content)
# ret = requests.post(url, data=post_data,params=get_data)


###################################### 插件 名片 #######################################

# url = ip + '/zhugeleida/admin/plugin_mingpian' # 添加产品
# ret = requests.get(url,params=get_data)



# url = ip + '/zhugeleida/admin/plugin_mingpian/add/0' # 添加
# post_data['name'] = 'hahhhha'
# post_data['avatar'] = 'xxxxxx'
# post_data['username'] = 'jjsfjadjfka'
# post_data['phone'] = 121231323
# post_data['webchat_code'] = 'fsafsaww23'
# post_data['position'] = '运维'
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip + '/zhugeleida/admin/plugin_mingpian/update/1' # 添加产品
# post_data['name'] = '回家哈哈哈'
# post_data['avatar'] = '232323'
# post_data['username'] = '方法的'
# post_data['phone'] = 6767676
# post_data['webchat_code'] = 'fsafsaww23'
# post_data['position'] = '运维x'
# ret = requests.post(url, data=post_data,params=get_data)


# url = ip + '/zhugeleida/admin/plugin_mingpian/delete/1' # 添加产品
# ret = requests.post(url, params=get_data)


#############################  插件- 名片管理 活动报名 商品管理   ################################

# url = ip + '/zhugeleida/admin/plugin_report/plugin_list' # 添加产品
# ret = requests.get(url,params=get_data)

# url = ip + '/zhugeleida/admin/plugin_report/report_customer' # 添加产品
# # get_data['activity_id'] = 2
# ret = requests.get(url,params=get_data)
#
# '/zhugeleida/admin/article/contextDiagram/3'

# url = ip + '/zhugeleida/admin/article/contextDiagram/3' # 添加产品
# # get_data['activity_id'] = 2
# ret = requests.get(url,params=get_data)



# url = ip + '/zhugeleida/admin/plugin_report/add/0' # 添加活动
# post_data['ad_slogan'] = '你值得拥有'   #广告语
# post_data['sign_up_button'] = '对方发送的发生'   #报名按钮
# post_data['title'] = '范德萨发生'    #活动标题
# post_data['introduce'] = 'dsfasfas的发生的发生'   #活动说明
# post_data['is_get_phone_code'] = False    #是否获取手机验证码
# post_data['skip_link'] = 'xxxxx'  #跳转链接
# ret = requests.post(url, data=post_data,params=get_data)

# url = ip + '/zhugeleida/admin/plugin_report/update/1' # 修改活动
# post_data['ad_slogan'] = '范德萨发生'
# post_data['sign_up_button'] = '是是是'
# post_data['title'] = '范德萨发生'
# post_data['introduce'] = 'SOUI金丰鼓酒行'
# post_data['is_get_phone_code'] = True
# post_data['skip_link'] = 'TTTT'
# ret = requests.post(url, data=post_data,params=get_data)

# url = ip + '/zhugeleida/admin/plugin_report/delete/4' # 修改活动
# ret = requests.post(url, params=get_data)

# url = ip + '/zhugeleida/admin/plugin_report/sign_up_activity/1' # 修改活动
# post_data['customer_name'] = 'FFFFF'
# post_data['phone'] =  1234425212
# post_data['phone_verify_code'] = 1231
# post_data['leave_message'] = 'e'
# ret = requests.post(url, data=post_data,params=get_data)

#############################  插件- 名片管理 活动报名 商品管理   ################################

# url = ip + '/zhugeleida/admin/plugin_goods/plugin_goods_list' # 添加产品
# ret = requests.get(url,params=get_data)




# content =  {
#     'goods_data':[
#
# 		{
#             'price': 128,
# 			'introduce': '本场演出将于【7月26日 10:55】开启销售，请提前下载大麦APP，关注本场演出最新信息。',
# 			'inventory_num' : 10,
# 			'person_limit_num' : 2,
#
#         },
# 		{
#             'price': 500,
# 			'introduce': '本场演出将于【7月28日 10:55】开启销售，请提前下载大麦APP，关注本场演出最新信息。',
# 			'inventory_num' : 10,
# 			'person_limit_num' : 2,
#
#         }
#     ],
#     'cover_data':[
#         {
#             'data':[
#                 'statics/zhugeleida/imgs/qiyeweixin/product/pbmh_s1.png'
#             ],
#             'type':'picture_url'
#         },
#         {
#             'type':'picture_url',
#             'data':[
#                 'statics/zhugeleida/imgs/qiyeweixin/product/1532484232056.png'
#             ]
#         }
#     ]
# }



# url = ip + '/zhugeleida/admin/plugin_goods/add/0' # 添加活动
# post_data['title'] = '林俊杰门票'
# post_data['content'] = json.dumps(content)
# ret = requests.post(url, data=post_data,params=get_data)

# url = ip + '/zhugeleida/admin/plugin_goods/update/1' # 添加活动
# post_data['title'] = '林俊杰门票1'
# post_data['content'] = json.dumps(content)
# ret = requests.post(url, data=post_data,params=get_data)

# url = ip + '/zhugeleida/admin/plugin_goods/delete/5' # 修改活动
# ret = requests.post(url, params=get_data)



############################ 官网编辑 #################################

# url = ip + '/zhugeleida/admin/website/edit/1' # 编辑官网
# website_content =  {
# 	'cover_data': [{
# 		'type': 'picture_url',
# 		'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_1.png', 'statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_2.png']
# 	}],
# 	'article_data': [{
# 			'type': 'title',
# 			'data': ['xx我是标题1']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_1.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_2.png']
# 		},
# 		{
# 			'type': 'title',
# 			'data': ['我是标题2']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_3.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容3']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_4.png']
# 		}
# 	]
# }
# post_data['website_content'] = json.dumps(website_content)
# ret = requests.post(url, data=post_data,params=get_data)



# url = ip + '/zhugeleida/admin/website' # 编辑官网
# get_data['company_id'] = 1
# ret = requests.get(url, params=get_data)



#######################################################################################

# url = ip + '/zhugeleida/admin/website/edit/1' # 编辑官网
# website_content =  {
# 	'cover_data': [{
# 		'type': 'picture_url',
# 		'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_1.png', 'statics/zhugeleida/imgs/xiaochengxu/website/Website_scroll_2.png']
# 	}],
# 	'article_data': [{
# 			'type': 'title',
# 			'data': ['xx我是标题1']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_1.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_2.png']
# 		},
# 		{
# 			'type': 'title',
# 			'data': ['我是标题2']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容1']
# 		},
#
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_3.png']
# 		},
# 		{
# 			'type': 'content',
# 			'data': ['我是内容3']
# 		},
# 		{
# 			'type': 'picture_url',
# 			'data': ['statics/zhugeleida/imgs/xiaochengxu/website/Content_4.png']
# 		}
# 	]
# }
# post_data['website_content'] = json.dumps(website_content)
# ret = requests.post(url, data=post_data,params=get_data)



# url = ip + '/zhugeleida/admin/website' # 编辑官网
# get_data['company_id'] = 1
# ret = requests.get(url, params=get_data)



# url = ip + '/zhugeleida/admin/website_template'      # 编辑官网
# ret = requests.get(url, params=get_data)

# url = ip + '/zhugeleida/admin/website_template/add/0'      # 编辑官网
# post_data['name'] = '模板1'
# post_data['template_content'] = 'xxxx'
# ret = requests.post(url, params=get_data,data=post_data)


# url = ip + '/zhugeleida/admin/website_template/update/1'      # 编辑官网
# post_data['id'] = 1
# post_data['name'] = '模板1'
# post_data['template_content'] = 'TTTT'
# ret = requests.post(url, params=get_data,data=post_data)

# url = ip + '/zhugeleida/admin/website_template/delete/1'      # 编辑官网
# ret = requests.post(url, params=get_data,data=post_data)







###########################################################################################
















# url = ip + '/zhugeleida/admin/department/add/0' # 分页获取消息列表
# post_data['name'] = '测试环境AAA'
#
# post_data['parentid'] = ''
# post_data['company_id'] = 1
# ret = requests.post(url, params=get_data, data=post_data)

# url = 'http://127.0.0.1:8000/zhugeleida/admin/department/update/8'   # 分页获取消息列表
# post_data['name'] = '八大胡同_A'
# post_data['parentid'] = ''
#
# post_data['company_id'] = 1
# ret = requests.post(url, params=get_data, data=post_data)
#



# url = 'http://127.0.0.1:8000/zhugeleida/admin/department/add/0'    # 分页获取消息列表
# post_data['name'] = '蓝翔技院-2'
# post_data['parentid'] = 1
# post_data['company_id'] = 1
# ret = requests.post(url, params=get_data, data=post_data)


# url = 'http://127.0.0.1:8000/zhugeleida/admin/department/delete/6' # 分页获取消息列表
# ret = requests.post(url, params=get_data,)


# url = 'http://192.168.100.20:8000/zhugeleida/qiyeweixin/tongxunlu'  # 查询-通讯录信息
# # url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/tongxunlu'  # 查询-通讯录信息
# # get_data['customer__source'] =1
#
# ret = requests.get(url, params=get_data)


# url = ip + '/zhugeleida/qiyeweixin/follow_language'  # 查询-跟进用语
# ret = requests.get(url, params=get_data)


# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/follow_language/add/0'  # 新增-跟进用语
# post_data['custom_language'] = '这个客户可能是个Gay'
# ret = requests.post(url, params=get_data,data=post_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/follow_language/delete/12'  # 删除-跟进用语
# ret = requests.post(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/follow_info/add/1'  # 发送-跟进信息。
# post_data['follow_info'] = '这个客户我惹不起！！！！'
# ret = requests.post(url, params=get_data,data=post_data)

# url = ip + '/zhugeleida/qiyeweixin/follow_info'  # 查询-跟进用语
# get_data['customer_id']  = 1
# ret = requests.get(url, params=get_data)



# url = 'http://127.0.0.1:8000/zhugeleida/xiaochengxu/product/product_single'  # 获取产品的列表
# get_data['product_id'] = 22
# get_data['uid'] = 1
# ret = requests.get(url, params=get_data)



# url = 'http://127.0.0.1:8000/zhugeleida/xiaochengxu/product/product_list'  # 获取产品的列表
#
# get_data['uid'] =1
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/xiaochengxu/product/forward_product'  # 记录转发产品动作。
# get_data['product_id'] = 22
# get_data['uid'] = 1
# ret = requests.get(url, params=get_data)

# url = 'http://127.0.0.1:8000/zhugeleida/xiaochengxu/product/forward_product'  # 记录转发产品动作。
# get_data['product_id'] = 22
# get_data['uid'] = 1
# ret = requests.get(url, params=get_data)


# url = 'http://127.0.0.1:8000/zhugeleida/qiyeweixin/product/product_list'  # 获取产品的列表
# get_data['status'] =1
#ret = requests.get(url, params=get_data)


print(ret.text)












