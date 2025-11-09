
# Настройки Сети и Глобальные переменные для клиента
 # Убедитесь, что это IP вашего сервера
import socket
import threading
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
import sys

# Настройки Сети и Глобальные переменные для клиента
SERVER_HOST = '192.168.1.6'
SERVER_PORT = 65432
# Мы убираем SERVER_HOST из констант, теперь он динамический

Window.size = (500, 650)
Window.clearcolor = (186/255, 133/255, 0/255)
Window.title = "UtkaEat Chat Client"

class UtkaEat(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_label = None
        self.chat_history_label = None
        self.ip_input_field = None  # Поле ввода для IP-адреса
        self.message_input_field = None # Поле ввода для сообщений
        self.client_socket = None
        self.listener_thread = None
        self.running_client = True
        self.server_ip = '127.0.0.1' # IP по умолчанию

    def connect_and_listen(self, instance):
        """Устанавливает соединение, используя IP из поля ввода."""
        self.server_ip = self.ip_input_field.text.strip()
        if not self.server_ip:
            self.add_message_to_chat(">>> Ошибка: Введите IP-адрес.", system=True)
            return

        if self.client_socket:
            self.add_message_to_chat(">>> Уже подключено. Сначала отключитесь.", system=True)
            return

        self.add_message_to_chat(f">>> Попытка подключения к {self.server_ip}:{SERVER_PORT}...", system=True)

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, SERVER_PORT))
            self.add_message_to_chat(f">>> Подключено успешно к {self.server_ip}.", system=True)
            
            # Запускаем поток для постоянного прослушивания сервера
            self.listener_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.listener_thread.start()

        except ConnectionRefusedError:
            self.add_message_to_chat(">>> Ошибка подключения: Сервер недоступен (ConnectionRefused).", system=True)
            self.client_socket = None
        except Exception as e:
            self.add_message_to_chat(f">>> Ошибка сети: {e}", system=True)
            self.client_socket = None

    def receive_messages(self):
        # ... (функция остается прежней, как в предыдущем ответе) ...
        while self.running_client and self.client_socket:
            try:
                data = self.client_socket.recv(1024)
                if data:
                    message = data.decode('utf-8')
                    Clock.schedule_once(lambda dt, msg=message: self.add_message_to_chat(msg), 0)
            except Exception as e:
                if self.running_client:
                    Clock.schedule_once(lambda dt: self.add_message_to_chat(f">>> Соединение потеряно.", system=True), 0)
                break
        if self.client_socket:
            self.client_socket.close()

    def send_message_to_server(self, message):
        # ... (функция остается прежней, как в предыдущем ответе) ...
        if not message or not self.client_socket:
            return

        try:
            self.client_socket.sendall(message.encode('utf-8'))
            self.add_message_to_chat(f"[Я] {message}")
            self.message_input_field.text = '' # Очищаем поле сообщения

        except Exception as e:
            Clock.schedule_once(lambda dt: self.add_message_to_chat(f">>> Ошибка отправки: {e}", system=True), 0)

    def add_message_to_chat(self, message, system=False):
        # ... (функция остается прежней, как в предыдущем ответе) ...
        if self.chat_history_label:
            current_text = self.chat_history_label.text
            new_text = f"{current_text}\n{message}"
            self.chat_history_label.text = new_text

    def button_pressed_send(self, instance):
        """Обработчик кнопки отправки сообщения."""
        message = self.message_input_field.text
        Clock.schedule_once(lambda dt: self.send_message_to_server(message), 0)

    def on_stop(self):
        # ... (функция остается прежней, как в предыдущем ответе) ...
        self.running_client = False
        if self.client_socket:
            self.client_socket.close()
        if self.listener_thread:
            self.listener_thread.join(timeout=1)

    def build(self):
        box_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        label_title = Label(text='UtkaEat Динамический Чат', font_size='30sp', size_hint_y=None, height=50)
        
        # --- Блок ввода IP-адреса и подключения ---
        ip_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.ip_input_field = TextInput(
            hint_text=f'Введите IP сервера (по умолчанию {self.server_ip})',
            multiline=False,
            text=self.server_ip # Устанавливаем значение по умолчанию в поле
        )
        btn_connect = Button(text='Подключиться', size_hint_x=None, width=120)
        btn_connect.bind(on_press=self.connect_and_listen)
        ip_box.add_widget(self.ip_input_field)
        ip_box.add_widget(btn_connect)
        
        # Область для вывода сообщений 
        self.chat_history_label = Label(text='Ожидание подключения...', halign='left', valign='top', 
                                        padding_x=10, padding_y=10, size_hint_y=None)
        self.chat_history_label.bind(texture_size=self.chat_history_label.setter('size'))
        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll_view.add_widget(self.chat_history_label)

        # --- Блок ввода сообщений и отправки ---
        self.message_input_field = TextInput(
            hint_text='Введите ваше сообщение...',
            multiline=False,
            size_hint_y=None, 
            height=40,
            on_text_validate=self.button_pressed_send
        )
        btn_send = Button(text='Отправить', size_hint_x=None, width=100)
        btn_send.bind(on_press=self.button_pressed_send) 

        input_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        input_box.add_widget(self.message_input_field)
        input_box.add_widget(btn_send)

        # Статус
        self.status_label = Label(text='', size_hint_y=None, height=30, font_size='12sp')


        box_layout.add_widget(label_title)
        box_layout.add_widget(ip_box)         # Добавляем блок ввода IP
        box_layout.add_widget(scroll_view)
        # box_layout.add_widget(self.status_label) # Статус теперь в чате
        box_layout.add_widget(input_box)

        return box_layout

if __name__ == "__main__":
    UtkaEat().run()
