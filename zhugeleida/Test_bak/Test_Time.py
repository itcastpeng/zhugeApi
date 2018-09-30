# data_list = [
#     (1, '基本功能', None),
#     (2, '关注点', None),
#     (3, '级别', None),
#     (4, '90后', 1),
#     (5, '一般客户', 3),
#     (6, '重要客户', 3),
#     (7, '在意质量', 2),
#     (8, '已婚', 1),
#     (9, '在意 服务', 2)
# 
# ]
# 
# tag_dict = {}
# ret_data = []
# for obj  in data_list:
#     if obj[2] == None:
#        tag_dict[obj[1]] = []
#        for tag in data_list:
#            if tag[2] == obj[0]:
#                tag_dict[obj[1]].append([tag[1]])
# 
#        ret_data.append(tag_dict)
#        tag_dict = {}
# 
# import json
# print(json.dumps(ret_data))
# data_dict = [
#     {'customer_id': 1, 'action': 1, 'action__count': 4},
#     {'customer_id': 1, 'action': 2, 'action__count': 1},
#     {'customer_id': 2, 'action': 3, 'action__count': 3},
#     {'customer_id': 2, 'action': 2, 'action__count': 3},
#     {'customer_id': 1, 'action': 3, 'action__count': 1},
#     {'customer_id': 2, 'action': 1, 'action__count': 1},
#     ]
#
# ret_data = []
#
# for c in data_dict:
#     temp_dict = {}
#     customer_id = c['customer_id']
#     action = c['action']
#     action_count = c['action__count']
#
#     if customer_id in  temp_dict['customer_id']:
#         pass
#
#     else:
#         temp_dict['customer_id'] = customer_id
#         temp_dict['detail'] = []
#         temp_dict['detail'].append({
#             'count' : action_count,
#             'action': action,
#         })



    # # for a in  data_dict:
    #
    #     if a['customer_id'] == customer_id:
    #         temp_dict['totalCount'] += action_count
    #         temp_dict['detail'] = {
    #             "count": action_count,
    #             "action": action,
    #         }

#     ret_data.append(temp_dict)
#
#
# print(ret_data)
#








