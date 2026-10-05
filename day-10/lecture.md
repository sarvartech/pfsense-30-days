# 📚 [KUN-10] LECTURE: Enterprise OpenVPN Remote Access (Road Warrior), PKI/CA va TLS-Crypt

**Kategoriya:** 2-Hafta: Marshrutlash, Multi-WAN va VPN  
**Maqsad:** Masofaviy xodimlar, dasturchilar va rahbarlar uchun har qanday joydan (uy, aeroport, kafe) korporativ serverlarga xavfsiz shifrlangan ulanish qurish. Korxona PKI infratuzilmasi, TLS-Crypt himoyasi va Multi-WAN sharoitida VPN failover mexanizmini o'rganish.

---

## 🧭 Mundarija
1. [OpenVPN Protokoli va SSL/TLS Arxitekturasi](#1-openvpn-protokoli)
2. [PKI (Public Key Infrastructure): CA, Server va Client Sertifikatlari](#2-pki-arxitekturasi)
3. [Nega UDP 1194 va TLS-Crypt?](#3-tls-crypt-va-port-skanerlashdan-himoya)
4. [Split Tunneling vs Full Tunneling](#4-split-vs-full-tunneling)
5. [Multi-WAN bilan OpenVPN Integratsiyasi](#5-multi-wan-bilan-openvpn)
6. [CARP Klasterida OpenVPN VIP Bog'lanishi](#6-carp-va-openvpn)
7. [Xulosa](#7-xulosa)

---

## 1. OpenVPN Protokoli va SSL/TLS Arxitekturasi

OpenVPN — dunyodagi eng sinovdan o'tgan, o'ta moslashuvchan ochiq kodli VPN protokoli hisoblanadi. U foydalanuvchilarni autentifikatsiya qilish va ma'lumotlarni shifrlash uchun **OpenSSL** kutubxonasiga tayanadi:
* **TUN (Tunnel) Rejimi:** Layer 3 (IP darajasida) ishlaydi. Masofaviy mijozlar uchun eng optimal rejim (Broadcast paketlarni o'tkazmaydi, trafik tejaladi).
* **TAP (Bridge) Rejimi:** Layer 2 (Ethernet darajasida) ishlaydi. Korxona bitta umumiy L2 broadcast domenida ishlashi kerak bo'lgan kamdan-kam holatlarda qo'llaniladi.

---

## 2. PKI (Public Key Infrastructure)

Korporativ xavfsizlikda faqat login/parolga ishonish xavflidir. OpenVPN ikki faktorli kriptografiyadan foydalanadi:
1. **Root Certificate Authority (CA):** Korxonaning bosh sertifikatlash markazi (pfSense ichida yaratiladi).
2. **Server Certificate:** pfSense OpenVPN serverining shaxsini tasdiqlovchi sertifikat.
3. **Client Certificates:** Har bir xodimga alohida shaxsiy sertifikat chiqariladi (`user-ali`, `user-nodir`). Agar xodim ishdan ketsa, uning sertifikati bekor qilinadi (Revocation List - CRL).

---

## 3. Nega UDP 1194 va TLS-Crypt?

* **UDP vs TCP:** Nega VPN TCP ustida qurilmasligi kerak? Chunki agar ichki trafik TCP bo'lsa va VPN ham TCP bo'lsa, paket yo'qolganda "TCP-over-TCP meltdown" effekti yuzaga keladi (ikkala qatlam ham qayta so'rov jo'natib kanalni tiqib qo'yadi). UDP 1194 esa yengil va eng tezkor ishlaydi.
* **TLS-Crypt Kuchi:** An'anaviy OpenVPN serveri UDP port 1194 da tinglab turadi va xakerlar skaner qilganda ochiq portni ko'ra oladi. **TLS-Crypt** yordamida esa hatto dastlabki TLS handshake paketlari ham maxsus simmetrik kalit bilan shifrlanadi. Natijada:
  1. Hujumchilar uchun port mutlaqo yopiq (filtrlanmagan/dead) ko'rinadi.
  2. Port skanerlari va DoS hujumlar pfSense yadrosi darajasidayoq to'xtatiladi.

---

## 4. Split Tunneling vs Full Tunneling

* **Split Tunneling (Tavsiya etiladi):** Xodim VPN ga ulanganda, faqat korporativ tarmoqqa boruvchi paketlar (`10.10.0.0/16`) tunnel orqali o'tadi. YouTube, Instagram va oddiy internet trafigi esa xodimning o'z uy interneti orqali ketadi.
* **Full Tunneling:** Xodimning 100% barcha trafigi ofis orqali filtrlanadi. Bu banklar va davlat tashkilotlarida xodimlarning internet xatti-harakatlarini qat'iy nazorat qilish uchun ishlatiladi.

---

## 5. Multi-WAN bilan OpenVPN Integratsiyasi

Agar korxonada 2 ta provayder bo'lsa, xodimlar asosiy provayder uzilganda ham VPN ga ulana olishi kerak:
1. pfSense da OpenVPN server interfeysi sifatida `Localhost` tanlanishi mumkin yoki ikkala WAN uchun alohida Port Forward qilinadi.
2. Xodimning `.ovpn` konfiguratsiya faylida bir nechta `remote` qatori yoziladi:
```text
remote 203.0.113.5 1194 udp
remote 198.51.100.14 1194 udp
```
OpenVPN mijozi birinchi IP javob bermasa, avtomatik ravishda ikkinchi IP ga ulanadi!

---

## 6. CARP Klasterida OpenVPN VIP Bog'lanishi

Ikkita pfSense (CARP klasteri) mavjud bo'lsa, OpenVPN Server jismoniy WAN IP siga emas, balki **WAN CARP VIP** ga biriktiriladi (`Interface: CARP VIP`). Natijada, agar Master firewall ishdan chiqsa, Backup firewall CARP VIP ni o'ziga oladi va OpenVPN serveri ikkinchi tugunda mijozlar uchun zudlik bilan xizmat ko'rsatishni boshlaydi.
