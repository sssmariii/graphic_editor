import sys
import base64
import math
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QToolBar, QStatusBar,
    QDockWidget, QWidget, QVBoxLayout, QSlider, QComboBox, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QHBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QInputDialog, QMessageBox, QColorDialog, QDialog, QDialogButtonBox
)
from PySide6 import QtCore
from PySide6.QtCore import Qt, QPointF, QUrl
from PySide6.QtGui import QPainter, QMouseEvent, QPen, QColor, QBrush, QWheelEvent, QIcon, QPixmap, QDesktopServices

from api.editor_api import (
    create_project, add_layer, get_layers,
    set_layer_visibility, set_layer_opacity, set_layer_blend_mode,
    remove_layer, set_layer_locked, get_combined_image,
    draw_on_layer, draw_line_on_layer
)

from cloud import (
    register, login, save_project_to_cloud, load_project_from_cloud,
    list_user_projects
)


try:
    from api.editor_api import draw_text_on_layer
    TEXT_SUPPORT = True
except ImportError:
    TEXT_SUPPORT = False
    print(" Функция draw_text_on_layer не найдена. Текст не будет рисоваться.")

#  Диалог выбора шаблона 
class TemplateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор шаблона")
        self.setModal(True)
        layout = QVBoxLayout(self)
        
        self.template_list = QListWidget()
        self.templates = []
        templates_dir = "templates"
        if os.path.exists(templates_dir):
            for f in sorted(os.listdir(templates_dir)):
                if f.lower().endswith('.png'):
                    self.templates.append(f)
        if not self.templates:
            self.templates = [f"template{i}.png" for i in range(1, 11)]
        
        for t in self.templates:
            self.template_list.addItem(t)
        
        layout.addWidget(QLabel("Выберите шаблон для нового проекта:"))
        layout.addWidget(self.template_list)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_selected_template(self):
        if self.template_list.currentItem():
            return self.template_list.currentItem().text()
        return None

#  Холст с рисованием 
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
        self.brush_size = 10
        self.brush_color = "#000000"   
        self.last_color = "#000000"    
        self.current_layer_index = 0

        self.pixmap_item = QGraphicsPixmapItem()
        self.scene().addItem(self.pixmap_item)

    def set_tool(self, tool):
        # Запоминаем предыдущий цвет перед переключением на ластик
        if tool == "eraser" and self.current_tool != "eraser":
            self.last_color = self.brush_color
            self.brush_color = "#FFFFFF"   # белый (ластик)
        elif tool != "eraser" and self.current_tool == "eraser":
            # Возвращаем цвет, который был до ластика
            self.brush_color = self.last_color
        self.current_tool = tool

    def set_brush_size(self, size):
        self.brush_size = size

    def set_brush_color(self, color_hex):
        self.brush_color = color_hex
        # Если мы не в режиме ластика, запоминаем цвет для возврата
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

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if self.current_tool == "text":
                self.add_text_at_position(self.mapToScene(event.pos()))
                return
            self.drawing = True
            self.start_point = self.mapToScene(event.pos())
            self.end_point = self.start_point
            if self.current_tool == "brush" or self.current_tool == "eraser":
                self.draw_point(self.start_point)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drawing:
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
            self.update_canvas_image()

    def add_text_at_position(self, point):
        x, y = int(point.x()), int(point.y())
        text, ok = QInputDialog.getText(self.window(), "Ввод текста", "Введите текст:")
        if ok and text:
            if TEXT_SUPPORT:
                draw_text_on_layer(self.current_layer_index, x, y, text, self.brush_color, 20)
                self.update_canvas_image()
            else:
                QMessageBox.warning(self.window(), "Ошибка", "Функция рисования текста не поддерживается бэкендом. Попросите Лизу добавить draw_text_on_layer.")

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

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.scale(factor, factor)
        main_window = self.window()
        if hasattr(main_window, 'update_zoom'):
            main_window.update_zoom(self.transform().m11() * 100)


#  Главное окно 
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graphitium")
        self.resize(1400, 900)
        self.current_layer_index = 0
        self.token = None

        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        self._create_right_panel()
        self._create_layers_panel()
        self._create_canvas()

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
        file_menu.addAction("Новый")
        file_menu.addAction("Открыть...")
        file_menu.addAction("Сохранить")
        file_menu.addSeparator()
        file_menu.addAction("Выход")
        file_menu.actions()[0].triggered.connect(self.new_project_from_template)

        edit_menu = menubar.addMenu("&Правка")
        edit_menu.addAction("Отменить")
        edit_menu.addAction("Повторить")

        view_menu = menubar.addMenu("&Вид")
        view_menu.addAction("Показать панели")

        cloud_menu = menubar.addMenu("&Облако")
        cloud_menu.addAction("Сохранить в облако")
        cloud_menu.addAction("Загрузить из облака")
        cloud_menu.addAction("Мои проекты")
        cloud_menu.addSeparator()
        cloud_menu.addAction("Вход")
        cloud_menu.addAction("Регистрация")

        help_menu = menubar.addMenu("&Помощь")
        help_menu.addAction("О программе")

        cloud_menu.actions()[0].triggered.connect(self.save_to_cloud)
        cloud_menu.actions()[1].triggered.connect(self.load_from_cloud)
        cloud_menu.actions()[2].triggered.connect(self.show_cloud_projects)
        cloud_menu.actions()[4].triggered.connect(self.login_cloud)
        cloud_menu.actions()[5].triggered.connect(self.register_cloud)

    def _create_toolbar(self):
        toolbar = QToolBar("Инструменты")
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        toolbar.setIconSize(QtCore.QSize(24, 24))

        tools = {
            "Кисть": "paintbrush.png",
            "Ластик": "eraser.png",
            "Линия": "remove.png",
            "Прямоугольник": "square.png",
            "Круг": "dry-clean.png",
            "Текст": "typography.png",
            "Заливка": "paint-bucket.png",
            "Пипетка": "water-droplet.png",
            "Лупа": "loupe.png",
            "Перемещение": "arrow.png"
        }

        for tool_name, icon_file in tools.items():
            icon_path = f"icons/{icon_file}"
            action = toolbar.addAction(QIcon(icon_path), tool_name)
            if tool_name == "Кисть":
                action.triggered.connect(lambda: self.canvas.set_tool("brush"))
            elif tool_name == "Ластик":
                action.triggered.connect(lambda: self.canvas.set_tool("eraser"))
            elif tool_name == "Линия":
                action.triggered.connect(lambda: self.canvas.set_tool("line"))
            elif tool_name == "Прямоугольник":
                action.triggered.connect(lambda: self.canvas.set_tool("rectangle"))
            elif tool_name == "Круг":
                action.triggered.connect(lambda: self.canvas.set_tool("circle"))
            elif tool_name == "Текст":
                action.triggered.connect(lambda: self.canvas.set_tool("text"))
            else:
                action.triggered.connect(lambda _, n=tool_name: print(f"Инструмент '{n}' пока не реализован"))

        # Кнопка выбора цвета с иконкой
        color_btn = toolbar.addAction(QIcon("icons/art.png"), "Цвет")
        color_btn.triggered.connect(self.choose_color)

        # Кнопка облака с иконкой
        cloud_btn = toolbar.addAction(QIcon("icons/cloud.png"), "Облако")
        cloud_btn.triggered.connect(self.open_cloud_web)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_brush_color(color.name())
            print(f"Выбран цвет: {color.name()}")

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
        layout.addStretch()
        dock.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def _create_layers_panel(self):
        dock = QDockWidget("Слои", self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.layers_list = QListWidget()
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

    #  Облачные функции
    def open_cloud_web(self):
        QDesktopServices.openUrl(QUrl("http://localhost:5000"))

    def save_to_cloud(self):
        if not self.token:
            QMessageBox.warning(self, "Ошибка", "Сначала войдите в облако (меню Облако -> Вход)")
            return
        from api.editor_api import export_project_to_cloud
        result = export_project_to_cloud()
        if result.get("status") != "ok":
            QMessageBox.warning(self, "Ошибка", result.get("error", "Не удалось экспортировать проект"))
            return
        project_data = result["project_data"]
        name, ok = QInputDialog.getText(self, "Сохранить в облако", "Название проекта:")
        if ok and name:
            cloud_res = save_project_to_cloud(project_data, self.token, name)
            if cloud_res.get("status") == "ok":
                QMessageBox.information(self, "Успех", "Проект сохранён в облако")
            else:
                QMessageBox.warning(self, "Ошибка", cloud_res.get("error", "Неизвестная ошибка"))

    def load_from_cloud(self):
        if not self.token:
            QMessageBox.warning(self, "Ошибка", "Сначала войдите в облако")
            return
        projects = list_user_projects(self.token)
        if projects.get("status") != "ok":
            QMessageBox.warning(self, "Ошибка", projects.get("error", "Не удалось получить список проектов"))
            return
        if not projects["projects"]:
            QMessageBox.information(self, "Информация", "У вас нет проектов в облаке")
            return
        project_id = projects["projects"][0]["id"]
        data = load_project_from_cloud(project_id, self.token)
        if data.get("status") == "ok":
            from api.editor_api import import_project_from_cloud
            import_project_from_cloud(data["project_data"])
            self.refresh_layers_list()
            self.canvas.update_canvas_image()
            QMessageBox.information(self, "Успех", "Проект загружен из облака")
        else:
            QMessageBox.warning(self, "Ошибка", data.get("error", "Не удалось загрузить проект"))

    def show_cloud_projects(self):
        QDesktopServices.openUrl(QUrl("http://localhost:5000"))

    def login_cloud(self):
        email, ok1 = QInputDialog.getText(self, "Вход в облако", "Email:")
        if not ok1 or not email:
            return
        password, ok2 = QInputDialog.getText(self, "Вход в облако", "Пароль:", QLineEdit.Password)
        if not ok2:
            return
        res = login(email, password)
        if res.get("status") == "ok":
            self.token = res.get("token")
            QMessageBox.information(self, "Успех", "Вход выполнен")
        else:
            QMessageBox.warning(self, "Ошибка", res.get("error", "Неверные данные"))

    def register_cloud(self):
        email, ok1 = QInputDialog.getText(self, "Регистрация", "Email:")
        if not ok1 or not email:
            return
        password, ok2 = QInputDialog.getText(self, "Регистрация", "Пароль:", QLineEdit.Password)
        if not ok2:
            return
        name, ok3 = QInputDialog.getText(self, "Регистрация", "Имя:")
        if not ok3:
            return
        res = register(email, password, name)
        if res.get("status") == "ok":
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно")
        else:
            QMessageBox.warning(self, "Ошибка", res.get("error", "Ошибка регистрации"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())