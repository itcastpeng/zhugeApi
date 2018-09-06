from urllib.parse import unquote



share_url = 'share_url=https%3A%2F%2F%2Fopen.weixin.qq.com%2Fc%2Fconnect%2Foauth2%2Fauthorize%3Fappid%3Dwxa77213c591897a13%26redirect_uri%3Dhttp%3A%2F%2F%2Fapi.zhugeyingxiao.com%2Fz%2Fzhugeleida%2Fgongzhonghao%2Fwork_gongzhonghao_auth%3Frelate%3Darticle_id_1%7Cpid_854%7Clevel_2%7Cuid_55%7Ccompany_id_1%26response_type%3Dcode%26scope%3Dsnsapi_base%26state%3Dsnsapi_base%26component_appid%3Dwx6ba07e6ddcdc69b3%23wechat_redirect]'

redirect_url = unquote(share_url, 'utf-8')

print(redirect_url)
