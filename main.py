import sys
import base64
import math
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QToolBar, QStatusBar,
    QDockWidget, QWidget, QVBoxLayout, QSlider, QComboBox, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QHBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QInputDialog, QMessageBox, QColorDialog, QDialog, QDialogButtonBox,
    QLineEdit, QTabWidget, QFrame, QFileDialog
)
from PySide6 import QtCore
from PySide6.QtCore import Qt, QPointF, QUrl
from PySide6.QtGui import QPainter, QMouseEvent, QPen, QColor, QBrush, QWheelEvent, QIcon, QPixmap, QDesktopServices, QGuiApplication

from api.editor_api import (
    create_project, add_layer, get_layers,
    set_layer_visibility, set_layer_opacity, set_layer_blend_mode,
    remove_layer, set_layer_locked, get_combined_image,
    draw_on_layer, draw_line_on_layer,
    move_layer_up, move_layer_down,
    remove_background_api,
    set_layer_position,
    save_current_project, load_project_from_folder,
    undo, redo
)

from cloud import (
    register, login, save_project_to_cloud, load_project_from_cloud,
    list_user_projects
)
from cloud.share import create_share_link

try:
    from api.editor_api import draw_text_on_layer
    TEXT_SUPPORT = True
except ImportError:
    TEXT_SUPPORT = False
    print("⚠️ Функция draw_text_on_layer не найдена. Текст не будет рисоваться.")

# ---------------------------- ДИАЛОГ ВХОДА/РЕГИСТРАЦИИ ----------------------------
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sign in to Cloud")
        self.setModal(True)
        self.resize(420, 520)
        self.setMinimumSize(400, 480)
        self.token = None

        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #85ADFF;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #85ADFF;
            }
            QTabWidget::pane {
                background-color: #2b2b2b;
                border: none;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #85ADFF;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        title = QLabel("Sign in to Cloud")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Manage your projects across devices")
        subtitle.setStyleSheet("color: #aaaaaa; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        layout.addSpacing(10)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabWidget::tab-bar { alignment: center; }")

        # ---- Вкладка LOGIN ----
        login_tab = QWidget()
        login_layout = QVBoxLayout(login_tab)
        login_layout.setSpacing(15)

        login_layout.addWidget(QLabel("Email"))
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("name@example.com")
        login_layout.addWidget(self.login_email)

        login_layout.addWidget(QLabel("Password"))
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        login_layout.addWidget(self.login_password)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.do_login)
        login_layout.addWidget(login_btn)

        login_layout.addStretch()
        self.tab_widget.addTab(login_tab, "Login")

        # ---- Вкладка SIGN UP ----
        signup_tab = QWidget()
        signup_layout = QVBoxLayout(signup_tab)
        signup_layout.setSpacing(15)

        signup_layout.addWidget(QLabel("Email"))
        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText("email@example.com")
        signup_layout.addWidget(self.signup_email)

        signup_layout.addWidget(QLabel("Password"))
        self.signup_password = QLineEdit()
        self.signup_password.setEchoMode(QLineEdit.Password)
        signup_layout.addWidget(self.signup_password)

        signup_layout.addWidget(QLabel("Name"))
        self.signup_name = QLineEdit()
        self.signup_name.setPlaceholderText("Your name")
        signup_layout.addWidget(self.signup_name)

        signup_btn = QPushButton("Sign Up")
        signup_btn.clicked.connect(self.do_signup)
        signup_layout.addWidget(signup_btn)
        signup_layout.addStretch()
        self.tab_widget.addTab(signup_tab, "Sign Up")

        layout.addWidget(self.tab_widget)

        footer = QLabel("Protected by Graphitium Security. Terms & Privacy")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #888888; font-size: 10px;")
        layout.addWidget(footer)

        self.login_email.setFocus()

    def do_login(self):
        email = self.login_email.text().strip()
        password = self.login_password.text().strip()
        if not email or not password:
            QMessageBox.warning(self, "Ошибка", "Введите email и пароль")
            return
        res = login(email, password)
        if res.get("ok"):
            self.token = res.get("token")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", res.get("error", "Неверные данные"))

    def do_signup(self):
        email = self.signup_email.text().strip()
        password = self.signup_password.text().strip()
        name = self.signup_name.text().strip()
        if not email or not password:
            QMessageBox.warning(self, "Ошибка", "Введите email и пароль")
            return
        res = register(email, password)
        if res.get("ok"):
            self.token = res.get("user_id")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", res.get("error", "Ошибка регистрации"))

# ---------------------------- ДИАЛОГ ВЫБОРА ШАБЛОНА ----------------------------
class TemplateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор шаблона")
        self.setModal(True)
        layout = QVBoxLayout(self)
        
        self.template_list = QListWidget()
        self.templates = []
        self.display_names = []
        
        file_to_display = {
            "template1.png": "Презентация",
            "template2.png": "Пост для соцсетей",
            "template3.png": "Открытка",
            "template4.png": "Визитка",
            "template5.png": "Плакат",
            "template6.png": "Обложка",
            "template7.png": "Баннер",
            "template8.png": "Листовка",
            "template9.png": "Сертификат",
            "template10.png": "Приглашение"
        }
        
        templates_dir = "templates"
        if os.path.exists(templates_dir):
            for f in sorted(os.listdir(templates_dir)):
                if f.lower().endswith('.png'):
                    self.templates.append(f)
                    display = file_to_display.get(f, f.replace('.png', ''))
                    self.display_names.append(display)
                    self.template_list.addItem(display)
        
        if not self.templates:
            for i in range(1, 11):
                self.templates.append(f"template{i}.png")
                self.display_names.append(f"Шаблон {i}")
                self.template_list.addItem(f"Шаблон {i}")
        
        layout.addWidget(QLabel("Выберите шаблон для нового проекта:"))
        layout.addWidget(self.template_list)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_selected_template(self):
        if self.template_list.currentItem():
            idx = self.template_list.currentRow()
            return self.templates[idx]
        return None

# ---------------------------- ХОЛСТ ----------------------------
class Canvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setSceneRect(0, 0, 800, 600)
        self.setBackgroundBrush(Qt.white)
        self.setRenderHint(QPainter.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.drawing = False
        self.start_point = QPointF()
        self.end_point = QPointF()
        self.current_tool = "brush"
        self.brush_size = 25
        self.brush_color = "#000000"   
        self.last_color = "#000000"    
        self.current_layer_index = 0
        self.text_size = 20

        self.move_start_pos = None
        self.move_start_xy = None

        self.pixmap_item = QGraphicsPixmapItem()
        self.pixmap_item.setAcceptDrops(False)
        self.scene().addItem(self.pixmap_item)

        self.setAcceptDrops(True)
        self.setAttribute(Qt.WA_AcceptDrops, True)
        self.setFocusPolicy(Qt.StrongFocus)

        self.current_zoom = 1.0

    def set_tool(self, tool):
        if tool == "eraser" and self.current_tool != "eraser":
            self.last_color = self.brush_color
            self.brush_color = "#FFFFFF"
        elif tool != "eraser" and self.current_tool == "eraser":
            self.brush_color = self.last_color
        self.current_tool = tool

    def set_brush_size(self, size):
        self.brush_size = size

    def set_brush_color(self, color_hex):
        self.brush_color = color_hex
        if self.current_tool != "eraser":
            self.last_color = color_hex

    def set_current_layer(self, index):
        self.current_layer_index = index

    def update_canvas_image(self):
        result = get_combined_image()
        if result.get("status") == "ok":
            if "image_data" in result:
                image_data = result["image_data"]
            elif "image_base64" in result:
                image_data = base64.b64decode(result["image_base64"])
            else:
                return
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.pixmap_item.setPixmap(pixmap)
            self.setSceneRect(0, 0, pixmap.width(), pixmap.height())

    def get_color_at_position(self, event_pos):
        scene_pos = self.mapToScene(event_pos)
        pixmap = self.pixmap_item.pixmap()
        if pixmap.isNull():
            return "#000000"
        image = pixmap.toImage()
        x = int(scene_pos.x())
        y = int(scene_pos.y())
        if 0 <= x < image.width() and 0 <= y < image.height():
            color = image.pixelColor(x, y)
            return color.name()
        return "#000000"

    def set_zoom_percent(self, percent):
        factor = percent / 100.0
        self.resetTransform()
        self.scale(factor, factor)
        self.current_zoom = factor
        main_window = self.window()
        if hasattr(main_window, 'update_zoom'):
            main_window.update_zoom(percent)

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.scale(factor, factor)
        self.current_zoom *= factor
        main_window = self.window()
        if hasattr(main_window, 'update_zoom_from_canvas'):
            main_window.update_zoom_from_canvas(int(self.current_zoom * 100))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                result = add_layer(os.path.basename(file_path), image_path=file_path)
                if result.get("status") == "ok":
                    main_window = self.window()
                    if hasattr(main_window, 'refresh_layers_list'):
                        main_window.refresh_layers_list()
                    self.update_canvas_image()
                    QMessageBox.information(self.window(), "Успех", "Изображение добавлено как новый слой")
                else:
                    QMessageBox.warning(self.window(), "Ошибка", result.get("error", "Не удалось добавить изображение"))
                break
        event.acceptProposedAction()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if self.current_tool == "text":
                self.add_text_at_position(self.mapToScene(event.pos()))
                return
            elif self.current_tool == "move":
                self.move_start_pos = event.pos()
                layers_info = get_layers()
                if self.current_layer_index < len(layers_info.get("layers", [])):
                    layer = layers_info["layers"][self.current_layer_index]
                    self.move_start_xy = (layer.get("x", 0), layer.get("y", 0))
                self.drawing = True
                return
            elif self.current_tool == "eyedropper":
                color = self.get_color_at_position(event.pos())
                self.set_brush_color(color)
                self.current_tool = "brush"
                QMessageBox.information(self.window(), "Пипетка", f"Выбран цвет: {color}")
                return
            self.drawing = True
            self.start_point = self.mapToScene(event.pos())
            self.end_point = self.start_point
            if self.current_tool == "brush" or self.current_tool == "eraser":
                self.draw_point(self.start_point)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drawing:
            if self.current_tool == "move" and self.move_start_pos:
                delta = event.pos() - self.move_start_pos
                new_x = self.move_start_xy[0] + delta.x()
                new_y = self.move_start_xy[1] + delta.y()
                set_layer_position(self.current_layer_index, new_x, new_y)
                self.update_canvas_image()
                return
            current_point = self.mapToScene(event.pos())
            if self.current_tool == "brush" or self.current_tool == "eraser":
                self.draw_line(self.end_point, current_point)
                self.end_point = current_point
            else:
                self.end_point = current_point
            main_window = self.window()
            if hasattr(main_window, 'update_coords'):
                main_window.update_coords(event.pos())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            if self.current_tool == "rectangle":
                self.draw_rectangle(self.start_point, self.end_point)
            elif self.current_tool == "circle":
                self.draw_circle(self.start_point, self.end_point)
            elif self.current_tool == "line":
                self.draw_line_shape(self.start_point, self.end_point)
            elif self.current_tool == "move":
                self.move_start_pos = None
                self.move_start_xy = None
            self.update_canvas_image()

    def add_text_at_position(self, point):
        x, y = int(point.x()), int(point.y())
        text, ok = QInputDialog.getText(self.window(), "Ввод текста", "Введите текст:")
        if ok and text:
            if TEXT_SUPPORT:
                draw_text_on_layer(self.current_layer_index, x, y, text, self.brush_color, self.text_size)
                self.update_canvas_image()
            else:
                QMessageBox.warning(self.window(), "Ошибка", "Функция рисования текста не поддерживается бэкендом.")

    def draw_point(self, point):
        x, y = int(point.x()), int(point.y())
        draw_on_layer(self.current_layer_index, x, y, self.brush_color, self.brush_size)
        self.update_canvas_image()

    def draw_line(self, p1, p2):
        x1, y1 = int(p1.x()), int(p1.y())
        x2, y2 = int(p2.x()), int(p2.y())
        draw_line_on_layer(self.current_layer_index, x1, y1, x2, y2, self.brush_color, self.brush_size)
        self.update_canvas_image()

    def draw_rectangle(self, p1, p2):
        x1, y1 = int(p1.x()), int(p1.y())
        x2, y2 = int(p2.x()), int(p2.y())
        draw_line_on_layer(self.current_layer_index, x1, y1, x2, y1, self.brush_color, self.brush_size)
        draw_line_on_layer(self.current_layer_index, x1, y2, x2, y2, self.brush_color, self.brush_size)
        draw_line_on_layer(self.current_layer_index, x1, y1, x1, y2, self.brush_color, self.brush_size)
        draw_line_on_layer(self.current_layer_index, x2, y1, x2, y2, self.brush_color, self.brush_size)
        self.update_canvas_image()

    def draw_circle(self, p1, p2):
        cx = (p1.x() + p2.x()) / 2
        cy = (p1.y() + p2.y()) / 2
        rx = abs(p2.x() - p1.x()) / 2
        ry = abs(p2.y() - p1.y()) / 2
        steps = 72
        for i in range(steps):
            angle1 = 2 * math.pi * i / steps
            angle2 = 2 * math.pi * (i + 1) / steps
            x1 = cx + rx * math.cos(angle1)
            y1 = cy + ry * math.sin(angle1)
            x2 = cx + rx * math.cos(angle2)
            y2 = cy + ry * math.sin(angle2)
            draw_line_on_layer(self.current_layer_index, int(x1), int(y1), int(x2), int(y2), self.brush_color, self.brush_size)
        self.update_canvas_image()

    def draw_line_shape(self, p1, p2):
        self.draw_line(p1, p2)

# ---------------------------- ГЛАВНОЕ ОКНО ----------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graphitium")
        self.resize(1400, 900)
        self.current_layer_index = 0
        self.token = None

        self._create_menu_bar()
        self._create_canvas()
        self._create_toolbar()
        self._create_status_bar()
        self._create_right_panel()
        self._create_layers_panel()

        self.new_project_from_template()

    def new_project_from_template(self):
        dialog = TemplateDialog(self)
        if dialog.exec() == QDialog.Accepted:
            template_name = dialog.get_selected_template()
            create_project(800, 600)
            add_layer("Фоновый слой")
            if template_name:
                template_path = os.path.join("templates", template_name)
                if os.path.exists(template_path):
                    remove_layer(0)
                    add_layer("Фон", image_path=template_path)
                else:
                    print(f"Шаблон {template_path} не найден")
            self.refresh_layers_list()
            self.canvas.update_canvas_image()
        else:
            create_project(800, 600)
            add_layer("Фоновый слой")
            self.refresh_layers_list()
            self.canvas.update_canvas_image()

    def _create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Файл")
        new_act = file_menu.addAction("Новый")
        new_act.triggered.connect(self.new_project_from_template)
        open_act = file_menu.addAction("Открыть...")
        open_act.triggered.connect(self.open_project_local)
        save_act = file_menu.addAction("Сохранить")
        save_act.triggered.connect(self.save_project_local)
        file_menu.addSeparator()
        exit_act = file_menu.addAction("Выход")
        exit_act.triggered.connect(self.close)

        edit_menu = menubar.addMenu("&Правка")
        undo_act = edit_menu.addAction("Отменить")
        undo_act.triggered.connect(self.undo_action)
        redo_act = edit_menu.addAction("Повторить")
        redo_act.triggered.connect(self.redo_action)

        view_menu = menubar.addMenu("&Вид")
        toggle_panels_act = view_menu.addAction("Показать панели")
        toggle_panels_act.triggered.connect(self.toggle_panels)

        cloud_menu = menubar.addMenu("&Облако")
        cloud_menu.addAction("Сохранить в облако")
        cloud_menu.addAction("Загрузить из облака")
        cloud_menu.addAction("Мои проекты")
        cloud_menu.addSeparator()
        cloud_menu.addAction("Вход")
        cloud_menu.addAction("Регистрация")
        cloud_menu.addSeparator()
        share_act = cloud_menu.addAction("Поделиться")
        share_act.triggered.connect(self.share_project)

        help_menu = menubar.addMenu("&Помощь")
        about_act = help_menu.addAction("О программе")
        about_act.triggered.connect(self.about_action)

        cloud_menu.actions()[0].triggered.connect(self.save_to_cloud)
        cloud_menu.actions()[1].triggered.connect(self.load_from_cloud)
        cloud_menu.actions()[2].triggered.connect(self.show_cloud_projects)
        cloud_menu.actions()[4].triggered.connect(self.login_cloud)
        cloud_menu.actions()[5].triggered.connect(self.login_cloud)   # регистрация через тот же диалог

    def toggle_panels(self):
        """Показывает или скрывает левую панель инструментов и все док-виджеты справа"""
        # Скрываем/показываем левую панель инструментов
        self.toolbar.setVisible(not self.toolbar.isVisible())
        # Скрываем/показываем правые док-виджеты (свойства и слои)
        for widget in self.findChildren(QDockWidget):
            widget.setVisible(not widget.isVisible())

    def about_action(self):
        QMessageBox.about(self, "О программе",
            "<b>Graphitium</b><br>"
            "Версия 1.0<br>"
            "Графический редактор для рисования и дизайна.<br><br>"
            "<b>Разработчики:</b><br>"
            "Титова Елизавета<br>"
            "Тишко Елизавета<br>"
            "Сукиасян Мариета<br><br>"
            "© 2026")

    def undo_action(self):
        try:
            res = undo()
            if res.get("status") == "ok":
                self.refresh_layers_list()
                self.canvas.update_canvas_image()
            else:
                QMessageBox.warning(self, "Ошибка", res.get("error", "Нечего отменять"))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"undo не поддерживается: {e}")

    def redo_action(self):
        try:
            res = redo()
            if res.get("status") == "ok":
                self.refresh_layers_list()
                self.canvas.update_canvas_image()
            else:
                QMessageBox.warning(self, "Ошибка", res.get("error", "Нечего повторять"))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"redo не поддерживается: {e}")

    def _create_toolbar(self):
        self.toolbar = QToolBar("Инструменты")
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)
        self.toolbar.setIconSize(QtCore.QSize(24, 24))

        tools = {
            "Кисть": "brush",
            "Ластик": "eraser.png",
            "Пипетка": "eyedropper",
            "Линия": "line",
            "Прямоугольник": "rectangle",
            "Круг": "circle",
            "Текст": "text",
            "Заливка": None,
            "AI": "ai",
            "Удалить фон": "remove_bg",
            "Перемещение": "move"
        }

        for name, action_key in tools.items():
            act = self.toolbar.addAction(name)
            act.setToolTip(name)
            if action_key == "brush":
                act.triggered.connect(lambda: self.canvas.set_tool("brush"))
            elif action_key == "eraser":
                act.triggered.connect(lambda: self.canvas.set_tool("eraser"))
            elif action_key == "eyedropper":
                act.triggered.connect(lambda: self.canvas.set_tool("eyedropper"))
            elif action_key == "line":
                act.triggered.connect(lambda: self.canvas.set_tool("line"))
            elif action_key == "rectangle":
                act.triggered.connect(lambda: self.canvas.set_tool("rectangle"))
            elif action_key == "circle":
                act.triggered.connect(lambda: self.canvas.set_tool("circle"))
            elif action_key == "text":
                act.triggered.connect(lambda: self.canvas.set_tool("text"))
            elif action_key == "ai":
                act.triggered.connect(lambda: QMessageBox.information(self, "AI", "Функция в разработке"))
            elif action_key == "remove_bg":
                act.triggered.connect(self.remove_background)
            elif action_key == "move":
                act.triggered.connect(lambda: self.canvas.set_tool("move"))
            else:
                act.triggered.connect(lambda _, n=name: print(f"Инструмент '{n}' пока не реализован"))

        color_btn = self.toolbar.addAction("Цвет")
        color_btn.setToolTip("Выбрать цвет для кисти и фигур")
        color_btn.triggered.connect(self.choose_color)

        cloud_btn = self.toolbar.addAction("Облако")
        cloud_btn.setToolTip("Открыть веб-страницу «Мои проекты»")
        cloud_btn.triggered.connect(self.open_cloud_web)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_brush_color(color.name())
            print(f"Выбран цвет: {color.name()}")

    def remove_background(self):
        if self.current_layer_index is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите слой")
            return
        res = remove_background_api(self.current_layer_index, threshold=128)
        if res.get("status") == "ok":
            self.refresh_layers_list()
            self.canvas.update_canvas_image()
            QMessageBox.information(self, "Успех", "Фон удалён")
        else:
            QMessageBox.warning(self, "Ошибка", res.get("error", "Не удалось удалить фон"))

    def open_cloud_web(self):
        QDesktopServices.openUrl(QUrl("http://localhost:5000"))

    def _create_status_bar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.coords_label = QLabel("X: 0, Y: 0")
        self.zoom_label = QLabel("100%")
        self.statusBar.addWidget(self.coords_label)
        self.statusBar.addWidget(self.zoom_label)

    def update_coords(self, pos):
        scene_pos = self.canvas.mapToScene(pos)
        self.coords_label.setText(f"X: {int(scene_pos.x())}, Y: {int(scene_pos.y())}")

    def update_zoom(self, percent):
        self.zoom_label.setText(f"{int(percent)}%")

    def update_zoom_from_canvas(self, percent):
        self.zoom_label.setText(f"{int(percent)}%")
        if hasattr(self, 'zoom_slider'):
            self.zoom_slider.blockSignals(True)
            self.zoom_slider.setValue(percent)
            self.zoom_slider.blockSignals(False)

    def _create_canvas(self):
        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)
        self.canvas.set_current_layer(self.current_layer_index)

    def _create_right_panel(self):
        dock = QDockWidget("Свойства", self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Прозрачность:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        layout.addWidget(self.opacity_slider)
        layout.addWidget(QLabel("Режим наложения:"))
        self.blend_mode_combo = QComboBox()
        self.blend_mode_combo.addItems(["normal", "multiply", "screen"])
        self.blend_mode_combo.currentTextChanged.connect(self.on_blend_mode_changed)
        layout.addWidget(self.blend_mode_combo)

        layout.addWidget(QLabel("Размер текста:"))
        self.text_size_combo = QComboBox()
        self.text_size_combo.addItems(["10", "12", "14", "16", "18", "20", "24", "28", "32", "36", "48", "72"])
        self.text_size_combo.setCurrentText("20")
        self.text_size_combo.currentTextChanged.connect(self.on_text_size_changed)
        layout.addWidget(self.text_size_combo)

        layout.addWidget(QLabel("Размер кисти/ластика:"))
        self.brush_size_slider = QSlider(Qt.Horizontal)
        self.brush_size_slider.setRange(1, 100)
        self.brush_size_slider.setValue(self.canvas.brush_size)
        self.brush_size_slider.valueChanged.connect(self.on_brush_size_changed)
        layout.addWidget(self.brush_size_slider)

        layout.addWidget(QLabel("Масштаб холста:"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 500)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        layout.addWidget(self.zoom_slider)

        layout.addStretch()
        dock.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def on_text_size_changed(self, size_str):
        self.canvas.text_size = int(size_str)

    def on_brush_size_changed(self, value):
        self.canvas.set_brush_size(value)

    def on_zoom_changed(self, value):
        self.canvas.set_zoom_percent(value)

    def on_opacity_changed(self, value):
        res = set_layer_opacity(self.current_layer_index, value)
        if res.get("status") == "ok":
            self.canvas.update_canvas_image()
        else:
            print("Ошибка прозрачности:", res.get("error"))

    def on_blend_mode_changed(self, mode):
        res = set_layer_blend_mode(self.current_layer_index, mode)
        if res.get("status") == "ok":
            self.canvas.update_canvas_image()
        else:
            print("Ошибка режима наложения:", res.get("error"))

    def _create_layers_panel(self):
        dock = QDockWidget("Слои", self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.layers_list = QListWidget()
        self.layers_list.setDragDropMode(QListWidget.InternalMove)
        self.layers_list.itemClicked.connect(self.on_layer_selected)
        layout.addWidget(self.layers_list)
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        add_btn = QPushButton("+")
        del_btn = QPushButton("-")
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        layout.addWidget(btn_widget)
        dock.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        add_btn.clicked.connect(self.add_new_layer)
        del_btn.clicked.connect(self.delete_selected_layer)
        self.layers_list.model().rowsMoved.connect(self.on_layers_reordered)

    def on_layers_reordered(self, parent, start, end, destination, row):
        if start == row:
            return
        if row < start:
            for i in range(start, row, -1):
                move_layer_up(i)
        else:
            for i in range(start, row):
                move_layer_down(start)
        self.refresh_layers_list()
        self.canvas.update_canvas_image()

    def on_layer_selected(self, item):
        self.current_layer_index = self.layers_list.row(item)
        self.canvas.set_current_layer(self.current_layer_index)
        layers_info = get_layers()
        if "layers" in layers_info and self.current_layer_index < len(layers_info["layers"]):
            layer = layers_info["layers"][self.current_layer_index]
            self.opacity_slider.blockSignals(True)
            self.opacity_slider.setValue(layer["opacity"])
            self.opacity_slider.blockSignals(False)
            self.blend_mode_combo.blockSignals(True)
            self.blend_mode_combo.setCurrentText(layer["blend_mode"])
            self.blend_mode_combo.blockSignals(False)

    def refresh_layers_list(self):
        current_row = self.layers_list.currentRow()
        self.layers_list.clear()
        layers_info = get_layers()
        if "layers" not in layers_info:
            return
        for idx, layer in enumerate(layers_info["layers"]):
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(5, 2, 5, 2)

            eye_btn = QPushButton("👁" if layer["visible"] else "👁‍🗨")
            eye_btn.setFixedSize(30, 25)
            eye_btn.setCheckable(True)
            eye_btn.setChecked(layer["visible"])
            eye_btn.clicked.connect(lambda checked, i=idx: self.toggle_visibility(i, checked))

            name_label = QLabel(layer["name"])
            name_label.setMinimumWidth(100)

            locked = layer.get("locked", False)
            lock_btn = QPushButton("🔒" if locked else "🔓")
            lock_btn.setFixedSize(30, 25)
            lock_btn.setCheckable(True)
            lock_btn.setChecked(locked)
            lock_btn.clicked.connect(lambda checked, i=idx: self.toggle_lock(i, checked))

            item_layout.addWidget(eye_btn)
            item_layout.addWidget(name_label)
            item_layout.addStretch()
            item_layout.addWidget(lock_btn)

            item_widget.setLayout(item_layout)
            list_item = QListWidgetItem(self.layers_list)
            list_item.setSizeHint(item_widget.sizeHint())
            self.layers_list.addItem(list_item)
            self.layers_list.setItemWidget(list_item, item_widget)
        if current_row >= 0 and current_row < self.layers_list.count():
            self.layers_list.setCurrentRow(current_row)

    def toggle_visibility(self, layer_index, visible):
        res = set_layer_visibility(layer_index, visible)
        if res.get("status") == "ok":
            self.refresh_layers_list()
            self.canvas.update_canvas_image()
        else:
            print("Ошибка видимости:", res.get("error"))

    def toggle_lock(self, layer_index, locked):
        res = set_layer_locked(layer_index, locked)
        if res.get("status") == "ok":
            self.refresh_layers_list()
        else:
            print("Ошибка блокировки:", res.get("error"))

    def add_new_layer(self):
        new_name = f"Слой {len(get_layers().get('layers', [])) + 1}"
        res = add_layer(new_name)
        if res.get("status") == "ok":
            self.refresh_layers_list()
            self.canvas.update_canvas_image()
        else:
            print("Ошибка добавления слоя:", res.get("error"))

    def delete_selected_layer(self):
        current_item = self.layers_list.currentItem()
        if not current_item:
            print("Выберите слой для удаления")
            return
        row = self.layers_list.row(current_item)
        res = remove_layer(row)
        if res.get("status") == "ok":
            self.refresh_layers_list()
            self.current_layer_index = 0
            self.canvas.set_current_layer(0)
            self.canvas.update_canvas_image()
        else:
            print("Ошибка удаления слоя:", res.get("error"))

    def save_project_local(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения проекта")
        if folder:
            res = save_current_project(folder)
            if res.get("status") == "ok":
                QMessageBox.information(self, "Успех", f"Проект сохранён в:\n{folder}")
            else:
                QMessageBox.warning(self, "Ошибка", res.get("error", "Не удалось сохранить проект"))

    def open_project_local(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку с проектом")
        if folder:
            res = load_project_from_folder(folder)
            if res.get("status") == "ok":
                self.refresh_layers_list()
                self.canvas.update_canvas_image()
                QMessageBox.information(self, "Успех", "Проект загружен")
            else:
                QMessageBox.warning(self, "Ошибка", res.get("error", "Не удалось загрузить проект"))

    def login_cloud(self):
        dialog = LoginDialog(self)
        if dialog.exec() == QDialog.Accepted and dialog.token:
            self.token = dialog.token
            QMessageBox.information(self, "Успех", "Вход выполнен")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось войти")

    def share_project(self):
        if not self.token:
            QMessageBox.warning(self, "Ошибка", "Сначала войдите в облако (меню Облако -> Вход)")
            return
        projects = list_user_projects(self.token)
        if not projects.get("ok") or not projects["projects"]:
            QMessageBox.warning(self, "Ошибка", "Нет проектов для шаринга")
            return
        project_id = projects["projects"][0]["id"]
        res = create_share_link(project_id, self.token, can_edit=False)
        if res.get("ok"):
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(res["url"])
            QMessageBox.information(self, "Ссылка скопирована", f"Ссылка для просмотра:\n{res['url']}\n\nСкопирована в буфер обмена.")
        else:
            QMessageBox.warning(self, "Ошибка", res.get("error", "Не удалось создать ссылку"))

    def save_to_cloud(self):
        if not self.token:
            QMessageBox.warning(self, "Ошибка", "Сначала войдите в облако (меню Облако -> Вход)")
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            from api.editor_api import export_project_to_cloud
            result = export_project_to_cloud()
            if result.get("status") != "ok":
                QMessageBox.warning(self, "Ошибка", result.get("error", "Не удалось экспортировать проект"))
                return
            project_data = result["project_data"]
            name, ok = QInputDialog.getText(self, "Сохранить в облако", "Название проекта:")
            if ok and name:
                cloud_res = save_project_to_cloud(project_data, self.token, name)
                if cloud_res.get("ok"):
                    QMessageBox.information(self, "Успех", "Проект сохранён в облако")
                else:
                    QMessageBox.warning(self, "Ошибка", cloud_res.get("error", "Неизвестная ошибка"))
        finally:
            QApplication.restoreOverrideCursor()

    def load_from_cloud(self):
        if not self.token:
            QMessageBox.warning(self, "Ошибка", "Сначала войдите в облако")
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            projects = list_user_projects(self.token)
            if not projects.get("ok"):
                QMessageBox.warning(self, "Ошибка", projects.get("error", "Не удалось получить список проектов"))
                return
            if not projects["projects"]:
                QMessageBox.information(self, "Информация", "У вас нет проектов в облаке")
                return

            proj_list = sorted(projects["projects"], key=lambda x: x.get("saved_at", ""), reverse=True)

            items = []
            for p in proj_list:
                name = p.get("name", "Без названия")
                date = p.get("saved_at", "")
                if date:
                    date_str = date[:19].replace("T", " ")
                else:
                    date_str = "дата неизвестна"
                items.append(f"{name} ({date_str})")

            selected, ok = QInputDialog.getItem(self, "Выберите проект", "Проекты в облаке:", items, 0, False)
            if not ok or not selected:
                return

            idx = items.index(selected)
            project_id = proj_list[idx]["id"]

            data = load_project_from_cloud(project_id, self.token)
            if data.get("ok"):
                from api.editor_api import import_project_from_cloud
                import_project_from_cloud(data["project"])
                self.refresh_layers_list()
                self.canvas.update_canvas_image()
                QMessageBox.information(self, "Успех", "Проект загружен из облака")
            else:
                QMessageBox.warning(self, "Ошибка", data.get("error", "Не удалось загрузить проект"))
        finally:
            QApplication.restoreOverrideCursor()

    def show_cloud_projects(self):
        QDesktopServices.openUrl(QUrl("http://localhost:5000"))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMainWindow { background-color: #2b2b2b; }
        QMenuBar { background-color: #3c3c3c; color: #ffffff; }
        QMenuBar::item:selected { background-color: #85ADFF; }
        QMenu { background-color: #3c3c3c; color: #ffffff; }
        QMenu::item:selected { background-color: #85ADFF; }
        QToolBar { background-color: #3c3c3c; border: none; spacing: 3px; }
        QToolButton { background-color: #3c3c3c; color: #ffffff; border-radius: 4px; padding: 4px; }
        QToolButton:hover { background-color: #4a4a4a; }
        QToolButton:pressed { background-color: #85ADFF; }
        QDockWidget { background-color: #3c3c3c; }
        QDockWidget::title { background-color: #4a4a4a; color: #ffffff; text-align: left; padding: 4px; }
        QWidget { background-color: #3c3c3c; color: #ffffff; }
        QPushButton { background-color: #4a4a4a; color: #ffffff; border: 1px solid #5a5a5a; border-radius: 4px; padding: 4px 8px; }
        QPushButton:hover { background-color: #5a5a5a; }
        QPushButton:pressed { background-color: #85ADFF; }
        QSlider::groove:horizontal { height: 6px; background: #5a5a5a; border-radius: 3px; }
        QSlider::handle:horizontal { background: #85ADFF; width: 14px; border-radius: 7px; margin: -4px 0; }
        QComboBox { background-color: #4a4a4a; color: #ffffff; border: 1px solid #5a5a5a; border-radius: 4px; padding: 4px; }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView { background-color: #4a4a4a; color: #ffffff; }
        QListWidget { background-color: #3c3c3c; color: #ffffff; border: 1px solid #5a5a5a; }
        QListWidget::item:selected { background-color: #85ADFF; }
        QStatusBar { background-color: #2b2b2b; color: #ffffff; }
        QScrollBar:vertical { background: #2b2b2b; width: 12px; border-radius: 6px; }
        QScrollBar::handle:vertical { background: #85ADFF; border-radius: 6px; min-height: 20px; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        QGraphicsView { background-color: #ffffff; }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())