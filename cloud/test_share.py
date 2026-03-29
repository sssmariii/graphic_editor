import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud.auth.auth import register, login
from cloud.cloud_saver import save_project_to_cloud
from cloud.share import create_share_link, get_project_by_share_code, revoke_share_link

def test_share():
    print("Тест шаринга\n")
    
    # 1. Регистрация и вход
    register("share@test.com", "123456")
    auth = login("share@test.com", "123456")
    token = auth["token"]
    
    # 2. Создаём проект
    test_project = {"width": 800, "height": 600, "layers": []}
    saved = save_project_to_cloud(test_project, token, "Шаринг проект")
    project_id = saved["project_id"]
    print(f"1. Создан проект: {project_id}")
    
    # 3. Создаём ссылку для просмотра
    link = create_share_link(project_id, token, can_edit=False)
    print(f"2. Ссылка для просмотра: {link.get('link')}")
    
    # 4. Открываем по ссылке
    share_code = link["code"]
    opened = get_project_by_share_code(share_code)
    print(f"3. Открыт по ссылке: can_edit={opened.get('can_edit')}")
    
    # 5. Создаём ссылку с редактированием
    link_edit = create_share_link(project_id, token, can_edit=True)
    print(f"4. Ссылка с редактированием: {link_edit.get('link')}")
    
    # 6. Отзываем ссылку
    revoked = revoke_share_link(share_code, token)
    print(f"5. Ссылка отозвана: {revoked.get('ok')}")
    
    print("\nТест шаринга пройден")

if __name__ == "__main__":
    test_share()