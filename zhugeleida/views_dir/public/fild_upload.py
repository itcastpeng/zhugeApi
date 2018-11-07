from django.shortcuts import render
from django.shortcuts import HttpResponse
from publicFunc import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect

import os


@csrf_exempt
def fild_upload(request):
    response = Response.ResponseObj()
    if request.method == "POST":
        file = request.FILES.get('file')  # 所有提交的文件

        file_name = file.name
        file_save_path = os.path.join('statics', 'zhugeleida', 'fild_upload', file_name)
        with open(file_save_path, "wb") as f:
            for chunk in file.chunks():
                f.write(chunk)

        response.code = 200
        response.data = {
            'file_path': '/' + file_save_path
        }

    return JsonResponse(response.__dict__)


