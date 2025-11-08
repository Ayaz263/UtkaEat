import socket
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.clock import Clock # Нужен для сетевых операций в Kivy

Window.size = (500, 500)
Window.clearcolor = (186/255, 133/255, 0/255)
Window.title = "UtkaEat"

# Настройки сервера, куда отправляем данные
SERVER_HOST = '127.0.0.1' # Если сервер на другом ПК, измените на его IP
SERVER_PORT = 65432

class UtkaEat(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_label = None
        self.server_address = (SERVER_HOST, SERVER_PORT)

    def send_order(self, message):
        """Функция отправки сообщения на сервер."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(self.server_address)
                s.sendall(message.encode('utf-8'))
                if self.status_label:
                    self.status_label.text = f"Статус: Отправлено: '{message}'"
        except ConnectionRefusedError:
            if self.status_label:
                self.status_label.text = "Ошибка: Сервер недоступен."
        except Exception as e:
            if self.status_label:
                self.status_label.text = f"Ошибка сети: {e}"

    def button_pressed(self, instance):
        """Обработчик кнопки: отправляет сообщение 'заказ'."""
        # Используем Clock для выполнения сетевой операции, чтобы не блокировать GUI
        Clock.schedule_once(lambda dt: self.send_order("заказ"), 0)

    def build(self):
        box = BoxLayout(orientation='vertical')
        btn = Button(text='Нажать для заказа', font_size='20sp')
        btn.bind(on_press=self.button_pressed) 
        
        label = Label(text='UtkaEats', font_size='30sp')
        self.status_label = Label(text='Статус: Готов')

        box.add_widget(label)
        box.add_widget(self.status_label)
        box.add_widget(btn)

        return box

if __name__ == "__main__":
    UtkaEat().run()