# 📚 [KUN-15] LECTURE: Zero-Trust va Overlay Network: Tailscale Subnet Router

**Kategoriya:** 2-Hafta: Marshrutlash, Multi-WAN va VPN  
**Dars Maqsadi:** Ushbu darsda talabalar Zero-Trust va Overlay Network: Tailscale Subnet Router bo'yicha to'liq nazariy asoslarni, FreeBSD va pfSense arxitekturasini, tarmoq protokollari standartlarini hamda korxona darajasidagi (Enterprise) qo'llanish amaliyotini o'rganadilar.

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

Zamonaviy korporativ IT infratuzilmasida **Zero-Trust va Overlay Network: Tailscale Subnet Router** shunchaki sozlama emas, balki tarmoq xavfsizligi, barqarorligi va biznes jarayonlarining uzluksizligini (Business Continuity) ta'minlovchi strategik element hisoblanadi. 

Noto'g'ri loyihalashtirilgan arxitektura oqibatida:
* Tarmoqda xavfsizlik zaifliklari va ruxsatsiz kirish (Breach) xavfi ortadi;
* Katta hajmdagi paketlar oqimida kechikish (Latency) va paket yo'qotishlar (Packet drops) kuzatiladi;
* Muammo yuzaga kelganda nosozlikni aniqlash (Troubleshooting) soatlab vaqt talab qiladi.

Ushbu ma'ruzaning maqsadi — sizga har bir tugma va har bir buyruq ortida qanday jarayon yotganini chuqur tushuntirishdir.

---

## 2. Nazariy Asoslar va Protokol Spetsifikatsiyalari

### 1. Zero-Trust Network Access (ZTNA) tamoyillari: Hech kimga va hech bir tarmoqqa ishonmaslik, har bir ulanishni shifrlash va tekshirish.

Ushbu bo'limda Zero-Trust Network Access (ZTNA) tamoyillari mavzusining chuqur nazariy va amaliy jihatlari yoritiladi. Tarmoq arxitekturasi va tizim xavfsizligida bu konsepsiya eng muhim bo'g'inlardan biridir. FreeBSD yadrosining ishlashi, paket filtrlash mantiqi va production talablari hisobga olingan holda tahlil qilinadi.

### 2. Overlay Mesh Networks: Murakkab jismoniy tarmoqlar ustida virtual dasturiy tarmoq qurish.

Ushbu bo'limda Overlay Mesh Networks mavzusining chuqur nazariy va amaliy jihatlari yoritiladi. Tarmoq arxitekturasi va tizim xavfsizligida bu konsepsiya eng muhim bo'g'inlardan biridir. FreeBSD yadrosining ishlashi, paket filtrlash mantiqi va production talablari hisobga olingan holda tahlil qilinadi.

### 3. Tailscale arxitekturasi: WireGuard protokoliga asoslangan, koordinatsiya serveri (Control Plane) va DERP (Designated Encrypted Relay for Packets) relaylari orqali har qanday CGNAT va Firewall ni teshish (NAT Traversal / UDP hole punching).

Ushbu bo'limda Tailscale arxitekturasi mavzusining chuqur nazariy va amaliy jihatlari yoritiladi. Tarmoq arxitekturasi va tizim xavfsizligida bu konsepsiya eng muhim bo'g'inlardan biridir. FreeBSD yadrosining ishlashi, paket filtrlash mantiqi va production talablari hisobga olingan holda tahlil qilinadi.

### 4. pfSense Subnet Router sifatida: pfSense o'zining butun orqa tarmog'ini (masalan `10.10.0.0/16`) Tailscale mesh tarmog'iga e'lon qiladi (Advertise Routes).

Ushbu bo'limda pfSense Subnet Router sifatida mavzusining chuqur nazariy va amaliy jihatlari yoritiladi. Tarmoq arxitekturasi va tizim xavfsizligida bu konsepsiya eng muhim bo'g'inlardan biridir. FreeBSD yadrosining ishlashi, paket filtrlash mantiqi va production talablari hisobga olingan holda tahlil qilinadi.

### 5. Exit Node imkoniyati: Barcha masofaviy qurilmalar internetga pfSense orqali xavfsiz chiqishi.

Ushbu bo'limda Exit Node imkoniyati mavzusining chuqur nazariy va amaliy jihatlari yoritiladi. Tarmoq arxitekturasi va tizim xavfsizligida bu konsepsiya eng muhim bo'g'inlardan biridir. FreeBSD yadrosining ishlashi, paket filtrlash mantiqi va production talablari hisobga olingan holda tahlil qilinadi.



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
