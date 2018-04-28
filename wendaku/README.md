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
参数名    是否必须    参数描述
username    是        获取用户名
password    是        获取密码

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
```
查询全部角色信息
    请求方法：GET
    请求URL:http://127.0.0.1:8000/wendaku/role?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID
    
    请求参数:
    参数名    是否必须    参数描述
    无           0           0
    
    获取参数：
    参数名    是否必须    参数描述
    id         是         角色的id 
    name       是         角色的名字
    
    返回结果：
        正确情况：
            {"data": {"role_data": [{"id": 1, "name": "\u8d85\u7ea7\u7ba1\u7406\u5458"}, {"id": 2, "name": "\u7ba1\u7406\u545811"}]}, "code": 200, "msg": ""}
            
            {
            "data": {"role_data":                                   # 所有数据
            [{"id": 1,                                              # 角色1 ID
             "name": "\u8d85\u7ea7\u7ba1\u7406\u5458"},             # 角色1 名字
             {"id": 2, "name": "\u7ba1\u7406\u545811"}]},           # 角色2 ID
             "code": 200,                                           # 角色2 名字
             "msg": ""}                                             # 提示信息
        错误情况:
            {
            "code": 400,                                            # 状态码
            "data": {},                                             # 返回数据
            "msg": "token\u5f02\u5e38"                              # 提示信息
            }


角色的增删改
    请求方法：POST
    请求URL:http://127.0.0.1:8000/wendaku/add/0?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID
    
    ID 为用户ID
    请求URL:http://127.0.0.1:8000/wendaku/delete/ID?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID  
    请求URL:http://127.0.0.1:8000/wendaku/update/ID?rand_str=RAND_STR&timestamp=TIME_STAMP&user_id=USER_ID 
    
    请求参数:
    参数名    是否必须    参数描述
    oper_type    是      请求增删改的条件
    id           是      用户的唯一id
    name         是      用户名需要更新操作
    
    获取参数：
    参数名    是否必须    参数描述
    id         是         角色的id 
    name       是         角色的名字
    
    返回结果：
        正确情况：
            增：
            {"code": 200, "data": {}, "msg": "\u6dfb\u52a0\u6210\u529f"}
                
            {
                "code": 200,                                                # 状态码  
                "data": {},                                                 # 返回数据
                "msg": "\u6dfb\u52a0\u6210\u529f"                           # 提示信息
            }
            删：
            {"code": 200, "data": {}, "msg": "\u5220\u9664\u6210\u529f"}
            
            {
                "code": 200,                                                # 状态码 
                "data": {},                                                 # 返回数据
                "msg": "\u5220\u9664\u6210\u529f"                           # 提示信息
            }
            改：
            {"code": 200, "msg": "\u4fee\u6539\u6210\u529f", "data": {}}
            
            {
                "code": 200,                                                # 状态码 
                "msg": "\u4fee\u6539\u6210\u529f",                          # 提示信息
                "data": {}                                                  # 返回数据
            }
            
        错误情况:
            增：
            {"code": 300, "data": {}, "msg": "\u89d2\u8272\u540d\u5df2\u5b58\u5728"}
            
            {
                "code": 300,                                                # 状态码 
                "data": {},                                                 # 返回数据
                "msg": "\u89d2\u8272\u540d\u5df2\u5b58\u5728"               # 提示信息
            }
            
            删：
            {"code": 302, "msg": "\u7528\u6237ID\u4e0d\u5b58\u5728", "data": {}}
            
            {
                "code": 302,                                                # 状态码
                "msg": "\u7528\u6237ID\u4e0d\u5b58\u5728",                  # 提示信息
                "data": {}                                                  # 返回数据
            }
            改：
            {"code": 302, "data": {}, "msg": "\u7528\u6237ID\u4e0d\u5b58\u5728"}
            
            {
                "code": 302,                                                # 状态码 
                "data": {},                                                 # 返回数据
                "msg": "\u7528\u6237ID\u4e0d\u5b58\u5728"                   # 提示信息
            }
```
### 用户管理
```
用户的查询展示
请求方法：GET
请求URL:http://127.0.0.1:8000/wendaku/user

请求参数:
参数名    是否必须    参数描述
无           0           0

获取参数：
参数名    是否必须    参数描述
id         是         角色的id 
name       是         角色的名字

返回结果：
    正确情况：
        状态码：   200
        data：'role_data': list(role_data)
    错误情况:
        状态码：   200
        message： 请求异常


请求方法：POST
请求URL:http://127.0.0.1:8000/wendaku/role/(num)

请求参数:
参数名    是否必须    参数描述
oper_type    是      请求增删改的条件
id           是      用户的唯一id
name         是      用户名需要更新操作

获取参数：
参数名    是否必须    参数描述
id         是         角色的id 
name       是         角色的名字

返回结果：
    正确情况：
        状态码：   200
        message：添加/删除/修改 -- 成功
    错误情况:
        状态码：   300/402
        message： 用户名已存在/请求异常
```


## api 返回值说明
```
200 正常
300 角色名已存在
301 数据类型验证失败
302 用户ID不存在
401 账号密码错误
402 请求方式异常 例如应该使用 POST 请求的使用的是 GET 请求

```
