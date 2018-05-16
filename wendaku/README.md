## api 说明文档

### 公共参数（登录后所有api都需要加的参数）
```
?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID
请求方法：GET
请求参数:
参数名    是否必须    参数描述
rand_str    是        md5(timestamp + token)
timestamp   是        时间戳   python获取方式: str(int(time.time() * 1000))   js 获取方式 new Date().getTime().toString();  
user_id     是        当前登录用户ID
```


### 登录功能
```
请求方法：POST
请求URL:http://127.0.0.1:8000/wendaku/login

请求参数:
参数名     请求方式    是否必须    参数描述
username     post       是        获取用户名
password     post       是        获取密码

返回结果：
    正确情况：
        {"data": {"token": "a263fe839f04392cc080fd37c285ae0b", "set_avator": "statics/imgs/setAvator.jpg", "user_id": 11}, "code": 200, "msg": "\u767b\u5f55\u6210\u529f"}

        {
            "data": {
                "token": "a263fe839f04392cc080fd37c285ae0b",    # 返回token
                "set_avator": "statics/imgs/setAvator.jpg",     # 头像路径前端需要进行域名拼接
                "user_id": 11                                   # 用户ID
            }, 
            "code": 200,                                        # 状态码
            "msg": "\u767b\u5f55\u6210\u529f"                   # 提示信息
        }
    错误情况:
        {"data": {}, "code": 401, "msg": "\u8d26\u53f7\u6216\u5bc6\u7801\u9519\u8bef"}
        
        {
            "data": {},                                         # 返回数据
            "code": 401,                                        # 状态码
            "msg": "\u8d26\u53f7\u6216\u5bc6\u7801\u9519\u8bef" # 提示信息
            }
```


### 角色管理
- 查询角色

```
请求方法：GET
请求URL: http://127.0.0.1:8000/wendaku/role?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名     请求方式        是否必须            参数描述
rand_str   （get,post）      是         参考顶部公共参数说明
timestamp  （get,post）      是         参考顶部公共参数说明
user_id    （get,post）      是         参考顶部公共参数说明

返回结果：
    正确情况：
        {"msg": "", "data": {"data_count": 13, "role_data": [{"create_date": "2018-04-27T19:03:17", "oper_user__username": "\u8d75\u6b23\u9e4f", "id": 17, "name": "\u5eb7\u6865o "}, {"create_date": "2018-04-27T15:20:23", "oper_user__username": "\u8d75\u6b23\u9e4f", "id": 16, "name": "\u5eb7\u6865"}]}, "code": 200}

    "msg":"",
    "data":{                                                                 # 返回数据 无内容为空 
        "data_count":13,                                                     # 数据总数
        "role_data":[
            {
                "create_date":"2018-04-27T19:03:17",                         # 创建时间1
                "oper_user__username":"赵欣鹏",                              # 操作人1
                "id":17,                                                     # 角色1 ID
                "name":"康桥o "                                              # 角色1 名字
            },
            {
                "create_date":"2018-04-27T15:20:23",                         # 创建时间2    
                "oper_user__username":"赵欣鹏",                              # 操作人2
                "id":16,                                                     # 角色2 ID
                "name":"康桥"                                                # 角色2 名字
            }
        ]
    },
    "code":200                                                               # 异常状态码
}
    错误情况:
        {"msg": "token\u5f02\u5e38", "data": {}, "code": 400}      
                 
        {
    "msg":"token异常",                                                        # 状态说明
    "data":{                                                                  # 返回数据 无内容为空 

    },
    "code":400                                                                # 状态码
}
        
```
- 增加角色

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/role/add/0?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
name                是         要增加的角色名字

返回结果：
    正常情况：
        {"msg": "\u6dfb\u52a0\u6210\u529f", "data": {}, "code": 200}
        
        {
    "msg":"添加成功",                                                         # 状态说明 
    "data":{                                                                 # 返回数据 无内容为空 

    },
    "code":200                                                               # 状态码
}

    错误情况：
        {"msg": {"name": [{"message": "\u89d2\u8272\u540d\u4e0d\u80fd\u4e3a\u7a7a", "code": "required"}]}, "data": {}, "code": 301}
        
        {
    {
    "msg":"token异常",                                                       # 状态说明
    "data":{                                                                 # 返回数据 无内容为空 

    },
    "code":400                                                               # 状态码
}

```

- 删除角色

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/role/delete/ID?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
ID                  是         要删除的角色ID（放在url里）


返回结果：
    正常情况：
        {"msg": "\u5220\u9664\u6210\u529f", "data": {}, "code": 200}
    
        {
    "msg":"删除成功",                                                          # 状态说明
    "data":{                                                                  # 返回数据 无内容为空 

    },
    "code":200                                                                # 状态码
}

    错误情况：
        {"msg": "\u89d2\u8272ID\u4e0d\u5b58\u5728", "data": {}, "code": 302}
    
        {
    "msg":"角色ID不存在",                                                      # 状态说明
    "data":{                                                                  # 返回数据 无内容为空 

    },
    "code":302                                                                # 状态码
}
```

- 修改角色

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/role/update/ID?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
name                是         要修改数据的名字
ID                  是         要修改数据的ID（放在URL里）

返回结果：
    正确情况：
        {"msg": "\u4fee\u6539\u6210\u529f", "data": {}, "code": 200}
      
        {   
    "msg":"修改成功",                                                          # 状态说明                   
    "data":{                                                                  # 返回数据 无内容为空   

    },
    "code":200                                                                 # 状态码
}
    
    错误情况：
        {"msg": {"name": [{"message": "\u89d2\u8272\u5df2\u5b58\u5728", "code": ""}]}, "data": {}, "code": 302}
        
        {
    "msg":{
        "name":[
            {
                "message":"角色已存在",                                         # 状态说明
                "code":""                                                       
            }
        ]
    },
    "data":{                                                                   # 返回数据 无内容为空   

    },
    "code":302                                                                 # 状态码
}


```


### 用户管理

- 查询角色

```
请求方法：GET
请求URL: http://127.0.0.1:8000/wendaku/user?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
length              否         接收每页条数（分页）默认10
current_page        否         接收第几页开始默认1
order               否         排序方法（默认升序）

返回结果：
    正确情况：
        {"code": 200, "msg": "", "data": {"role_data": [{"role_id": 18, "create_date": "2018-04-28T10:15:11", "id": 18, "oper_user__username": "\u79d1\u6280\u8ba4\u611f\u89c9\u4e3a\u7231\u8fc7", "name": "\u90fd\u5f88\u5927\u65b9"}], "data_count": 10}}

              
{
    "code":200,
    "msg":"",
    "data":{
        "role_data":[
            {
                "role_id":18,                                       
                "create_date":"2018-04-28T10:15:11",                
                "id":18,                                                
                "oper_user__username":"科技认感觉为爱过",                   
                "name":"都很大方"                                           
            }
        ],
        "data_count":10
    }
}

    错误情况:
        {"code": 400, "msg": "token\u5f02\u5e38", "data": {}}
        
        {
    "code":400,
    "msg":"token异常",
    "data":{

    }
}
```

- 增加用户

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/user/add/0?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
username            是         增加用户的名字
role_id             是         属于哪个角色 的用户
password            是         此用户的密码

返回结果：
    正确情况：
        {"msg": "\u6dfb\u52a0\u6210\u529f", "code": 200, "data": {}}
        
        {
    "msg":"添加成功",                                                           # 状态说明
    "code":200,                                                                # 状态码
    "data":{                                                                   # 返回数据 无内容为空 

    }
}
    
    错误情况：
        {"msg": {"username": [{"message": "\u7528\u6237\u540d\u5df2\u5b58\u5728", "code": ""}], "password": [{"message": "\u5bc6\u7801\u4e0d\u80fd\u4e3a\u7a7a", "code": "required"}]}, "code": 301, "data": {}}
        
       {
    "msg":{
        "password":[
            {
                "message":"密码不能为空",                                       # 状态说明
                "code":"required"   
            }
        ]
    },
    "code":301,                                                                # 状态码 
    "data":{                                                                   # 返回数据 无内容为空 

    }
}

```

- 删除用户

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/user/delete/ID?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
ID                  是         要删除数据的ID

返回结果：
    正确情况：
        {"msg": "\u5220\u9664\u6210\u529f", "code": 200, "data": {}}
        
        {
    "msg":"删除成功",                                                           # 状态说明
    "code":200,                                                                # 状态码
    "data":{                                                                   # 返回数据 无内容为空 

    }
}
    
    错误情况：
        {"data": {}, "code": 302, "msg": "\u7528\u6237ID\u4e0d\u5b58\u5728"}
    
        {
    "data":{                                                                  # 返回数据 无内容为空 

    },
    "code":302,                                                               # 状态码
    "msg":"用户ID不存在"                                                      # 状态说明
}
```

- 修改用户

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/user/update/ID?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
ID                  是         要修改数据的ID
username            是         要修改用户的名字

返回结果：
    正确情况：
        {"msg": "\u4fee\u6539\u6210\u529f", "code": 200, "data": {}}
        
        {
    "msg":"修改成功",                                                       # 状态说明
    "code":200,                                                             # 状态码
    "data":{                                                                # 返回数据，无内容为空

    }
}
    
    错误情况：
        {"data": {}, "code": 301, "msg": {"role_id": [{"message": "\u89d2\u8272\u4e0d\u80fd\u4e3a\u7a7a", "code": "required"}]}}

        {
    "data":{

    },
    "code":301,                                                              # 状态码                                                      
    "msg":{
        "role_id":[
            {
                "message":"角色不能为空",                                     # 状态说明
                "code":"required"
            }
        ]
    }
}

```


### 科室管理

- 科室查询

```
请求方法：GET
请求URL: http://127.0.0.1:8000/wendaku/keshi?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
length              否         接收每页条数（分页）默认10
current_page        否         接收第几页开始默认1
order               否         排序方法（默认升序）

返回结果：
    正确情况：
        {"code": 200, "msg": "", "data": {"role_data": [{"create_date": "2018-04-27T12:01:39", "id": 7, "oper_user__username": "\u79d1\u6280\u8ba4\u611f\u89c9\u4e3a\u7231\u8fc7", "name": "\u6309\u5403", "pid_id": 1}], "data_count": 5}}
                
        {
    "code":200,
    "msg":"",
    "data":{
        "role_data":[
            {
                "create_date":"2018-04-27T12:01:39",
                "id":7,
                "oper_user__username":"科技认感觉为爱过",
                "name":"按吃",
                "pid_id":1
            }
        ],
        "data_count":5
    }
}
    
    错误情况：
        {"code": 400, "msg": "token\u5f02\u5e38", "data": {}}
        
        {
    "code":400,
    "msg":"token异常",
    "data":{

    }
}
```

- 增加科室

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/keshi/add/0?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
name                是         要增加的科室名字
pid                 是         父级ID  

返回结果：
    正确情况：
        {"msg": "\u6dfb\u52a0\u6210\u529f", "data": {}, "code": 200}
        
        {
    "msg":"添加成功",                                                         # 状态说明
    "data":{                                                                 # 返回数据，无内容为空

    },
    "code":200                                                               # 状态码
}

    错误情况：
    {"msg": {"pid_id": [{"message": "\u7236\u7ea7ID\u4e0d\u80fd\u4e3a\u7a7a", "code": "required"}]}, "data": {}, "code": 300}

        {
    "msg":{
        "pid_id":[                                                          # 父级的ID
            {
                "message":"父级ID不能为空",                                  # 状态说明
                "code":"required"
            }
        ]
    },
    "data":{                                                                # 返回数据，无内容为空

    },
    "code":300                                                              # 状态码
}

```

- 删除科室

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/keshi/delete/ID?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
ID                  是         要删除数据的ID（放在url里）

返回结果：
    正确情况：
        {"msg": "\u5220\u9664\u6210\u529f", "data": {}, "code": 200}
        
        {
    "msg":"添加成功",                                                         # 状态说明
    "data":{                                                                 # 返回数据，无内容为空

    },
    "code":200                                                               # 状态码
}

    错误情况：
        {"msg": "\u7528\u6237ID\u4e0d\u5b58\u5728", "data": {}, "code": 302}
        
        {
    "msg":"用户ID不存在",                                                    # 状态说明
    "data":{                                                                # 返回数据，无内容为空

    },
    "code":302                                                              # 状态码
}

```

- 修改科室

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/keshi/update/0?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
name                是         要修改数据的名字
pip_id              是         父级数据的ID

返回结果：
    正确情况：
        {"msg": "\u4fee\u6539\u6210\u529f", "code": 200, "data": {}}
        
        {
    "msg":"修改成功",                                                       # 状态说明
    "code":200,                                                            # 状态码
    "data":{                                                               # 返回数据，无内容为空

    }
}
    
    错误情况：
        {"code": 400, "msg": "token\u5f02\u5e38", "data": {}}
    
        {
    "code":400,                                                            # 状态码
    "msg":"token异常",                                                     # 状态说明
    "data":{                                                               # 返回数据，无内容为空

    }
}
```


### 词类管理

- 词类查询

```
请求方法：GET
请求URL: http://127.0.0.1:8000/wendaku/keshi?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
length              否         接收每页条数（分页）默认10
current_page        否         接收第几页开始默认1
order               否         排序方法（默认升序）

返回结果：
    正确情况：
        {"code": 200, "msg": "", "data": {"role_data": [{"create_date": "2018-04-28T16:27:59", "id": 13, "oper_user__username": "\u79d1\u6280\u8ba4\u611f\u89c9\u4e3a\u7231\u8fc7", "name": "\u4e8c\u5341\u51e0\u5e74"}], "data_count": 4}}
        
        {
    "code":200,
    "msg":"",
    "data":{
        "role_data":[
            {
                "create_date":"2018-04-28T16:27:59",
                "id":13,
                "oper_user__username":"科技认感觉为爱过",
                "name":"二十几年"
            }
        ],
        "data_count":4
    }
}
    错误情况：
        {"code": 400, "msg": "token\u5f02\u5e38", "data": {}}
        
        {
    "code":400,
    "msg":"token异常",
    "data":{

    }
}
```

- 增加词类

```\
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/keshi/add/0?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
name                是         要增加的名字

返回结果：
    正确情况：
            {"msg": "\u6dfb\u52a0\u6210\u529f", "code": 200, "data": {}}
        
        {
    "msg":"添加成功",                                                       # 状态说明
    "code":200,                                                            # 状态码
    "data":{                                                               # 返回数据，无内容为空

    }
}
    错误情况：
        {"code": 301, "msg": {"name": [{"message": "\u8bcd\u540d\u4e0d\u80fd\u4e3a\u7a7a", "code": "required"}]}, "data": {}}

        {
    "code":301,                                                            # 状态码
    "msg":{
        "name":[
            {
                "message":"词名不能为空",                                   # 状态说明
                "code":"required"                                           
            }
        ]
    },
    "data":{                                                               # 返回数据,无内容为空

    }
}
    
```

- 删除词类

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/keshi/delete/ID?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
ID                  是         要删除数据的ID（放在URL里）

返回结果：
    正确情况：
        {"msg": "\\u5220\u9664\u6210\u529f", "code": 200, "data": {}}
        
        {
    "msg":"删除成功",                                                       # 状态说明
    "code":200,                                                            # 状态码
    "data":{                                                               # 返回数据，无内容为空

    }
}
    错误情况：
        {"code": 302, "msg": "\u672c\u8bcd\u4e0d\u5b58\u5728", "data": {}}
        
        {
    "code":302,                                                            # 状态码
    "msg":"本词不存在",                                                     # 状态说明
    "data":{                                                               # 返回数据，无内容为空

    }
}
```

- 修改词类

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/keshi/update/ID?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
ID                  是         要修改数据的ID（放在url里）
name                是         要修改数据的名字

返回结果：
    正确情况：
        {"msg": "\u4fee\u6539\u6210\u529f", "code": 200, "data": {}}
        
        {
    "msg":"修改成功",                                                       # 状态说明
    "code":200,                                                            # 状态码
    "data":{                                                               # 返回数据，无内容为空

    }
}
    错误情况：
        {"code": 400, "msg": "token\u5f02\u5e38", "data": {}}
        
              
{
    "code":400,                                                            # 状态码 
    "msg":"token异常",                                                     # 状态说明
    "data":{                                                               # 返回数据，无内容为空

    }
}
        
```


### 答案类型管理

- 答案类型查询

```
请求方法：GET
请求URL: http://127.0.0.1:8000/wendaku/keshi?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
length              否         接收每页条数（分页）默认10
current_page        否         接收第几页开始默认1
order               否         排序方法（默认升序）

返回结果：
    正确情况：
        {"code": 200, "msg": "", "data": {"role_data": [{"create_date": "2018-04-28T17:28:50", "id": 9, "oper_user__username": "\u79d1\u6280\u8ba4\u611f\u89c9\u4e3a\u7231\u8fc7", "name": "sa\u5965\u65f6\u4ee3\u611fi"}], "data_count": 6}}
    
        {
    "code":200,
    "msg":"",
    "data":{
        "role_data":[
            {
                "create_date":"2018-04-28T17:28:50",
                "id":9,
                "oper_user__username":"科技认感觉为爱过",
                "name":"sa奥时代感i"
            }
        ],
        "data_count":6
    }
}
    错误情况：
        {"code": 400, "msg": "token\u5f02\u5e38", "data": {}}
        
        {
    "code":400,
    "msg":"token异常",
    "data":{

    }
}
```

- 增加答案类型

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/daanleixing/add/0?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
name                是         要增加的答案类型名字


返回结果：
    正确情况：
        {"msg": "\u6dfb\u52a0\u6210\u529f", "code": 200, "data": {}}
        
        {
    "msg":"添加成功",                                                       # 状态说明
    "code":200,                                                            # 状态码
    "data":{                                                               # 返回数据，无内容为空

    }
}

    错误结果：
        {"msg": {"name": [{"message": "\u7c7b\u578b\u4e0d\u80fd\u4e3a\u7a7a", "code": "required"}]}, "code": 301, "data": {}}
    {
    "msg":{
        "name":[
            {
                "message":"类型不能为空",                                   # 状态说明
                "code":"required"                                          
            }
        ]
    },
    "code":301,                                                            # 状态码
    "data":{                                                               # 返回数据，无内容为空

    }
}
        
    

```

- 删除答案类型

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/daanleixing/delete/ID?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
ID                  是         要删除数据的ID（放在url里）

返回结果：
    正确情况：
        {"msg": "\u5220\u9664\u6210\u529f", "code": 200, "data": {}}
        
        {
    "msg":"删除成功",                                                      # 状态说明
    "code":200,                                                           # 状态码 
    "data":{                                                              # 返回数据，无内容为空

    }
}

    错误情况：
        {"msg": "\u672c\u8bcd\u4e0d\u5b58\u5728", "code": 302, "data": {}}
        
        {
    "msg":"本词不存在",                                                    # 状态说明
    "code":302,                                                           # 状态码
    "data":{                                                              # 返回数据，无内容为空

    }
}
```

- 修改答案类型

```

请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/daanleixing/update/ID?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
ID                  是         答案类型ID（放在url里）
name                是         要修改答案类型的名字


返回结果：
    正确情况：
        {"msg": "\u4fee\u6539\u6210\u529f", "code": 200, "data": {}}
        
        {
    "msg":"修改成功",                                                     # 状态说明
    "code":200,                                                           # 状态码
    "data":{                                                              # 返回数据，无内容为空

    }
}

    错误情况：
        {"msg": {}, "code": 303, "data": {}}
        
              
{
    "msg":{                                                              # 状态说明 

    },
    "code":303,                                                          # 状态码
    "data":{                                                             # 返回数据，无内容为空

    }
}
    

```


### 答案库管理

- 答案库查询

```
请求方法：GET
请求URL: http://127.0.0.1:8000/wendaku/user?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
length              否         接收每页条数（分页）默认10
current_page        否         接收第几页开始默认1
order               否         排序方法（默认升序）

返回结果：
    正确情况：
        {"code": 200, "msg": "", "data": {"role_data": [{"cilei__name": "\u6309\u63ed\u9996\u4ed8", "id": 17, "keshi_name": "\u6309\u65f6\u5403", "content": "\u5b8c\u5584\u6cd5\u89c4\u554a", "shenhe_date": null, "create_date": "2018-04-28T09:29:19", "oper_user__username": "\u79d1\u6280\u8ba4\u611f\u89c9\u4e3a\u7231\u8fc7", "daan_leiixng": "\u6697\u4e16\u8fdb\u754c"}], "data_count": 10}}
    
        {
    "code":200,
    "msg":"",
    "data":{
        "role_data":[
            {
                "cilei__name":"按揭首付",
                "id":17,
                "keshi_name":"按时吃",
                "content":"完善法规啊",
                "shenhe_date":null,
                "create_date":"2018-04-28T09:29:19",
                "oper_user__username":"科技认感觉为爱过",
                "daan_leiixng":"暗世进界"
            }
        ],
        "data_count":10
    }
}
    错误情况：
         {"code": 400, "msg": "token\u5f02\u5e38", "data": {}}
        
        {
    "code":400,
    "msg":"token异常",
    "data":{

    }
}
```

- 增加答案

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/daanku/add/0?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
content             是         答案内容 （必填字段）

返回结果：
    正确情况：
        {"msg": "\u6dfb\u52a0\u6210\u529f", "data": {}, "code": 200}
        
        {
    "msg":"添加成功",                                                      # 状态说明
    "data":{                                                              # 返回数据，无内容为空

    },
    "code":200                                                            # 状态码
}
        
    错误情况：
        {"msg": {"content": [{"message": "\u7b54\u6848\u4e0d\u80fd\u4e3a\u7a7a", "code": "required"}]}, "data": {}, "code": 301}

        {
    "msg":{
        "content":[                                                 
            {
                "message":"答案不能为空",                                   # 状态说明  
                "code":"required"   
            }
        ]
    },
    "data":{                                                               # 返回数据，无状态为空

    },
    "code":301                                                             # 状态码
}   


```

- 删除答案

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/daanku/delete/ID?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
ID                  是         要删除的ID号(要放在url中) 
返回结果：
    正确情况：
        {"msg": "\u5220\u9664\u6210\u529f", "data": {}, "code": 200}
        
        {
    "msg":"删除成功",                                                      # 状态说明
    "data":{                                                               # 返回数据，无数据为空

    },
    "code":200                                                             # 状态码
}

    错误情况：
        {"msg": "\u7b54\u6848\u4e0d\u5b58\u5728", "data": {}, "code": 302}
        
        {
    "msg":"答案不存在",                                                   # 状态说明
    "data":{                                                              # 返回数据，无数据为空

    },
    "code":302                                                            # 状态码
}


```

- 修改答案

```
请求方法：POST
请求URL: http://127.0.0.1:8000/wendaku/daanku/update/ID?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order

请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
content             是         要修改的答案内容
ID                  是         要修改答案的ID（写在url里）

返回结果：
    正确情况：
        {"msg": "\u4fee\u6539\u6210\u529f", "data": {}, "code": 200}
        
        {
    "msg":"修改成功",                                                   # 状态说明
    "data":{                                                            # 返回数据，无数据为空

    },
    "code":200                                                          # 状态码
}
        
    错误情况：
        {"msg": "token\u5f02\u5e38", "data": {}, "code": 400}
        
        {
    "msg":"token异常",                                                  # 状态说明
    "data":{                                                            # 返回数据，无数据为空

    },
    "code":400                                                          # 状态码
}
```

- 批量删除答案 

```
请求方法：POST
请求URL：http://127.0.0.1:8000/wendaku/daanku/batch_delete/0?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID&order
请求参数:
参数名             是否必须    参数描述
rand_str            是         参考顶部公共参数说明
timestamp           是         参考顶部公共参数说明
user_id             是         参考顶部公共参数说明
list_ids            是         要删除的所有ID号(字符串类型) 如要删除ID为1, 2, 3的数据：list_ids = '1,2,3'
                     
返回结果：
    正确情况：
       {"code": 200, "data": {}, "msg": "\u5220\u9664\u6210\u529f"}
        
        {
    "msg":"删除成功",                                                      # 状态说明
    "data":{                                                               # 返回数据，无数据为空

    },
    "code":200                                                             # 状态码
}

    错误情况：
        {"code": 400, "data": {}, "msg": "token\u5f02\u5e38"}
      
        {
    "code":400,                                                            # 状态码
    "data":{                                                               # 返回数据，无数据为空

    },
    "msg":"token异常"                                                      # 状态说明
} 
```

## api 返回值说明

```
200 正常

300 角色名已存在
301 数据类型验证失败
302 对应ID不存在
303 form 验证错误
304 含有子级数据,请先删除或转移子级数据

401 账号密码错误
402 请求方式异常 例如应该使用 POST 请求的使用的是 GET 请求
403 无任务
```