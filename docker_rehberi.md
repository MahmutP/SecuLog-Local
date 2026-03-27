# Docker ile PostgreSQL Kurulum ve Başlatma Rehberi

SecuLog-Local projesi veritabanı olarak **PostgreSQL** kullanmaktadır. Geliştirme sürecinde bilgisayarınıza kalıcı bir veritabanı kurmamak ve izole bir ortamda çalışmak için **Docker** tercih edilmiştir. Aşağıdaki adımlarla saniyeler içinde veritabanınızı çalıştırabilirsiniz.

## Adım 1: Docker'ın Kurulu Olduğundan Emin Olun
Sisteminizde (Mac/Windows/Linux) Docker Desktop veya Docker Engine'in çalıştığından emin olmak için terminale şu komutu yazın:
```bash
docker --version
```
*Eğer sürüm numarası görüyorsanız Docker çalışıyor demektir.*

## Adım 2: Veritabanını Ayağa Kaldırma (Docker Compose ile)

Projenin kök dizininde yer alan `docker-compose.yml` dosyası, PostgreSQL veritabanını çalıştırmak için gerekli tüm ayarları (kullanıcı: `seculog_user`, şifre: `seculog_pass`, db: `seculog`) içerisinde barındırır. Ayrıca verilerinizin kaybolmaması için kalıcı bir volume (`seculog_pgdata`) tanımlanmıştır.

Terminalinizi açıp projenin **kök dizininde** (yani `docker-compose.yml` dosyasının olduğu `/Users/mahmutpasa/Desktop/Antigravity/SecuLog-Local` klasöründe) şu komutu çalıştırın:

```bash
docker-compose up -d
```
*-d parametresi bağımsız (detached) modda çalışmasını sağlar, böylece terminalinizi kapatmadan kullanmaya devam edebilirsiniz.*

### Konteynerin durumunu kontrol etmek için:
```bash
docker ps
```
Listede `seculog_db` isminde ve `5432` portunda çalışan bir konteyner göreceksiniz.

## Adım 3: Veritabanını Durdurma ve Kapatma

Eğer işiniz biterse ve veritabanını durdurmak isterseniz (yine aynı dizindeyken):
```bash
docker-compose stop
```
(İhtiyacınız olduğunda tekrar `docker-compose start` veya `docker-compose up -d` ile başlatabilirsiniz, **verileriniz silinmez**.)

Eğer sistemi tamamen silmek (konteynerı kaldırmak, **verileriniz hariç**) isterseniz:
```bash
docker-compose down
```

## Adım 4: İçeriğe Direkt Erişmek (İsteğe Bağlı)
Veritabanına manuel bir SQL sorgusu yazmak veya içeriği kendi gözünüzle görmek isterseniz, Docker üzerinden PostgreSQL terminal arayüzüne (psql) giriş yapabilirsiniz:
```bash
docker exec -it seculog_db psql -U seculog_user -d seculog
```
*(Çıkmak için komut satırında `\q` yazıp Enter tuşuna basabilirsiniz.)*

---

🎉 **Tebrikler!** Artık SecuLog-Local API (Backend) sistemi ayağa kalktığında otomatik olarak `localhost:5432` portu üzerinden PostgreSQL veritabanınıza başarılı bir biçimde bağlanacaktır.
