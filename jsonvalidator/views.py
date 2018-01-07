import json

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from jsonvalidator.decorators import request_body_json_required
from jsonvalidator.utils import JsonPropertyType, JsonDataValidator


@csrf_exempt
@require_POST
@request_body_json_required
def create_order_api(request):

    data_dict = json.loads(request.body)
    # create your json_schema here
    json_schema = {
        "order": {
            # use only one dictionary in list for representation
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

    # Put your schema in to JsonDataValidator and then call validate method to get validate_result
    validate_result = JsonDataValidator(json_schema).validate(data_dict)
    if not validate_result:
        return validate_result.json_response  # generate json_response with http 400
    else:
        # The json data is already validated, you're ready to go.
        return HttpResponse('success')
