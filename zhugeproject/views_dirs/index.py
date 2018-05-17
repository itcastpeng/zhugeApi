
from django.shortcuts import render, HttpResponse, redirect, HttpResponsePermanentRedirect
from django.http import JsonResponse
from bson.objectid import ObjectId
from django.views.decorators.csrf import csrf_exempt
import datetime
import random
from django.db.models import Q
from django.db.models import Count
import re
import json
from publickFunc import Response ,account
from zhugeproject import models
from django.http import HttpResponse
from zhugeproject import pub


@account.is_token(models.ProjectUserProfile)
def index(request):
    response = Response.ResponseObj()



    return HttpResponse('sduygfyszd')









