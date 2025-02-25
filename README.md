# 🍔 Cafe Order Management System

Система управления заказами для кафе на Django с возможностью:
- Создания/редактирования/удаления заказов
- Отслеживания статусов заказов
- Просмотра статистики выручки
- Управления меню блюд

## 🚀 Начало работы

### Требования
- Docker >= 20.10
- Docker Compose >= 1.29
- Python 3.9+ (опционально)

### Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/AndreyMelman/django-cafe-manager-project.git
   ```
2. Для быстрого запуска приложения запустите:

   ```bash
   docker compose up --build
   ```


Приложение будет доступно по адресу [http://localhost:8000](http://127.0.0.1:8000).

3. Создайте суперпользователя для доступа к админке:

   ```bash
   docker compose exec web python manage.py createsuperuser
   ```
4. API Endpoints
Доступны через DRF:

    - GET /api/orders/ - список заказов
    - POST /api/orders/ - создание заказа
    - GET /api/orders/{id}/ - детали заказа
    - PUT/PATCH /api/orders/{id}/ - обновление заказа
    - DELETE /api/orders/{id}/ - удаление заказа
    - POST /api/orders/{id}/add_items/ - добавление позиций
    - POST /api/orders/{id}/update_status/ - обновление статуса
    - GET /api/orders/statistics/ - статистика по заказам