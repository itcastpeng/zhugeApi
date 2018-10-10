

import sys
from zhugeleida.public.crypto_.WXBizMsgCrypt_qiyeweixin import WXBizMsgCrypt
# from  zhugeleida.views_dir.admin import WXBizMsgCrypt

import xml.etree.cElementTree as ET

sToken = "5lokfwWTqHXnb58VCV"
sEncodingAESKey = "ee2taRqANMUsH7JIhlSWIj4oeGAJG08qLCAXNf6HCxt"
sCorpID = "wx5d26a7a856b22bec"
decrypt_obj = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)

msg_signature = "2b29a5534ed8b50981ae0069c1f4c48127789cec"
timestamp = "1538228121"
nonce = "1537294388"
sReqData = '<xml><ToUserName><![CDATA[wx5d26a7a856b22bec]]></ToUserName><Encrypt><![CDATA[uh2c6Yqs5f8nPcXQmTtxifpYEIX0Y5FV/nrsbAo4FGKdCPCLVA1p7XSDnC6XN5/1YiFE4ywFs2CvT0n1xHbJ4vSksICKqkPr0z9PtxhJDcbuhz7wgsUSLmEMeXWR1f6YVaOGkFKqa6YJ0lalvpGcS03RRwTuqb49VccfuV5KO4y3eabi6qQRh5QG6SHYKGPZmTfD32Q5GGgGhm4QH3ne/hUTLtMdk3CONblGcodRs5/iAArxfGCFxYADT9d/9Q6ZoNoLruYD66RPrX8AghjKE6KoCqNomsgLHbINJEBxkyEaTBd9qqJe+zoXJMXhyFJ6CsmfKRITwC/Lz32wZF0bF44fzhybguIyMOohxZEhyl1pJpwpgX5DjpjKs47jKf76]]></Encrypt><AgentID><![CDATA[]]></AgentID></xml>'


ret,sMsg = decrypt_obj.DecryptMsg(sReqData, msg_signature, timestamp, nonce)
print (ret, sMsg)
if (ret != 0):
    print ("ERR: DecryptMsg ret: " + str(ret))
    sys.exit(1)

# 解密成功，sMsg即为xml格式的明文
xml_tree = ET.fromstring(sMsg)
SuiteTicket = xml_tree.find("SuiteTicket").text
SuiteId = xml_tree.find("SuiteId").text
print ('---',SuiteId)