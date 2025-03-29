# سیستم مدیریت سرویس دوره‌ای خودرو

این پروژه یک سیستم مدیریت سرویس دوره‌ای خودرو است که به تعمیرکاران اجازه می‌دهد سوابق سرویس خودروها را مدیریت کنند و به مشتریان اجازه می‌دهد وضعیت سرویس خودروی خود را پیگیری کنند.

## ویژگی‌ها

- ثبت و مدیریت سرویس‌های خودرو
- ارسال یادآوری خودکار برای سرویس دوره‌ای
- پیگیری وضعیت سرویس توسط مشتری از طریق پیامک
- پنل مدیریت برای تعمیرکاران
- گزارش‌گیری از سوابق سرویس

## نیازمندی‌ها

- Python 3.8+
- Django 4.2+
- MySQL
- کلید API کاوه‌نگار

## نصب و راه‌اندازی

1. نصب پکیج‌های مورد نیاز:
```bash
pip install -r requirements.txt
```

2. تنظیم متغیرهای محیطی در فایل .env:
```
KAVENEGAR_API_KEY=your_api_key
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
```

3. اجرای مایگریشن‌ها:
```bash
python manage.py migrate
```

4. ایجاد کاربر ادمین:
```bash
python manage.py createsuperuser
```

5. اجرای سرور توسعه:
```bash
python manage.py runserver
```

## API Endpoints

- `POST /api/customer/service-status/`: استعلام وضعیت سرویس توسط مشتری
- `GET /api/cars/`: لیست خودروها
- `POST /api/cars/`: ثبت خودروی جدید
- `GET /api/services/`: لیست سرویس‌ها
- `POST /api/services/`: ثبت سرویس جدید

## مجوزها

این پروژه تحت مجوز MIT منتشر شده است. 