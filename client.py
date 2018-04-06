import socket
import settings
import json
import sys
from jim import ClientJSONResponse, ClientJSONRequest


class EchoClient:

    def __init__(self):

        # Создаем экземпляр сокет соединения
        self._sock = socket.socket()

        # Связываем сокет соединение с хостом и портом сервера 
        self._sock.connect((sys.argv[1], int(sys.argv[2])))

    def read(self, _sock):

        # Получаем данные с сервера
        bytes_data = self._sock.recv(settings.BUFFER_SIZE)

        # декодируем байты в json
        j_response = ClientJSONResponse(bytes_data)

        # Выводим полученные данные на экран
        print(j_response.body)

    def write(self):

        # Вводим данные с клавиатуры
        str_data = input('Enter data: ')

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

        except KeyboardInterrupt:

            # Обрабатываем сочетание клавишь Ctrl+C
            pass


if __name__ == '__main__':
    client = EchoClient()

    client.run()
