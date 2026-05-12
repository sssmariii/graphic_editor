import requests
import base64
import os
from PIL import Image
import io
from PySide6.QtWidgets import QInputDialog, QMessageBox, QApplication
from PySide6.QtCore import Qt

def handle_ai_generation(main_window):
    prompt, ok = QInputDialog.getText(main_window, "AI Генерация", 
                                      "Введите описание изображения:", 
                                      text="красивое небо, горы, закат")
    if not ok or not prompt.strip():
        return

    QApplication.setOverrideCursor(Qt.WaitCursor)

    try:
        url = "http://localhost:5000/api/ai/generate"
        response = requests.post(url, json={"prompt": prompt}, timeout=60)
        
        if response.status_code != 200:
            QMessageBox.warning(main_window, "Ошибка", 
                                f"Сервер вернул ошибку {response.status_code}")
            return

        data = response.json()
        if not data.get("ok"):
            QMessageBox.warning(main_window, "Ошибка AI", 
                                data.get("error", "Неизвестная ошибка"))
            return

        image_base64 = data.get("image_base64")
        if not image_base64:
            QMessageBox.warning(main_window, "Ошибка", "Сервер не вернул изображение")
            return

        image_bytes = base64.b64decode(image_base64)
        pil_image = Image.open(io.BytesIO(image_bytes))

        temp_path = "temp_ai_image.png"
        pil_image.save(temp_path)

        from api.editor_api import add_layer, get_project_info, scale_layer_api, set_layer_position
        result = add_layer("AI Generated", image_path=temp_path)
        
        if result.get("status") == "ok":
            layer_index = result.get("layer_index")
            if layer_index is not None:
                info = get_project_info()
                if info and "width" in info:
                    canvas_w = info["width"]
                    canvas_h = info["height"]
                    img_w, img_h = pil_image.size
                    # Масштабируем под размер холста
                    scale_x = canvas_w / img_w
                    scale_y = canvas_h / img_h
                    scale_layer_api(layer_index, scale_x, scale_y)
                    # После масштабирования сдвигаем в (0,0)
                    set_layer_position(layer_index, 0, 0)
            
            main_window.refresh_layers_list()
            main_window.canvas.update_canvas_image()
            QMessageBox.information(main_window, "Успех", 
                                    "Изображение сгенерировано и добавлено как новый слой")
        else:
            QMessageBox.warning(main_window, "Ошибка", 
                                result.get("error", "Не удалось добавить слой"))

        try:
            os.remove(temp_path)
        except:
            pass

    except requests.exceptions.ConnectionError:
        QMessageBox.warning(main_window, "Ошибка", 
                            "Не удалось подключиться к серверу AI.\n"
                            "Запустите cloud/web_server.py и попробуйте снова.")
    except Exception as e:
        QMessageBox.warning(main_window, "Ошибка", f"Что-то пошло не так:\n{e}")
    finally:
        QApplication.restoreOverrideCursor()