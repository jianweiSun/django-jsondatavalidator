# -*- coding: utf-8 -*-

import json
from functools import wraps
from django.http import JsonResponse


def request_body_json_required(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        try:
            json.loads(request.body)
        except ValueError:
            return JsonResponse({'errors': 'Invalid json format.'}, status=400)
        else:
            return f(request, *args, **kwargs)
    return wrapper
