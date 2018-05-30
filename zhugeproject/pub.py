
# 装饰器 判断是否登录
from django.shortcuts import redirect

def is_login(func):
    def inner(request, *args, **kwargs):
        # return redirect("/statics/err_page/wzwhz.html")
        is_login = request.session.get("is_login", False)  # 从session中获取用户的username对应的值
        if not is_login:
            return redirect("/zhugeproject/login/")
        return func(request, *args, **kwargs)
    return inner