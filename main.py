import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QToolBar, QStatusBar
from PySide6.QtCore import Qt


from api.editor_api import create_project, add_layer, get_layers

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graphitium")
        self.resize(1400, 900)
        
        
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        
       
        create_project(800, 600)
        add_layer("Фоновый слой") 
        print(" Проект создан, добавлен слой")
        
        
        layers_info = get_layers()
        if "layers" in layers_info:
            print(f" Слоёв в проекте: {len(layers_info['layers'])}")
        else:
            print(" Ошибка получения слоёв:", layers_info.get("error"))
    
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
        tools = ["Кисть", "Ластик", "Текст", "Прямоугольник", "Круг",
                 "Линия", "Заливка", "Пипетка", "Лупа", "Перемещение"]
        for name in tools:
            toolbar.addAction(name)
    
    def _create_status_bar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Готово")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())