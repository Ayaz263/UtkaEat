import socket
import threading
import sys 
import time
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.textinput import TextInput # Импортируем TextInput
from kivy.uix.scrollview import ScrollView # Импортируем ScrollView для логов

Window.size = (800, 500)
Window.clearcolor = (186/255, 133/255, 0/255)
Window.title = "UtkaEat Server"

# --- Настройки Сети и Глобальные переменные для сервера ---
HOST = '192.168.1.6'
PORT = 65432
server_socket = None 
server_running = False 
# --------------------------------------------------------
# Глобальный список для хранения всех активных клиентских сокетов
client_connections = []
# Мьютекс для безопасного доступа к списку соединений из разных потоков
connections_lock = threading.Lock()

class UtkaEat(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_label = None
        self.message_input = None # Добавляем ссылку на текстовое поле
        self.server_address = (HOST, PORT)
        self.log_label = None # Добавляем ссылку на виджет для логов

    def log_message(self, message):
        """Функция для обновления логов в UI из любого потока."""
        def do_log(dt):
            if self.log_label:
                self.log_label.text += message + "\n"
        # Безопасно вызываем обновление UI в основном потоке Kivy
        Clock.schedule_once(do_log)

    # Функция отправки для кнопки "KRYA" (старая логика)
    def send_to_server(self, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(self.server_address)
                s.sendall(message.encode('utf-8'))
                self.log_message(f"Отправлено на свой же сервер: '{message}'")
                if self.status_label:
                    self.status_label.text = "Статус: Сообщение отправлено!"
        except ConnectionRefusedError:
             self.log_message("Ошибка подключения к серверу через UI (сервер еще не запущен?)")
             if self.status_label:
                self.status_label.text = "Статус: Ошибка подключения к серверу!"
        except Exception as e:
            self.log_message(f"Неизвестная ошибка отправки: {e}")

    # НОВАЯ ФУНКЦИЯ: Отправка сообщения со всем клиентам напрямую из сервера
    def send_from_server_ui(self, instance):
        message = self.message_input.text.strip()
        if message:
            # Префикс, чтобы было понятно, что сообщение от самого сервера
            full_message = f"[SERVER BROADCAST] {message}" 
            # Используем Clock.schedule_once, хотя эта функция уже вызывается 
            # из потока Kivy (обработчик кнопки), это безопасно.
            Clock.schedule_once(lambda dt: broadcast_message(full_message, None), 0)
            self.log_message(f"Отправлено всем клиентам: '{message}'")
            self.message_input.text = '' # Очищаем поле ввода
        else:
            self.log_message("Поле сообщения пустое.")


    def button_pressed_send(self, instance):
        """Обработчик кнопки отправки KRYA."""
        Clock.schedule_once(lambda dt: self.send_to_server("KRYA"), 0)

    def button_pressed_stop_server(self, instance):
        """Обработчик кнопки: Останавливает сервер и завершает приложение."""
        self.stop() 

    def stop_server_safely(self):
        """Функция, которую вы просили: отключает сервер."""
        global server_running, server_socket
        if server_running and server_socket:
            print("[ОСТАНОВКА] Попытка остановить сервер...")
            server_running = False
            server_socket.close() 
            print("[ОСТАНОВКА] Сервер успешно остановлен.")
        else:
            print("[ОСТАНОВКА] Сервер не был запущен или уже остановлен.")

    def build(self):
        # Используем общий BoxLayout для всего интерфейса
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        label = Label(text='UtkaEats Server UI', font_size='30sp', size_hint_y=None, height=40)
        self.status_label = Label(text='Статус: Готов', size_hint_y=None, height=30)
        
        # --- Секция отправки сообщения с сервера ---
        send_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.message_input = TextInput(hint_text='Введите сообщение для рассылки всем')
        btn_send_server = Button(text='Отправить всем', size_hint_x=None, width=100)
        btn_send_server.bind(on_press=self.send_from_server_ui)
        send_box.add_widget(self.message_input)
        send_box.add_widget(btn_send_server)

        # --- Секция логов ---
        # ScrollView позволяет прокручивать логи, если их много
        self.log_label = Label(text='[ЗАПУСК] Ожидание событий...\n', halign='left', valign='top', 
                               text_size=(Window.width - 20, None), padding_x=10, padding_y=10)
        scroll_view = ScrollView()
        scroll_view.add_widget(self.log_label)
        
        # --- Нижние кнопки ---
        btn_send_krya = Button(text='Нажать для отправки KRYA (тест клиента)', font_size='20sp', size_hint_y=None, height=50)
        btn_send_krya.bind(on_press=self.button_pressed_send)
        btn_stop = Button(text='Остановить сервер и выйти', font_size='15sp', background_color=(1, 0, 0, 1), size_hint_y=None, height=50)
        btn_stop.bind(on_press=self.button_pressed_stop_server)

        # Добавляем все виджеты в главный макет
        main_layout.add_widget(label)
        main_layout.add_widget(self.status_label)
        main_layout.add_widget(send_box) # Добавлено поле ввода и кнопка сервера
        main_layout.add_widget(scroll_view) # Добавлены логи
        main_layout.add_widget(btn_send_krya)
        main_layout.add_widget(btn_stop)
        
        return main_layout

    def on_stop(self):
        print("[KIVY] Приложение Kivy завершает работу.")
        self.stop_server_safely()
        time.sleep(0.1) 
        sys.exit(0) 

# --- Функции Сервера (обновлены для использования функции логирования UI) ---
def broadcast_message(message, sender_conn):
    """Рассылает сообщение всем клиентам, кроме отправителя."""
    # Получаем ссылку на экземпляр приложения Kivy
    app_instance = App.get_running_app()
    
    with connections_lock:
        # app_instance.log_message(f"[ШИРОКОВЕЩАТЕЛЬНОЕ СООБЩЕНИЕ] {message}")
        clients_to_remove = []
        for client_conn in client_connections:
            if client_conn != sender_conn:
                try:
                    client_conn.sendall(message.encode('utf-8'))
                except:
                    # Если отправка не удалась, помечаем клиента на удаление
                    app_instance.log_message(f"[ОШИБКА] Не удалось отправить клиенту, удаляем: {client_conn.getpeername()}")
                    client_conn.close()
                    clients_to_remove.append(client_conn)
        
        for client in clients_to_remove:
            client_connections.remove(client)

def handle_client(conn, addr):
    """Обрабатывает входящие сообщения от конкретного клиента."""
    app_instance = App.get_running_app()
    app_instance.log_message(f"[ПОДКЛЮЧЕНИЕ] Установлено с {addr}")

    with connections_lock:
        client_connections.append(conn)
    try:
        while server_running: 
            data = conn.recv(1024)
            if not data:
                break
            # Получили сообщение, рассылаем его всем и логируем
            message_decoded = data.decode('utf-8')
            app_instance.log_message(f"[ОТ КЛИЕНТА {addr[0]}] {message_decoded}")
            message_with_prefix = f"[{addr[0]}] {message_decoded}"
            broadcast_message(message_with_prefix, conn)
    finally:
        with connections_lock:
            if conn in client_connections:
                client_connections.remove(conn)
        app_instance.log_message(f"[ОТКЛЮЧЕНИЕ] Клиент {addr} отключен.")
        conn.close()

def start_server():
    """Запускает сервер в отдельном потоке."""
    global server_socket, server_running
    app_instance = None
    # Ждем пока приложение Kivy запустится и app_instance станет доступен
    while not app_instance:
        app_instance = App.get_running_app()
        time.sleep(0.1)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        server_running = True
        app_instance.log_message(f"[ЗАПУСК] Сервер запущен и слушает на {HOST}:{PORT}")
        while server_running:
            server_socket.settimeout(1.0)
            try:
                conn, addr = server_socket.accept()
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.daemon = True 
                client_thread.start()
            except socket.timeout:
                continue
            except socket.error as e:
                if server_running: 
                    app_instance.log_message(f"Ошибка сокета в цикле приема: {e}")
                break
    except Exception as e:
        app_instance.log_message(f"[ОШИБКА ЗАПУСКА] Не удалось запустить сервер: {e}")
    finally:
        if server_socket:
            server_socket.close()
        server_running = False
        app_instance.log_message("[ОСТАНОВКА] Фоновый процесс сервера завершен.")

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    app = UtkaEat()
    app.run()
