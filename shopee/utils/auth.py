from rest_framework.exceptions import APIException

class Authtication(object):
    def authenticate(self, request):
        if request.path in ['/docs/', '/swagger/']:
            return (False, None)
        else:
            token = request.META.get('HTTP_TOKEN')
            if token:
                return True, None
            else:
                raise APIException({"detail": "Please Add Token To Your Request Headers"})

    def authenticate_header(self, request):
        pass
