
#
# objs = [
#     # {'name': 1 ,'action__count': 5},
#     # {'name': 2 ,'action__count': 6},
#     # {'name': 3 ,'action__count': 2},
#     # {'name': 4 ,'action__count': 5},
#     # {'name': 5 ,'action__count': 55},
#     # {'name': 6 ,'action__count': 53},
#     # {'name': 7 ,'action__count': 12},
#     # {'name': 8 ,'action__count': 3}
#
# ]

objs =   [(854, 'SnUgZG8gaXQ=', None, 1), (851, '6L+H5a6i5Li2', 854, 2), (886, '5Y+I6IOW5LqG', 851, 3), (887, 'TElqaUHwn5iY', 886, 4), (890, 'Qe6AgyDkuIDmirnujK7pmLPlhYk=', None, 1), (891, '5pm26I655piO5r6I', 890, 2), (892, '5p2O5oms', 891, 3), (893, '5p6X5pWP', 886, 4), (894, 'c3Vubnk=', 892, 4), (895, '5a6J5qyn5be07oSd', None, 1), (896, '6qeB5Yed6Zyc6qeC', 895, 1), (897, '5byg546l', 887, 3), (884, '5qKm5oOz5LiA5a6a6KaB5pyJW+Wli+aWl10=', None, 1), (898, '6IOh6JOJ8J+Sl1Jvc2U=', 894, 5), (899, '5p2O5Lqa6b6Z4oKB4oKH4oKG4oKA4oKA4oKB4oKF4oKF4oKC4oKE4oKE5aSn5Zyj', 893, 5), (900, 'Q2hlc251dO6AsA==', 851, 3), (901, '57Gz5aSa6Z2i5aSa77yI5rC45bm05bqX77yJ', 900, 4), (902, '5bi46Z+15p2w', None, 1), (904, 'QmlsbA==', 902, 2), (862, '5L+u54K854ix5oOF55qE5oKy5qyi', 904, 3), (905, '5qKm6a2H', 862, 4)]

    # {'id': 1, 'name': '无限',    'parent_id': None},
    # {'id': 2, 'name': '医疗美容', 'parent_id': None},
    # {'id': 3, 'name': '汽车保养', 'parent_id': None},
    # {'id': 4, 'name': '美食购物', 'parent_id': None},
    # {'id': 5, 'name': '时尚芭莎', 'parent_id': None},
    # {'id': 6, 'name': '海峡两岸', 'parent_id': None},
    # {'id': 7, 'name': '历史纪实', 'parent_id': None},
    # {'id': 8, 'name': '清史', 'parent_id': 7},
    # {'id': 9, 'name': '蓝营阵容', 'parent_id': 6},
    # {'id': 10, 'name': '特别关注', 'parent_id': None},
    # {'id': 11,'name': '明史', 'parent_id': 7},
    # {'id': 12, 'name': '绿营阵容', 'parent_id': 6},
    # {'id': 13, 'name': '京津冀', 'parent_id': 10},
    # {'id': 14, 'name': '海外代购', 'parent_id': 4},
    # {'id': 15, 'name': '江浙沪', 'parent_id': 10},
    # {'id': 16, 'name': '话说三国', 'parent_id': 7}

    # ( 1, '无限', None),
    # (2, '医疗美容',  None),
    # ( 3, '汽车保养',  None),
    # ( 4, '美食购物',  None),
    # ( 5, '时尚芭莎',  None),
    # ( 6, '海峡两岸',  None),
    # ( 7, '历史纪实',  None),
    # ( 8, '清史',  7),
    # ( 9, '蓝营阵容',  6),
    # ( 10, '特别关注',  None),
    # ( 11, '明史',  7),
    # ( 12, '绿营阵容',  6),
    # ( 13, '京津冀',  10),
    # ( 14, '海外代购',  4),
    # ( 15, '江浙沪',  10),
    # ( 16, '话说三国',  7)







import collections

def build_tree(query_set_list):
    set_new_list  = []

    # d_dic = collections.OrderedDict()
    d_dic = { }

    for tag_dic in query_set_list:

        if tag_dic[2] is None:
            # d_dic[tag_dic] = collections.OrderedDict()
            d_dic[tag_dic] = {}

        else:
            tree_search(d_dic, tag_dic)

    return d_dic

def tree_search(d_dic,tag_dic):

    for k,v in d_dic.items():

        if k[0] == tag_dic[2]:

            # d_dic[k][tag_dic] = collections.OrderedDict()
            d_dic[k][tag_dic] = {}
            return
        else:
            if v:
                tree_search(d_dic[k],tag_dic)

import json
# print(build_tree(objs))

objs = build_tree(objs)
# print ('---------->>\n',objs)
print ('---------->>\n',json.dumps(objs))
# print (json.dumps(objs))


# for o in  objs.keys():
#     print(o)



# # 方法一
# ret_list = []
# for obj in objs:
#     if not ret_list: # 首次添加
#         ret_list.append(obj)
#
#     else: # ret_list 中有数据
#
#         for index, data in enumerate(ret_list):
#             print('for ret_list', ret_list )
#             if obj['action__count'] > data['action__count']:
#                 ret_list.insert(index, obj)
#                 print('--------->>',obj['action__count'],data['action__count'])
#                 break
#
#         else:
#             ret_list.append(obj)
#
# print(ret_list)

#方法二

# def insert_sort(objs):
#     for i in  range(1,len(objs)):
#         if  objs[i]['action__count']  <  objs[i-1]['action__count']:
#             temp = objs[i]['action__count']
#             for j in range(i-1,-1,-1):
#                 if objs[j]['name'] > temp:
#                     objs[j + 1]['name'] = objs[j]['action__count']
#                     index = j  # 记下应该插入的位置
#                 else:
#                     break
#
#                 objs[index]['action__count'] = temp
#     return objs
#
# print(insert_sort(objs))
# #





