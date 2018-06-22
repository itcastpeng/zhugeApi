
#### code 说明：
```python
200 正常

300 角色名已存在
301 数据类型验证失败
302 对应ID不存在
303 form 验证错误
304 含有子级数据,请先删除或转移子级数据
305 不允许删除自己
306 账户未启用

401 账号密码错误
402 请求方式异常 例如应该使用 POST 请求的使用的是 GET 请求
403 无任务
404 非法请求



```
####   公共参数（登录后所有api都需要加的参数）

``` python
?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID
请求方法：GET
请求参数:
参数名    是否必须    参数描述
rand_str    是        md5(timestamp + token) 使用 md5 进行加密
timestamp   是        时间戳   python获取方式: str(int(time.time() * 1000))   js 获取方式 new Date().getTime().toString(); 
user_id     是        当前登录用户ID

```



####   查询用户：
GET的数据部分【公共参数】：

```python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,                             
}
```

搜索参数说明：
```
 参数名                 搜索                        说明
username                  是                         用户名(可模糊搜索）
role__name             是                         角色名(可模糊）   
company__name          是                         公司名（可模糊）
create_date            是                         创建时间            
```

 请求示例:

>http://127.0.0.1:8000/zhugeleida/qiyeweixin/user?rand_str=d51d2ab1cec69db820c08adddf2f3a61&timestamp=1528114804033&user_id=1


返回结果:
``` json
{
    "code":200,
    "msg":"查询成功",
    "data":{
        "ret_data":[
            {
                "id":2,
                "username":"zhangju",
                "role_name":"普通用户",
                "role_id":1,
                "create_date":"2018-05-31T08:18:42",
                "last_login_date":"2018-05-31T08:18:39",
                "status":"启用"
            },
            {
                "id":1,
                "username":"zhangcong",
                "role_name":"普通用户",
                "role_id":1,
                "create_date":"2018-05-30T22:16:20",
                "last_login_date":"2018-05-30T22:16:23",
                "status":"启用"
            }
        ],
        "data_count":3
    }
}
```

### 增加用户:


POST数据示例：

``` python
{  
    'userid' = 'zhangcong'  
    'username' = 'H2O'
    'password' = '123456'
    'role_id' = 1
    'company_id' = 1
}
```

POST请求 发送参数说明

``` python
参数          必填            说明                              
usedid        否             成员UserID,通过微信认证获取的。        
username      是             登录用户名
password      是             密码     
role_id       是             角色ID
company_id    是             公司ID
```

GET 请求发送参数：

``` python
  {
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
   }
```

请求示例：

>http://127.0.0.1:8000/zhugeleida/qiyeweixin/user/add/0?rand_str=ce663215f5c33b93c710c7af952da914&timestamp=1528121862752&user_id=1   # 增加用户
 
 


#### 删除用户:
GET 请求发送数据部分：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
```
 
请求访问示例:

>http://127.0.0.1:8000/zhugeleida/qiyeweixin/user/delete/4

 
#### 修改用户：
 
GET 请求发送数据部分：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
``` 

POST数据示例：

``` python
{  
    'username' ：'张三'
    'password' ： '123456'
    'role_id' ： 1
    'company_id' ： 1
}

``` 

POST参数说明：

``` python
 
参数        说明
username    登录用户名
password    密码
role_id     角色ID
company_id  公司ID

```

访问示例:
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/user/update/5?rand_str=4c75edb76b06a2983040980f171b83e7&timestamp=1528169127235&user_id=1
      
####  查询【单个】客户信息：

GET 请求发送数据部分：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
	'customer_id'；2  
}
```

GET 参数说明：

``` python
参数名                 必填                说明
customer_id            是                  客户ID
user_id                是                  用户ID                                                    
```

访问示例:
 
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/customer      #查询-单个客户信息


返回结果：

``` python
{
    "code":200,
    "msg":"查询成功",
    "data":{
        "ret_data":[
            {
                "id":1,
                "username":"张炬[客户2]",       #客户名称  
                "headimgurl":"statics/imgs/setAvator.jpg",
                "expected_time":"2018-06-14",   #预计成交时间
                "expedted_pr":"80",             # 预计成交概率
                "ai_pr":"80",                   # AI 成交率
                "superior":"张聪[客户1]",       # 上级人
                "source":"扫码",                # 客户通过扫码方式来关注此用户。
                "memo_name":null,               # 客户的备注名
                "phone":"",                     #  客户的手机号
                "email":"",                     # 邮箱 
                "company":"",                   # 在职公司
                "position":"",                  # 所在职位
                "address":"",                   # 客户所在的住址 
                "birthday":"",                  # 客户的生日
                "mem":"",                       # 客户个人信息备注等  
                "tag":[                         #客户的标签
                    "在意质量",
                    "一般客户",
                    "重要客户",
                    "已婚",
                    "爱撸串",
                    "90后",
                    "爱吃串"
                ]
            }
        ],
        "data_count":1
    }
}
  
```

#### 修改或增加 客户关联的【信息表】：

请求方式：POST（HTTP）
请求示例:
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/customer/update_information/2?rand_str=4c75edb76b06a2983040980f171b83e7&timestamp=1528169127235&user_id=1


GET 请求发送数据部分：
``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
```  
POST 请求数据部分:
 
``` python
{
   'openid' : 'dgasdcdafwcxgavrasc',
   'username' : '张三丰',
   'expected_time' : '2018-06-5',
   'belonger' : 1,
   'superior' : 1,
   'source' : 1,
   'memo_name' : '太乙真人',
   'phone': '15931788974',
   'email' : '1224423@qq.com',
   'company': '合众康桥',
   'position': '开发TTT',
   'address' : '通州区xxx',
   'mem' : '我是一个兵',
   'birthday' : '2018-06-1'
   
}
```

POST参数说明：

``` python
参数        必填          说明
id          是           客户ID
source      是           客户来源
username    否           客户名【备注名】
password    否           密码
email       否           电子邮件
company     否           客户所属公司
position    否           职位
address     否           住址
birthday    否           生日
mem         否           备注
```

返回结果：   

{"code": 200, "msg": "\u6dfb\u52a0\u6210\u529f", "data": {}}
 
 
####  修改|添加 -  客戶表信息

请求方式：POST（HTTP）
请求示例:
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/customer/update_customer/1?rand_str=4c75edb76b06a2983040980f171b83e7&timestamp=1528169127235&user_id=1
 

GET 请求发送数据部分【公共参数】：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
 
```  
 
POST 请求数据部分:

``` python
{
   'tag_list' : [2,3],
   'expedted_pr' : '80%',
   'expected_time':  '2018-06-06'
}
```
   
POST参数说明：

``` python
参数            必填          说明
tag_list        否           标签tag
expedted_pr     否           成交概率
expected_time   否           成交时间

``` 

返回结果：

``` python
{"code": 200, "msg": "\u6dfb\u52a0\u6210\u529f", "data": {}}

``` 

####  删除客户：

请求方式：GET（HTTP）
请求示例:
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/customer/delete/3?rand_str=RAND_STR&timestamp=TIMESTAMP&user_id=USER_ID


GET 请求发送数据部分【公共参数】：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
```

####  查询角色：

请求方式：GET（HTTP）
请求示例:
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/role?rand_str=94e83293256bed726191ba207c53e342&timestamp=1528209075753&user_id=1

GET 请求发送数据部分：
```  python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
```

返回结果：
``` python
{
    "code":200,
    "msg":"",
    "data":{
        "ret_data":[
            {
                "id":1,
                "name":"普通用户",
                "role_id":1,
                "create_date":"2018-06-04T10:12:08.474"
            }
        ],
        "data_count":1
    }
}

```
####  增加角色：

请求方式：POST（HTTP）
请求示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/role?rand_str=94e83293256bed726191ba207c53e342&timestamp=1528209075753&user_id=1


GET 请求发送数据部分：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
```

POST参数说明:
 
``` python
参数            必填          说明
name            是            角色名称
```


####  删除角色：

请求方式：PSOT（HTTP）
请求示例：
> http://127.0.0.1:8000/zhugeleida/qiyeweixin/role/delete/3?rand_str=94e83293256bed726191ba207c53e342&timestamp=1528209075753&user_id=1

GET 请求发送数据部分：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
```


####   修改角色

请求方式：POST（HTTP）
请求示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/role/update/3?rand_str=94e83293256bed726191ba207c53e342&timestamp=1528209075753&user_id=1


GET 请求发送数据部分：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
```
 
POST 数据格式：

``` python
{
  'name': '普通用户' 
}
```

POST参数说明：

``` python
参数            必填          说明
name            是            角色名称
```

####  增加权限：
请求方式：POST（HTTP）
请求示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/role/add/0?rand_str=94e83293256bed726191ba207c53e342&timestamp=1528209075753&user_id=1


GET 请求发送数据部分：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
```

POST 数据格式

``` python
{
 'path' : /admin/zhugeleida/quanxian/1111/,
 'icon' : 'xxxxx',
 'title': '访问admin后台'
 'pid_id' : 1,
 'order_num' : 2 
}
```

POST参数说明：

``` python
参数            必填          说明
path            是            访问URL
icon            否           
title           是            父级ID
order           是            排序序号
```

 
####    删除权限条目：
请求方式：POST（HTTP）
请求示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/role/add/0?rand_str=94e83293256bed726191ba207c53e342&timestamp=1528209075753&user_id=1


GET发送数据部分：
``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
```

####  修改权限条目：
请求方式：POST（HTTP）
请求示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/role/update/3?rand_str=94e83293256bed726191ba207c53e342&timestamp=1528209075753&user_id=1

GET 请求发送数据部分：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
``` 

POST 数据格式

``` python
{
 'path' : /admin/zhugeleida/quanxian/1111/,
 'icon' : 'xxxxx',
 'title': '访问admin后台'
 'pid_id' : 1,
 'order_num' : 2 
}
``` 

POST参数说明：

``` python
参数            必填          说明
path            是            访问URL
icon            否           
title           是            父级ID
order           是            排序序号
```

####  查询公司：

请求方式：GET（HTTP）
请求示例
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/company
 

GET 请求发送数据部分【公共参数】：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
```

返回结果：
```python
{
    "code":200,
    "msg":"",
    "data":{
        "ret_data":[
            {
                "id":1,
                "name":"合众康桥",
                "company_id":1,
                "create_date":"2018-06-04T10:12:38.381"
            }
        ],
        "data_count":1
    }
}
```
 

####  增加公司：
请求方式：POST（HTTP）
请示示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/company/delete/3?rand_str=88648074e6e50180796ba8def0154ef9&timestamp=1528203315968&user_id=1

GET 请求发送数据部分【公共参数】：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
    'name' :   '合众康桥2',
}
``` 

POST 数据格式:
 
``` python
 {
    'name': '东方银谷',
 }
``` 
   
GET 参数说明：

``` python
参数            必填          说明
name            是           公司名
```

请示示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/company/add/0?rand_str=88648074e6e50180796ba8def0154ef9&timestamp=1528203315968&user_id=1
 
####   删除公司：
请求方式：POST（HTTP）
请示示例：
http://127.0.0.1:8000/zhugeleida/qiyeweixin/company/delete/3?rand_str=88648074e6e50180796ba8def0154ef9&timestamp=1528203315968&user_id=1

GET 请求发送数据部分【公共参数】：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
    'name' :   '合众康桥2',
}
```
   

####   修改公司：
请求方式：POST（HTTP）
请求示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/company/update/2?rand_str=88648074e6e50180796ba8def0154ef9&timestamp=1528203315968&user_id=1
 
GET 请求发送数据部分【公共参数】:

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
``` 

POST参数说明：

``` python
参数            必填          说明
name            是            角色名称
```

POST 数据格式：

``` python
 {
    'name': '东方银谷',
 }
```

 
POST参数说明：

``` python
参数            必填          说明
name            是           公司名

```
请求示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/company/update/2?rand_str=88648074e6e50180796ba8def0154ef9&timestamp=1528203315968&user_id=1


####  查询标签（有客户关联的标签全部显示出来）：
请求方式：GET（HTTP）
请求示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_customer?rand_str=f107cb8bdce9794748dfe01bb240cea5&timestamp=1529033091635&user_id=1


GET 发送数据部分【公共参数】：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
``` 
 

返回结果：

``` python
{
    "code":200,
    "msg":"",
    "data":{
        "ret_data":[
            {
                "id":11,
                "name":"90后",
                "tag_id":11,
                "customer_num":5,
                "customer_list":[
                    {
                        "id":1,
                        "headimgurl":"statics/imgs/setAvator.jpg",
                        "name":"张炬[客户2]"
                    },
                    {
                        "id":2,
                        "headimgurl":"statics/imgs/setAvator.jpg",
                        "name":"张聪[客户1]"
                    },
                    {
                        "id":3,
                        "headimgurl":"dfdsfas",
                        "name":"王五"
                    },
                    {
                        "id":4,
                        "headimgurl":"sfdfasd",
                        "name":"赵六"
                    },
                    {
                        "id":5,
                        "headimgurl":"fdsaf",
                        "name":"dfasdf"
                    }
                ]
            },
            {
                "id":8,
                "name":"已婚",
                "tag_id":8,
                "customer_num":4,
                "customer_list":[
                    {
                        "id":1,
                        "headimgurl":"statics/imgs/setAvator.jpg",
                        "name":"张炬[客户2]"
                    },
                    {
                        "id":2,
                        "headimgurl":"statics/imgs/setAvator.jpg",
                        "name":"张聪[客户1]"
                    },
                    {
                        "id":3,
                        "headimgurl":"dfdsfas",
                        "name":"王五"
                    },
                    {
                        "id":4,
                        "headimgurl":"sfdfasd",
                        "name":"赵六"
                    }
                ]
            },
            {
                "id":10,
                "name":"爱撸串",
                "tag_id":10,
                "customer_num":4,
                "customer_list":[
                    {
                        "id":1,
                        "headimgurl":"statics/imgs/setAvator.jpg",
                        "name":"张炬[客户2]"
                    },
                    {
                        "id":2,
                        "headimgurl":"statics/imgs/setAvator.jpg",
                        "name":"张聪[客户1]"
                    },
                    {
                        "id":3,
                        "headimgurl":"dfdsfas",
                        "name":"王五"
                    },
                    {
                        "id":4,
                        "headimgurl":"sfdfasd",
                        "name":"赵六"
                    }
                ]
            },
            {
                "id":7,
                "name":"在意质量",
                "tag_id":7,
                "customer_num":3,
                "customer_list":[
                    {
                        "id":1,
                        "headimgurl":"statics/imgs/setAvator.jpg",
                        "name":"张炬[客户2]"
                    },
                    {
                        "id":2,
                        "headimgurl":"statics/imgs/setAvator.jpg",
                        "name":"张聪[客户1]"
                    },
                    {
                        "id":4,
                        "headimgurl":"sfdfasd",
                        "name":"赵六"
                    }
                ]
            },
            {
                "id":14,
                "name":"爱吃串",
                "tag_id":14,
                "customer_num":2,
                "customer_list":[
                    {
                        "id":1,
                        "headimgurl":"statics/imgs/setAvator.jpg",
                        "name":"张炬[客户2]"
                    },
                    {
                        "id":2,
                        "headimgurl":"statics/imgs/setAvator.jpg",
                        "name":"张聪[客户1]"
                    }
                ]
            },
            {
                "id":15,
                "name":"大傻子客户",
                "tag_id":15,
                "customer_num":2,
                "customer_list":[
                    {
                        "id":2,
                        "headimgurl":"statics/imgs/setAvator.jpg",
                        "name":"张聪[客户1]"
                    },
                    {
                        "id":4,
                        "headimgurl":"sfdfasd",
                        "name":"赵六"
                    }
                ]
            },
            {
                "id":9,
                "name":"在意 服务",
                "tag_id":9,
                "customer_num":1,
                "customer_list":[
                    {
                        "id":3,
                        "headimgurl":"dfdsfas",
                        "name":"王五"
                    }
                ]
            }
        ],
        "ret_count":9
    }
}
 
```

####   查询所有标签 【分级展示】
请求方式：GET（HTTP）

请求示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_list?rand_str=c0154475f83759e5851644425c5833e0&timestamp=1529041855696&user_id=1 

GET 请求发送数据部分【公共参数】：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
```
 
返回结果:

POST 数据格式：

``` python
{
    "code":200,
    "msg":"请求成功",
    "data":{
        "ret_data":[
            {
                "tags":[
                    {
                        "id":8,
                        "name":"已婚"
                    },
                    {
                        "id":11,
                        "name":"90后"
                    }
                ],
                "name":"基本功能"
            },
            {
                "tags":[
                    {
                        "id":7,
                        "name":"在意质量"
                    },
                    {
                        "id":9,
                        "name":"在意 服务"
                    }
                ],
                "name":"关注点"
            },
            {
                "tags":[
                    {
                        "id":5,
                        "name":"一般客户"
                    },
                    {
                        "id":6,
                        "name":"重要客户"
                    }
                ],
                "name":"级别"
            },
            {
                "tags":[
                    {
                        "id":10,
                        "name":"爱撸串"
                    },
                    {
                        "id":14,
                        "name":"爱吃串"
                    },
                    {
                        "id":15,
                        "name":"大傻子客户"
                    }
                ],
                "name":"自定义"
            }
        ],
        "tag_count":4
    }
}
```
   
 POST参数说明：

``` python
参数            必填          说明
name            是            标签名
customer_list   是           【客户id1，客户id2】
```



####   添加标签 (并绑定对应的客户)
请求方式：POST（HTTP）

请求示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_customer/add/0?rand_str=a8a0d211d38f9dad59dae633629463e5&timestamp=1528206224801&user_id=1

GET 请求发送数据部分【公共参数】：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
```
 
POST 数据格式：

``` python
 {
	'name' : '客户不好惹',
	'customer_list':  '[2,3]'
 }
```
   
 POST参数说明：

``` python
参数            必填          说明
name            是            标签名
customer_list   是           【客户id1，客户id2】
```



####   添加标签 （同时绑定此标签到此客户）
请求方式：POST（HTTP）

请求示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_list/add_tag/2?rand_str=a8a0d211d38f9dad59dae633629463e5&timestamp=1528206224801&user_id=1
GET 请求发送数据部分【公共参数】：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
``` 

URL 说明：
``` python
参数：       必填        说明
{{o_id}}     是         /zhugeleida/qiyeweixin/tag_list/add_tag/{{ o_id }}   o_id 代表 customer_id 

```

POST 数据格式：

``` python
 {
	'name' : '大傻子型客户',
 }
```
   
 POST参数说明：

``` python
参数            必填          说明
name            是            标签名
```





####   为客户绑定标签
请求方式：POST（HTTP）

请求示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_list/customer_tag/2?rand_str=a8a0d211d38f9dad59dae633629463e5&timestamp=1528206224801&user_id=1
GET 请求发送数据部分【公共参数】：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
``` 

POST 数据格式：

``` python
 {
     'tag_list' : [1,2]
 }
```    


POST参数说明：

``` python
参数            必填          说明
name            是            标签名
tag_list        否           【标签id1，标签id2】
```

URL参数说明：

``` python
参数：       必填        说明
{{o_id}}     是         /zhugeleida/qiyeweixin/tag_list/customer_tag/{{ o_id }}   o_id 代表 customer_id 

```




####   分页获取 - 消息联系人
请求方式：GET（HTTP）
请求示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/contact?rand_str=267880efc9fc674d7f088c19c4d0bab2&timestamp=1528870581400&user_id=1

GET 请求发送数据部分【公共参数】：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
}
``` 

GET 参数说明：

``` python
参数说明         必填        参数说明:
current_page     否          当前页数
length           否          每页长度20页
``` 


返回结果:


``` python

{
    "code":200,
    "msg":"",
    "data":{
        "ret_data":[
            {
                "customer_id":1,
                "src":"http://api.zhugeyingxiao.com/statics/imgs/setAvator.jpg",
                "name":"张炬[客户2]",
                "dateTime":"11:49",
                "msg":"近年来，中俄两国领导人每年都会会晤多次，今年也不例外。报道称，普京在参加完上合峰会后，还会陆续出席金砖四国峰会和亚太经合组织峰会(APEC) 峰会。"
            },
            {
                "customer_id":2,
                "src":"http://api.zhugeyingxiao.com/statics/imgs/setAvator.jpg",
                "name":"张聪[客户1]",
                "dateTime":"11:48",
                "msg":"，俄总统普京将在上海合作组织成员国元首理事会青岛峰会（上合峰会）前夕对中国进行国事访问。这一消息已经得到了克里姆林宫的证实。"
            }
        ],
        "data_count":2
    }
}
```
####   分页获取 - 所有的聊天信息记录

请求方式：GET（HTTP）
请求示例：

>http://127.0.0.1:8000//zhugeleida/qiyeweixin/chat?rand_str=53444e4ca12d03176c9b6109c0c557b0&timestamp=1528871213546&user_id=1&customer_id=1

GET 请求参数部分：

``` python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 2,   
    'customer_id': 1,
	'current_page'：1,            
    'length'     :   20           
}

```

GET参数说明:

``` python
参数           必填          说明
user_id        是           用户的ID
customer_id    是           客户的ID
current_page   否           当前页数
length         否           每页长度
current_page   否           当前页数
length'        否           每页长度(每页长度为20页)
```

返回结果：

```  python
{
    "code":200,
    "msg":"分页获取聊天消息成功",
    "data":[
        {
            "customer_id":1,
            "user_id":1,
            "src":"http://api.zhugeyingxiao.com/statics/imgs/setAvator.jpg",
            "name":"张炬[客户2]",
            "dateTime":"2018-06-13T11:49:57.000",
            "msg":"近年来，中俄两国领导人每年都会会晤多次，今年也不例外。报道称，普京在参加完上合峰会后，还会陆续出席金砖四国峰会和亚太经合组织峰会(APEC) 峰会。",
            "send_type":2
        },
        {
            "customer_id":1,
            "user_id":1,
            "src":"http://api.zhugeyingxiao.com/statics/imgs/setAvator.jpg",
            "name":"张炬[客户2]",
            "dateTime":"2018-06-13T11:44:32.456",
            "msg":"据中国日报网报道，在记者会上，特朗普再次对朝鲜领导人金正恩表示感谢",
            "send_type":1
        }
    ]
}
``` 



####  实时聊天  -  发送消息接口

请求方式：POST（HTTP）

请求示例

>http://127.0.0.1:8000/zhugeleida/qiyeweixin/chat/send_msg/0?rand_str=7931b9ab560500e52492fbe92e1f3d6c&timestamp=1528182912675&user_id=1

 GET 请求参数部分：
```  python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 2,
}
``` 

 
POST 请求参数部分：
```  python
参数             必填        说明
customer_id      是          客户ID
user_id          是          用户ID
msg              是          消息
send_type        发送        发送类型，1代表 用户发送给客户 ,  2代表 客户发送给用户。
``` 

返回结果：
```  python
{"code": 200, "msg": "send msg successful", "data": {}}
``` 
 


####    实时聊天 - 获取最新的聊天信息

请求方式：GET（HTTP）
请求示例:

>http://127.0.0.1:8000/zhugeleida/qiyeweixin/chat/getmsg/0?rand_str=51d703e387eb75da00f32520d7964d24&timestamp=1528872527395&user_id=1&customer_id=2
 
 
GET 请求参数部分：

```  python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 2,
    'customer_id': 1
}

``` 

GET请求参数部分：

```  python
参数            必填         说明
customer_id     是           客户ID
user_id         是           用户ID
``` 

 返回结果：

```  python
{
    "code":200,
    "msg":"实时获取-最新聊天记录成功",
    "data":[
        {
            "customer_id":2,
            "user_id":1,
            "src":"http://api.zhugeyingxiao.com/statics/imgs/setAvator.jpg",
            "name":"张聪[客户1]",
            "dateTime":"2018-06-13T11:48:25.456",
            "send_type":2,
            "msg":"，俄总统普京将在上海合作组织成员国元首理事会青岛峰会（上合峰会）前夕对中国进行国事访问。这一消息已经得到了克里姆林宫的证实。"
        },
        {
            "customer_id":2,
            "user_id":1,
            "src":"http://api.zhugeyingxiao.com/statics/imgs/setAvator.jpg",
            "name":"张聪[客户1]",
            "dateTime":"2018-06-13T11:45:40.456",
            "send_type":1,
            "msg":"武汉大四学生坠楼的最新相关信息"
        }
    ]
}
``` 

#### 企业微信登录认证
请求方式：GET（HTTP）
请求示例：
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/work_weixin_auth/{{company_id}}?code={{code}}&user_type=1&source=2
 

GET 请求参数部分：
```  python
{
    'code':  'pm4Mp2zwTb0GOxcJ3hhYETNaWhPWF5lDwDZ_mHWHOqQ', 
    'user_type': 1
}
``` 
GET请求参数部分：
```  python
参数            必填         说明
code            是           微信访问带的code
company_id      是           企业的company_id
user_type       是           客户访问类型     1,微信公众号  2,微信小程序
source          是           客户的来源       1,扫码  2,转发
 
```


#### 小程序登录认证
请求方式：GET（HTTP）
请求示例：
>http://127.0.0.1:8000/zhugeleida/xiaochengxu/login?code='pm4Mp2zwTb0GOxcJ3hhYETNaWhPWF5lDwDZ_mHWHOqQ'&user_type=2&source=1     #

GET 请求参数部分：
```  python
{
    'code':  'pm4Mp2zwTb0GOxcJ3hhYETNaWhPWF5lDwDZ_mHWHOqQ', 
    'user_type': 2,
    'source' :   1,
}
```
GET请求参数部分：
```  python
参数            必填             说明
code            是              微信小程序访问带的code
user_type       是              客户访问类型 1,微信公众号  2,微信小程序
source          是              客户的来源   1,扫码  2,转发
```



####  【 企业微信-雷达】 按时间展示访问日志
请求方式：GET（HTTP）
访问示例
>http://127.0.0.1:8000//zhugeleida/qiyeweixin/action/time?user_id=1 & timestamp=1528620512844&rand_str=d968b0af1cc345943d6adf8a3a6d3e0a&length=5&current_page=1

GET 请求参数部分【公共参数】
```  python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
    'id' : 1,
	'action' : 1, 
	'create_date__gte' : 2018-06-07,
	'create_date__lt' :  2018-06-14,
}
```

GET 参数说明:
```  python
参数        		 必填         	   说明
	action       	 否          (1, '查看名片'),  # 查看了名片第XXX次。
									 (2, '查看产品'),  # 查看您的产品; 查看竞价排名; 转发了竞价排名。
									 (3, '查看动态'),  # 查看了公司的动态。 评论了您的企业动态。
									 (4, '查看官网'),  # 查看了您的官网 , 转发了您官网。

									 (5,  '复制微信'),
									 (6,  '转发名片'),  #
									 (7,  '咨询产品'),   
									 (8,  '保存电话'),
									 (9,  '觉得靠谱'),  #取消了对您的靠谱
									 (10, '拨打电话'),
									 (11, '播放语音'),
									 (12, '复制邮箱'),
				
create_date__gte     否             开始时间
create_date__lt      否		        技术时间
			
```


返回结果：
```  python
{
    "code":200,
    "msg":"查询日志记录成功",
    "data":{
        "ret_data":[
            {
                "user_id":1,
                "customer_id":2,
                "headimgurl":"statics/imgs/setAvator.jpg",
                "log":"张聪觉得靠谱",
                "create_date":"2018-06-19T10:03:29"
            },
            {
                "user_id":1,
                "customer_id":2,
                "headimgurl":"statics/imgs/setAvator.jpg",
                "log":"张聪访问了产品",
                "create_date":"2018-06-09T14:01:34"
            },
            {
                "user_id":1,
                "customer_id":2,
                "headimgurl":"statics/imgs/setAvator.jpg",
                "log":"张聪访问您的产品",
                "create_date":"2018-06-09T10:03:29"
            },
            {
                "user_id":1,
                "customer_id":1,
                "headimgurl":"statics/imgs/setAvator.jpg",
                "log":"张炬又一次访问了您的名片，他娘的。",
                "create_date":"2018-06-09T10:02:12"
            },
            {
                "user_id":1,
                "customer_id":2,
                "headimgurl":"statics/imgs/setAvator.jpg",
                "log":"张聪访问了产品",
                "create_date":"2018-06-09T10:01:34"
            }
        ],
        "data_count":36
    }
}
```

####  【企业微信雷达】 按人头展示访问日志

请求方式：GET（HTTP）
访问示例
>http://127.0.0.1:8000//zhugeleida/qiyeweixin/action/customer?rand_str=4b417a2c445095431b9699db4cb4f13b&timestamp=1528617092808&user_id=1&customer_id=1

GET 请求参数部分【公共参数】
```  python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
    'id' : 1,
	'create_date__gte' : 2018-06-07,
	'create_date__lt' :  2018-06-14,
}


```
GET 参数说明:
```  python
参数        		 必填         	   说明
create_date__gte     否             开始时间
create_date__lt      否		        技术时间
			
```


返回结果：
```  python
{
    "code":200,
    "msg":"查询日志记录成功",
    "data":[
        {
            "totalCount":5,
            "customer_id":1,
            "customer__username":"张炬[客户2]",
            "user_id":"1",
            "headimgurl":"statics/imgs/setAvator.jpg",
            "detail":{
                "1":{
                    "count":3,
                    "name":"查看名片"
                },
                "2":{
                    "count":1,
                    "name":"查看产品"
                },
                "3":{
                    "count":1,
                    "name":"查看动态"
                }
            }
        },
        {
            "totalCount":6,
            "customer_id":2,
            "customer__username":"张聪[客户1]",
            "user_id":"1",
            "headimgurl":"statics/imgs/setAvator.jpg",
            "detail":{
                "2":{
                    "count":3,
                    "name":"查看产品"
                },
                "3":{
                    "count":3,
                    "name":"查看动态"
                }
            }
        }
    ]
}
```




####  【企业微信-雷达】按行为统计
请求方式：GET（HTTP）
访问示例
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/action/count?rand_str=9bccf5e05cc92f994f26250c25ae2336&timestamp=1528617397112&user_id=1&customer_id=1r_id=1&customer_id=1

GET 请求参数部分【公共参数】
```  python
{
    'rand_str': account.str_encrypt(timestamp + token),
    'timestamp': timestamp,
    'user_id': 1,
    'id' : 1,
	'create_date__gte' : 2018-06-07,
	'create_date__lt' :  2018-06-14,
}
```


```
GET 参数说明:
```  python
参数        		 必填         	   说明
create_date__gte     否             开始时间
create_date__lt      否		        技术时间
			
```



返回结果：

```  python
{
    "code":200,
    "msg":"查询日志记录成功",
    "data":[
        {
            "action":{
                "1":"查看名片",
                "2":"查看产品",
                "3":"查看动态",
                "4":"查看官网",
                "5":"复制微信",
                "6":"转发名片",
                "7":"咨询产品",
                "8":"保存电话",
                "9":"觉得靠谱",
                "10":"拨打电话",
                "11":"播放语音",
                "12":"复制邮箱"
            },
            "detail":{
                "1":1,
                "2":1,
                "3":1,
                "4":1,
                "5":1,
                "6":1,
                "7":1,
                "8":1,
                "9":1,
                "12":1
            },
            "user_id":"1"
        }
    ]
}

```

#### 企业微信 - 通讯录信息

请求方式：GET（HTTP）
访问示例
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/tongxunlu?rand_str=9b7905e5a1887cc3809e410e3847146b&timestamp=1528783998540&user_id=1


GET 请求参数部分【公共参数】

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 1,
        'customer__source': 1,
        'order' : '  customer__expedted_pr(默认的排序) | last_follow_time | last_activity_time
      
    }
```

GET请求参数部分：
```  python
参数            必填         说明
user_id         是          用户的ID
customer__source          否          搜索方式： 1 代表扫码 2 转发
order           否          排序方式:  1、customer__expedted_pr 预计成交概率  2、last_follow_time 代表最后跟进时间   3、last_activity_time 最后活动时间     

```
返回结果
``` python
{
    "code":200,
    "msg":"查询成功",
    "data":{
        "ret_data":[
            {
                "customer_id":1,
                "customer_username":"习大大",
                "headimgurl":"statics/imgs/setAvator.jpg",
                "expected_time":"2018-06-09",
                "expedted_pr":null,
                "belonger":"zhangcong",
                "source":1,
                "last_follow_time":"昨天",
                "last_activity_time":"昨天",
                "follow_status":"昨天已跟进"
            },
            {
                "customer_id":2,
                "customer_username":"普京",
                "headimgurl":"statics/imgs/setAvator.jpg",
                "expected_time":"2018-06-28",
                "expedted_pr":null,
                "belonger":"zhangcong",
                "source":1,
                "last_follow_time":"今天",
                "last_activity_time":"今天",
                "follow_status":"今天跟进"
            }
        ],
        "data_count":2
    }
}
```


#### 分页获取-跟进常用语
请求方式：GET（HTTP）
访问示例
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/follow_language?rand_str=716d6d211c9bd69650ef1580a8264ddd&timestamp=1528795760875&user_id=1


GET 请求参数部分【公共参数】

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 1,
        'current_page': 1,
        'length':  20  		
    }
```

GET 参数说明：

``` python
参数说明         必填        参数说明:
current_page     否          当前页数
length           否          每页长度20页
``` 

返回结果:

``` python
{
    "code":200,
    "msg":"",
    "data":{
        "ret_data":[
            {
                "user_id":"1",
                "follow_language":[
                    {
                        "language_id":11,
                        "language":"呵呵呵，客户让我陪他睡，"
                    },
                    {
                        "language_id":1,
                        "language":"哈哈哈，客户是个屌丝，跟赵欣鹏一样。"
                    },
                    {
                        "language_id":10,
                        "language":"已成交客户,维护好后续关系"
                    },
                    {
                        "language_id":9,
                        "language":"已发报价,待客户反馈"
                    },
                    {
                        "language_id":8,
                        "language":"标记一下,需要给客户发送报价"
                    },
                    {
                        "language_id":7,
                        "language":"曾拜访过的客户"
                    },
                    {
                        "language_id":6,
                        "language":"见面聊过,客户有合作意向"
                    },
                    {
                        "language_id":5,
                        "language":"意向客户,需安排拜访"
                    },
                    {
                        "language_id":4,
                        "language":"计划近期安排拜访"
                    },
                    {
                        "language_id":3,
                        "language":"标记一下,客户有合作意向"
                    },
                    {
                        "language_id":2,
                        "language":"客户查看了公司产品,有合作意向"
                    }
                ]
            }
        ],
        "data_count":2
    }
}

```


####  添加-跟进常用语
请求方式：POST（HTTP）
访问示例
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/follow_language/add/0?rand_str=716d6d211c9bd69650ef1580a8264ddd&timestamp=1528795760875&user_id=1

GET 请求参数【公共参数】

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 1,      
    }
```
POST 请求参数:
``` python
    {
        'custom_language': "这个客户可能是个Gay",      
    }
```

POST 请求参数说明:
```  python
参数                   必填         说明
custom_language       是           自定义常用语     
```

返回结果:
``` python
{"code": 200, "msg": "\u5220\u9664\u6210\u529f", "data": {}}

```

#### 删除 - 跟进常用语
请求方式：POST（HTTP）
访问示例
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/follow_language/delete/12?rand_str=716d6d211c9bd69650ef1580a8264ddd&timestamp=1528795760875&user_id=1

GET 请求参数【公共参数】

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 1,      
    }
```

返回结果:
``` python
{"code": 200, "msg": "\u5220\u9664\u6210\u529f", "data": {}}
```


####  获取用户【跟进客户】消息记录

请求方式：GET（HTTP）
访问示例
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/follow_info?/zhugeleida/qiyeweixin/follow_info?rand_str=a9d35cb5e7fcd82f2dfc15f9f24c245b&timestamp=1528858666902&user_id=1&customer_id=1

GET 请求参数【公共参数】

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 1,
        'customer_id' :1      
    }
```



返回结果:

``` python
{
    "code":200,
    "msg":"",
    "data":{
        "ret_data":[
            {
                "user_customer_flowup__customer__headimgurl":"statics/imgs/setAvator.jpg",
                "user_customer_flowup__user__avatar":"statics/imgs/setAvator.jpg",
                "user_customer_flowup__user__username":"zhangcong",
                "follow_info":"这个客户我惹不起！！！！",
                "create_date":"2018-06-12T21:52:31.456"
            },
            {
                "user_customer_flowup__customer__headimgurl":"statics/imgs/setAvator.jpg",
                "user_customer_flowup__user__avatar":"statics/imgs/setAvator.jpg",
                "user_customer_flowup__user__username":"zhangcong",
                "follow_info":"客户想睡我！！！！",
                "create_date":"2018-06-12T21:52:31.456"
            },
            {
                "user_customer_flowup__customer__headimgurl":"statics/imgs/setAvator.jpg",
                "user_customer_flowup__user__avatar":"statics/imgs/setAvator.jpg",
                "user_customer_flowup__user__username":"zhangcong",
                "follow_info":"更新预计成交日期: 2018-06-14",
                "create_date":"2018-06-13T10:12:00.416"
            },
            {
                "user_customer_flowup__customer__headimgurl":"statics/imgs/setAvator.jpg",
                "user_customer_flowup__user__avatar":"statics/imgs/setAvator.jpg",
                "user_customer_flowup__user__username":"zhangcong",
                "follow_info":"更新预计成交率为: 80%",
                "create_date":"2018-06-13T10:24:50.491"
            }
        ],
        "data_count":7
    }
}

```


####    修改-客户预计成交时间

请求方式：POST（HTTP）
访问示例
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/customer/update_expected_time/1?rand_str=a9d35cb5e7fcd82f2dfc15f9f24c245b&timestamp=1528858666902&user_id=1

GET 请求参数【公共参数】

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 1,
       
    }
```
POST 请求参数说明:
``` python
    {
        'expected_time': '2018-06-14',
    }
```

URL 参数说明:

``` python
参数：      必填      说明
o_id       是      /zhugeleida/qiyeweixin/customer/update_expected_time/{{ o_id}} o_id 操作的是 customer_id
```


####    修改-客户预计成交日期

请求方式：POST（HTTP）
访问示例
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/customer/update_expected_pr/1?rand_str=a9d35cb5e7fcd82f2dfc15f9f24c245b&timestamp=1528858666902&user_id=1

GET 请求参数【公共参数】

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 1,
       
    }
```

POST 请求参数说明:
``` python
    {
        'update_expected_pr': '80%',
    }
```



URL参数说明:

``` python
参数：      必填      说明
o_id       是      /zhugeleida/qiyeweixin/customer/update_expected_pr/{{ o_id}} o_id 指的的是 customer_id
```


####    修改-客户tag 标签

请求方式：POST（HTTP）
访问示例
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/customer/update_expected_pr/1?rand_str=a9d35cb5e7fcd82f2dfc15f9f24c245b&timestamp=1528858666902&user_id=1

GET 请求参数【公共参数】

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 1,
       
    }
```

POST 请求参数说明:

``` python
    {
        'tag_list':   '[1,2]',
    }
```


URL参数说明:

``` python
参数：      必填      说明
o_id       是      /zhugeleida/qiyeweixin/customer/update_expected_pr/{{ o_id}} o_id 操作的是 customer_id
```



####    【小程序- 显示单个用户的信息 并记录【访问名片】日志信息】


请求方式：GET（HTTP）
访问示例:

>http://127.0.0.1:8000/zhugeleida/xiaochengxu/mingpian?rand_str=cae406b10a53dac573369b0eb5200ff0&timestamp=1529499334685&user_id=1&uid=2&action=1


GET 请求参数【公共参数】

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 1,
		'uid' :  2
		'action' : 1 
       
    }
```

GET参数说明:

``` python
参数：      必填      参数说明
uid          是       所属用户的ID
user_id      是       小程序客户端的客户ID      
action       是       action 等于 1 时，代表查看名片功能。

```

返回结果：

``` python
	{
		"code":200,
		"msg":"查询成功",
		"data":{
			"ret_data":[
				{
					"id":2,
					"username":"zhangju",            #用户名
					"avatar":"statics/imgs/setAvator.jpg",  #头像
					"company":"合众康桥",            #公司名称
					"address":"1",                   #公司地址 
					"position":"技术经理",           #职位
					"email":"",                      #邮箱
					"wechat":"",                     #微信号  
					"mingpian_phone":"18511123918",  # 名片上显示的手机号
					"create_date":"2018-06-08T22:03:23.772",
					"popularity":12,                 # 产看多少次
					"praise":1,                      # 点赞多少次
					"forward":2                      # 转发多少次 
					"is_up_down": false              #是否点赞了
					"sign": '我是你爸爸'                      # 签名
					"photo":[
						[
							1,
							"xxxxx"
						],
						[
							4,
							"statics/zhugeleida/imgs/xiaochengxu/qr_code/4_uemthqpcdn_photo.jpg"
						],
						[
							5,
							"statics/zhugeleida/imgs/xiaochengxu/qr_code/5_uemthqpcdn_photo.jpg"
						]
                    ],
				}
			],
			"data_count":1
		}
	}
```

####    【小程序 - 显示所有的用户】

请求方式：GET（HTTP）
访问示例:
>http://127.0.0.1:8000/zhugeleida/xiaochengxu/mingpian/all?rand_str=e77523b1c848768f040deb530b04bd57&timestamp=1529540109759&user_id=2

GET 请求参数
``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 1,
    }
```

GET参数必要说明:

``` python
参数：      必填      参数说明
user_id      是       小程序客户端的客户ID      

```
返回结果：

``` python
{
    "code":200,
    "msg":"查询成功",
    "data":{
        "ret_data":[
            {
                "id":2,
                "username":"zhangju",
                "source":"扫码",
                "avatar":"statics/imgs/setAvator.jpg",
                "company":"合众康桥",
                "position":"技术经理",
                "email":"",
                "mingpian_phone":"18511123918",
                "create_date":"2018-06-08T22:03:23.772"
            },
            {
                "id":1,
                "username":"zhangcong",
                "source":"扫码",
                "avatar":"statics/imgs/setAvator.jpg",
                "company":"合众康桥",
                "position":"技术经理",
                "email":"",
                "mingpian_phone":"18511125018",
                "create_date":"2018-06-07T19:47:43"
            }
        ],
        "data_count":2
    }
}

```

####    【小程序 - 记录日志拨打手机动作】

请求方式：GET（HTTP）
访问示例:
>http://127.0.0.1:8000/zhugeleida/xiaochengxu/mingpian/calling?rand_str=b1c3f902e8d15a5e617328d35abc630a&timestamp=1529542925528&user_id=2&uid=2&action=10

GET 请求参数

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 1,
		'uid' : 2,
		'action': 10
    }
```


GET参数必要说明:

``` python
参数：      必填      参数说明
user_id      是       小程序客户端的客户ID      
uid          是       所属用户ID
action       是       10 代表访问名片的动作。

```

返回结果：
``` python
	{
		"code":200,
		"msg":"记录日志成功",
		"data":{

		}
	}
```


####    【小程序 - 记录点赞或者取消点赞 你名片的动作】

请求方式：GET（HTTP）
访问示例:
>http://127.0.0.1:8000/zhugeleida/xiaochengxu/mingpian/praise?rand_str=b587cab28de63a05cdec5e789e6f2b54&timestamp=1529543973411&user_id=2&uid=2&action=9

GET 请求参数

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 1,
		'uid' : 2,
		'action': 9
    }
```


GET参数必要说明:

``` python
参数：      必填      参数说明
user_id      是       小程序客户端的客户ID      
uid          是       所属用户ID
action       是       9 代表 点赞名片的动作。

```

返回结果 ：

``` python
	{
		"code":200,
		"msg":"记录日志成功",
		"data":{

		}
	}
```

####    【小程序 - 记录转发用户名片的动作】

请求方式：GET（HTTP）
访问示例:
>http://127.0.0.1:8000/zhugeleida/xiaochengxu/mingpian/forward?rand_str=2db7d341300b1ab4aec9238ed8618d53&timestamp=1529544299602&user_id=2&uid=2&action=6

GET 请求参数

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 1,
		'uid' : 2,
		'action': 6
    }
```


GET参数必要说明:

``` python
参数：      必填      参数说明
user_id      是       小程序客户端的客户ID      
uid          是       所属用户ID
action       是       6 代表转发的动作。

```

返回结果 ：

``` python
	{
		"code":200,
		"msg":"记录日志成功",
		"data":{

		}
	}
```


####    【小程序 - 实时获取各个动作的最新访问日志】

请求方式：GET（HTTP）
访问示例:
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/action/get_new_log?rand_str=4b8120c4a83c83ad3a2d2a4d91887f19&timestamp=1529545515255&user_id=2&action=6 【获取用户ID为2的最新动作日志消息】

GET 请求参数

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 1,
		
    }
```


GET参数必要说明:

``` python
参数：      必填      参数说明
user_id      是       企业微信-用户ID      

```

返回结果 ：

``` python
{
    "code":200,
    "msg":"查询日志记录成功",
    "data":{
        "ret_data":[
            {
                "user_id":2,
                "customer_id":2,
                "action":"转发名片",
                "log":"张聪[客户1]转发了你的名片,你的人脉圈正在裂变",
                "create_date":"2018-06-21T09:24:59.613"
            },
            {
                "user_id":2,
                "customer_id":2,
                "action":"拨打电话",
                "log":"张聪[客户1]拨打您的手机",
                "create_date":"2018-06-21T08:55:35.570"
            },
            {
                "user_id":2,
                "customer_id":1,
                "action":"觉得靠谱",
                "log":"张炬[客户2]取消对你的靠谱评价",
                "create_date":"2018-06-20T13:34:51.858"
            },
            {
                "user_id":2,
                "customer_id":1,
                "action":"查看名片",
                "log":"张炬[客户2]查看你的名片",
                "create_date":"2018-06-20T13:05:11.081"
            }
        ],
        "data_count":4
    }
}
```


####    【小程序 - 生成小程序的二维码（放在小程序名片）】


请求方式：GET（HTTP）
访问示例:
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/qr_code_auth?rand_str=245416a1d0f21129e8e028afaadb592a&timestamp=1529551521953&user_id=2 【获取用户ID为2的最新动作日志消息】


GET 请求参数

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 2,   # 企业微信的用户ID
		
    }
```


GET参数必要说明:

``` python
参数：      必填      参数说明
user_id      是       企业微信-用户ID      

```

返回结果 ：

``` python
	{
		"code":200,
		"msg":"生成小程序二维码成功",
		"data":{

		}
	}
```



####    【小程序 - 查询名片里的用户标签】


请求方式：GET（HTTP）
访问示例:
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_user?rand_str=a932b4ac5620edafa2822755a93974bc&timestamp=1529565105630&user_id=2 【获取用户ID为2的最新动作日志消息】


GET 请求参数

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 2,   # 企业微信的用户ID
		
    }
```


GET参数必要说明:

``` python
参数：      必填      参数说明
user_id      是       企业微信-用户ID      

```

返回结果 ：

``` python
	{
		"code":200,
		"msg":"",
		"data":{
			"user_id":"2",
			"ret_data":[
				{
					"id":1,
					"name":"有志青年"
				},
				{
					"id":2,
					"name":"靠谱人士"
				}
			],
			"data_count":2
		}
	}
```


####    【小程序 - 名片里-新增用户标签】


请求方式：POST（HTTP）
访问示例:
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_user/add?rand_str=5b199e75f45bcc94c0c4e46e20c0efdb&timestamp=1529569831934&user_id=2 


GET 请求参数

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 2,   # 企业微信的用户ID
		
    }
```


GET参数必要说明:

``` python
参数：      必填      参数说明
user_id      是       企业微信-用户ID      

```

POST 请求参数

``` python
    {
     "name" : "积极少年"
		
    }
```

POST参数必要说明:

``` python
参数：      必填      参数说明
name        是        标签名      

```

返回结果 ：

``` python
	{
		"code":200,
		"msg":"添加成功",
		"data":[
			{
				"id":3,
				"name":"积极少年"
			}
		]
	}
```

####    【小程序 - 名片里-保存所有的用户标签】


请求方式：POST（HTTP）
访问示例:
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_user/save?rand_str=5b199e75f45bcc94c0c4e46e20c0efdb&timestamp=1529569831934&user_id=2 


GET 请求参数

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 2,   # 企业微信的用户ID
		
    }
```


GET参数必要说明:

``` python
参数：      必填      参数说明
user_id      是       企业微信-用户ID      

```

POST 请求参数

``` python
    {
     "tag_list" : '[1,2,3]'
		
    }
```

POST参数必要说明:

``` python
参数：          必填      参数说明
tag_list        是        [标签id,标签id2,标签id3....]      

```

返回结果 ：

``` python
	{
		"code":200,
		"msg":"添加成功",
		"data":[
			
		]
	}
```

####    【小程序 - 名片里-删除用户标签】


请求方式：POST（HTTP）
访问示例:
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_user/delete?rand_str=5b199e75f45bcc94c0c4e46e20c0efdb&timestamp=1529569831934&user_id=2 


GET 请求参数

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 2,   # 企业微信的用户ID
		
    }
```


GET参数必要说明:

``` python
参数：      必填      参数说明
user_id      是       企业微信-用户ID      

```

POST 请求参数

``` python
    {
     "id" : 3
		
    }
```

POST参数必要说明:

``` python
参数：      必填      参数说明
id          是        标签id    

```

返回结果 ：

``` python
	{
		"code":200,
		"msg":"删除成功",
		"data":{

		}
	}
```



####    【小程序 - 名片里-修改并保存手机号】


请求方式：POST（HTTP）
访问示例:
>http://127.0.0.1:8000/zhugeleida/qiyeweixin/tag_user/save_phone?rand_str=5b199e75f45bcc94c0c4e46e20c0efdb&timestamp=1529569831934&user_id=2 


GET 请求参数

``` python
    {
        'rand_str': account.str_encrypt(timestamp + token),
        'timestamp': timestamp,
        'user_id': 2,   # 企业微信的用户ID
		
    }
```


GET参数必要说明:

``` python
参数：      必填      参数说明
user_id      是       企业微信-用户ID      

```

POST 请求参数

``` python
    {
     "id" : 3
		
    }
```

POST参数必要说明:

``` python
参数：      必填      参数说明
id          是        标签id    

```

返回结果 ：

``` python
	{
		"code":200,
		"msg":"删除成功",
		"data":{

		}
	}
```

