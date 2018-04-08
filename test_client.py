import socket
import settings
import sys
from jim import ClientJSONResponse, ClientJSONRequest
import pytest


@pytest.fixture
def ip_addr():
    return "127.0.0.1"


@pytest.fixture
def port():
    return 7777


@pytest.fixture
def test_string():
    return 'test'


class EchoClient:

    def __init__(self):

        # Создаем экземпляр сокет соединения
        self._sock = socket.socket()

        # Связываем сокет соединение с хостом и портом сервера 
        self._sock.connect((ip_addr(), port()))

    def read(self, _sock):

        # Получаем данные с сервера
        bytes_data = self._sock.recv(settings.BUFFER_SIZE)

        # декодируем байты в json
        j_response = ClientJSONResponse(bytes_data)

        # Выводим полученные данные на экран
        print(j_response.body)


    def write(self):

        # Вводим данные с клавиатуры
        str_data = test_string()

        json_data = ClientJSONRequest('url', 'method', str_data)

        # Приводим отправляемые данные к байтовому виду
        # Отправляем данные на сервер
        self._sock.send(json_data.to_bytes())

    def run(self):

        try:

            while True:
                # Вводим данны и отправляем на сервер
                self.write()

                # Получаем ответ сервера
                self.read(self._sock)
                test_client()
        except KeyboardInterrupt:

            # Обрабатываем сочетание клавишь Ctrl+C
            pass


if __name__ == '__main__':
    client = EchoClient()

    client.run()




