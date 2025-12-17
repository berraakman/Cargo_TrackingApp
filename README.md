# 📦 Cargo Tracking App

**Cargo Tracking App**, Python ve PyQt6 kullanılarak geliştirilmiş bir **masaüstü kargo takip ve yönetim uygulamasıdır**.  
Bu proje, bir üniversite dersi kapsamında akademik bir proje olarak geliştirilmiş olup; masaüstü uygulama geliştirme, dosya tabanlı veri yönetimi ve kullanıcı arayüzü tasarımı konularını kapsamaktadır.

---

## 🎓 Projenin Amacı

Bu projenin temel hedefleri şunlardır:

* **Masaüstü Uygulama Geliştirme:** GUI (Grafik Kullanıcı Arayüzü) süreçlerini deneyimlemek.
* **Arayüz Tasarımı:** PyQt6 kütüphanesi ile kullanıcı dostu ve işlevsel bir tasarım oluşturmak.
* **Veri Yönetimi:** CSV dosyaları üzerinden veri okuma, yazma ve manipülasyon süreçlerini yönetmek.
* **Sistem Modelleme:** Gerçek hayattaki kargo takip sistemlerinin temel mantığını yazılıma dökmek.
* **Dağıtılabilir Yazılım:** Uygulamayı çalıştırılabilir bir macOS `.app` paketine dönüştürme sürecini tamamlamak.

---

## 🧩 Uygulama Özellikleri

### 🔹 Kargo Yönetimi
* Kargo kayıtlarını merkezi CSV dosyalarından dinamik olarak okuma.
* Kargo bilgilerini (ID, Alıcı, Durum vb.) tablo halinde listeleme.
* Kargo durumlarını anlık olarak takip etme.

### 🔹 Kullanıcı ve Personel Yönetimi
* Sisteme erişimi olan kullanıcı ve personel bilgilerinin CSV üzerinden yönetilmesi.
* Personel listesinin uygulama içerisinden görüntülenebilmesi.

### 🔹 Kayıt ve Log Sistemi
* Yapılan işlemlerin ve kargo hareketlerinin adım adım loglanması.
* Log kayıtlarının şeffaflık adına ayrı bir `kargo_loglari.csv` dosyasında saklanması.

### 🔹 Masaüstü Deneyimi
* **PyQt6** tabanlı modern grafik arayüz.
* Terminale ihtiyaç duymadan, bağımsız bir uygulama olarak çalışabilme.
* macOS ekosistemi için optimize edilmiş paket yapısı.

---

## 🛠️ Kullanılan Teknolojiler

| Teknoloji | Açıklama |
| :--- | :--- |
| **Python 3.9** | Ana programlama dili |
| **PyQt6** | Grafik kullanıcı arayüzü framework'ü |
| **pandas** | Yüksek performanslı veri işleme ve CSV yönetimi |
| **NumPy** | Veri analizi ve yardımcı hesaplamalar |
| **PyInstaller** | Uygulamanın paketlenmesi ve `.app` dönüşümü |

> [!IMPORTANT]
> **Not:** Proje, Apple Silicon (M1/M2/M3) işlemci uyumluluğu ve stabilite nedeniyle Python **3.9** ile paketlenmiştir.

---

## 📁 Proje Klasör Yapısı

```text
Cargo_TrackingApp/
├── kargoTakip.py          # Ana uygulama giriş noktası
├── data/
│   ├── kargolar_ana.csv   # Mevcut kargo verileri
│   ├── kargo_loglari.csv  # İşlem geçmişi logları
│   └── kullanicilar.csv   # Kullanıcı ve personel verileri
├── README.md              # Proje dokümantasyonu
├── .gitignore             # Git dışı bırakılacak dosyalar
├── venv/                  # Sanal ortam (Virtual Env)
├── build/                 # Derleme ara dosyaları
└── dist/                  # Derlenmiş .app paketinin bulunduğu klasör
## ▶️ Uygulamayı Çalıştırma

### 🔹 Kaynak Koddan Çalıştırma

Bilgisayarınızda **Python 3.9** yüklü olduğundan emin olun.

Bir sanal ortam oluşturun ve aktif edin:

``` bash
python3.9 -m venv venv
source venv/bin/activate
```

Gerekli kütüphaneleri yükleyin:

``` bash
pip install --upgrade pip
pip install pyqt6 pandas numpy pyinstaller
```

Uygulamayı başlatın:

``` bash
python kargoTakip.py
```

------------------------------------------------------------------------

### 🔹 macOS (.app) Olarak Çalıştırma

Uygulama, son kullanıcı için paketlenmiş haldedir:

-   `dist/CargoTrackingApp.app` dosyasını bulun
-   Çift tıklayarak çalıştırın

> **Not:**\
> macOS güvenlik uyarısı alırsanız\
> **Sağ tık → Aç → Aç** yolunu izleyin.

------------------------------------------------------------------------

## 📦 Uygulamayı Paketleme (Derleme)

Kendi `.app` dosyanızı oluşturmak isterseniz aşağıdaki **PyInstaller**
komutunu kullanabilirsiniz:

``` bash
python -m PyInstaller \
  --windowed \
  --name CargoTrackingApp \
  --add-data "data:data" \
  kargoTakip.py
```

------------------------------------------------------------------------

## 🧠 Teknik Notlar

-   **Veri Yapısı:**\
    Uygulama, hafif ve taşınabilir olması amacıyla SQL yerine dosya
    tabanlı (**CSV**) bir mimari kullanır.

-   **Mimari:**\
    Proje, akademik bir demo niteliğinde olup, kod okunabilirliği ve
    eğitimsel amaçlar ön planda tutularak geliştirilmiştir.

-   **Ticari Durum:**\
    Gerçek bir ticari kargo otomasyonu değildir, fonksiyonel bir
    prototiptir.

------------------------------------------------------------------------

## 👩‍💻 Geliştirici

**Berra Akman**

-   GitHub: https://github.com/berraakman\
-   Proje Bağlantısı: Cargo_TrackingApp

------------------------------------------------------------------------

## 📄 Lisans

Bu proje **eğitim ve öğretim amaçlı** geliştirilmiştir.\
Ticari kullanım için uygun değildir.
