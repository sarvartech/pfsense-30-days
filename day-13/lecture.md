# 📚 [KUN-13] LECTURE: Enterprise IPsec IKEv2 Site-to-Site va Routed VTI (Virtual Tunnel Interface)

**Kategoriya:** 2-Hafta: Marshrutlash, Multi-WAN va VPN  
**Maqsad:** Korporativ gigantlar, banklar va telekom operatorlari standarti bo'lgan IPsec IKEv2 protokolini, Phase 1 va Phase 2 kripto-to'plamlarini, hamda an'anaviy Policy-based IPsec o'rniga zamonaviy Route-based VTI arxitekturasini o'rganish.

---

## 🧭 Mundarija
1. [IPsec Arxitekturasi va Standartlari](#1-ipsec-arxitekturasi)
2. [IKEv1 vs IKEv2: Nega IKEv2 Sanoat Standarti?](#2-ikev1-vs-ikev2)
3. [Phase 1 (IKE SA) va Phase 2 (Child SA) Jarayoni](#3-phase-1-va-phase-2)
4. [Policy-Based IPsec vs Route-Based VTI](#4-policy-vs-route-based-vti)
5. [VTI ustida BGP/OSPF Dinamik Marshrutlash](#5-vti-ustida-dinamik-marshrutlash)
6. [Xulosa](#6-xulosa)

---

## 1. IPsec Arxitekturasi

IPsec (Internet Protocol Security) — tarmoq qatlamida (Layer 3) ishlovchi eng xavfsiz protokollar to'plamidir.
* **ESP (Encapsulating Security Payload - IP Protocol 50):** Ma'lumotlarni shifrlash va yaxlitligini ta'minlash uchun asosiy protokol.
* **AH (Authentication Header - IP Protocol 51):** Faqat autentifikatsiya beradi, shifrlamaydi (ishlab chiqarishda kam ishlatiladi).
* **UDP 500 (IKE) va UDP 4500 (NAT-Traversal):** Kalitlarni kelishish va NAT ortidagi qurilmalarni ulash portlari.

---

## 2. IKEv1 vs IKEv2

* **IKEv1 (Eskirgan):** Ko'p paket almashinuvi (Main Mode - 6 ta paket), sekin qayta ulanish, NAT bilan ishlashda qiyinchiliklar.
* **IKEv2 (RFC 7296):**
  * Atigi 4 ta paketda tunnelni o'rnatadi.
  * O'rnatilgan **NAT-Traversal (NAT-T)**.
  * **Dead Peer Detection (DPD):** Aloqa uzilganda soniyalarda aniqlash.
  * **MOBIKE:** IP manzil o'zgarganda tunnelni uzmasdan davom ettirish.

---

## 3. Phase 1 (IKE SA) va Phase 2 (Child SA)

1. **Phase 1 (IKE SA):** Ikki router bir-birini taniydi va o'zaro boshqaruv kanalini xavfsiz qiladi:
   * Diffie-Hellman (DH) guruhlari: Group 14 (2048-bit) yoki Group 19/20 (Elliptic Curve).
   * Shifrlash: `AES-256-GCM` yoki `AES-CBC`.
2. **Phase 2 (Child SA):** Haqiqiy foydalanuvchi ma'lumotlarini tashuvchi shifrlangan tunnel:
   * Perfect Forward Secrecy (PFS): Har bir sessiya uchun yangi mustaqil kalitlar generatsiyasi.

---

## 4. Policy-Based IPsec vs Route-Based VTI

* **Policy-Based (An'anaviy):** Shpion qoidalari (SPD) orqali ishlaydi. Tarmoq interfeysi yo'q, `ping` va `traceroute` bilan tekshirish qiyin, dinamik marshrutlash (OSPF/BGP) ulab bo'lmaydi.
* **Route-Based (VTI - Virtual Tunnel Interface):** pfSense da haqiqiy virtual tarmoq kartasi (`ipsecX`) paydo bo'ladi.
  * Unga IP manzil beriladi (masalan `10.254.254.1/30`).
  * Siz oddiy `route add` orqali trafikni tunnelga yo'naltirasiz.
  * VTI ustidan OSPF va BGP protokollarini bemalol yurgizish mumkin!
