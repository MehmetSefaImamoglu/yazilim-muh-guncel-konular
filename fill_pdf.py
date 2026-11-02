# -*- coding: utf-8 -*-
"""Safety 4.0 Bootcamp föylerini Kenar Bantlama Makinesi (PUR - AİMSAD) için doldurur."""
import os, re, sys
import pymupdf

sys.stdout.reconfigure(encoding="utf-8")

REG = pymupdf.Font(fontfile="C:/Windows/Fonts/calibri.ttf")
BLD = pymupdf.Font(fontfile="C:/Windows/Fonts/calibrib.ttf")
INK = (0.04, 0.14, 0.52)
RED = (0.70, 0.08, 0.08)
GRN = (0.06, 0.45, 0.20)

NAME, GROUP = "Mehmet Sefa İmamoğlu", "Gündüz B"
DATES = ["02.10.2026", "09.10.2026", "16.10.2026", "23.10.2026", "30.10.2026", "06.11.2026", "13.11.2026"]
MACHINE = "Makine: Endüstriyel Kenar Bantlama Makinesi – PUR Tutkal Teknolojili (AİMSAD)"

def put(page, rect, text, size=9.0, min_size=5.8, font=REG, color=INK, align=0):
    """Metni kutuya sığacak en büyük punto ile yazar (Unicode güvenli)."""
    rect = pymupdf.Rect(rect)
    s = size
    while s >= min_size:
        tw = pymupdf.TextWriter(page.rect)
        left = tw.fill_textbox(rect, text, font=font, fontsize=s, align=align, lineheight=1.08)
        if not left:
            tw.write_text(page, color=color)
            return s
        s -= 0.2
    tw = pymupdf.TextWriter(page.rect)
    tw.fill_textbox(rect, text, font=font, fontsize=min_size, align=align, lineheight=1.05)
    tw.write_text(page, color=color)
    print("  UYARI: sığmadı ->", text[:50])
    return min_size

def header(page, date):
    put(page, (79, 98, 245, 114), NAME, size=10.5, font=BLD)
    put(page, (272, 98, 440, 114), GROUP, size=10.5, font=BLD)
    put(page, (482, 98, 556, 114), date, size=10.5, font=BLD)
    put(page, (40, 88.2, 556, 99.6), MACHINE, size=6.6, font=BLD, color=(0.1, 0.35, 0.6))

def questions(page):
    qs = []
    for b in page.get_text("blocks"):
        t = b[4].strip()
        if b[1] > 120 and b[0] < 52 and re.match(r"^\d\s", t):
            qs.append(b)
    return sorted(qs, key=lambda b: b[1])

def answer_questions(page, answers, bottom):
    qs = questions(page)
    assert len(qs) == len(answers), (page.number, len(qs), len(answers))
    for i, (q, a) in enumerate(zip(qs, answers)):
        top = q[3] + 3
        end = (qs[i + 1][1] - 4) if i + 1 < len(qs) else bottom
        put(page, (64, top, 552, end), a, size=9.0)

# ------------------------------------------------------------------ İÇERİK
L1 = [
    "Yüksek devirli ön freze, kazıma ve baş-son kesme testereleri (12.000–18.000 RPM) uzuv kesilmesi/sıkışması; 180–210°C PUR tutkal kazanı ise ağır yanık, yangın ve izosiyanat buharı tehlikesi yaratır.",
    "Muhafaza kapağı açıldığında, acil stop basıldığında veya tutkal kazanı aşırı sıcaklığa ulaştığında Safety PLC'nin STO ile freze/testere tahriklerini kesmesi ve emniyet kontaktörüyle ısıtıcı enerjisini bağımsız keserek makineyi durdurmasıdır.",
    "Şemadaki alt emniyet zinciridir: Acil stop / kapak kilidi / termostat → Safety PLC → STO / Kontaktör → Safe State. (Şemada yeşil çerçeveyle işaretlendi.)",
    "Normal PLC üretimi yönetir: tutkal sıcaklık PID'si, VFD devirleri, pnömatik zamanlama. Safety PLC ise emniyet girişlerini izler, kendi kendini denetler ve arızada makineyi güvenli duruma geçirir; üretim PLC'sinden bağımsız çalışır.",
    "PLr/SIL, emniyet fonksiyonunun riske göre ne kadar güvenilir olması gerektiğini belirler. Freze takımı ve 200°C tutkal ağır yaralanma riski taşıdığı için yüksek PLr/SIL (ör. PL d–e) gerekir.",
    "Tahriklerin torku kesilmiş (STO), muhafazalar motorlar durana dek kilitli, ısıtıcı kontaktörü açık ve pnömatik enerji tahliye edilmiş; makinenin istemsiz yeniden kalkışı engellenmiş durumdur. Kazanın kalan sıcaklığı ayrıca korunur.",
    "Safety PLC yazılımı ve yapılandırması, emniyet I/O ve sensör sinyalleri, emniyet haberleşmesi, VFD'lerin STO girişleri ve sıcaklık limit parametreleri. Bu bileşenlerin bütünlüğü korunmalıdır.",
    "İnternete açık uzak bakım modülü / IPC ile üretim PLC'si arasındaki dijital kesişim noktasıdır. Saldırgan buradan Safety PLC yapılandırmasını, sıcaklık limitini veya VFD parametrelerini değiştirirse emniyet fonksiyonu devre dışı kalabilir.",
]

L2_Q1_PAKET = ("Z1 Emniyet: Safety PLC, acil stop, kapak kilitleri, aşırı sıcaklık termostatı | Z2 Üretim: Üretim PLC'si, tutkal ısı kontrolü, mühendislik istasyonu | "
               "Z3 Saha/Tahrik: Freze ve testere VFD'leri, ısıtıcılar, pnömatik valfler | Z4 Operatör: HMI (port 80) | Z5 DMZ: Uzak bakım modülü, jump server | "
               "Z6 Dış: Wi-Fi AP, bulut telemetri, ofis ağı. Not: Kilitsiz USB ve admin/admin ayrı bölge değil, kapatılacak açıklardır.")
L2_Q1_GENEL = ("Z1 Emniyet: Safety PLC, acil stop, kapak kilitleri, aşırı sıcaklık termostatı | Z2 Üretim: PLC, tutkal ısı kontrolü, VFD/pnömatik tahrik kontrolü (robot kontrolörü yerine) | "
               "Z3 Operatör: HMI, SCADA istemcisi, mühendislik istasyonu | Z4 DMZ: Uzak servis erişimi (jump server) | Z5 Kurumsal: Ofis ağı (ERP/e-posta). "
               "Emniyet PLC'si hiçbir bölgeyle ortaklaşa tutulmaz.")
L2_Q2_PAKET = ("Uzak bakım modülü Z5 (DMZ) bölgesine düşer ve internete doğrudan açık HAYIR kalamaz: yetkisiz erişim freze devrini ve tutkal ısısını değiştirebilir. "
               "VPN + MFA + jump server + güvenlik duvarı arkasına alınmalı, varsayılan kapalı olmalıdır.")
L2_Q2_GENEL = ("Safety PLC'yi ayrı Z1 Emniyet bölgesine koydum; çünkü üretim ağı ele geçirilse bile insan güvenliğini sağlayan fonksiyon siber olaydan etkilenmemeli (emniyet bağımsızlığı). "
               "Uzak servis erişimi ise yalnızca DMZ'de, VPN + MFA + jump server ile kontrollü olmalıdır.")
L2_Q3 = ("1) DMZ → Üretim PLC: VPN/MFA, izinli IP-port, oturum kaydı, yazma koruma anahtarı. 2) HMI → PLC: yalnızca tanımlı etiketler, yetki kontrolü. "
         "3) Üretim PLC ↔ Safety PLC: tek yönlü durum bilgisi, parametre yazımı yasak. 4) PLC → VFD: devir/sıcaklık sınır filtresi. "
         "5) Wi-Fi/Ofis → OT: OT güvenlik duvarı, varsayılan engelleme.")
L2_TABLE = [
    "Jump server: Doğrudan PLC erişimini engeller, tüm bakım erişimi tek denetimli noktadan geçer.",
    "VPN: Bakım trafiği şifrelenir, yalnızca yetkili kaynak bağlanabilir.",
    "MFA: Parola çalınsa bile ikinci doğrulama olmadan oturum açılamaz.",
    "Kişisel: Her teknisyen ayrı hesap kullanır; işlemler kişiye bağlanır.",
    "Tam oturum kaydı: Parametre değişiklikleri denetlenebilir, delil olur.",
    "Varsayılan kapalı: Erişim yalnızca onaylı bakım süresince açılır.",
]

L3_ROWS = [
    ("Dış saldırgan → açık uzak bakım modülü → freze VFD devrini yükseltir → takım parçalanır → fırlayan parça operatörü ağır yaralar.", "3", "3", "3", "27", "Kritik"),
    ("Yetkisiz kişi → zayıf Wi-Fi/HMI → tutkal set değerini yükseltir → PUR aşırı ısınır → yangın/toksik buhar, operatör yanar.", "2", "3", "2", "12", "Yüksek"),
    ("Yetkisiz kişi → kilitsiz USB → hatalı yazılım kapak kilidi sinyalini atlatır → muhafaza açıkken testere döner → el yaralanır.", "1", "3", "1", "3", "Düşük (S=3!)"),
]
L3_Q = [
    "1. senaryo (27 – Kritik) en önceliklidir; çünkü açık uzak bakım modülü olasılığı yükseltir, fırlayan freze takımı ise operatör için ölümcül/ağır yaralanma sonucu doğurur.",
    "Evet, 3. senaryonun skoru 3 (Düşük) ama S=3'tür. Risk Register'da \"Kritik Fiziksel Sonuç (S=3)\" uyarısıyla kırmızı işaretleyip emniyet önlemlerini (kapak kilidi izleme, USB kilidi, güvenli duruş testi) önceliklendireceğim.",
]

L4_MEVCUT = ("• Uzak bakım modülü internete doğrudan açık.\n• admin/admin ortak hesabı kullanılıyor; MFA ve oturum kaydı yok.\n"
             "• Freze VFD devri ve tutkal sıcaklığı OT ağı üzerinden yazılabiliyor.\n• Üretim PLC'si ile emniyet sistemi arasında izole olmayan dijital bağlantı var.")
L4_HEDEF = ("1) Erişim yalnızca DMZ'deki jump server üzerinden.\n2) VPN + MFA ile kimlik doğrulama.\n3) Kişisel hesap, asgari yetki.\n"
            "4) Tam oturum kaydı; erişim varsayılan kapalı.\n5) Safety PLC bağımsız; VFD/sıcaklık parametreleri yazma koruma anahtarıyla kilitli.")
L4_Q = [
    "Evet, emniyet sistemi üretim/uzak erişim ağına bağımlıysa etkilenir: içeri giren saldırgan sıcaklık limitini, VFD parametrelerini veya emniyet yapılandırmasını bozabilir. Bu yüzden emniyet fonksiyonu erişim güvenliğinden bağımsız çalışmalıdır; erişim kontrolleri tek başına insan güvenliğini garanti etmez.",
    "Üretim ağı veya uzak bakım yolu ele geçirilse, çökse ya da yanlış komut verse bile; kapak açılması, acil stop veya tutkal aşırı sıcaklığı durumunda tahrikler ve ısıtıcı, hiçbir dijital onaya bağlı olmadan tanımlı sürede güvenli duruma geçmeli ve yetkisiz yeniden başlatma engellenmelidir.",
]

L5_Q = [
    "Evet etkiliyor: (1) Component X makinedeki PLC firmware kütüphanesinde var, (2) kurulu sürüm 2.4 etkilenen sürüm, (3) uzak bakım modülü internete açık olduğu için açık ulaşılabilir. Üçü de sağlanıyor.",
    "Hayır, hemen durdurmam: plansız duruş kazan tutkalının bozulmasına ve panel hasarına yol açar. Önce uzak erişimi keser/izole ederim (açık ulaşılabilirliği kapatır), yamayı planlı bakım penceresinde uygularım.",
    "Doğrudan değil; önce test ederim. Hat dışındaki test/staging ortamında (yedek PLC + VFD simülasyonu) yama denenir, ısı kontrolü ve devir davranışı doğrulanır, geri dönüş planı hazırlanır.",
    "Evet etkileyebilir: firmware döngü süresini ve emniyet haberleşmesini değiştirebilir. Yama sonrası emniyet fonksiyonları (acil stop, kapak kilidi, termostat, STO) yeniden test edilir; tepki süreleri ölçülerek anlaşılır.",
    "Uzak erişimi kapatmak, ilgili portları OT güvenlik duvarında engellemek, yazma koruma anahtarını kilitlemek, jump server + VPN + MFA zorunlu kılmak, trafiği izlemek (IDS) ve USB/servis erişimini kısıtlamak.",
]

L6_Q = [
    "Önce vardiya amiri ve OT güvenlik/bakım sorumlusunu ararım. İlk üç eylem: (1) makineyi kontrollü güvenli duruma alırım, (2) ısıtıcı enerjisini keserim, (3) uzak erişimi izole ederim. Hiçbir şeyi resetlemem.",
    "Emniyet zincirinin (acil stop, kapak kilidi, termostat, STO) bağımsız çalıştığını test ederim. PLC/VFD yapılandırma yedeği, log, VPN ve jump server kayıtları korunur (kanıt). Ele geçirilen servis hesabı kapatılır.",
    "Olayın özeti, etkilenen ürün/sürüm, ilk etki (emniyet etkilendi mi), şüpheli saldırı yolu ve alınan acil önlemler hazır olmalı; yetkili otoriteye erken uyarı verilir.",
    "Kök neden (açık servis hesabı/uzak erişim) – OT güvenlik uzmanı; etki ve emniyet doğrulama – emniyet mühendisi; önlem/yama – yazılım ekibi; bildirim metni – yönetim/uyum sorumlusu.",
    "Oturum ve VPN kayıtları, PLC/VFD/Safety PLC yapılandırma ve değişiklik geçmişi, güvenlik duvarı/IDS logları, alarm kayıtları, delil zinciri ile yama ve önlem doğrulama kayıtları.",
]

L7_Q = [
    "Sistem tek modele güvenmez: bağımsız ikinci kontrol (sensör/ölçüm) ve şüpheli parçada insan onayı olur. YZ yalnızca kalite kararı verir; emniyet YZ dışında Safety PLC'de kalır.",
    "Kamera görüntüsü süreklilik, aydınlatma ve ikinci sensörle tutarlılık kontrolüyle doğrulanır. Şüpheli girdide parça OK sayılmaz (RED/karantina), alarm verilir, gerekirse hat güvenli durdurulur, olay loglanır.",
    "Eşik risk analizine göre belirlenir (ör. %90). Eşik altında YZ kararı kullanılmaz: fallback ile parça insana yönlendirilir; art arda düşük güvende hat yavaşlatılır/durdurulur. Varsayılan RED'dir.",
]
L7_TABLE = [
    "İkinci bağımsız kontrol + insan onayı (human override, monitoring); emniyet YZ dışında.",
    "Girdi doğrulama/monitoring ile tespit; şüpheli girdide RED + güvenli duruş (fail-safe) ve alarm.",
    "Confidence threshold: eşik altında fallback – insana sor, yavaşlat/durdur; varsayılan güvenli taraf.",
]

# ------------------------------------------------------------------ DOLDURMA
def fill(src, dst, paket):
    doc = pymupdf.open(src)
    for pg in doc:
        pg.wrap_contents()

    # Kapak
    p = doc[0]
    y = 252 if paket else 228
    p.draw_rect(pymupdf.Rect(50, y, 545, y + 28), color=(0.1, 0.45, 0.65), fill=(0.90, 0.95, 1.0), width=1)
    put(p, (58, y + 3, 540, y + 14), "SEÇİLEN MAKİNE", size=7.5, font=BLD, color=(0.1, 0.4, 0.6))
    put(p, (58, y + 13, 540, y + 27), "Endüstriyel Kenar Bantlama Makinesi – PUR Tutkal Teknolojili (AİMSAD)", size=10.5, font=BLD, color=(0.05, 0.15, 0.4))

    for i in range(1, 8):
        header(doc[i], DATES[i - 1])

    # LAB 1
    p = doc[1]
    p.draw_rect(pymupdf.Rect(37, 268, 483, 300), color=(0.1, 0.65, 0.3), width=2)
    put(p, (372, 258, 540, 267), "Emniyet zinciri (Safety Chain)", size=7, font=BLD, color=GRN, align=2)
    p.draw_rect(pymupdf.Rect(237, 240, 308, 256), color=(0.9, 0.4, 0.05), width=1.6)
    answer_questions(p, L1, 758)

    # LAB 2
    p = doc[2]
    answer_questions(p, [L2_Q1_PAKET if paket else L2_Q1_GENEL, L2_Q2_PAKET if paket else L2_Q2_GENEL, L2_Q3],
                     (518 if paket else 504) - 6)
    hdr_bottom = 541 if paket else 527
    for i, t in enumerate(L2_TABLE):
        top = hdr_bottom + 25.5 * i
        put(p, (357, top + 1.5, 553, top + 25), t, size=7.6, min_size=6)

    # LAB 3
    p = doc[3]
    top0 = 310 if paket else 234
    rh = 42.0
    for i, (sc, l, s, e, sk, pr) in enumerate(L3_ROWS):
        t = top0 + rh * i
        put(p, (43, t + 2, 213, t + rh - 2), sc, size=7.4, min_size=5.8)
        for x0, x1, v in ((215, 270, l), (270, 326, s), (326, 382, e)):
            put(p, (x0, t + 13, x1, t + 31), v, size=12, font=BLD, align=1)
        put(p, (382, t + 12, 472, t + 32), sk, size=13, font=BLD, align=1, color=RED if sk == "27" else INK)
        put(p, (474, t + 12, 553, t + 32), pr, size=9.5, font=BLD, align=1, color=RED if pr == "Kritik" else INK)
    answer_questions(p, L3_Q, (587 if paket else 512) - 4)

    # LAB 4
    p = doc[4]
    ytop = 254 if paket else 238
    ybot = 333 if paket else 317
    put(p, (50, ytop, 288, ybot), L4_MEVCUT, size=8.4, color=RED)
    put(p, (312, 238, 552, ybot), L4_HEDEF, size=8.4, color=GRN)
    answer_questions(p, L4_Q, (521 if paket else 504) - 4)

    # LAB 5
    p = doc[5]
    answer_questions(p, L5_Q, 612)

    # LAB 6
    p = doc[6]
    answer_questions(p, L6_Q, 514)

    # LAB 7
    p = doc[7]
    answer_questions(p, L7_Q, (480 if paket else 462) - 8 - 14)
    hb = 503 if paket else 486
    for i, t in enumerate(L7_TABLE):
        top = hb + 25.5 * i
        put(p, (197, top + 2, 553, top + 25), t, size=8.0, min_size=6)

    doc.save(dst, garbage=3, deflate=True)
    print("Kaydedildi:", dst)

if __name__ == "__main__":
    up = r"C:\Users\VICTUS\.gemini\antigravity\brain\cd65f6dc-b5ac-4e9f-8a4d-9d53c24a201a\.user_uploaded"
    out = r"C:\Users\VICTUS\.gemini\antigravity\scratch\out"
    os.makedirs(out, exist_ok=True)
    fill(os.path.join(up, "media_1793373801981_554a0d4e.pdf"), os.path.join(out, "Foy_Paketleme_Surumu_Kenar_Bantlama_DOLU.pdf"), True)
    fill(os.path.join(up, "media_1793373801937_41861db9.pdf"), os.path.join(out, "Foy_Genel_Surum_Kenar_Bantlama_DOLU.pdf"), False)
