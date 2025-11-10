import socket
import threading
import sys
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock

# Настройки сети
SERVER_IP = "192.168.1.6"  # или ваш IP
SERVER_PORT = 65432

Window.clearcolor = (186/255, 133/255, 0/255)
Window.title = "UtkaEat Chat Client"

class UtkaEat(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_label = None
        self.chat_history_label = None
        self.username_input_field = None
        self.message_input_field = None
        self.client_socket = None
        self.listener_thread = None
        self.running_client = True
        self.connected = False
        self.username = ""

    def connect_to_server(self):
        """Подключается к серверу и инициализирует прием сообщений"""
        username = self.username_input_field.text.strip()
        if not username:
            self.add_message_to_chat(">>> Введите свое имя пользователя.", system=True)
            return

        if self.connected:
            self.add_message_to_chat(">>> Уже подключены. Сначала выйдите из текущего чата.", system=True)
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_IP, SERVER_PORT))
            self.client_socket.send(username.encode('utf-8'))
            self.add_message_to_chat(f">>> Подключились к серверу как '{username}'.", system=True)
            self.connected = True
            self.username_input_field.disabled = True
            self.listener_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.listener_thread.start()
        except ConnectionRefusedError:
            self.add_message_to_chat(">>> Невозможно подключиться к серверу (отказано в соединении)", system=True)
        except Exception as e:
            self.add_message_to_chat(f">>> Произошла ошибка при подключении: {e}", system=True)

    def receive_messages(self):
        """Принимает сообщения от сервера и выводит их в окно чата"""
        while self.running_client and self.client_socket:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    raise ConnectionResetError("Сервер закрыл соединение")
                message = data.decode('utf-8')
                Clock.schedule_once(lambda dt, msg=message: self.add_message_to_chat(msg), 0)
            except Exception as e:
                if self.running_client:
                    self.add_message_to_chat(f">>> Произошла ошибка: {e}. Переподключение...", system=True)
                    self.reconnect()
                break

    def reconnect(self):
        """Перезапускает соединение с сервером после сбоя"""
        self.connected = False
        self.client_socket.close()
        self.connect_to_server()

    def send_message_to_server(self, message):
        """Отправляет сообщение на сервер"""
        if not message or not self.client_socket:
            return
        try:
            self.client_socket.sendall(message.encode('utf-8'))
            self.message_input_field.text = ''
        except Exception as e:
            self.add_message_to_chat(f">>> Ошибка отправки сообщения: {e}", system=True)

    def add_message_to_chat(self, message, system=False):
        """Добавляет сообщение в чат с возможностью отмечать систему отдельно"""
        if self.chat_history_label:
            current_text = self.chat_history_label.text
            new_text = f"{current_text}\n{message}"
            self.chat_history_label.text = new_text

    def disconnect_from_server(self):
        """Отключает клиента от сервера"""
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            self.connected = False
            self.username_input_field.disabled = False
            self.add_message_to_chat(">>> Отключились от сервера.", system=True)

    def button_pressed_send(self, instance):
        """Обработчик кнопки отправки сообщения"""
        message = self.message_input_field.text
        Clock.schedule_once(lambda dt: self.send_message_to_server(message), 0)

    def on_stop(self):
        """Осуществляется при выходе из приложения"""
        self.disconnect_from_server()
        if self.listener_thread:
            self.listener_thread.join(timeout=1)

    def build(self):
        """Создаем основной интерфейс приложения"""
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        title_label = Label(text='УткаЕдят Чат', font_size='30sp', size_hint_y=None, height=50)

        # Блок выбора имени пользователя и подключения
        user_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.username_input_field = TextInput(hint_text='Введите своё имя:')
        btn_connect = Button(text='Подключиться', size_hint_x=None, width=120)
        btn_connect.bind(on_press=lambda x: self.connect_to_server())
        user_box.add_widget(self.username_input_field)
        user_box.add_widget(btn_connect)

        # Область истории сообщений
        self.chat_history_label = Label(text="Ожидание подключения...", halign='left', valign='top', padding_x=10, padding_y=10)
        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll_view.add_widget(self.chat_history_label)

        # Блок ввода сообщений и отправки
        self.message_input_field = TextInput(hint_text='Введите сообщение...', multiline=False, size_hint_y=None, height=40)
        btn_send = Button(text='Отправить', size_hint_x=None, width=100)
        btn_send.bind(on_press=self.button_pressed_send)
        input_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        input_box.add_widget(self.message_input_field)
        input_box.add_widget(btn_send)

        layout.add_widget(title_label)
        layout.add_widget(user_box)
        layout.add_widget(scroll_view)
        layout.add_widget(input_box)

        return layout

if __name__ == "__main__":
    UtkaEat().run()
