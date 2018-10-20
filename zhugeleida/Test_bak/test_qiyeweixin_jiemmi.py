

import sys
from zhugeleida.public.crypto_.WXBizMsgCrypt_qiyeweixin import WXBizMsgCrypt
# from  zhugeleida.views_dir.admin import WXBizMsgCrypt

import xml.etree.cElementTree as ET

# sToken = "5lokfwWTqHXnb58VCV"
# sEncodingAESKey = "ee2taRqANMUsH7JIhlSWIj4oeGAJG08qLCAXNf6HCxt"
# sCorpID = "ww24123520340ba230"
# decrypt_obj = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)
#
# msg_signature = "f2919de2c73e792c3b778a173f7c5f55df92ced1"
# timestamp = "1539253005"
# nonce = "1539040416"
#
# sReqData = '<xml><ToUserName><![CDATA[ww24123520340ba230]]></ToUserName><Encrypt><![CDATA[WBLfE7Kkn0faeJ0asgyiUvdAquGyXA35YDigDgO9BgvH9kBbjDdJ8/E267kBgFVgw3Vuxn+iioHYUM/kOTZAO1ROO1EEGa7qw8bRJ+xAYGVnOa4xSW1XMiC25zOi0dY+KPW7OFJk/KbIYNSZ0zt8MPvkNqCW5ZBQ5mTKS5rcJZFsZpAN5cZIhpCdUs7mDuQgTqDiQqIt+654XWxB9qsfO/pGfdwHXvQnT5heNvVzSyw8klDXmZaqV9jJ5XD7YLpM+f4toBffnB232bWdrh8+LYYn+oxbMm9KcY1fwe98u6wYDvz+0yqCNwpBoctRAGBx+5nDMI2HFJufwSEDZbt6wOJBuS0RxjNFzKsDAxzHxpCQBSimcuZykPfE2YBvYOEL]]></Encrypt><AgentID><![CDATA[1000007]]></AgentID></xml>'
#
#
# ret,sMsg = decrypt_obj.DecryptMsg(sReqData, msg_signature, timestamp, nonce)
# print (ret, sMsg)
# if (ret != 0):
#     print ("ERR: DecryptMsg ret: " + str(ret))
#     sys.exit(1)
#
# # 解密成功，sMsg即为xml格式的明文
# xml_tree = ET.fromstring(sMsg)
# # SuiteTicket = xml_tree.find("SuiteTicket").text
# SuiteId = xml_tree.find("SuiteId").text
# print ('---',SuiteId)




######### 公众号事件解密 #################

sMsg ='<xml><ToUserName><![CDATA[gh_21c48bcaa193]]></ToUserName><Encrypt><![CDATA[UYT10UW9rJEWMtGCbMWdHXaTCdMggtLWAVh6dmM+keV74xjJ3MpDeaf5fE9pRHqN3djG1oTYEiQU2O0HUf996o8hu0WTMiytOunj2Tyg7uw2OWKNaFgk9bqIKGHbTUOilp00SfDRCTSQUsFJwzLRStwaj+7CM/i/j9sdwoeZsB0iz4sh3dVNjXwkmIB5Hmi9F7tnzSHziOr/Nfg9ISXNgif1Zly/aoRlwaEakcS12vU9nyIh3l/8lQZWFgo+jvH+Jx5P6qAv52noX3YCnCyb1gMj8A80umDGWCTko1kf0OoG5o5Y6zF6k/R6Uwxqr1YOJSdcs6twxgdOvxqO2CuP/h6ZePJ67/sFRpcXP+1u3JvDhqZkjGaN28e7W/KLlDOhkR85ukv3cF4ecsBuU3uhBF7Pia3NMPZTbpaqDs4uGmM=]]></Encrypt>\x0A</xml>'

# sMsg = '''
# <catalog>
#     < maxid>4< /maxid>
#     <login username="pytest" passwd='123456'>dasdas
#         <caption>Python</caption>
#         <item id="4">
#             <caption>测试</caption>
#         </item>
#     </login>
#     <item id="2">
#         <caption>Zope</caption>
#     </item>
# </catalog>
# '''

import hashlib, random, xml.dom.minidom as xmldom
from zhugeleida.public.crypto_.WXBizMsgCrypt import WXBizMsgCrypt
token = 'R8Iqi0yMamrgO5BYwsODpgSYjsbseoXg'
encodingAESKey = 'iBCKEEYaVCsY5bSkksxiV5hZtBrFNPTQ2e3efsDC143'
appid = 'wx6ba07e6ddcdc69b3'

xml_tree = ET.fromstring(sMsg)
# print(xml_tree)

msg_signature = "c1a43c5bdb77386d5ed72e341150891f5e913f03"
timestamp = "1539827462"
nonce = "1250886219"
encrypt = xml_tree.find("Encrypt").text

decrypt_obj = WXBizMsgCrypt(token, encodingAESKey, appid)
# ret, decryp_xml = decrypt_obj.DecryptMsg(encrypt, msg_signature, timestamp, nonce)

# print('--->>',decryp_xml)

# decryp_xml_tree = ET.fromstring(decryp_xml)
#
# print(xml_tree.find("FromUserName"))
# print(xml_tree.find("Event"))

# print(decryp_xml)
# DOMTree = xmldom.parseString(decryp_xml)
# collection = DOMTree.documentElement
# original_id = collection.getElementsByTagName("ToUserName")[0].childNodes[0].data
# openid = collection.getElementsByTagName("FromUserName")[0].childNodes[0].data
# Event = collection.getElementsByTagName("Event")[0].childNodes[0].data
# print('--original_id-->>',original_id)
# print('--Event-->>',Event)
# print('--openid-->>',openid)

# import time
# createtime = int(time.time())
# openid = 'ob5mL1Q4faFlL2Hv2S43XYKbNO-k'
# original_id = 'gh_21c48bcaa193'
#
# content = '手动阀大'
# _nonce = '1152221748'
# res_msg = '<xml><ToUserName><![CDATA[{openid}]]></ToUserName><FromUserName><![CDATA[{original_id}]]></FromUserName><CreateTime>{createtime}</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[{content}]]></Content></xml>'.format(
#     openid=openid, original_id=original_id, createtime=createtime, content=content.encode('utf-8'))
#
# # print('----- 【加密前】的 消息---->>', res_msg)
#
# ret, encrypt_xml = decrypt_obj.EncryptMsg(res_msg, _nonce)
# print('-----ret, encrypt_xml----->>', ret, encrypt_xml)
# print('-------【加密后】的 消息---->>', encrypt_xml)
# ComponentVerifyTicket = decryp_xml_tree.find("ComponentVerifyTicket").text

# print('----ret -->', ret)
# print('-----decryp_xml -->', decryp_xml)


# print(xml_tree.find("Encrypt").text)