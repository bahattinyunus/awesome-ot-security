# 🏛️ Purdue Kurumsal Referans Mimarisi (PERA / ISA-95) Derinlemesine Rehber

Purdue Modeli (Purdue Enterprise Reference Architecture), 1990'larda Theodore J. Williams ve Purdue Üniversitesi Konsorsiyumu tarafından geliştirilmiş ve daha sonra ANSI/ISA-95 standardı olarak kabul edilmiş olan endüstriyel ağ ve sistem hiyerarşisidir.

---

## 📐 Purdue Katmanları ve Güvenlik Sorumlulukları

```text
=============================================================================
KATMAN           TİPİK CİHAZLAR VE BİLEŞENLER              GÜVENLİK ODAĞI
=============================================================================
Seviye 5         ERP, CRM, İş Zekası (BI), İnternet         Kurumsal Veri Gizliliği
(Enterprise)     Bulut Altyapıları, E-Ticaret               ve Kimlik Yönetimi
-----------------------------------------------------------------------------
Seviye 4         Ofis Bilgisayarları, Tesis İK/Lojistik,    Uç Nokta Koruması (EDR)
(Site Business)  İntranet, E-posta Sunucuları               ve E-posta Güvenliği
=============================================================================
Seviye 3.5       Çift Güvenlik Duvarı, Jump Server (PAM),   Katı Segmentasyon,
(Industrial DMZ) OT Replica Historian, WSUS Yama Dağıtımı  MFA ve Trafik Sonlandırma
=============================================================================
Seviye 3         SCADA Sunucuları, MES (Üretim Yürütme),    Uygulama Beyaz Listeleme,
(Site Ops)       Mühendislik İstasyonları (EWS)             Pasif Ağ Tespiti (NDR)
-----------------------------------------------------------------------------
Seviye 2         HMI (Operatör Panelleri), Alarm Sistemleri, Operatör İzolasyonu,
(Area Control)   Veri Toplama Konsolları                    USB/Port Engelleme
-----------------------------------------------------------------------------
Seviye 1         PLC (Denetleyici), RTU (Uzak Uç),          Lojik Bütünlüğü,
(Basic Control)  IED (Koruma Rölesi), SIS (Emniyet PLC)     Fiziksel Mod Anahtarı
-----------------------------------------------------------------------------
Seviye 0         Sensörler (Basınç, Akış, Sıcaklık),        Fiziksel Kablo Bütünlüğü,
(Process)        Aktüatörler, Vanalar, Pompalar, Şalt       HART/Sinyal Güvenliği
=============================================================================
```

---

## 🚫 Altın Segmentasyon Kuralları

1. **Hiçbir Zaman Seviye 4/5'ten Seviye 1/2'ye Doğrudan Paket Geçemez:**
   - Kurumsal ağdaki bir muhasebe bilgisayarından veya IT çalışanının laptopundan doğrudan sahadaki bir PLC'nin 502 veya 102 portuna bağlantı açılamaz.
2. **Tüm Dış Trafik IDMZ'de (Seviye 3.5) Sonlanmalıdır:**
   - Dışarıdan veya kurumsal ağdan sahaya erişmesi gereken bir mühendis, önce Seviye 3.5'teki MFA korumalı Jump Box'a (Atlama Sunucusu) bağlanır.
   - Jump Box üzerinden yeni bir iç oturum açılarak Seviye 3 Mühendislik İstasyonuna geçilir.
3. **Veri Çekme (Data Push vs Pull):**
   - Saha ağından kurumsal ağa veri akarken "Push" (itme) yöntemi tercih edilmeli veya Seviye 3.5'te çift taraflı ara sunucu (Historian Mirror) kullanılmalıdır.
4. **Fiziksel İzolasyon ve Veri Diyotları (Data Diodes):**
   - Nükleer santraller veya stratejik rafineriler gibi ultra kritik tesislerde, Seviye 3'ten Seviye 3.5/4'e veri aktarımı yalnızca tek yönlü fiber optik veri diyotları ile sağlanır.
