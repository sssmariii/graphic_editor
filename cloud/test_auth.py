import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud.auth.auth import register, login, get_user

def test_auth():
    print("Тест авторизации\n")
    
    # 1. Регистрация
    print("1. Регистрация...")
    reg = register("test@example.com", "123456")
    print(f"   {reg}")
    
    if not reg["ok"]:
        print("Ошибка регистрации")
        return
    
    # 2. Попытка зарегистрировать того же пользователя
    print("\n2. Повторная регистрация (должна быть ошибка)...")
    reg2 = register("test@example.com", "123456")
    print(f"   {reg2}")
    
    # 3. Вход с правильным паролем
    print("\n3. Вход с правильным паролем...")
    auth = login("test@example.com", "123456")
    print(f"   {auth}")
    
    # 4. Вход с неправильным паролем
    print("\n4. Вход с неправильным паролем...")
    auth2 = login("test@example.com", "wrong")
    print(f"   {auth2}")
    
    # 5. Получить информацию о пользователе
    if auth["ok"]:
        print("\n5. Получение информации о пользователе...")
        user_info = get_user(auth["token"])
        print(f"   {user_info}")
    
    print("\n=== Тест авторизации пройден ===")

if __name__ == "__main__":
    test_auth()