# django-jsondatavalidator
An easy and elegant json data validator which generate well-formatted error response for you.

This repository is just a django project which is meant to show you how to use the jsondatavalidator.

Feel free to copy or tweak the code as you need, just don't forget to add reference to this repository.

## example view
An django example view to show you how to use JsonDataValidator.

Pay extra attention to the comment in the code block.
```python
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
	# Write your logic here without any concern.
        return HttpResponse('success')

```
## Response is well formatted and nested if the validation failed.
Recall the json_schema we defined in the example view:

``` python 
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
```
## examples
``` json
Request Body
{	
	"order": {
        "products": [
            {
                "product_id": 1,
                "quantity": 1
            }, 
            {
                "product_id": 2,
                "quantity": 3
            }
        ],
        "email": "wang@example.com", 
        "contact_information": {
            "first_name": "王",
            "last_name": "大明",
            "title": "先生",
            "address": "台北市的王大明家",
            "phone": "12345"
        }
    }
}
```
```json
Response Body
{
    "errors": {
        "order": {
            "contact_information": {
                "phone": "length of phone number must be 10."
            }
        }
    }
}
```
---
``` json
Request Body
{	
	"order": {
        "products": [
            {
                "product_id": 1,
                "quantity": 1
            }, 
            {
                "product_id": "the_fancy_product",
                "quantity": 3
            }
        ],
        "email": "wang@example.com", 
        "contact_information": {
            "first_name": "王",
            "last_name": "大明",
            "title": "先生",
            "address": "台北市的王大明家",
            "phone": "1234567890"
        }
    }
}
```
```json
Response Body
{
    "errors": {
        "order": {
            "products": {
                "product_id": "integer is required."
            }
        }
    }
}
```
---
``` json
Request Body
{	
    "order": 123
}
```
```json
Response Body
The order should be an object, so that syntax error is raised.
{
    "errors": {
        "order": "syntax error."
    }
}
```
---
``` json
Request Body
{	
	"order": {
        "products": [
            {
                "product_id": 1,
                "quantity": 1
            }, 
            {
                "product_id": 2,
                "quantity": 3
            }
        ],
        "email": "wang@example.com"
    }
}
```
```json
Response Body
Right now, every property in json_schema is required.
{
    "errors": {
        "order": "contact_information is required"
    }
}
```
---
``` json
Request Body
{	
	"order": {
        "products": [
            {
                "product_id": 1,
                "quantity": 1
            }, 
            {
                "product_id": 2,
                "quantity": 3
            }
        ],
        "email": "wang@example.com", 
        "contact_information": {
            "first_name": "王",
            "last_name": "大明",
            "title": "先生",
            "address": "台北市的王大明家",
            "phone": "1234567890"
        }, 
        "abcde": 123
    }
}
```
```json
Response Body
{
    "errors": {
        "order": "abcde is not valid property name."
    }
}
```
## Define your custom type
It's easy to add your custom json property type with your custom validation method.

Just add it to JsonPropertyType.

Example:
```python
class JsonPropertyType:
    ...
    # add your custom type in class attribute
    TYPE_MY_CUSTOM_TYPE = "my_custom_type"
    
    # add your custom validation function in class method
    # note that the validate method name must be "_validate_{}".format(your_custom_type_name)
    @staticmethod
    def _validate_my_custom_type(data):
        if data != "I love python":
            return ValidateResult(False, "You dont know python.")
        else:
            return ValidateResult(True)
```

## You're ready to go

Star if you like :)
