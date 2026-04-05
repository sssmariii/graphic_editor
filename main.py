import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QToolBar, QStatusBar,
    QDockWidget, QWidget, QVBoxLayout, QSlider, QComboBox, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QHBoxLayout,
    QGraphicsView, QGraphicsScene
)
from PySide6 import QtCore
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QMouseEvent, QPen, QColor, QBrush, QWheelEvent, QIcon

from api.editor_api import (
    create_project, add_layer, get_layers,
    set_layer_visibility, set_layer_opacity, set_layer_blend_mode,
    remove_layer
)


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
        self.last_point = QPointF()
        self.current_tool = "brush"
        self.brush_size = 10
        self.brush_color = QColor(0, 0, 0)      # чёрный

    def set_tool(self, tool):
        self.current_tool = tool
        if tool == "eraser":
            self.brush_color = QColor(255, 255, 255)  # белый (ластик)
        else:
            self.brush_color = QColor(0, 0, 0)        # чёрный

    def set_brush_size(self, size):
        self.brush_size = size

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = self.mapToScene(event.pos())
            self.draw_point(self.last_point)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drawing:
            current_point = self.mapToScene(event.pos())
            self.draw_line(self.last_point, current_point)
            self.last_point = current_point
            main_window = self.window()
            if hasattr(main_window, 'update_coords'):
                main_window.update_coords(event.pos())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def draw_point(self, point):
        pen = QPen(self.brush_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.scene().addEllipse(point.x() - self.brush_size/2,
                                 point.y() - self.brush_size/2,
                                 self.brush_size, self.brush_size, pen, QBrush(self.brush_color))

    def draw_line(self, p1, p2):
        pen = QPen(self.brush_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.scene().addLine(p1.x(), p1.y(), p2.x(), p2.y(), pen)

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.scale(factor, factor)
        main_window = self.window()
        if hasattr(main_window, 'update_zoom'):
            main_window.update_zoom(self.transform().m11() * 100)

# Главное окно 
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graphitium")
        self.resize(1400, 900)
        self.current_layer_index = 0

        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        self._create_right_panel()
        self._create_layers_panel()
        self._create_canvas()

        create_project(800, 600)
        add_layer("Фоновый слой")
        print("✅ Проект создан, добавлен слой")
        self.refresh_layers_list()

    def _create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Файл")
        file_menu.addAction("Новый")
        file_menu.addAction("Открыть...")
        file_menu.addAction("Сохранить")
        file_menu.addSeparator()
        file_menu.addAction("Выход")
        edit_menu = menubar.addMenu("&Правка")
        edit_menu.addAction("Отменить")
        edit_menu.addAction("Повторить")
        view_menu = menubar.addMenu("&Вид")
        view_menu.addAction("Показать панели")
        help_menu = menubar.addMenu("&Помощь")
        help_menu.addAction("О программе")

    def _create_toolbar(self):
        toolbar = QToolBar("Инструменты")
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        toolbar.setIconSize(QtCore.QSize(24, 24))   # размер иконок

        
        tools = {
            "Кисть": "paintbrush.png",
            "Ластик": "eraser.png",
            "Текст": "typography.png",
            "Прямоугольник": "square.png",
            "Круг": "dry-clean.png",
            "Линия": "remove.png",
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
            else:
                action.triggered.connect(lambda _, n=tool_name: print(f"Инструмент '{n}' пока не реализован"))

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

            lock_btn = QPushButton("🔓")
            lock_btn.setFixedSize(30, 25)
            lock_btn.setCheckable(True)
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
        else:
            print("Ошибка видимости:", res.get("error"))

    def toggle_lock(self, layer_index, locked):
        # Заглушка блокировки (интерфейсная)
        print(f"Слой {layer_index} {'заблокирован' if locked else 'разблокирован'} (заглушка)")

    def add_new_layer(self):
        new_name = f"Слой {len(get_layers().get('layers', [])) + 1}"
        res = add_layer(new_name)
        if res.get("status") == "ok":
            self.refresh_layers_list()
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
        else:
            print("Ошибка удаления слоя:", res.get("error"))

    def on_opacity_changed(self, value):
        res = set_layer_opacity(self.current_layer_index, value)
        if res.get("status") != "ok":
            print("Ошибка прозрачности:", res.get("error"))

    def on_blend_mode_changed(self, mode):
        res = set_layer_blend_mode(self.current_layer_index, mode)
        if res.get("status") != "ok":
            print("Ошибка режима наложения:", res.get("error"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())