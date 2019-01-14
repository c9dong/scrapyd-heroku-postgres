HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_404_NOT_FOUND = 404
HTTP_204_NO_CONTENT = 204

class HttpException(Exception):
  def __init__(self, code):
    self._code = code

  @property
  def code(self):
    return self._code