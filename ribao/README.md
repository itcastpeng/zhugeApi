## api 说明
### 数据库使用说明
多数据库参考文档 https://blog.csdn.net/songfreeman/article/details/70229839

### 项目名称-------> 日报

### app 说明

### 公共参数（登录后所有api都需要加的参数）

```
请求参数:
参数名      传参方式      是否必须    参数描述
rand_str     get            是        md5(timestamp + token)
timestamp    get            是        时间戳   python获取方式: str(int(time.time() * 1000))   js 获取方式 new Date().getTime().toString();  
user_id      get            是        当前登录用户ID
```


### 登录中心

```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/login
请求参数:
参数名      传参方式    是否必须      参数描述
username     post         是      要登录的用户名
password     post         是      登录使用的密码

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


### 用户管理

- 添加

```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/user/add/0  

请求参数:
参数名         传参方式      是否必须      参数描述
username        post         是         要增加的用户名字
password        post         是         要增加的密码 
role_id         post         是         该用户的角色

正确结果：
{
    "code":200,
    "data":{

    },
    "msg":"添加成功"
}
```

- 修改

```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/user/update/ID 

请求参数：
参数名         传参方式      是否必须      参数描述
username        post         是         要修改的用户名 
role_id         post         是         要修改用户的角色
ID              url          是         要修改哪个用户ID

正确结果：
{
    "code":200,
    "data":{

    },
    "msg":"修改成功"
}
```

 - 删除

```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/user/delete/ID

请求参数：
参数名         传参方式      是否必须      参数描述
ID              url          是         要删除的用户ID

正确结果：
{
    "code":200,
    "data":{

    },
    "msg":"删除成功"
}
```
- 查询

```
请求方法：GET    
请求URL: http://127.0.0.1:8000/ribao/user  

请求参数：
参数名             传参方式      是否必须      参数描述
username            get            否       模糊匹配用户名
role_id             get            否       模糊匹配角色ID
create_date         get            否       查询创建时间
oper_user__username get            否       模糊匹配操作人
```


### 角色管理

 - 添加
 
```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/role/add/0  

请求参数:
参数名         传参方式      是否必须      参数描述
name            post           是        添加的角色名

正确结果：
{
    "code":200,
    "data":{

    },
    "msg":"添加成功"
} 
```

- 修改 

```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/role/update/ID 

请求参数：
参数名         传参方式      是否必须      参数描述
ID              url           是         要修改的ID
name            post          是         要修改的角色名 

正确结果：
{
    "code":200,
    "data":{

    },
    "msg":"修改成功"
}
```

 - 删除 

```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/role/delete/ID 

请求参数：
参数名         传参方式      是否必须      参数描述
ID              get          是         要删除的用户ID

正确结果：
{
    "code":200,
    "data":{

    },
    "msg":"删除成功"
}
```

 - 查询
 
 ```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/role

请求参数
参数名            传参方式      是否必须      参数描述
name                get            否       模糊匹配角色名 
create_date         get            否       查询创建时间
oper_user__username get            否       模糊匹配操作人

```


### 项目管理

 - 添加

```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/xiangmuguanli/add/0  

请求参数:
参数名             传参方式         是否必须       参数描述
project_name        post           是             项目名称   
person_people_id    post           是             责任人ID外键链用户名   

正确结果：
{
    "code":200,
    "data":{

    },
    "msg":"添加成功"
}  
```

- 修改 

```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/xiangmuguanli/update/o_id 

请求参数：
参数名         传参方式      是否必须      参数描述
o_id             get           是         要修改的角色ID
project_name     post          是         要修改的项目名称

正确结果：
{
    "code":200,
    "data":{

    },
    "msg":"修改成功"
}
```

 - 删除 

```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/xiangmuguanli/delete/ID 

请求参数：
参数名         传参方式      是否必须      参数描述
ID              get          是         要删除的用户ID

正确结果：
{
    "code":200,
    "data":{

    },
    "msg":"删除成功"
}
```

 - 查询
 
 ```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/xiangmuguanli

请求参数：
参数名                 传参方式      是否必须      参数描述
project_name             get            否        模糊匹配项目名称
person_people_username   get            否        模糊匹配责任开发人
```


### 任务管理

 - 添加
 
```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/renwuguanli/add/0  

请求参数:
参数名            传参方式       是否必须          参数描述
task_name           post           是             任务名称   
belog_task_id       post           是             归属项目(此任务归哪个项目)    
director_id         post           是             责任开发人
boor_urgent         post           是             是否加急

正确结果：
{
    "code":200,
    "data":{

    },
    "msg":"添加成功"
}
```

- 修改 

```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/renwuguanli/update/ID 

请求参数：
参数名         传参方式      是否必须      参数描述
ID               url           是         要修改的任务ID
task_name        post          是         要修改的项目名称
director         post          否         责任开发人
issuer           post          否         任务发布人

正确结果：
{
    "code":200,
    "data":{

    },
    "msg":"修改成功"
}
```

 - 删除 

```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/renwuguanli/delete/ID 

请求参数：
参数名         传参方式      是否必须      参数描述
ID              url          是         要删除的用户ID

正确结果：
{
    "code":200,
    "data":{

    },
    "msg":"删除成功"
}
```

 - 查询
 
```
请求方法：GET
请求URL: http://127.0.0.1:8000/ribao/renwuguanli

请求参数：
参数名         传参方式      是否必须      参数描述
task_name         get           否       模糊匹配任务名
detail            get           否       查询任务详情
belog_task        get           否       模糊匹配归属名    
director          get           否       模糊匹配责任开发人    
issuer            get           否       查询发布人    
boor_urgent       get           否       查询是否加急    
create_date       get           否       查询创建时间    
```     


### 任务日志

 - 添加
   
```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/renwurizhi/add/0  

请求参数:
参数名            传参方式       是否必须          参数描述
belog_log_id       post           是              归属日志(此日志归哪个项目)   
log_status         post           是              当前状态    

正确结果：
{
    "code":200,
    "data":{

    },
    "msg":"添加成功"
}
```

- 修改 

```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/renwurizhi/update/ID 

请求参数：
参数名         传参方式      是否必须      参数描述
log_status      post           是      修改项目日志状态    
正确结果：
{
    "code":200,
    "data":{

    },
    "msg":"修改成功"
}
```

 - 删除 

```
请求方法：POST
请求URL: http://127.0.0.1:8000/ribao/renwurizhi/delete/ID 

请求参数：
参数名         传参方式      是否必须      参数描述
ID              get          是         要删除的用户ID

正确结果：
{
    "code":200,
    "data":{

    },
    "msg":"删除成功"
}
```

 - 查询
 
```
请求方法：GET
请求URL: http://127.0.0.1:8000/ribao/renwurizhi

请求参数：
参数名                  传参方式      是否必须      参数描述
belog_log                 get           否        查询该日志属于哪个任务
log_status                get           否        查询当前项目状态
oper_user__username       get           否        模糊匹配操作人
create_date               get           否        查询创建日志时间
```