## Industrial Site – B2B Bayi Sipariş Sistemi

Django ile kurumsal site ve web tabanlı B2B bayi sipariş sistemi. SQLite, Bootstrap.

### Özellikler

- **Bayi paneli**
  - Bayi girişi (login)
  - Ürün listesi: fotoğraf, ürün adı, fiyat, stok adedi
  - Ürün arama + kategori filtre
  - Sepet: adet seç, sepete ekle, toplam tutar
  - Sipariş oluştur: teslimat adresi + sipariş notu
  - Sipariş geçmişi ve sipariş durumu takibi
- **Admin panel**
  - Ürün yönetimi: ad, açıklama, fiyat, stok, kategori, fotoğraf
  - Kategori yönetimi
  - Bayi kullanıcıları (DealerProfile; isteğe bağlı “Dealer” grubu)
  - Sipariş yönetimi: listele, detay, durum değiştir
- **Sipariş durumları**  
  Beklemede → Onaylandı → Hazırlanıyor → Kargoda → Teslim / İptal
- **Stok kuralı**  
  Bayi sipariş oluşturunca stok düşmez. Admin siparişi **Onaylandı** yaptığında stok otomatik düşer; stok yetersizse onay verilmez ve uyarı gösterilir.

### Gereksinimler

- Python 3.11+
- Sanal ortam (proje içinde `venv` kullanılabilir)

### Kurulum ve çalıştırma

1. **Sanal ortamı etkinleştir**
   ```bash
   cd path/to/LOVESANAİ
   venv\Scripts\activate
   ```

2. **Bağımlılıkları yükle** (Pillow ürün fotoğrafları için gerekli)
   ```bash
   pip install -r requirements.txt
   ```

3. **Veritabanı**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Sunucuyu başlat**
   ```bash
   python manage.py runserver
   ```
   Tarayıcıda: `http://127.0.0.1:8000/`

### Kullanım

- **Bayi**
  - Kayıt: `/dealer/register/`
  - Giriş: `/dealer/login/`
  - Admin, ilgili kullanıcı için **DealerProfile** oluşturup **is_approved** işaretlemeli (veya kullanıcı kendisi kayıt olmuşsa sadece onay verilmeli).
  - Onaylı bayiler: Ürünler, Sepet, Siparişi tamamla, Siparişlerim sayfalarına erişir.
- **Admin** (`/admin/`)
  - **Kategoriler**: Ürün kategorileri (ad, slug).
  - **Ürünler**: Ad, açıklama, fiyat, stok, kategori, fotoğraf.
  - **DealerProfile**: Bayi firma bilgisi, onay (is_approved).
  - **Siparişler**: Listele, detay, teslimat adresi/not, durum. Siparişi **Onaylandı** yapınca stok düşer; yetersizse kaydetmez ve uyarı verir.
- **Dealer grubu (isteğe bağlı)**  
  Admin → Authentication and Authorization → Groups → “Dealer” adında grup oluşturup bayi kullanıcılarını bu gruba ekleyebilirsiniz. Erişim kontrolü uygulama tarafında **DealerProfile** ve **is_approved** ile yapılmaktadır.

### Yetkilendirme

- Bayi: Sadece bayi sayfaları (ürünler, sepet, checkout, siparişler). Onaylı olmayan bayiler sadece dashboard görür ve uyarı alır.
- Admin (staff): Django admin’e tam erişim; gerekirse bayi paneli sayfalarına da girebilir.

### Medya (ürün fotoğrafları)

- `MEDIA_URL` ve `MEDIA_ROOT` ayarlı. Geliştirme ortamında medya dosyaları `runserver` ile sunulur.
- Ürün fotoğrafı yüklemek: Admin → Ürünler → ilgili ürün → Image alanı.

### Genel

- Bootstrap ile arayüz.
- SQLite kullanılır; mevcut yapı korunarak B2B akışı eklenmiştir.
