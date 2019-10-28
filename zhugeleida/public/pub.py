
from bs4 import BeautifulSoup
from urllib.parse import unquote
from zhugeleida import models
import re, os, requests, time, json, base64, datetime
from urllib.parse import quote






def deal_gzh_picture_url(leixing, article_url):
    # print('---------------------@!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@_-----------------------> ', datetime.datetime.today())
    '''
    ata-src 替换为src，将微信尾部?wx_fmt=jpeg去除
    http://mmbiz.qpic.cn/mmbiz_jpg/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7lBRILWoKKVuvdHe4BmVxhiclQnYo2F1TDU7CcibXawl9E2n1MOicTkt6w/0?wx_fmt=jpeg

    '''
    # content = 'data-src="111?wx_fmt=png data-src="222?wx_fmt=jpg'
    # phone = "2004-959-559#这是一个电话号码"
    # # 删除注释
    # num = re.sub(r'#.*$', "", phone)
    # print("电话号码 : ", num)

    # 移除非数字的内容
    # url = 'https://mp.weixin.qq.com/s?__biz=MzA5NzQxODgzNw==&mid=502884331&idx=1&sn=863da48ef5bd01f5ba8ac30d45fea912&chksm=08acecd13fdb65c72e407f973c4db69a988a93a169234d2c4a95c0ca6c97054adff54c48a24f#rd'
    print('---------------请求微信链接------------> ', datetime.datetime.today())
    ret = requests.get(article_url)
    print('---------------结束请求微信链接------------> ', datetime.datetime.today())

    ret.encoding = 'utf8'

    soup = BeautifulSoup(ret.text, 'lxml')

    msg_title = ''
    msg_desc = ''
    cover_url = ''
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    is_video_original_link = None  # 是否有视频 如果有则返回原文链接
    if leixing == 'only_url':
        ### 匹配出标题 描述 和 封面URL
        results_url_list_1 = re.compile(r'var msg_title = (.*);').findall(ret.text)   # 标题
        results_url_list_2 = re.compile(r'var msg_desc = (.*);').findall(ret.text)    # 封面摘要
        results_url_list_3 = re.compile(r'var msg_cdn_url = (.*);').findall(ret.text) # 封面图片

        msg_title = results_url_list_1[0].replace('"', '')
        msg_desc = results_url_list_2[0].replace('"', '')
        cover_url = results_url_list_3[0].replace('"', '')

        ## 把封面图片下载到本地
        now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')
        print('------------请求1=================> ', datetime.datetime.today())
        html = s.get(cover_url)
        print('------------请求1=================> ', datetime.datetime.today())
        if 'wx_fmt=gif' in cover_url:
            filename = "/gzh_article_%s.gif" % (now_time)
        else:
            filename = "/gzh_article_%s.jpg" % (now_time)

        file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'article') + filename
        with open(file_dir, 'wb') as file:
            file.write(html.content)
        # print('-----【正则处理个别】公众号 生成本地文章URL file_dir ---->>', file_dir)
        #######
        cover_url = file_dir # 封面图片

    style_tags = soup.find_all('style')

    style = ""
    for style_tag in style_tags:
        # print('style_tag -->', style_tag)
        style += str(style_tag)

    body = soup.find('div', id="js_content")

    body.attrs['style'] = "padding: 20px 16px 12px;"

    img_tags = soup.find_all('img')
    for img_tag in img_tags:
        if img_tag.attrs.get('style'):
            style_list = img_tag.attrs.get('style').split(';')
            style_tag = ''
            for i in style_list:
                if i and i.split(':')[0] == 'width':
                    style_tag = i.split(':')[1]

            img_tag.attrs['style'] = style_tag

        data_src = img_tag.attrs.get('data-src')
        if data_src:

            #######
            now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')
            html = s.get(data_src)

            if 'wx_fmt=gif' in data_src:
                filename = "/gzh_article_%s.gif" % (now_time)
            else:

                filename = "/gzh_article_%s.jpg" % (now_time)

            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'article') + filename
            with open(file_dir, 'wb') as file:
                file.write(html.content)
            # print('-----公众号 生成 本地文章URL file_dir ---->>', file_dir)
            #######

            img_tag.attrs['data-src'] = 'http://statics.api.zhugeyingxiao.com/' + file_dir
            # print('data_src ----->', data_src)
    flag = False
    ### 处理视频的URL
    iframe = body.find_all('iframe', attrs={'class': 'video_iframe'})
    for iframe_tag in iframe:
        data_src = iframe_tag.get('data-cover')
        shipin_url = iframe_tag.get('data-src')
        if data_src:
            data_src = unquote(data_src, 'utf-8')

            now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')
            html = s.get(data_src)
            if 'wx_fmt=gif' in data_src:
                filename = "/gzh_article_img_%s.gif" % (now_time)
            else:

                filename = "/gzh_article_img_%s.jpg" % (now_time)

            file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'article') + filename
            with open(file_dir, 'wb') as file:
                file.write(html.content)
            data_src = 'http://api.zhugeyingxiao.com/' + file_dir # 封面地址


        vid = shipin_url.split('vid=')[1]

        if 'wxv' in vid:  # 下载
            flag = True
            iframe_url = 'https://mp.weixin.qq.com/mp/videoplayer?vid={}&action=get_mp_video_play_url'.format(vid)
            ret = requests.get(iframe_url)
            src_url = ret.json().get('url_info')[0].get('url')

            iframe_tag_new = """<div style="width: 100%; background: #000; position:relative; height: 0; padding-bottom:75%;">
                                   <video style="width: 100%; height: 100%; position:absolute;left:0;top:0;" id="videoBox" src="{}" poster="{}" controls="controls"></video>
                               </div>""".format(src_url, data_src)

        else:
            if '&' in shipin_url and 'vid=' in shipin_url:
                _url = shipin_url.split('?')[0]
                shipin_url = _url + '?vid=' + vid
            if vid:
                shipin_url = 'https://v.qq.com/txp/iframe/player.html?origin=https%3A%2F%2Fmp.weixin.qq.com&vid={}&autoplay=false&full=true&show1080p=false&isDebugIframe=false'.format(vid)
            iframe_tag.attrs['data-src'] = shipin_url
            iframe_tag.attrs['allowfullscreen'] = True
            iframe_tag.attrs['data-cover'] = data_src

            iframe_tag_new = str(iframe_tag).replace('></iframe>', ' width="100%" height="300px"></iframe>')

        body = str(body).replace(str(iframe_tag), iframe_tag_new)
        body = BeautifulSoup(body, 'html.parser')
    content = str(style) + str(body)

    dict = {'url': '', 'data-src': 'src', '?wx_fmt=jpg': '', '?wx_fmt=png': '', '?wx_fmt=jpeg': '',
            '?wx_fmt=gif': '', }  # wx_fmt=gif
    for key, value in dict.items():

        if key == 'url':

            pattern1 = re.compile(r'https:\/\/mmbiz.qpic.cn\/\w+\/\w+\/\w+\?\w+=\w+', re.I)  # 通过 re.compile 获得一个正则表达式对象
            pattern2 = re.compile(r'https:\/\/mmbiz.qpic.cn\/\w+\/\w+\/\w+', re.I)
            results_url_list_1 = pattern1.findall(content)
            results_url_list_2 = pattern2.findall(content)
            # print(' 匹配的微信图片链接 results_url_list_1 ---->', json.dumps(results_url_list_1))
            # print(' 匹配的微信图片链接 results_url_list_2 ---->', json.dumps(results_url_list_2))
            results_url_list_1.extend(results_url_list_2)
            # print('合并的 results_url_list ----->>',results_url_list_1)

            for pattern_url in results_url_list_1:
                # print('匹配的url--------<<', pattern_url)
                now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')
                ## 把图片下载到本地
                html = s.get(pattern_url)
                if 'wx_fmt=gif' in pattern_url:
                    filename = "/gzh_article_%s.gif" % (now_time)
                else:
                    filename = "/gzh_article_%s.jpg" % (now_time)

                file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'article') + filename
                with open(file_dir, 'wb') as file:
                    file.write(html.content)
                # print('-----【正则处理个别】公众号 生成本地文章URL file_dir ---->>', file_dir)
                #######
                sub_url = 'http://statics.api.zhugeyingxiao.com/' + file_dir
                content = content.replace(pattern_url, sub_url)

        else:
            content = content.replace(key, value)
        # print(url)

    if flag:
        is_video_original_link = article_url

    if leixing == 'only_url':

        return msg_title, msg_desc, cover_url, content, is_video_original_link

    else:

        return content



# 创建 分享 转播视频链接
def pub_create_link_repost_video(user_id, video_id, company_id, pid):

    gongzhonghao_app_obj = models.zgld_gongzhonghao_app.objects.get(company_id=company_id)
    authorization_appid = gongzhonghao_app_obj.authorization_appid
    three_service_objs = models.zgld_three_service_setting.objects.filter(three_services_type=2)  # 公众号
    qywx_config_dict = ''
    if three_service_objs:
        three_service_obj = three_service_objs[0]
        if three_service_obj.config:
            qywx_config_dict = json.loads(three_service_obj.config)

    api_url = qywx_config_dict.get('api_url')
    component_appid = qywx_config_dict.get('app_id')
    leida_http_url = qywx_config_dict.get('authorization_url')

    # （弹出授权页面，可通过openid拿到昵称、性别、所在地。并且， 即使在未关注的情况下，只要用户授权，也能获取其信息 ）
    scope = 'snsapi_userinfo'  # snsapi_base
    state = ''      # 自定义参数
    redirect_uri = '{}/zhugeleida/gongzhonghao/forwarding_video_jump_address?relate={}'.format(
        api_url,
        str(company_id) + '_' + str(video_id) + '_' + str(user_id) + '_' + str(pid)
    )

    share_url = """https://open.weixin.qq.com/connect/oauth2/authorize?appid={}&redirect_uri={}&response_type=code&scope={}&state={}&component_appid={}#wechat_redirect
                   """.format(
        authorization_appid,
        redirect_uri,
        scope,
        state,
        component_appid
    )
    print('share_url============> ', share_url)
    bianma_share_url = quote(share_url, 'utf-8')
    share_url = '%s/zhugeleida/gongzhonghao/work_gongzhonghao_auth/redirect_share_url?share_url=%s' % (
        leida_http_url, bianma_share_url)
    print('share_url--------share_url----------share_url-----------share_url---------share_url--------> ', share_url)
    return share_url


# 验证手机号
def verify_phone_number(phone_number):
    phone_pat = re.compile('^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$')
    res = re.search(phone_pat, phone_number)
    flag = False
    if res:
        flag = True
    return flag


#
def get_min_s(seconds):
    date_time = datetime.timedelta(seconds=seconds)

    day = date_time.days
    hour, date_time = divmod(date_time.seconds, 3600)
    min, date_time = divmod(date_time, 60)
    second = date_time
    days = ''
    hours = ''
    mins = ''
    seconds = ''
    if day:
        days = str(day) + '天'
    if hour:
        hours = str(hour) + '小时'
    if min:
        mins = str(min) + '分钟'
        if second:
            mins = str(min) + '分'
    if second:
        seconds = str(second) + '秒'

    return days + hours + mins + seconds
