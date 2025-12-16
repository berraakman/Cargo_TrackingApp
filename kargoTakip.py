import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QTabWidget, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QFormLayout, QGridLayout, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from datetime import datetime, timedelta
import pandas as pd
import os

# =========================================================================
# DİKKAT: SABİT DOSYA YOLU ATAMASI
# Lütfen bu 3 satırı, Mac'inizdeki CSV dosyalarının TAM YOLU ile değiştirin.
# =========================================================================
CSV_LOGLARI = '/Users/berra/Desktop/Cargo_TrackingApp/kargo_loglari.csv'
CSV_KULLANICILAR = '/Users/berra/Desktop/Cargo_TrackingApp/kullanicilar.csv'
CSV_KARGOLAR_ANA = '/Users/berra/Desktop/Cargo_TrackingApp/kargolar_ana.csv'

# --- 1. CSV Tabanlı Veritabanı Sınıfı (3 Tabloyu Yönetir) ---
class CargoDatabase:
    def __init__(self):
        self.kargo_df = None       
        self.kullanicilar_df = None
        self.kargolar_ana_df = None
        
        self.load_data()
    
    def load_data(self):
        """Üç CSV dosyasını da yükler ve dosyaların varlığını kontrol eder."""
        
        def check_and_load(path, cols, is_datetime=False):
            if not os.path.exists(path):
                # Dosya yoksa, boş bir DataFrame oluştur ve dosyayı yaz.
                df = pd.DataFrame(columns=cols)
                try:
                    df.to_csv(path, index=False)
                except Exception as e:
                    raise IOError(f"Dosya oluşturulamadı veya yazılamadı (İzin Hatası): {path} -> {e}")
                return df
            else:
                # Dosya varsa, yükle.
                try:
                    df = pd.read_csv(path)
                    # KRİTİK: ID ve giriş alanlarını stringe zorla (eşleşme sorunlarını önler)
                    for col in ['takip_no', 'kullanici_adi', 'sifre']:
                        if col in df.columns:
                            df[col] = df[col].astype(str).str.strip()
                    if df.empty and len(cols) > 0:
                         df = pd.DataFrame(columns=cols)

                    if is_datetime and 'tarih' in df.columns and not df.empty:
                        # Tarih formatlarını akıllı şekilde çöz (ISO + TR), uyarı üretmez
                        try:
                            # ISO format: 2025-12-15 18:30
                            df['tarih'] = pd.to_datetime(
                                df['tarih'],
                                format='%Y-%m-%d %H:%M',
                                errors='raise'
                            )
                        except Exception:
                            # TR formatları: 15.12.2025 18:30 / 15/12/2025 18:30
                            df['tarih'] = pd.to_datetime(
                                df['tarih'],
                                dayfirst=True,
                                errors='coerce'
                            )
                        
                    return df
                except Exception as e:
                    # Format veya İçerik Hatası
                    raise IOError(f"Dosya okunamadı veya format hatası var: {path} -> {e}")

        try:
            # 1. Kargo Logları (Kargo_Loglari)
            self.kargo_df = check_and_load(
                CSV_LOGLARI, ['takip_no', 'tarih', 'konum', 'durum'], is_datetime=True
            )
            if not self.kargo_df.empty and 'tarih' in self.kargo_df.columns:
                self.kargo_df = self.kargo_df.sort_values(by='tarih', ascending=True)

            # 2. Kullanıcılar (Kullanicilar)
            self.kullanicilar_df = check_and_load(
                CSV_KULLANICILAR, ['kullanici_adi', 'sifre', 'rol']
            )
            # Varsayılan kullanıcıları kontrol et ve ekle
            if self.kullanicilar_df.empty or len(self.kullanicilar_df) == 0:
                self.kullanicilar_df = pd.DataFrame({
                    'kullanici_adi': ['lojisfk', 'yonetici'],
                    'sifre': ['1234', '4321'],
                    'rol': ['Personel', 'Yonetici']
                })
                self.kullanicilar_df.to_csv(CSV_KULLANICILAR, index=False)


            # 3. Kargolar Ana Bilgi (Kargolar)
            self.kargolar_ana_df = check_and_load(
                CSV_KARGOLAR_ANA, ['takip_no', 'gonderici_ad', 'alici_ad', 'mevcut_durum']
            )

        except Exception as e:
            QMessageBox.critical(None, "KRİTİK BAŞLANGIÇ HATASI", str(e))
            sys.exit(1)


    def get_user_credentials(self, user, password):
        """Kullanıcıyı ve rolünü CSV'den doğrular."""
        user_row = self.kullanicilar_df[
            (self.kullanicilar_df['kullanici_adi'] == user) &
            (self.kullanicilar_df['sifre'] == password)
        ]
        if not user_row.empty:
            return user_row.iloc[0]['rol']
        return None
    
    def get_logs(self, takip_no):
        """Belirli bir takip numarasına ait logları çeker."""
        logs = self.kargo_df[self.kargo_df['takip_no'] == takip_no]
        if logs.empty:
            return None
        return logs.sort_values(by='tarih').to_dict('records')

    def add_log(self, takip_no, konum, durum):
        """Operasyon personeli log ekleme."""
        yeni_log = pd.DataFrame([{
            "takip_no": takip_no,
            "tarih": datetime.now(),
            "konum": konum,
            "durum": durum
        }])
        
        # 1. Kargo Loglarını Güncelle ve Kaydet
        self.kargo_df = pd.concat([self.kargo_df, yeni_log], ignore_index=True)
        self.kargo_df.to_csv(CSV_LOGLARI, index=False, date_format='%Y-%m-%d %H:%M')
        
        # 2. Ana Kargo Durumunu Güncelle (Kargolar tablosu simülasyonu)
        if takip_no in self.kargolar_ana_df['takip_no'].values:
            self.kargolar_ana_df.loc[self.kargolar_ana_df['takip_no'] == takip_no, 'mevcut_durum'] = durum
        else:
             # Yeni bir kargo ilk kez sisteme giriyorsa (Basit Ana Kargo kaydı oluştur)
             yeni_ana = pd.DataFrame([{'takip_no': takip_no, 'gonderici_ad': 'Bilinmiyor', 'alici_ad': 'Bilinmiyor', 'mevcut_durum': durum}])
             self.kargolar_ana_df = pd.concat([self.kargolar_ana_df, yeni_ana], ignore_index=True)

        self.kargolar_ana_df.to_csv(CSV_KARGOLAR_ANA, index=False)
        return True

    def calculate_eta(self, loglar):
        """Tahmini teslim tarihi hesaplama (F-006)."""
        if not loglar:
             return "-"
        son_log_dt = loglar[-1]['tarih']
        if isinstance(son_log_dt, str):
            son_log_dt = datetime.strptime(son_log_dt, '%Y-%m-%d %H:%M')
        
        tahmini_teslim = son_log_dt + timedelta(days=1) 
        return tahmini_teslim.strftime('%d/%m/%Y %H:%M')

# --- 2. Ana Uygulama Sınıfı ---

class CargoTrackingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LojisFk Kargo Takip Sistemi Prototipi")
        self.resize(1000, 750) 
        
        self.db = CargoDatabase()
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.current_user_role = None 
        
        self.customer_tab = self.create_customer_tab()
        self.tabs.addTab(self.customer_tab, "📦 Kargo Takip (Müşteri)")
        
        self.personnel_login_widget = self.create_login_form()
        self.manager_panel_widget = self.create_manager_panel()
        self.personnel_form_widget = self.create_data_entry_form()
        
        self.personnel_tab = self.create_personnel_tab()
        self.tabs.addTab(self.personnel_tab, "👨‍💼 Veri Girişi (Personel)")
        
        self.tabs.currentChanged.connect(self.check_personnel_access)
        
    # --- 4. Operasyon Personeli Sekmesi için Container ---
    def create_personnel_tab(self):
        tab = QWidget()
        self.personnel_main_layout = QVBoxLayout(tab)
        
        self.personnel_main_layout.addWidget(self.personnel_login_widget)
        self.personnel_main_layout.addWidget(self.manager_panel_widget)
        self.personnel_main_layout.addWidget(self.personnel_form_widget)
        
        self.manager_panel_widget.hide() 
        self.personnel_form_widget.hide() 
        
        self.personnel_main_layout.addStretch()
        return tab

    # --- Personel Erişim Kontrolü ---
    def check_personnel_access(self, index):
        """Sekme değiştiğinde personel sekmesini kontrol eder ve rolüne göre yönlendirir."""
        if self.tabs.tabText(index) == "👨‍💼 Veri Girişi (Personel)":
            if self.current_user_role is None:
                self.personnel_form_widget.hide()
                self.manager_panel_widget.hide() 
                self.personnel_login_widget.show()
            
            elif self.current_user_role == 'Personel':
                self.personnel_login_widget.hide()
                self.manager_panel_widget.hide()
                self.personnel_form_widget.show()
                
            elif self.current_user_role == 'Yonetici':
                self.personnel_login_widget.hide()
                self.personnel_form_widget.hide()
                self.manager_panel_widget.show()
                self.update_manager_panel()

    def handle_back_to_login(self):
        """Yönetici veya Personel ekranından giriş ekranına geri döner"""
        # Rolü sıfırla
        self.current_user_role = None

        # Tüm personel/yönetici widgetlarını gizle
        self.manager_panel_widget.hide()
        self.personnel_form_widget.hide()

        # Login ekranını göster
        self.personnel_login_widget.show()

        # Giriş alanlarını temizle
        self.login_user_input.clear()
        self.login_pass_input.clear()

        # Personel sekmesinde kal ama login ekranına dön
        self.tabs.setCurrentIndex(1)

    # --- 3. Müşteri Takip Sekmesi ---
    def create_customer_tab(self):
        tab = QWidget()
        main_v_layout = QVBoxLayout(tab)
        
        header_label = QLabel("<h1>LojisFk Kargo Takip Sorgulama</h1>")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        input_and_button_widget = QWidget()
        input_h_layout = QHBoxLayout(input_and_button_widget)
        
        self.customer_takip_input = QLineEdit()
        self.customer_takip_input.setPlaceholderText("Kargo Takip Numarası Giriniz")
        self.customer_takip_input.setFixedWidth(400)
        
        self.sorgula_button = QPushButton("Kargomu Takip Et")
        self.sorgula_button.setObjectName("TrackButton")
        self.sorgula_button.clicked.connect(self.handle_customer_sorgula)
        self.sorgula_button.setFixedWidth(150)

        input_h_layout.addStretch() 
        input_h_layout.addWidget(self.customer_takip_input)
        input_h_layout.addWidget(self.sorgula_button)
        input_h_layout.addStretch() 
        
        results_frame = QFrame()
        results_frame.setObjectName("ResultsFrame") 
        results_frame.setMinimumHeight(500)
        results_v_layout = QVBoxLayout(results_frame)
        
        self.anlik_durum_label = QLabel("<h4>Anlık Durum:</h4> Henüz sorgulama yapılmadı.")
        self.anlik_durum_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.eta_label = QLabel("<h4>Tahmini Teslimat:</h4> -")
        self.eta_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        history_header = QLabel("<h3>Hareket Geçmişi Detayı</h3>")
        history_header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.table_widget = QTableWidget()
        self.table_widget.setCornerButtonEnabled(False)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setMinimumHeight(350)
        self.table_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["Tarih/Saat", "Konum", "Durum"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch) 

        results_v_layout.addWidget(self.anlik_durum_label)
        results_v_layout.addWidget(self.eta_label)
        results_v_layout.addWidget(history_header)
        results_v_layout.addWidget(self.table_widget)
        
        main_v_layout.addWidget(header_label)
        main_v_layout.addWidget(input_and_button_widget)
        
        center_h_layout = QHBoxLayout()
        center_h_layout.addStretch()
        center_h_layout.addWidget(results_frame)
        center_h_layout.addStretch()
        
        main_v_layout.addLayout(center_h_layout)
        main_v_layout.addStretch() 

        return tab
    
    def handle_customer_sorgula(self):
        takip_no = self.customer_takip_input.text().strip()
        
        if not takip_no:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir takip numarası giriniz.")
            self.clear_customer_display()
            return
            
        logs = self.db.get_logs(takip_no)
        
        if logs is None or not logs:
            QMessageBox.critical(self, "Hata", f'"{takip_no}" numaralı kargo kaydı bulunamadı veya numara geçersizdir. (F-005 Hatası)')
            self.clear_customer_display()
            
            self.anlik_durum_label.setStyleSheet("color: #dc3545;") 
            self.anlik_durum_label.setText("<h4>Sorgulama Hatası:</h4> Kargo Bulunamadı.")
            return

        son_log = logs[-1]
        
        durum_renk = "#28a745" if son_log['durum'] == "Teslim Edildi" else "#007bff"
        
        self.anlik_durum_label.setStyleSheet(f"color: {durum_renk};")
        self.anlik_durum_label.setText(f"<h4>Anlık Durum:</h4> <b>{son_log['durum']}</b> ({son_log['konum']})")
        
        eta = self.db.calculate_eta(logs)
        self.eta_label.setText(f"<h4>Tahmini Teslimat:</h4> <span style='color: #00aaff;'>{eta}</span>")
        
        df = pd.DataFrame(logs)
        df = df.sort_values(by='tarih', ascending=False)
        self.table_widget.setRowCount(len(df))
        
        df['tarih'] = pd.to_datetime(df['tarih'], errors='coerce')
        df['tarih_str'] = df['tarih'].dt.strftime('%Y-%m-%d %H:%M')
        
        for i, row in enumerate(df.itertuples()):
            self.table_widget.setItem(i, 0, QTableWidgetItem(row.tarih_str))
            self.table_widget.setItem(i, 1, QTableWidgetItem(row.konum))
            self.table_widget.setItem(i, 2, QTableWidgetItem(row.durum))
            
        QMessageBox.information(self, "Başarılı", f"Kargo {takip_no} bilgileri başarıyla yüklendi.")

    def clear_customer_display(self):
        self.anlik_durum_label.setStyleSheet("color: #f0f0f0;") 
        self.anlik_durum_label.setText("<h4>Anlık Durum:</h4> Henüz sorgulama yapılmadı.")
        self.eta_label.setText("<h4>Tahmini Teslimat:</h4> -")
        self.table_widget.setRowCount(0)
        
    def create_login_form(self):
        login_widget = QWidget()
        login_layout = QGridLayout(login_widget)
        
        header_label = QLabel("<h2>Operasyon Girişi</h2>")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(header_label, 0, 0, 1, 2)
        
        self.login_user_input = QLineEdit()
        self.login_user_input.setPlaceholderText("Kullanıcı Adı")
        login_layout.addWidget(QLabel("Kullanıcı Adı:"), 1, 0)
        login_layout.addWidget(self.login_user_input, 1, 1)

        self.login_pass_input = QLineEdit()
        self.login_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_pass_input.setPlaceholderText("Şifre")
        login_layout.addWidget(QLabel("Şifre:"), 2, 0)
        login_layout.addWidget(self.login_pass_input, 2, 1)

        login_button = QPushButton("Giriş Yap")
        login_button.clicked.connect(self.handle_personnel_login)
        login_layout.addWidget(login_button, 3, 0, 1, 2)
        
        layout_container = QVBoxLayout()
        layout_container.addStretch(1)
        frame = QFrame()
        frame.setLayout(login_layout)
        frame.setStyleSheet(
            "background-color: #ffffff;"
            "border: 1px solid #dde1e8;"
            "border-radius: 15px;"
            "padding: 25px;"
            "color: #0a1f44;"
        )
        
        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(frame)
        h_layout.addStretch(1)
        
        layout_container.addLayout(h_layout)
        layout_container.addStretch(2)
        
        final_widget = QWidget()
        final_widget.setLayout(layout_container)
        return final_widget

    def handle_personnel_login(self):
        user = self.login_user_input.text().strip()
        password = self.login_pass_input.text().strip()
        
        role = self.db.get_user_credentials(user, password)
        
        if role:
            self.current_user_role = role
            QMessageBox.information(self, "Başarılı Giriş", f"{role} sistemine hoş geldiniz!")
            
            self.tabs.setCurrentIndex(1) 
            self.check_personnel_access(1) 
                
        else:
            QMessageBox.critical(self, "Giriş Hatası", "Kullanıcı adı veya şifre yanlış.")
            self.login_pass_input.clear()

    def create_manager_panel(self):
        """Yönetici Rolü için yer tutucu/rapor paneli"""
        panel = QWidget()
        v_layout = QVBoxLayout(panel)
        
        header = QLabel("<h1>Yönetici Paneli</h1>")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v_layout.addWidget(header)
        back_button_manager = QPushButton("⬅ Geri Dön")
        back_button_manager.setFixedWidth(140)
        back_button_manager.clicked.connect(self.handle_back_to_login)
        v_layout.addWidget(back_button_manager, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # Kullanıcılar Tablosu (kullanicilar.csv)
        user_frame = QFrame()
        user_frame.setObjectName("ManagerFrame")
        user_frame_layout = QVBoxLayout(user_frame)
        
        user_frame_layout.addWidget(QLabel("<h3>Kullanıcı Hesapları</h3>"))
        self.user_table = QTableWidget()
        self.user_table.setCornerButtonEnabled(False)
        self.user_table.verticalHeader().setVisible(False)
        self.user_table.setColumnCount(3)
        self.user_table.setHorizontalHeaderLabels(["Kullanıcı Adı", "Şifre (Simülasyon)", "Rol"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        user_frame_layout.addWidget(self.user_table)
        self.user_table.setMinimumWidth(1000)
        self.user_table.setMinimumHeight(200)
        self.user_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Kargo Ana Tablosu (kargolar_ana.csv)
        kargo_frame = QFrame()
        kargo_frame.setObjectName("ManagerFrame")
        kargo_frame_layout = QVBoxLayout(kargo_frame)
        
        kargo_frame_layout.addWidget(QLabel("<h3>Ana Kargo Bilgileri</h3>"))
        self.kargo_ana_table = QTableWidget()
        self.kargo_ana_table.setCornerButtonEnabled(False)
        self.kargo_ana_table.verticalHeader().setVisible(False)
        self.kargo_ana_table.setColumnCount(4)
        self.kargo_ana_table.setHorizontalHeaderLabels(["Takip No", "Gönderici", "Alıcı", "Mevcut Durum"])
        self.kargo_ana_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        kargo_frame_layout.addWidget(self.kargo_ana_table)
        self.kargo_ana_table.setMinimumWidth(900)
        self.kargo_ana_table.setMinimumHeight(300)
        self.kargo_ana_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Ortalamak için
        center_h_layout = QHBoxLayout()
        center_h_layout.addWidget(user_frame)
        
        center_h_layout2 = QHBoxLayout()
        center_h_layout2.addWidget(kargo_frame)

        v_layout.addLayout(center_h_layout)
        v_layout.addLayout(center_h_layout2)
        return panel

    def update_manager_panel(self):
        """Yönetici Paneli verilerini CSV'den yükler."""
        # Kullanıcı Tablosu
        if self.db.kullanicilar_df is not None:
            df_user = self.db.kullanicilar_df
            self.user_table.setRowCount(len(df_user))
            for i, row in enumerate(df_user.itertuples()):
                self.user_table.setItem(i, 0, QTableWidgetItem(str(row.kullanici_adi)))
                self.user_table.setItem(i, 1, QTableWidgetItem(str(row.sifre)))
                self.user_table.setItem(i, 2, QTableWidgetItem(str(row.rol)))

        # Kargo Ana Tablosu
        if self.db.kargolar_ana_df is not None:
            df_kargo_ana = self.db.kargolar_ana_df
            self.kargo_ana_table.setRowCount(len(df_kargo_ana))
            for i, row in enumerate(df_kargo_ana.itertuples()):
                self.kargo_ana_table.setItem(i, 0, QTableWidgetItem(str(row.takip_no)))
                self.kargo_ana_table.setItem(i, 1, QTableWidgetItem(str(row.gonderici_ad)))
                self.kargo_ana_table.setItem(i, 2, QTableWidgetItem(str(row.alici_ad)))
                self.kargo_ana_table.setItem(i, 3, QTableWidgetItem(str(row.mevcut_durum)))

    def create_data_entry_form(self):
        form_widget = QWidget()
        main_v_layout = QVBoxLayout(form_widget)
        
        personnel_header = QLabel("<h1>Operasyon Veri Giriş Ekranı</h1>")
        personnel_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_v_layout.addWidget(personnel_header)
        back_button_personnel = QPushButton("⬅ Geri Dön")
        back_button_personnel.setFixedWidth(140)
        back_button_personnel.clicked.connect(self.handle_back_to_login)
        main_v_layout.addWidget(back_button_personnel, alignment=Qt.AlignmentFlag.AlignLeft)

        layout_label = QLabel("Lütfen kargonun yeni durumunu tarayarak/girerek sisteme kaydediniz.")
        layout_label.setStyleSheet("color: #3b4a6b;")
        main_v_layout.addWidget(layout_label)

        form_frame = QFrame()
        form_v_layout = QVBoxLayout(form_frame)
        
        form_layout = QFormLayout()
        
        self.personnel_takip_input = QLineEdit()
        self.personnel_takip_input.setPlaceholderText("Kargo Takip Numarası")
        form_layout.addRow(QLabel("Takip No:"), self.personnel_takip_input)
        
        self.personnel_konum_input = QLineEdit()
        self.personnel_konum_input.setPlaceholderText("Şube/Merkez Konumu")
        form_layout.addRow(QLabel("Yeni Konum:"), self.personnel_konum_input)
        
        self.personnel_durum_combo = QComboBox()
        self.personnel_durum_combo.addItems([
            "Kabul Edildi", "Transfer Sürecinde", "Merkeze Ulaştı", 
            "Dağıtıma Çıktı", "Teslim Edildi", "Adreste Bulunamadı"
        ])
        form_layout.addRow(QLabel("Yeni Durum:"), self.personnel_durum_combo)
        
        self.guncelle_button = QPushButton("Durumu Kaydet (Veri Girişi)")
        self.guncelle_button.clicked.connect(self.handle_personnel_guncelle)
        
        form_v_layout.addLayout(form_layout)
        form_v_layout.addWidget(self.guncelle_button)
        
        center_h_layout = QHBoxLayout()
        center_h_layout.addStretch()
        center_h_layout.addWidget(form_frame)
        center_h_layout.addStretch()
        
        main_v_layout.addLayout(center_h_layout)
        main_v_layout.addStretch()
        
        form_frame.setStyleSheet(
            "background-color: #ffffff;"
            "border: 1px solid #dde1e8;"
            "border-radius: 15px;"
            "padding: 25px;"
        )
        form_frame.setFixedWidth(500)
        
        return form_widget

    def handle_personnel_guncelle(self):
        takip_no = self.personnel_takip_input.text().strip()
        konum = self.personnel_konum_input.text().strip()
        durum = self.personnel_durum_combo.currentText()
        
        if not takip_no or not konum:
            QMessageBox.critical(self, "Hata", "Lütfen Takip Numarası ve Konum alanlarını doldurunuz.")
            return

        self.db.add_log(takip_no, konum, durum)
        QMessageBox.information(self, "Başarılı", f"Kargo {takip_no} için yeni durum ({durum}) başarıyla kaydedildi.")
        
        self.personnel_takip_input.clear()
        self.personnel_konum_input.clear()


# --- 5. Qt Style Sheet Tanımı (Açık Tema) ---
LIGHT_STYLE_SHEET = """
/* ===============================
   GENEL ARKA PLAN (AÇIK GRİ)
   =============================== */
QMainWindow {
    background-color: #f2f3f5;
}

/* ===============================
   SEKME SAYFALARI ARKA PLAN
   =============================== */
QWidget {
    background-color: transparent;
}

QTabWidget::pane {
    background-color: #f2f3f5;
}

QTabWidget QWidget {
    background-color: #f2f3f5; /* sekme içi açık gri */
}

/* ===============================
   SEKME YAPISI
   =============================== */
QTabWidget::pane { border: none; background: transparent; }

QTabBar::tab {
    background: #e0e2e6;
    color: #0a1f44; /* lacivert */
    padding: 12px 20px;
    border-radius: 8px;
    margin-right: 6px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background: #0a1f44;
    color: white;
}

QTabBar::tab:hover {
    background: #cfd4dc;
}

/* ===============================
   BUTONLAR (BEBEK MAVİSİ)
   =============================== */
QPushButton {
    background-color: #9fd6ff; /* bebek mavisi */
    color: #0a1f44;
    border: none;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #6fc2ff; /* hover rengi */
}

QPushButton:pressed {
    background-color: #4faee8;
}

/* ===============================
   INPUT & COMBOBOX
   =============================== */
QLineEdit, QComboBox {
    background-color: white;
    color: #0a1f44;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #c7cbd3;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #6fc2ff;
}

/* ===============================
   ETİKETLER
   =============================== */
QLabel { color: #0a1f44; }

QLabel h1, QLabel h2, QLabel h3 {
    color: #0a1f44; /* lacivert başlıklar */
}

QLabel h4 {
    color: #3b4a6b;
}

/* ===============================
   TABLO
   =============================== */
QTableWidget {
    background-color: white;
    alternate-background-color: #f2f4f7;
    color: #0a1f44;
    border-radius: 10px;
    border: 1px solid #d5d9e0;
    gridline-color: #e1e4ea;
}

QHeaderView::section {
    background-color: #0a1f44;
    color: white;
    padding: 8px;
    border: none;
    font-weight: bold;
}

/* ===============================
   KARTLAR / FRAME
   =============================== */
#ResultsFrame, #ManagerFrame {
    background-color: #ffffff;
    border-radius: 15px;
    padding: 20px;
    min-width: 900px;
    border: 1px solid #dde1e8;
}

QFrame {
    background-color: #ffffff;
    border-radius: 15px;
    padding: 25px;
    border: 1px solid #dde1e8;
}
"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    app.setStyleSheet(LIGHT_STYLE_SHEET)
    
    window = CargoTrackingApp()
    window.show()
    sys.exit(app.exec())