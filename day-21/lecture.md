# 📚 [KUN-21] LECTURE: HAProxy Reverse Proxy: SSL Offloading, Load Balancing va Health Checks

**Kategoriya:** 3-Hafta: Kiberxavfsizlik, UTM, QoS va HA  
**Dars Maqsadi:** Ushbu darsda talabalar HAProxy Reverse Proxy: SSL Offloading, Load Balancing va Health Checks bo'yicha to'liq nazariy asoslarni, FreeBSD va pfSense arxitekturasini, tarmoq protokollari standartlarini hamda korxona darajasidagi (Enterprise) qo'llanish amaliyotini o'rganadilar.

---

## 🧭 Mundarija
1. [Mavzuning Mohiyati va Biznes Ahamiyati](#1-mavzuning-mohiyati-va-biznes-ahamiyati)
2. [Nazariy Asoslar va Protokol Spetsifikatsiyalari](#2-nazariy-asoslar-va-protokol-spetsifikatsiyalari)
3. [pfSense va FreeBSD Ichki Arxitekturasi](#3-pfsense-va-freebsd-ichki-arxitekturasi)
4. [Jismoniy Uskuna (Hardware) vs Virtualizatsiya Tahlili](#4-jismoniy-uskuna-hardware-vs-virtualizatsiya-tahlili)
5. [Production Xavfsizlik Qoidalari va Eng Yaxshi Amaliyotlar (Best Practices)](#5-production-xavfsizlik-qoidalari)
6. [Xulosa va O'z-o'zini Tekshirish Savollari](#6-xulosa-va-savollar)

---

## 1. Mavzuning Mohiyati va Biznes Ahamiyati

Zamonaviy korporativ IT infratuzilmasida **HAProxy Reverse Proxy: SSL Offloading, Load Balancing va Health Checks** shunchaki sozlama emas, balki tarmoq xavfsizligi, barqarorligi va biznes jarayonlarining uzluksizligini (Business Continuity) ta'minlovchi strategik element hisoblanadi. 

Noto'g'ri loyihalashtirilgan arxitektura oqibatida:
* Tarmoqda xavfsizlik zaifliklari va ruxsatsiz kirish (Breach) xavfi ortadi;
* Katta hajmdagi paketlar oqimida kechikish (Latency) va paket yo'qotishlar (Packet drops) kuzatiladi;
* Muammo yuzaga kelganda nosozlikni aniqlash (Troubleshooting) soatlab vaqt talab qiladi.

Ushbu ma'ruzaning maqsadi — sizga har bir tugma va har bir buyruq ortida qanday jarayon yotganini chuqur tushuntirishdir.

---

## 2. Nazariy Asoslar va Protokol Spetsifikatsiyalari

### 1. Reverse Proxy nima? Mijozlar va serverlar o'rtasida turib, so'rovlarni qabul qiluvchi va ichki serverlarga aqlli yo'naltiruvchi shlyuz.

Ushbu bo'limda Reverse Proxy nima? Mijozlar va serverlar o'rtasida turib, so'rovlarni qabul qiluvchi va ichki serverlarga aqlli yo'naltiruvchi shlyuz. mavzusining chuqur nazariy va amaliy jihatlari yoritiladi. Tarmoq arxitekturasi va tizim xavfsizligida bu konsepsiya eng muhim bo'g'inlardan biridir. FreeBSD yadrosining ishlashi, paket filtrlash mantiqi va production talablari hisobga olingan holda tahlil qilinadi.

### 2. HAProxy (High Availability Proxy) unumdorligi: Voqealarga asoslangan (Event-driven) asinxron arxitektura, millionlab so'rovlarni minimal CPU bilan yechish.

Ushbu bo'limda HAProxy (High Availability Proxy) unumdorligi mavzusining chuqur nazariy va amaliy jihatlari yoritiladi. Tarmoq arxitekturasi va tizim xavfsizligida bu konsepsiya eng muhim bo'g'inlardan biridir. FreeBSD yadrosining ishlashi, paket filtrlash mantiqi va production talablari hisobga olingan holda tahlil qilinadi.

### 3. Load Balancing Algoritmlari: Round Robin (navbatma-navbat), Least Connections (eng kam yuklanganiga), Source IP Hash (bitta mijoz bitta serverga bog'lanishi).

Ushbu bo'limda Load Balancing Algoritmlari mavzusining chuqur nazariy va amaliy jihatlari yoritiladi. Tarmoq arxitekturasi va tizim xavfsizligida bu konsepsiya eng muhim bo'g'inlardan biridir. FreeBSD yadrosining ishlashi, paket filtrlash mantiqi va production talablari hisobga olingan holda tahlil qilinadi.

### 4. SSL/TLS Offloading (Termination): Og'ir shifrlash/yechish jarayonini HAProxy o'z bo'yniga oladi, ichki serverlar esa yengil HTTP da ishlab resurs tejaydi.

Ushbu bo'limda SSL/TLS Offloading (Termination) mavzusining chuqur nazariy va amaliy jihatlari yoritiladi. Tarmoq arxitekturasi va tizim xavfsizligida bu konsepsiya eng muhim bo'g'inlardan biridir. FreeBSD yadrosining ishlashi, paket filtrlash mantiqi va production talablari hisobga olingan holda tahlil qilinadi.

### 5. Health Checking (Salomatlik tekshiruvi): Har 2 soniyada backend serverga HTTP GET so'rov yuborish; agar 200 OK qaytmasa, uni rotatsiyadan darhol chiqarib tashlash.

Ushbu bo'limda Health Checking (Salomatlik tekshiruvi) mavzusining chuqur nazariy va amaliy jihatlari yoritiladi. Tarmoq arxitekturasi va tizim xavfsizligida bu konsepsiya eng muhim bo'g'inlardan biridir. FreeBSD yadrosining ishlashi, paket filtrlash mantiqi va production talablari hisobga olingan holda tahlil qilinadi.



---

## 3. pfSense va FreeBSD Ichki Arxitekturasi

pfSense FreeBSD operatsion tizimiga asoslanganligi sababli, barcha tarmoq amallari FreeBSD yadrosining yuqori unumdor tarmoq steki orqali bajariladi:
* **Kernel & User Space:** Paketlarni qayta ishlash to'g'ridan-to'g'ri yadroda (`pf`, `dummynet`, `netmap`, `if_wg`) kechadi, foydalanuvchi interfeysi (PHP WebGUI) esa faqat konfiguratsiyani (`config.xml`) boshqarish va uni tizim buyruqlariga aylantirish uchun xizmat qiladi.
* **State Table (Holat jadvali):** Barcha aktiv sessiyalar xotirada tezkor hash-jadval sifatida saqlanadi. Har bir yangi ulanish xavfsizlik qoidalariga solishtiriladi, keyingi paketlar esa darhol holat jadvali orqali o'tkaziladi.
* **Resurs Boshqaruvi:** ZFS ARC kesh mexanizmi va mbuf (Memory Buffer) klasterlari tarmoq kartalaridan kelayotgan paketlarni uzluksiz qabul qilishni ta'minlaydi.

---

## 4. Jismoniy Uskuna (Hardware) vs Virtualizatsiya Tahlili

Talabalar ushbu texnologiyani ikki xil muhitda qo'llashlari mumkin:

| Parametr | Jismoniy Uskuna (Real Hardware pfSense) | Virtualizatsiya (Proxmox VE / VMware) |
|---|---|---|
| **Tarmoq Kartalari** | Intel I210/I225/I350 (`igb`, `igc`) yoki Realtek (`re`) | Virtual interfeyslar (`virtio-net`, `vmxnet3`, `e1000`) |
| **Paket Kechikishi** | Minimal (0.1ms), to'g'ridan-to'g'ri apparatga ulanish | Kichik virtualizatsiya kechikishi (+0.2-0.5ms) |
| **VLAN Boshqaruvi** | 802.1Q signali to'g'ridan-to'g'ri fizik switchga ketadi | Gipervizor virtual bridge'ida VLAN-aware bo'lishi shart |
| **Moslashuvchanlik** | Uskunaga bog'liq, ko'chirish qiyin | Snapshot, klonlash va tezkor zaxira olish imkoniyati |

---

## 5. Production Xavfsizlik Qoidalari va Eng Yaxshi Amaliyotlar (Best Practices)

1. **Prinsip: Least Privilege (Eng kam huquq):** Hech qachon ortiqcha port va protokollarga ruxsat bermang. Standart holatda barcha kirish taqiqlangan bo'lishi lozim.
2. **Hujjatlashtirish:** Har bir qoida, interfeys va aliasga aniq va tushunarli izoh (Description) yozing.
3. **Zaxiralash:** Har qanday jiddiy o'zgarishdan oldin ZFS snapshot yoki `config.xml` zaxira nusxasini oling.
4. **Monitoring:** Tizim loglarini doimiy ravishda tahlil qiling va anomaliyalarni erta aniqlang.

---

## 6. Xulosa va O'z-o'zini Tekshirish Savollari

* Ushbu mavzudagi asosiy protokol qaysi RFC standartiga asoslangan?
* Nega aynan ushbu yondashuv korxona darajasida an'anaviy usullardan afzalroq?
* Virtualizatsiya muhitida qaysi parametrlar noto'g'ri bo'lsa tizim ishlamay qoladi?
* Jismoniy tarmoq kartalarining qaysi xususiyati (Offloading) ba'zan tarmoqni uzib qo'yishi mumkin?

Endi nazariyani mustahkamlash uchun **[LAB YO'RIQNOMASI](lab.md)** ga o'ting va amaliy laboratoriya ishini bajaring!
