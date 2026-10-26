# Katkıda Bulunma Rehberi (Contributing Guidelines)

**Awesome OT & ICS Security** projesine katkıda bulunmak istediğiniz için teşekkür ederiz! Bu depo, endüstriyel kontrol sistemleri ve kritik altyapı güvenliği alanında çalışan araştırmacılar, mühendisler ve öğrenciler için dünya çapında referans niteliğinde açık bir kaynaktır.

---

## 🛠️ Nasıl Katkıda Bulunabilirsiniz?

1. **Yeni Araç veya Kaynak Önerme:**
   - Açık kaynaklı simülatörler, tehdit avcılığı araçları, honeypotlar veya analiz scriptleri.
2. **Dokümantasyon ve Çeviri:**
   - Standart analizleri (IEC 62443, NIST, NERC CIP) genişletme, imla ve teknik terim düzeltmeleri.
3. **Pratik Senaryo ve Lab Ekleme:**
   - `labs/` dizinine yeni Docker tabanlı simülasyonlar (Profinet, BACnet, DNP3, OPC UA vb.).
4. **Güvenlik Kuralları (Suricata / Snort / Zeek):**
   - Endüstriyel protokol anomalilerini tespit eden yeni imza ve algılama kuralları.

---

## 📌 Katkı Kuralları

- **Etik İlkelere Bağlılık:** Yalnızca savunma, eğitim, meşru güvenlik araştırmaları ve yasal yetkili test senaryolarına yönelik içerikler kabul edilir. Kötü niyetli istismar (weaponized malware) kodları eklenemez.
- **Biçimlendirme:** Markdown başlık hiyerarşisine, kod bloklarına ve tablo formatlarına özen gösteriniz.
- **Commit Mesajları:** [Conventional Commits](https://www.conventionalcommits.org/) formatına uyunuz:
  - `feat: add OPC UA discovery script`
  - `docs: update Purdue model reference`
  - `fix: correct Modbus function code description`

---

## 🚀 Adım Adım Katkı Süreci

1. Depoyu çatallayın (Fork).
2. Özellik dalınızı oluşturun:
   ```bash
   git checkout -b feature/yeni-protokol-analizi
   ```
3. Değişikliklerinizi commit edin:
   ```bash
   git commit -m "feat: add DNP3 SAv5 authentication analysis"
   ```
4. Dalınızı uzak depoya pushlayın:
   ```bash
   git push origin feature/yeni-protokol-analizi
   ```
5. GitHub üzerinden bir **Pull Request (PR)** açın.

Sorularınız ve önerileriniz için GitHub Issues üzerinden tartışma başlatmaktan çekinmeyin!
