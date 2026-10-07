# Procfile (Heroku / systemd / manuel gunicorn için örnek)
# Web process: gunicorn ile WSGI uygulamasını çalıştırır.
# Proje kökünden çalıştırın: gunicorn industrial_site.wsgi:application

web: gunicorn industrial_site.wsgi:application --bind 0.0.0.0:8000 --workers 3
