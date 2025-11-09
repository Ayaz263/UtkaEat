import socket
import threading
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput # Импортируем TextInput
from kivy.uix.scrollview import ScrollView # Добавим для прокрутки сообщений
from kivy.core.window import Window
from kivy.clock import Clock
import sys

# Настройки Сети и Глобальные переменные для клиента
SERVER_HOST = '192.168.1.6' # Убедитесь, что это IP вашего сервера
SERVER_PORT = 65432

Window.clearcolor = (186/255, 133/255, 0/255)
Window.title = "UtkaEat Chat Client"

class UtkaEat(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_label = None
        self.chat_history_label = None
        self.input_field = None
        self.server_address = (SERVER_HOST, SERVER_PORT)
        self.client_socket = None # Сокет для постоянного соединения
        self.listener_thread = None
        self.running_client = True # Флаг работы клиента

    def connect_and_listen(self):
        """Устанавливает соединение и запускает поток слушателя."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(self.server_address)
            self.add_message_to_chat(">>> Подключено к серверу.", system=True)
            
            # Запускаем поток для постоянного прослушивания сервера
            self.listener_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.listener_thread.start()

        except ConnectionRefusedError:
            self.add_message_to_chat(">>> Ошибка подключения: Сервер недоступен.", system=True)
        except Exception as e:
            self.add_message_to_chat(f">>> Ошибка сети: {e}", system=True)

    def receive_messages(self):
        """Постоянно слушает сервер в отдельном потоке."""
        while self.running_client and self.client_socket:
            try:
                data = self.client_socket.recv(1024)
                if data:
                    message = data.decode('utf-8')
                    # Обновляем GUI через Clock, так как мы в другом потоке
                    Clock.schedule_once(lambda dt, msg=message: self.add_message_to_chat(msg), 0)
            except Exception as e:
                if self.running_client:
                    Clock.schedule_once(lambda dt: self.add_message_to_chat(f">>> Соединение потеряно: {e}", system=True), 0)
                break

    def send_message_to_server(self, message):
        """Отправляет сообщение через уже установленное соединение."""
        if not message or not self.client_socket:
            return

        try:
            # Отправляем сообщение
            self.client_socket.sendall(message.encode('utf-8'))
            # Сразу добавляем свое сообщение в историю чата
            self.add_message_to_chat(f"[Я] {message}")
            # Очищаем поле ввода
            self.input_field.text = ''

        except Exception as e:
            Clock.schedule_once(lambda dt: self.add_message_to_chat(f">>> Ошибка отправки: {e}", system=True), 0)

    def add_message_to_chat(self, message, system=False):
        """Безопасно добавляет сообщение в текстовую область чата."""
        if self.chat_history_label:
            current_text = self.chat_history_label.text
            new_text = f"{current_text}\n{message}"
            self.chat_history_label.text = new_text
            # В реальном приложении ScrollView нужно прокручивать вниз

    def button_pressed_send(self, instance):
        """Обработчик кнопки отправки."""
        message = self.input_field.text
        # Используем Clock/отдельный вызов для отправки
        Clock.schedule_once(lambda dt: self.send_message_to_server(message), 0)

    def on_stop(self):
        """Вызывается при закрытии Kivy приложения."""
        self.running_client = False
        if self.client_socket:
            self.client_socket.close()
        if self.listener_thread:
            self.listener_thread.join(timeout=1) # Ждем немного закрытия потока

    def build(self):
        box_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        label_title = Label(text='UtkaEat Чат', font_size='30sp', size_hint_y=None, height=50)
        
        # Область для вывода сообщений (Label внутри ScrollView)
        self.chat_history_label = Label(text='Ожидание сообщений...', halign='left', valign='top', 
                                        padding_x=10, padding_y=10, size_hint_y=None)
        # Важно установить размер текста, чтобы ScrollView знал высоту
        self.chat_history_label.bind(texture_size=self.chat_history_label.setter('size'))

        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll_view.add_widget(self.chat_history_label)

        # Поле ввода
        self.input_field = TextInput(
            hint_text='Введите ваше сообщение...',
            multiline=False,
            size_hint_y=None, 
            height=40,
            on_text_validate=self.button_pressed_send # Отправка по Enter
        )

        btn_send = Button(text='Отправить', size_hint_y=None, height=40)
        btn_send.bind(on_press=self.button_pressed_send) 

        self.status_label = Label(text='Статус: Подключение...', size_hint_y=None, height=30, font_size='12sp')

        box_layout.add_widget(label_title)
        box_layout.add_widget(scroll_view) # Добавляем ScrollView вместо просто Label
        box_layout.add_widget(self.status_label)

        # Нижний блок ввода и кнопки в отдельном горизонтальном боксе
        input_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        input_box.add_widget(self.input_field)
        input_box.add_widget(btn_send)
        box_layout.add_widget(input_box)


        # Запускаем подключение при старте интерфейса
        # Даем интерфейсу проинициализироваться, затем подключаемся
        Clock.schedule_once(lambda dt: self.connect_and_listen(), 0.5)

        return box_layout

if __name__ == "__main__":
    UtkaEat().run()
