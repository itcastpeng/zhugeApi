
data = [
    {'id': 18, 'order': 7, 'picture_url': 'statics/zhugeleida/imgs/qiyeweixin/product/20180624205207853123.jpg'},
    {'id': 17, 'order': 5, 'picture_url': 'statics/zhugeleida/imgs/qiyeweixin/product/20180624205207853482.jpg'},
    {'id': 1, 'order': 1, 'content': None,          'title': '我是标题党-1'},
    {'id': 2, 'order': 3, 'content': '我是内容派-1',  'title': ''},
    {'id': 3, 'order': 4, 'content': None,          'title': '我是标题党-2'},
    {'id': 4, 'order': 6, 'content': '我是内容派-2',  'title': None},

    {'id': 16, 'order': 2, 'picture_url': 'statics/zhugeleida/imgs/qiyeweixin/product/20180624205207853481.jpg'},


   ]


ret_list = []
for obj in data:
    if not ret_list:
        # tmp_dict[obj['order']] = obj
        ret_list.append(obj)

    else:
        for index,data  in  enumerate(ret_list):
            if  obj['order'] < data['order']:
                ret_list.insert(index,obj)
                break
        else:
            ret_list.append(obj)

import json
print(json.dumps(ret_list))










