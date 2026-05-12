import sys
import base64
import math
import os
import argparse
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QToolBar, QStatusBar,
    QDockWidget, QWidget, QVBoxLayout, QSlider, QComboBox, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QHBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QInputDialog, QMessageBox, QColorDialog, QDialog, QDialogButtonBox,
    QLineEdit, QTabWidget, QFrame, QFileDialog
)
from PySide6 import QtCore
from PySide6.QtCore import Qt, QPointF, QUrl, QTimer
from PySide6.QtGui import QPainter, QMouseEvent, QPen, QColor, QBrush, QWheelEvent, QIcon, QPixmap, QDesktopServices, QGuiApplication, QKeySequence

from api.editor_api import (
    create_project, add_layer, get_layers,
    set_layer_visibility, set_layer_opacity, set_layer_blend_mode,
    remove_layer, set_layer_locked, get_combined_image,
    draw_on_layer, draw_line_on_layer,
    move_layer_up, move_layer_down,
    remove_background_api,
    set_layer_position,
    save_current_project, load_project_from_folder,
    undo, redo,
    import_psd, export_to_pdf_api, export_project,
    apply_filter_to_layer_api, rotate_layer_api, scale_layer_api,
    crop_layer_api, resize_canvas_api,
    erase_on_layer
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

try:
    from api.editor_api import flood_fill_api
    FLOOD_FILL_SUPPORT = True
except ImportError:
    FLOOD_FILL_SUPPORT = False
    print("⚠️ Функция flood_fill_api не найдена. Заливка будет недоступна.")

# AI интеграция
from ai_integration import handle_ai_generation

# ----------------------------------------------------------------------
# Диалог входа / регистрации (без изменений)
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# Диалог выбора шаблона (без изменений)
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# Холст (Canvas) – исправлен wheelEvent + ластик через erase_on_layer + заливка
# ----------------------------------------------------------------------
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

    def zoom_in(self):
        factor = 1.2
        self.scale(factor, factor)
        self.current_zoom *= factor
        main_window = self.window()
        if hasattr(main_window, 'update_zoom_from_canvas'):
            main_window.update_zoom_from_canvas(int(self.current_zoom * 100))

    def zoom_out(self):
        factor = 0.8
        self.scale(factor, factor)
        self.current_zoom *= factor
        main_window = self.window()
        if hasattr(main_window, 'update_zoom_from_canvas'):
            main_window.update_zoom_from_canvas(int(self.current_zoom * 100))

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        if abs(delta) < 1:
            return
        # Если дельта положительная – увеличиваем, отрицательная – уменьшаем
        if delta > 0:
            factor = 1.1
        else:
            factor = 0.9
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
            elif self.current_tool == "flood_fill":
                if not FLOOD_FILL_SUPPORT:
                    QMessageBox.warning(self.window(), "Ошибка", "Функция заливки ещё не добавлена в бэкенд.")
                    return
                scene_pos = self.mapToScene(event.pos())
                x, y = int(scene_pos.x()), int(scene_pos.y())
                res = flood_fill_api(self.current_layer_index, x, y, self.brush_color)
                if res.get("status") == "ok":
                    self.update_canvas_image()
                else:
                    QMessageBox.warning(self.window(), "Ошибка", res.get("error", "Заливка не удалась"))
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
        if self.current_tool == "eraser":
            erase_on_layer(self.current_layer_index, x, y, self.brush_size)
        else:
            draw_on_layer(self.current_layer_index, x, y, self.brush_color, self.brush_size)
        self.update_canvas_image()

    def draw_line(self, p1, p2):
        x1, y1 = int(p1.x()), int(p1.y())
        x2, y2 = int(p2.x()), int(p2.y())
        if self.current_tool == "eraser":
            steps = max(abs(x2 - x1), abs(y2 - y1))
            if steps == 0:
                erase_on_layer(self.current_layer_index, x1, y1, self.brush_size)
            else:
                for i in range(steps + 1):
                    t = i / steps
                    x = int(x1 + t * (x2 - x1))
                    y = int(y1 + t * (y2 - y1))
                    erase_on_layer(self.current_layer_index, x, y, self.brush_size)
        else:
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

# Главное окно (расширенное)

class MainWindow(QMainWindow):
    def __init__(self, open_project_id=None):
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

        if open_project_id:
            QTimer.singleShot(500, lambda: self.try_open_project(open_project_id))

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

    # ---------------------- Меню (расширенное) ----------------------
    def _create_menu_bar(self):
        menubar = self.menuBar()
        # Файл
        file_menu = menubar.addMenu("&Файл")
        file_menu.addAction("Новый").triggered.connect(self.new_project_from_template)
        file_menu.addAction("Открыть...").triggered.connect(self.open_project_local)
        file_menu.addAction("Сохранить").triggered.connect(self.save_project_local)
        file_menu.addSeparator()
        file_menu.addAction("Импорт PSD...").triggered.connect(self.import_psd_file)
        file_menu.addAction("Экспорт PDF...").triggered.connect(self.export_pdf)
        file_menu.addAction("Экспорт PNG...").triggered.connect(self.export_png)
        file_menu.addSeparator()
        file_menu.addAction("Выход").triggered.connect(self.close)

        # Правка
        edit_menu = menubar.addMenu("&Правка")
        self.undo_act = edit_menu.addAction("Отменить")
        self.undo_act.setShortcut(QKeySequence.Undo)
        self.undo_act.triggered.connect(self.undo_action)
        self.redo_act = edit_menu.addAction("Повторить")
        self.redo_act.setShortcuts([
            QKeySequence(Qt.CTRL + Qt.Key_Y),
            QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Z)
        ])
        self.redo_act.triggered.connect(self.redo_action)

        # Вид
        view_menu = menubar.addMenu("&Вид")
        view_menu.addAction("Показать панели").triggered.connect(self.toggle_panels)

        # Слой (новое)
        layer_menu = menubar.addMenu("&Слой")
        # Поворот
        rotate_menu = layer_menu.addMenu("Повернуть")
        rotate_menu.addAction("90° по часовой").triggered.connect(self.rotate_90_cw)
        rotate_menu.addAction("90° против часовой").triggered.connect(self.rotate_90_ccw)
        rotate_menu.addAction("180°").triggered.connect(self.rotate_180)
        rotate_menu.addAction("Произвольный...").triggered.connect(self.rotate_arbitrary)
        layer_menu.addSeparator()
        layer_menu.addAction("Масштабировать...").triggered.connect(self.scale_layer)
        layer_menu.addAction("Обрезать...").triggered.connect(self.crop_layer)
        layer_menu.addSeparator()
        # Фильтры
        filters_menu = layer_menu.addMenu("Фильтры")
        brightness_menu = filters_menu.addMenu("Яркость")
        brightness_menu.addAction("+10").triggered.connect(self.brightness_plus)
        brightness_menu.addAction("-10").triggered.connect(self.brightness_minus)
        contrast_menu = filters_menu.addMenu("Контраст")
        contrast_menu.addAction("+10").triggered.connect(self.contrast_plus)
        contrast_menu.addAction("-10").triggered.connect(self.contrast_minus)

        # Изображение (новое)
        image_menu = menubar.addMenu("&Изображение")
        image_menu.addAction("Размер холста...").triggered.connect(self.resize_canvas_dialog)

        # Облако
        cloud_menu = menubar.addMenu("&Облако")
        cloud_menu.addAction("Сохранить в облако").triggered.connect(self.save_to_cloud)
        cloud_menu.addAction("Загрузить из облака").triggered.connect(self.load_from_cloud)
        cloud_menu.addAction("Мои проекты").triggered.connect(self.show_cloud_projects)
        cloud_menu.addSeparator()
        cloud_menu.addAction("Вход").triggered.connect(self.login_cloud)
        cloud_menu.addAction("Регистрация").triggered.connect(self.login_cloud)
        cloud_menu.addSeparator()
        cloud_menu.addAction("Поделиться").triggered.connect(self.share_project)

        # Помощь
        help_menu = menubar.addMenu("&Помощь")
        help_menu.addAction("О программе").triggered.connect(self.about_action)

    # (Старые методы (без изменений) 
    def toggle_panels(self):
        self.toolbar.setVisible(not self.toolbar.isVisible())
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
            QMessageBox.warning(self, "Ошибка", f"undo не поддержижается: {e}")

    def redo_action(self):
        try:
            res = redo()
            if res.get("status") == "ok":
                self.refresh_layers_list()
                self.canvas.update_canvas_image()
            else:
                QMessageBox.warning(self, "Ошибка", res.get("error", "Нечего повторять"))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"redo не поддержижается: {e}")

    def _create_toolbar(self):
        self.toolbar = QToolBar("Инструменты")
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)
        self.toolbar.setIconSize(QtCore.QSize(24, 24))

        tools = {
            "Кисть": ("brush", "brush.png"),
            "Ластик": ("eraser", "eraser-2.png"),
            "Пипетка": ("eyedropper", "pipette.png"),
            "Линия": ("line", "line.png"),
            "Прямоугольник": ("rectangle", "square-2.png"),
            "Круг": ("circle", "circle.png"),
            "Текст": ("text", "type-outline.png"),
            "Заливка": ("flood_fill", "paint-bucket-2.png"),
            "AI": ("ai", "bot.png"),   # <--- ИСПРАВЛЕНО: добавлен ключ "ai"
            "Удалить фон": ("remove_bg", "background.remover.png"),
            "Перемещение": ("move", "move.png"),
        }

        for name, (action_key, icon_file) in tools.items():
            if icon_file:
                icon_path = os.path.join("icons", icon_file)
                act = self.toolbar.addAction(QIcon(icon_path), name)
            else:
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
            elif action_key == "flood_fill":
                act.triggered.connect(lambda: self.canvas.set_tool("flood_fill"))
            elif action_key == "remove_bg":
                act.triggered.connect(self.remove_background)
            elif action_key == "move":
                act.triggered.connect(lambda: self.canvas.set_tool("move"))
            elif action_key == "ai":
                # Правильный вызов AI
                act.triggered.connect(lambda: handle_ai_generation(self))
            else:
                act.triggered.connect(lambda _, n=name: print(f"Инструмент '{n}' пока не реализован"))

        color_icon = os.path.join("icons", "palette.png")
        color_btn = self.toolbar.addAction(QIcon(color_icon), "Цвет")
        color_btn.setToolTip("Выбрать цвет для кисти и фигур")
        color_btn.triggered.connect(self.choose_color)

        cloud_icon = os.path.join("icons", "cloud-2.png")
        cloud_btn = self.toolbar.addAction(QIcon(cloud_icon), "Облако")
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
        self.title_label = QLabel("Graphitium")
        self.coords_label = QLabel("X: 0, Y: 0")
        self.zoom_label = QLabel("100%")
        self.statusBar.addWidget(self.title_label)
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
            link = res.get("url") or res.get("link")
            if link:
                clipboard = QGuiApplication.clipboard()
                clipboard.setText(link)
                QMessageBox.information(self, "Ссылка скопирована", f"Ссылка для просмотра:\n{link}\n\nСкопирована в буфер обмена.")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить ссылку")
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

    def try_open_project(self, project_id):
        if self.token:
            self.open_project_from_cloud(project_id)
        else:
            reply = QMessageBox.question(self, "Открытие проекта", 
                                         "Для открытия проекта нужно войти в облако. Выполнить вход сейчас?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.login_cloud()
                QTimer.singleShot(500, lambda: self.try_open_project(project_id))
            else:
                QMessageBox.information(self, "Отмена", "Проект не открыт. Войдите и повторите.")

    def open_project_from_cloud(self, project_id):
        if not self.token:
            QMessageBox.warning(self, "Ошибка", "Вы не вошли в облако")
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
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

    # ---------------------- НОВЫЕ МЕТОДЫ (экспорт PNG, импорт PSD, PDF, фильтры, повороты, масштаб, обрезка, размер холста) ----------------------
    def export_png(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Сохранить PNG", "", "PNG files (*.png)")
        if filepath:
            res = export_project(filepath)
            if res.get("status") == "ok":
                QMessageBox.information(self, "Успех", "PNG сохранён")
            else:
                QMessageBox.warning(self, "Ошибка", res.get("error", "Не удалось сохранить PNG"))

    def import_psd_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Выберите PSD-файл", "", "PSD files (*.psd)")
        if filepath:
            res = import_psd(filepath)
            if res.get("status") == "ok":
                self.refresh_layers_list()
                self.canvas.update_canvas_image()
                QMessageBox.information(self, "Успех", f"PSD загружен, слоёв: {res.get('layers')}")
            else:
                QMessageBox.warning(self, "Ошибка", res.get("error", "Не удалось импортировать PSD"))

    def export_pdf(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Сохранить PDF", "", "PDF files (*.pdf)")
        if filepath:
            res = export_to_pdf_api(filepath)
            if res.get("status") == "ok":
                QMessageBox.information(self, "Успех", "PDF сохранён")
            else:
                QMessageBox.warning(self, "Ошибка", res.get("error", "Не удалось сохранить PDF"))

    def rotate_90_cw(self):
        if self.current_layer_index is None:
            QMessageBox.warning(self, "Ошибка", "Выберите слой")
            return
        res = rotate_layer_api(self.current_layer_index, 90)
        if res.get("status") == "ok":
            self.refresh_layers_list()
            self.canvas.update_canvas_image()
        else:
            QMessageBox.warning(self, "Ошибка", res.get("error"))

    def rotate_90_ccw(self):
        if self.current_layer_index is None:
            QMessageBox.warning(self, "Ошибка", "Выберите слой")
            return
        res = rotate_layer_api(self.current_layer_index, -90)
        if res.get("status") == "ok":
            self.refresh_layers_list()
            self.canvas.update_canvas_image()
        else:
            QMessageBox.warning(self, "Ошибка", res.get("error"))

    def rotate_180(self):
        if self.current_layer_index is None:
            QMessageBox.warning(self, "Ошибка", "Выберите слой")
            return
        res = rotate_layer_api(self.current_layer_index, 180)
        if res.get("status") == "ok":
            self.refresh_layers_list()
            self.canvas.update_canvas_image()
        else:
            QMessageBox.warning(self, "Ошибка", res.get("error"))

    def rotate_arbitrary(self):
        if self.current_layer_index is None:
            QMessageBox.warning(self, "Ошибка", "Выберите слой")
            return
        angle, ok = QInputDialog.getDouble(self, "Произвольный поворот", "Угол (градусы):", 0, -360, 360, 1)
        if ok:
            res = rotate_layer_api(self.current_layer_index, angle)
            if res.get("status") == "ok":
                self.refresh_layers_list()
                self.canvas.update_canvas_image()
            else:
                QMessageBox.warning(self, "Ошибка", res.get("error"))

    def scale_layer(self):
        if self.current_layer_index is None:
            QMessageBox.warning(self, "Ошибка", "Выберите слой")
            return
        factor, ok = QInputDialog.getDouble(self, "Масштабирование слоя", "Коэффициент (например, 1.5 для увеличения, 0.5 для уменьшения):", 1.0, 0.1, 10.0, 2)
        if ok:
            res = scale_layer_api(self.current_layer_index, factor, factor)
            if res.get("status") == "ok":
                self.refresh_layers_list()
                self.canvas.update_canvas_image()
            else:
                QMessageBox.warning(self, "Ошибка", res.get("error"))

    def crop_layer(self):
        if self.current_layer_index is None:
            QMessageBox.warning(self, "Ошибка", "Выберите слой")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Обрезка слоя")
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        x_edit = QLineEdit("0")
        y_edit = QLineEdit("0")
        w_edit = QLineEdit("100")
        h_edit = QLineEdit("100")
        form.addRow("X:", x_edit)
        form.addRow("Y:", y_edit)
        form.addRow("Ширина:", w_edit)
        form.addRow("Высота:", h_edit)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec() == QDialog.Accepted:
            try:
                x = int(x_edit.text())
                y = int(y_edit.text())
                w = int(w_edit.text())
                h = int(h_edit.text())
            except:
                QMessageBox.warning(self, "Ошибка", "Некорректные числа")
                return
            res = crop_layer_api(self.current_layer_index, x, y, w, h)
            if res.get("status") == "ok":
                self.refresh_layers_list()
                self.canvas.update_canvas_image()
            else:
                QMessageBox.warning(self, "Ошибка", res.get("error"))

    def resize_canvas_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Размер холста")
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        width_edit = QLineEdit("800")
        height_edit = QLineEdit("600")
        anchor_combo = QComboBox()
        anchor_combo.addItems(["center", "top-left", "bottom-right"])
        form.addRow("Ширина:", width_edit)
        form.addRow("Высота:", height_edit)
        form.addRow("Якорь:", anchor_combo)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec() == QDialog.Accepted:
            try:
                new_w = int(width_edit.text())
                new_h = int(height_edit.text())
                anchor = anchor_combo.currentText()
            except:
                QMessageBox.warning(self, "Ошибка", "Некорректные числа")
                return
            res = resize_canvas_api(new_w, new_h, anchor)
            if res.get("status") == "ok":
                self.refresh_layers_list()
                self.canvas.update_canvas_image()
                QMessageBox.information(self, "Успех", f"Холст изменён на {new_w}x{new_h}")
            else:
                QMessageBox.warning(self, "Ошибка", res.get("error"))

    def brightness_plus(self):
        if self.current_layer_index is None:
            QMessageBox.warning(self, "Ошибка", "Выберите слой")
            return
        res = apply_filter_to_layer_api(self.current_layer_index, "brightness", 10)
        if res.get("status") == "ok":
            self.canvas.update_canvas_image()
        else:
            QMessageBox.warning(self, "Ошибка", res.get("error"))

    def brightness_minus(self):
        if self.current_layer_index is None:
            QMessageBox.warning(self, "Ошибка", "Выберите слой")
            return
        res = apply_filter_to_layer_api(self.current_layer_index, "brightness", -10)
        if res.get("status") == "ok":
            self.canvas.update_canvas_image()
        else:
            QMessageBox.warning(self, "Ошибка", res.get("error"))

    def contrast_plus(self):
        if self.current_layer_index is None:
            QMessageBox.warning(self, "Ошибка", "Выберите слой")
            return
        res = apply_filter_to_layer_api(self.current_layer_index, "contrast", 10)
        if res.get("status") == "ok":
            self.canvas.update_canvas_image()
        else:
            QMessageBox.warning(self, "Ошибка", res.get("error"))

    def contrast_minus(self):
        if self.current_layer_index is None:
            QMessageBox.warning(self, "Ошибка", "Выберите слой")
            return
        res = apply_filter_to_layer_api(self.current_layer_index, "contrast", -10)
        if res.get("status") == "ok":
            self.canvas.update_canvas_image()
        else:
            QMessageBox.warning(self, "Ошибка", res.get("error"))

# ----------------------------------------------------------------------
# Точка входа
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Graphitium графический редактор")
    parser.add_argument("--open-project-id", help="Открыть проект по ID из облака")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMainWindow { background-color: #0a0a0a; }
        QMenuBar { background-color: #1a1a1a; color: #e0e0e0; }
        QMenuBar::item:selected { background-color: #85ADFF; }
        QMenu { background-color: #1a1a1a; color: #e0e0e0; }
        QMenu::item:selected { background-color: #85ADFF; }
        QToolBar { background-color: #1a1a1a; border: none; spacing: 3px; }
        QToolButton { background-color: #1a1a1a; color: #e0e0e0; border-radius: 4px; padding: 4px; }
        QToolButton:hover { background-color: #2a2a2a; }
        QToolButton:pressed { background-color: #85ADFF; }
        QDockWidget { background-color: #1a1a1a; }
        QDockWidget::title { background-color: #2a2a2a; color: #e0e0e0; text-align: left; padding: 4px; }
        QWidget { background-color: #1a1a1a; color: #e0e0e0; }
        QPushButton { background-color: #2a2a2a; color: #e0e0e0; border: 1px solid #3a3a3a; border-radius: 4px; padding: 4px 8px; }
        QPushButton:hover { background-color: #3a3a3a; }
        QPushButton:pressed { background-color: #85ADFF; }
        QSlider::groove:horizontal { height: 6px; background: #3a3a3a; border-radius: 3px; }
        QSlider::handle:horizontal { background: #85ADFF; width: 14px; border-radius: 7px; margin: -4px 0; }
        QComboBox { background-color: #2a2a2a; color: #e0e0e0; border: 1px solid #3a3a3a; border-radius: 4px; padding: 4px; }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView { background-color: #2a2a2a; color: #e0e0e0; }
        QListWidget { background-color: #1a1a1a; color: #e0e0e0; border: 1px solid #3a3a3a; }
        QListWidget::item:selected { background-color: #85ADFF; }
        QStatusBar { background-color: #0a0a0a; color: #e0e0e0; }
        QScrollBar:vertical { background: #1a1a1a; width: 12px; border-radius: 6px; }
        QScrollBar::handle:vertical { background: #85ADFF; border-radius: 6px; min-height: 20px; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        QGraphicsView { background-color: #ffffff; }
    """)

    window = MainWindow(open_project_id=args.open_project_id)
    window.show()
    sys.exit(app.exec())