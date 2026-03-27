# SecuLog-Local Kapsamlı Çalıştırma ve Temizlik Rehberi

Bu rehber, projenin **sıfırdan ayağa kaldırılması**, günlük olarak **kapatılması** ve işleminiz tamamen bittiğinde sistemde hiçbir artık veya Docker kalıntısı kalmayacak şekilde **tamamen temizlenmesi** için hazırlanmıştır.

---

## 🚀 1. Uygulamayı Baştan Çalıştırma (Start)

Uygulamanın mimarisi 3 farklı koldan oluşur ve sırayla çalıştırılmaları gerekir. Bu işlemler için terminal/komut satırı kullanmalısınız. Tüm işlemler projenin ana klasöründe (`SecuLog-Local`) yapılmalıdır.

### Adım 1: Veritabanını (PostgreSQL) Başlatmak
Önce veritabanı Docker üzerinde başlatılmalıdır:
```bash
# Projenin ana klasöründeyken:
docker-compose up -d
```
*(Eğer daha önce indirdiyseniz hemen saniyeler içinde bağlanacaktır. İlk kez çalıştırıyorsanız imajın inmesi biraz sürebilir. `-d` parametresi arka planda sessiz çalışmasını sağlar.)*

### Adım 2: Backend (Python API) Sunucusunu Çalıştırmak
İkinci bir terminal açın ve Python sanal ortamını aktif edip API'yi başlatın:
```bash
# Projenin ana klasöründeyken:
cd backend-api
source venv/bin/activate
uvicorn main:app --reload
```
*(Bu komuttan sonra `Application startup complete` ve `Uvicorn running on http://127.0.0.1:8000` yazısını görmelisiniz.)*

### Adım 3: Frontend (React) Arayüzünü Çalıştırmak
Üçüncü bir terminal açın ve React uygulamanızı başlatın:
```bash
# Projenin ana klasöründeyken:
cd frontend-ui
npm run dev
```
*(Terminalde beliren `http://localhost:5173/` veya benzeri URL'ye tıklayarak SecuLog-Local arayüzünüze erişebilirsiniz.)*

---

## 🛑 2. Uygulamayı Geçici Olarak Durdurma (Stop)

İşiniz bittiğinde veya ertesi gün devam etmek üzere sistemi askıya alacağınız zamanki adımlardır. Verileriniz kalıcı olarak **saklanmaya** devam eder.

1. **Frontend'i Kapatmak:** React'in çalıştığı terminale gidin ve `CTRL + C` tuşlarına aynı anda basarak işlemi sonlandırın.
2. **Backend'i Kapatmak:** Python'un çalıştığı terminale gidin ve yine `CTRL + C` tuşlarına basarak Uvicorn'u kapatın.
3. **Veritabanını Kapatmak:** Ana proje dizininde yeni bir terminal açarak (veya varolanlarda) şu komutu girin:
   ```bash
   docker-compose stop
   ```
*(Bu işlem veritabanını sadece uyutur, girilen hedefler veya projeler asla silinmez.)*

---

## 🧹 3. Sistemi Kökünden Temizleme (Destructive Clean-Up)

Proje tamamen bittiyse ve bilgisayarınızda (Docker dahil) hiçbir veri izi kalmamasını istiyorsanız aşağıdaki adımları sırayla uygulayın. **DİKKAT: Görevleriniz, projeleriniz, veritabanına yazdığınız tüm kayıtlar KALICI OLARAK SİLİNECEKTİR.**

### Adım 1: Docker Veritabanını ve Volume'leri Silmek
Terminalde projenin ana klasöründeyken (`SecuLog-Local`):
```bash
docker-compose down -v --rmi all
```
*Bu komutun anlamları:*
- `down`: Konteyneri durdurur ve siler.
- `-v` (Volume): Oluşturulan kalıcı veritabanı saklama alanlarını (tüm verilerinizi) kökünden yok eder.
- `--rmi all`: Cihazınıza inmiş olan PostgreSQL 15 imajını da bilgisayardan siler.

### Adım 2: Bağımlılık (Cache / venv / node_modules) Dosyalarını Silmek
Sabit diskinizde yer kaplayan node kütüphanelerini ve Python sanal ortamını silmek isterseniz:
```bash
# Mac/Linux Cihazlar için (Ana klasördeyken):
rm -rf backend-api/venv
rm -rf frontend-ui/node_modules
```

*(Bu aşamadan sonra projenizi tekrar çalıştırmak isterseniz Faz 0'daki `npm install` ve `python -m venv` kurulum adımlarını en baştan yapmanız gerekecektir.)*
