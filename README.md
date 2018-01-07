# django-jsondatavalidator
An easy and elegant json data validator.

This project is just a django project which is meant to show you how to use the jsondatavalidator.

## example view
An django example view to show you how to use JsonDataValidator.

Pay extra attention to the comment in the code block.
```
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

```
## request and response example if the validation failed

request
``` javascript

```
