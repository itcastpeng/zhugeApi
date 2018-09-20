

from zhugeleida.public.WXBizDataCrypt import WXBizDataCrypt
def main():
    appId = 'wx1add8692a23b5976'
    sessionKey = 'Imct7Zw6LXsHJiaYyCNS8A=='
    encryptedData ='W0DDjkpimrhw9QKOv3Aa0tUqRRduqjKFkINFirobCl8z/xNDJRtjB/o02VGC49Xw50RuJQc1zvryjK3We/roaLmIJQtTZKU7K6BAZ8PIZaANPex1NnhGhG/crYXUGYwGZR5l6hyFToRwfohO/HebQtxa4jSvnQb424GbFcnR+INLu+FTeyh7jPgF9X86Wo4c0LRdssAEiL+kufRoNv3IAg=='
    iv = 'YnEZyhwp4wHN7iVU8yZbFQ=='

    pc = WXBizDataCrypt(appId, sessionKey)

if __name__ == '__main__':
    main()
