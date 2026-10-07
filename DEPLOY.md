# Production deployment notları

## Gunicorn çalıştırma

Proje kök dizininde (manage.py'nin olduğu yerde):

```bash
gunicorn industrial_site.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

Socket kullanarak (Nginx ile birlikte):

```bash
gunicorn industrial_site.wsgi:application --bind unix:/run/gunicorn/socket --workers 3 --chdir /path/to/LOVESANAİ
```

---

## Nginx örnek ayarı (yorum: reverse proxy + static/media)

```nginx
# Örnek: /etc/nginx/sites-available/yourproject
# HTTPS için certificate ile birlikte kullanın (örn. Let's Encrypt).

upstream django {
    server unix:/run/gunicorn/socket fail_timeout=0;
    # veya: server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name example.com www.example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    client_max_body_size 20M;

    location /static/ {
        alias /var/www/yourproject/staticfiles/;
    }
    location /media/ {
        alias /var/www/yourproject/media/;
    }

    location / {
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://django;
    }
}
```

---

## Adım adım terminal komutları (production geçiş)

1. **Sunucuda proje dizinine geç**
   ```bash
   cd /var/www/yourproject
   ```

2. **Sanal ortam oluştur ve aktif et**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/macOS
   # Windows: venv\Scripts\activate
   ```

3. **Bağımlılıkları yükle**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ortam değişkenlerini ayarla**
   ```bash
   cp .env.production.example .env
   # .env dosyasını düzenleyin: SECRET_KEY, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, PAYTR_* vb.
   ```

5. **.env yükle (python-dotenv kullanıyorsanız Django otomatik yükler; yoksa export ile)**
   ```bash
   export $(grep -v '^#' .env | xargs)
   ```

6. **Migration uygula**
   ```bash
   python manage.py migrate
   ```

7. **Static dosyaları topla**
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Süper kullanıcı oluştur (admin için)**
   ```bash
   python manage.py createsuperuser
   ```

9. **Gunicorn ile test**
   ```bash
   gunicorn industrial_site.wsgi:application --bind 0.0.0.0:8000 --workers 3
   ```

10. **Systemd servisi veya Nginx + gunicorn socket ile sürekli çalıştırın; HTTPS sertifikası ekleyin.**
