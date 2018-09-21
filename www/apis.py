import json,logging as lg,inspect,functools

class APIError(Exception):
    def __init__(self,error,data='',message=''):
        super().__init__(message)
        self.error = error
        self.data = data
        self.message = message

class APIValueReeor(APIError):
    def __init__(self,field,message=''):
        super().__init__('value:invalid',field,message)

class APIResourceNotFoundError(APIError):
    def __init__(self,field,message=''):
        super().__init__('value:notfound',field,message)

class APIPermissionError(APIError):
    def __init__(self,field,message=''):
        super().__init__('permission:forbidden','permission',message)

print(__file__)