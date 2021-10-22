# -*- coding: utf-8 -*-
from django.http import JsonResponse
from rest_framework.views import exception_handler


def custom_error(exc, context):
    error = exception_handler(exc, context)
    if error:
        error = error.data
    else:
        error = exc.args
    return JsonResponse({"result": False, "message": error})
