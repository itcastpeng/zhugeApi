import base64
import json
from Crypto.Cipher import AES

class WXBizDataCrypt:
    def __init__(self, appId, sessionKey):
        self.appId = appId
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        # base64 decode
        print('------- self._unpad(cipher.decrypt(encryptedData)) ------->>', encryptedData, '|')

        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)

        iv = base64.b64decode(iv)

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)

        decrypted = json.loads(self._unpad(cipher.decrypt(encryptedData)).decode('utf-8'))

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        print('---- decrypted | cipher ---->>',decrypted,'|',cipher)

        return decrypted


    def _unpad(self, s):
        print('------- s[:-ord(s[len(s)-1:])] --------->>',s[:-ord(s[len(s)-1:])])
        return s[:-ord(s[len(s)-1:])]
