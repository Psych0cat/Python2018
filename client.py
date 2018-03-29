import socket
import settings
import json


class JSONResponse:

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


class JSONRequest:
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
        data_str = json.dump(envelope)
        return data_str.encode(settings.ENCODING)


class EchoClient:

    def __init__(self):

        # Создаем экземпляр сокет соединения
        self._sock = socket.socket()

        # Связываем сокет соединение с хостом и портом сервера 
        self._sock.connect((settings.HOST, settings.PORT))

    def read(self, _sock):

        # Получаем данные с сервера
        bytes_data = self._sock.recv(settings.BUFFER_SIZE)

        # Приводим полученные данные к строковому виду
        str_data = bytes_data.decode(settings.ENCODING)

        # Выводим полученные данные на экран
        print(str_data)

    def write(self):

        # Вводим данные с клавиатуры
        str_data = input('Enter data: ')

        # Приводим отправляемые данные к байтовому виду
        bytes_data = str_data.encode(settings.ENCODING)

        # Отправляем данные на сервер
        self._sock.send(bytes_data)

    def run(self):

        try:

            while True:
                # Вводим данны и отправляем на сервер
                self.write()

                # Получаем ответ сервера
                self.read(self._sock)

        except KeyboardInterrupt:

            # Обрабатываем сочетание клавишь Ctrl+C
            pass


if __name__ == '__main__':
    client = EchoClient()

    client.run()
