
ret_data = [
    { "id": 15,"name": "大傻子客户","tag_id": 15, "customer_num": 6, "customer_id_list": [ 2,4 ]},
    {"id": 14, "name": "爱吃串", "tag_id": 14, "customer_num": 2, "customer_id_list": [ 1, 2 ] },
    {"id": 11, "name": "90后","tag_id": 11,"customer_num": 4, "customer_id_list": [ 1, 2,3, 4]},
    {"id": 10, "name": "爱撸串","tag_id": 10,"customer_num": 4, "customer_id_list": [ 1, 2,3, 4]},
    { "id": 9,"name": "在意 服务", "tag_id": 9, "customer_num": 1, "customer_id_list": [ 3]},
    { "id": 8,"name": "已婚", "tag_id": 8,"customer_num": 4,"customer_id_list": [1, 2,3, 4]},
    { "id": 7,"name": "在意质量", "tag_id": 7,"customer_num": 3,"customer_id_list": [ 1,2, 4] },
    { "id": 6,"name": "重要客户", "tag_id": 6, "customer_num": 1, "customer_id_list": [ 1 ]},
    # { "id": 5,"name": "一般客户", "tag_id": 5, "customer_id_list": [1]}
]

import json
objs = json.dumps(ret_data)

def insert_sort(objs):
    for i in  range(1,len(objs)):
        if  objs[i]['customer_num']  >  objs[i-1]['customer_num']:
            temp = objs[i]['customer_num']
            temp_tag_id = objs[i]['tag_id']
            name = objs[i]['name']
            id = objs[i]['id']
            customer_id_list =  objs[i]['customer_id_list']

            for j in range(i-1,-1,-1):
                if objs[j]['customer_num'] < temp:
                    objs[j + 1]['customer_num'] = objs[j]['customer_num']
                    objs[j + 1]['tag_id'] = objs[j]['tag_id']
                    objs[j + 1]['name'] = objs[j]['name']
                    objs[j + 1]['id'] = objs[j]['id']
                    objs[j + 1]['customer_id_list'] = objs[j]['customer_id_list']

                    index = j  # 记下应该插入的位置
                else:
                    break
                objs[index]['customer_num'] = temp
                objs[index]['tag_id'] = temp_tag_id
                objs[index]['name'] = name
                objs[index]['id'] = id
                objs[index]['customer_id_list'] = customer_id_list

    return objs

import json
data = json.dumps(ret_data)
print(insert_sort(ret_data))



