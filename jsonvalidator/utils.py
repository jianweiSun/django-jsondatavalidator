# -*- coding: utf-8 -*-

import re

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse


class ValidateResult:
    """
    Encapsulate is_valid, and message.
    Message is generally used in the case which is_valid=False.
    """
    def __init__(self, is_valid, message=""):
        self.is_valid = is_valid
        self.message = message

    def __bool__(self):
        return self.is_valid


class JsonPropertyType:
    """
    JsonPropertyType refer to low level data structure in JSON, which means not dict and list ( refer to
    Javascript object and array).
    """
    # JSON format allow type
    # refer to https://www.w3schools.com/js/js_json_datatypes.asp
    TYPE_STRING = "string"
    TYPE_NUMBER = "number"
    TYPE_BOOLEAN = "boolean"

    # custom validator
    TYPE_INTEGER = "integer"
    TYPE_POSITIVE_INTEGER = "positive_integer"
    TYPE_EMAIL = "email"
    TYPE_PHONE = "phone"
    TYPE_ZIP = "zip"
    TYPE_TITLE = "title"
    TYPE_ORDER_NAME = "order_name"

    def __init__(self, type_string):
        if type_string not in {JsonPropertyType.TYPE_STRING, JsonPropertyType.TYPE_NUMBER,
                               JsonPropertyType.TYPE_BOOLEAN, JsonPropertyType.TYPE_INTEGER,
                               JsonPropertyType.TYPE_POSITIVE_INTEGER, JsonPropertyType.TYPE_EMAIL,
                               JsonPropertyType.TYPE_PHONE, JsonPropertyType.TYPE_ZIP,
                               JsonPropertyType.TYPE_TITLE, JsonPropertyType.TYPE_ORDER_NAME}:
            raise Exception("type:{} is not supported".format(type_string))
        else:
            self.type_string = type_string

    def validate(self, data_to_validate):
        validate_function = getattr(self, '_validate_{}'.format(self.type_string))
        return validate_function(data_to_validate)

    @staticmethod
    def _validate_string(data):
        # IMPORTANT: use unicode, because json.loads will turn json string to python unicode
        if not isinstance(data, str):
            return ValidateResult(False, "string is required.")
        else:
            return ValidateResult(True)

    @staticmethod
    def _validate_number(data):
        if not (isinstance(data, int) or isinstance(data, float)):
            return ValidateResult(False, "number is required.")
        else:
            return ValidateResult(True)

    @staticmethod
    def _validate_boolean(data):
        if not isinstance(data, bool):
            return ValidateResult(False, "boolean is required.")
        else:
            return ValidateResult(True)

    @staticmethod
    def _validate_integer(data):
        if not isinstance(data, int):
            return ValidateResult(False, "integer is required.")
        else:
            return ValidateResult(True)

    @classmethod
    def _validate_positive_integer(cls, data):
        integer_validate_result = cls._validate_integer(data)
        if not integer_validate_result:
            return integer_validate_result
        else:
            if not data > 0:
                return ValidateResult(False, "positive integer is required.")
            else:
                return ValidateResult(True)

    @classmethod
    def _validate_email(cls, data):
        string_validate_result = cls._validate_string(data)
        if not string_validate_result:
            return string_validate_result
        else:
            try:
                validate_email(data)
            except ValidationError:
                return ValidateResult(False, "email is not valid.")
            else:
                return ValidateResult(True)

    @classmethod
    def _validate_phone(cls, data):
        """
        必須為 10碼 手機號碼
        """
        string_validate_result = cls._validate_string(data)
        if not string_validate_result:
            return string_validate_result
        else:
            regex = re.compile(r"[^\d]+")
            if regex.findall(data):  # strange character found
                return ValidateResult(False, "phone has strange character.")
            else:
                if len(data) != 10:
                    return ValidateResult(False, "length of phone number must be 10.")
                return ValidateResult(True)

    @classmethod
    def _validate_zip(cls, data):
        string_validate_result = cls._validate_string(data)
        if not string_validate_result:
            return string_validate_result
        else:
            regex = re.compile(r"[^\d]+")
            if regex.findall(data):
                return ValidateResult(False, "zip has strange character.")
            string_length = len(data)
            if string_length not in {3, 5}:
                return ValidateResult(False, "zip is not valid.")
            else:
                return ValidateResult(True)

    @classmethod
    def _validate_title(cls, data):
        string_validate_result = cls._validate_string(data)
        if not string_validate_result:
            return string_validate_result
        else:
            if data not in {"先生", "小姐", ""}:
                return ValidateResult(False, 'title is restricted to only "先生", "小姐" and ""(empty string).')
            else:
                return ValidateResult(True)

    @classmethod
    def _validate_order_name(cls, data):
        string_validate_result = cls._validate_string(data)
        if not string_validate_result:
            return string_validate_result
        else:
            regex = re.compile(r"^#\d+$")
            if not regex.match(data):
                return ValidateResult(False, 'order_name must start with #, then followed by numbers.')
            else:
                return ValidateResult(True)


class JsonResponseResult:
    """
    The most important property is JsonResponseResult.json_response, which return JsonResponse object.
    :param: key_path_list: which is used to build nested error message for JsonResponseResult.json_response.
            ex:
                j = JsonResponseResult(False, "invalid", ["first", "second"])
                j.json_response.content --> '{"errors": {"first": {"second": "invalid"}}}'
    """
    def __init__(self, is_valid, message="", key_path_list=None, status=400):
        self.is_valid = is_valid
        self.message = message
        self.key_path_list = key_path_list
        self.status = status

    def __bool__(self):  # __nonzero__ in python 2 is equivalent to __bool__ in python 3
        return self.is_valid

    @property
    def json_response(self):
        """
        Return JsonResponse object.
        """
        if not self.is_valid:
            if not self.key_path_list:
                return JsonResponse({"errors": self.message}, status=self.status)
            else:
                # refer to https://stackoverflow.com/questions/13238255/is-it-possible-to-turn-a-list-into-
                #          a-nested-dict-of-keys-without-recursion
                result_dict = current_dict = dict()
                key_path_length = len(self.key_path_list)
                for index, key in enumerate(self.key_path_list, 1):
                    if index < key_path_length:
                        current_dict[key] = dict()
                        current_dict = current_dict[key]
                    else:
                        current_dict[key] = self.message
                return JsonResponse({"errors": result_dict}, status=self.status)
        else:
            raise Exception('json_response is only used for invalid json_response.')


class JsonDataValidator:
    """
    Right now, you can only put dicts in list.( string/number in list is not supported )
    Also, all attributes in json_data_schema is required, which means you need to fill in all attributes in
    json_data_schema explicitly.

    NOTE: Use only one dict in list to represent the object property structures.
    json_schema = {
        "line_items": [{
            "variant_id": JsonPropertyType("integer"),
            "quantity": JsonPropertyType("integer")
        }],
        "email": JsonPropertyType("email"),
        "shipping_address": {
            "first_name": JsonPropertyType("string"),
            "last_name": JsonPropertyType("string"),
            "title": JsonPropertyType("title"),
            "zip": JsonPropertyType("zip"),
            "city": JsonPropertyType("string"),
            "address1": JsonPropertyType("string"),
            "address2": JsonPropertyType("string"),
            "phone": JsonPropertyType("phone")
        },
        "transaction_amount": JsonPropertyType("integer")
    }
    """

    def __init__(self, json_data_schema):
        self.json_data_schema = json_data_schema
        # insure the schema is valid
        self.json_data_schema_recursive_validate(self.json_data_schema)

    def validate(self, json_data):
        """
        Return True if validate successfully.
        result JsonResponseResult if validation failed.
        """
        result = self.recursive_validate(self.json_data_schema, json_data)
        if result is not None:
            return result
        else:
            return True

    @classmethod
    def json_data_schema_recursive_validate(cls, schema):
        if isinstance(schema, dict):
            for k, v in schema.items():
                assert isinstance(k, str), "dict key:{} is not string".format(k)
                cls.json_data_schema_recursive_validate(v)

        elif isinstance(schema, list):
            assert len(schema) == 1, "Please use only one dict to object schema in list."
            cls.json_data_schema_recursive_validate(schema[0])
        else:
            assert isinstance(schema, JsonPropertyType), "the lowest level value need to be JsonPropertyType"

    @classmethod
    def recursive_validate(cls, json_schema, json_data, key_path_list=None):
        """
        This function will be called recursively.
        It will only return JsonResponseResult while validation error occurred, which means
        if the json_data pass the validation, it will return None.
        """
        if not key_path_list:
            key_path_list = list()

        if isinstance(json_schema, dict):
            if not isinstance(json_data, dict):
                return JsonResponseResult(False, "syntax error.", key_path_list)
            else:
                # validate keys
                for key in json_schema.keys():
                    if key not in json_data:
                        return JsonResponseResult(False, "{} is required".format(key), key_path_list)
                for key in json_data.keys():
                    if key not in json_schema.keys():
                        return JsonResponseResult(False, "{} is not valid property name.".format(key), key_path_list)
                # if key is matched
                for key in json_schema.keys():
                    key_path_list.append(key)
                    result = cls.recursive_validate(json_schema[key], json_data[key], key_path_list)
                    if isinstance(result, JsonResponseResult) and not result:
                        return result
                    else:
                        key_path_list.remove(key)
        elif isinstance(json_schema, list):
            if not isinstance(json_data, list):
                return JsonResponseResult(False, "syntax error.", key_path_list)
            else:
                for data in json_data:
                    if not isinstance(data, dict):
                        return JsonResponseResult(False, "syntax error.", key_path_list)
                    else:
                        result = cls.recursive_validate(json_schema[0], data, key_path_list)
                        if isinstance(result, JsonResponseResult) and not result:
                            return result
        else:
            assert isinstance(json_schema, JsonPropertyType), "Must to be JsonPropertyType."
            validate_result = json_schema.validate(json_data)
            if not validate_result:
                return JsonResponseResult(False, validate_result.message, key_path_list)