

import sys
from zhugeleida.public.crypto_.WXBizMsgCrypt_qiyeweixin import WXBizMsgCrypt
# from  zhugeleida.views_dir.admin import WXBizMsgCrypt

import xml.etree.cElementTree as ET

sToken = "5lokfwWTqHXnb58VCV"
sEncodingAESKey = "ee2taRqANMUsH7JIhlSWIj4oeGAJG08qLCAXNf6HCxt"
sCorpID = "ww24123520340ba230"
decrypt_obj = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)

msg_signature = "f2919de2c73e792c3b778a173f7c5f55df92ced1"
timestamp = "1539253005"
nonce = "1539040416"

sReqData = '<xml><ToUserName><![CDATA[ww24123520340ba230]]></ToUserName><Encrypt><![CDATA[WBLfE7Kkn0faeJ0asgyiUvdAquGyXA35YDigDgO9BgvH9kBbjDdJ8/E267kBgFVgw3Vuxn+iioHYUM/kOTZAO1ROO1EEGa7qw8bRJ+xAYGVnOa4xSW1XMiC25zOi0dY+KPW7OFJk/KbIYNSZ0zt8MPvkNqCW5ZBQ5mTKS5rcJZFsZpAN5cZIhpCdUs7mDuQgTqDiQqIt+654XWxB9qsfO/pGfdwHXvQnT5heNvVzSyw8klDXmZaqV9jJ5XD7YLpM+f4toBffnB232bWdrh8+LYYn+oxbMm9KcY1fwe98u6wYDvz+0yqCNwpBoctRAGBx+5nDMI2HFJufwSEDZbt6wOJBuS0RxjNFzKsDAxzHxpCQBSimcuZykPfE2YBvYOEL]]></Encrypt><AgentID><![CDATA[1000007]]></AgentID></xml>'


ret,sMsg = decrypt_obj.DecryptMsg(sReqData, msg_signature, timestamp, nonce)
print (ret, sMsg)
if (ret != 0):
    print ("ERR: DecryptMsg ret: " + str(ret))
    sys.exit(1)

# 解密成功，sMsg即为xml格式的明文
xml_tree = ET.fromstring(sMsg)
# SuiteTicket = xml_tree.find("SuiteTicket").text
SuiteId = xml_tree.find("SuiteId").text
print ('---',SuiteId)