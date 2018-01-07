import json

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from jsonvalidator.decorators import request_body_json_required
from jsonvalidator.utils import JsonPropertyType, JsonDataValidator


@csrf_exempt
@require_POST
@request_body_json_required
def buy_product_api(request):

    data_dict = json.loads(request.body)
    json_schema = {
        "order": {
            "products": [{
                "product_id": JsonPropertyType(JsonPropertyType.TYPE_POSITIVE_INTEGER),
                "quantity": JsonPropertyType(JsonPropertyType.TYPE_POSITIVE_INTEGER)
            }],
            "email": JsonPropertyType(JsonPropertyType.TYPE_EMAIL),
            "contact_information": {
                "first_name": JsonPropertyType(JsonPropertyType.TYPE_STRING),
                "last_name": JsonPropertyType(JsonPropertyType.TYPE_STRING),
                "title": JsonPropertyType(JsonPropertyType.TYPE_TITLE),
                "address": JsonPropertyType(JsonPropertyType.TYPE_STRING),
                "phone": JsonPropertyType(JsonPropertyType.TYPE_PHONE)
            }
        }
    }

    validate_result = JsonDataValidator(json_schema).validate(data_dict)
    if not validate_result:
        return validate_result.json_response
    else:
        # the json data is already validated
        # write whatever you want to do
        return HttpResponse('success')
