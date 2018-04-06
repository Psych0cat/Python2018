import settings
import json


class JSONRequest:

    # Конструктор в качестве аргументов принимает исключительно "сырые" данные
    # Внутри конструктора "сырые" данные преобразуются в словарь
    def __init__(self, message_bytes):

        message_str = message_bytes.decode(settings.ENCODING)
        self._envelope = json.loads(message_str)

    @property
    def action(self):

        # Read only свойство action
        action = self._envelope.get('action')

        return action

    @property
    def headers(self):

        # Read only свойство headers
        # Свойство headers содержит дополнительные данные о запросе, например время его совершения
        headers = self._envelope.get('headers')

        for key, value in headers.items():
            yield key, value

    @property
    def body(self):

        # Read only свойство body
        # Свойство body содержит тело запроса
        body = self._envelope.get('body')

        return body


# Response-объект - используется для приведения python-объекта в байтовый вид (для генерации "сырых" данных)
class JSONResponse:

    # Конструктор в качестве аргументов принимает основные данные об ответе сервера
    def __init__(self, code, action, body, **headers):

        self._headers = headers

        self._action = action

        self._code = code

        self._body = body

    # Метод add_header - используется для добавления дополнительных
    # данных об товете сервера, например времени его совершения
    def add_header(self, key, value):

        self._headers.update({key: value})

    # Метод add_header - используется для удаления дополнительных данных
    #  об товете сервера, если во время его заполнения была допущена ошибка
    def remove_header(self, key):

        del self._headers[key]

    # Метод to_bytes - используется для преобразования данных об ответе сервера в байты
    def to_bytes(self):

        envelope = dict()

        envelope.update({'code': self._code})

        envelope.update({'action': self._action})

        envelope.update({'headers': self._headers})

        envelope.update({'body': self._body})

        data_str = json.dumps(envelope)

        return data_str.encode(settings.ENCODING)


class ClientJSONResponse:

    def __init__(self, message_bytes):
        message_str = message_bytes.decode(settings.ENCODING)
        self._envelope = json.loads(message_str)
        self._startline = self._envelope.get('startline')

    @property
    def code(self):
        code = self._startline.get('code')
        return code

    @property
    def method(self):
        method = self._startline.get('method')
        return method

    @property
    def headers(self):
        headers = self._startline.get('headers')
        for key, value in headers.items():
            yield key, value

    @property
    def body(self):

        # Read only свойство body
        # Свойство body содержит тело ответа сервера
        body = self._envelope.get('body')
        return body


class ClientJSONRequest:
    def __init__(self, url, method, body, **headers):
        self._headers = headers
        self._url = url
        self._method = method
        self._body = body

    def add_header(self, key, value):
        self._headers.update({key: value})

    def remove_header(self, key):
        del self._headers[key]

    def to_bytes(self):
        envelope = dict()
        start_line = dict()
        start_line.update({'url': self._url})
        start_line.update({'method': self._method})
        start_line.update({'version': settings.VERSION})
        envelope.update({'startline': start_line})
        envelope.update({'headers': self._headers})
        envelope.update({'body': self._body})
        data_str = json.dumps(envelope)
        return data_str.encode(settings.ENCODING)
