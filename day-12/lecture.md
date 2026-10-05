# 📚 [KUN-12] LECTURE: WireGuard High-Performance VPN — FreeBSD Kernel Module va Benchmarking

**Kategoriya:** 2-Hafta: Marshrutlash, Multi-WAN va VPN  
**Maqsad:** Eng zamonaviy, tezkor va xavfsiz VPN protokoli — WireGuard ning pfSense 2.7.2 dagi rasmiy yadro moduli (`if_wg`), kriptografik tamoyillari va gigabitli optik kanallarda OpenVPN bilan ishlash unumdorligini solishtirish.

---

## 🧭 Mundarija
1. [WireGuard Inqilobi va Arxitekturasi](#1-wireguard-inqilobi)
2. [Zamonaviy Kriptografik Stek](#2-zamonaviy-kriptografik-stek)
3. [Cryptokey Routing Tamoyili](#3-cryptokey-routing)
4. [FreeBSD Kernel if_wg vs Go Userspace](#4-freebsd-kernel-moduli)
5. [OpenVPN vs WireGuard Benchmark Tahlili](#5-benchmark-tahlili)
6. [Xulosa](#6-xulosa)

---

## 1. WireGuard Inqilobi va Arxitekturasi

WireGuard — Jason A. Donenfeld tomonidan yaratilgan bo'lib, an'anaviy VPN protokollarining (IPsec, OpenVPN) ulkan kod bazasi va sekinligini butkul o'zgartirdi:
* **Kod hajmi:** OpenVPN ~100,000 qatordan ortiq kodga ega, IPsec esa 400,000 qator. WireGuard esa atigi **~4,000 qator kod**. Bu uning xavfsizlik auditini osonlashtiradi va zaifliklar (vulnerabilities) ehtimolini keskin kamaytiradi.
* **Soddalik:** Murakkab kriptografik kelishuvlar (Cipher Negotiation) yo'q. Bir xil va eng xavfsiz zamonaviy algoritmlar qat'iy belgilangan.

---

## 2. Zamonaviy Kriptografik Stek

WireGuard eskirgan RSA va SHA-1 dan mutlaqo voz kechgan:
* **Shifrlash va Autentifikatsiya:** ChaCha20 va Poly1305 (AEAD).
* **Kalit almashinuvi:** Curve25519 (ECDH - Elliptic Curve).
* **Xeshlash:** BLAKE2s.
* **Kalit derivatsiyasi:** HKDF.

---

## 3. Cryptokey Routing Tamoyili

WireGuard har bir Peer (hamkor) ni oddiy marshrut jadvaliga bog'laydi:
* Har bir Peer o'zining **Public Key** si va ruxsat berilgan IP manzillar ro'yxatiga (**AllowedIPs**) ega.
* Agar paket jo'natilayotganda manzil `AllowedIPs` ga to'g'ri kelsa, u o'sha Peerning ochiq kaliti bilan shifrlanadi.
* Begona kalit bilan shifrlangan yoki `AllowedIPs` dan tashqaridagi IP manzildan kelgan paketlar shunchaki e'tiborsiz tashlab yuboriladi (Drop).

---

## 4. FreeBSD Kernel if_wg vs Go Userspace

pfSense 2.7.2 da WireGuard rasmiy FreeBSD yadro drayveri (`if_wg`) sifatida ishlaydi:
* Userspace (Go/Rust) da har bir paket yadro va dastur o'rtasida xotiradan-xotiraga (Context Switch) nusxalanadi, bu esa protsessorni kuchli yuklaydi.
* **Kernel Module (`if_wg`):** Paketlar bevosita yadro ichida shifrlanadi va marshrutlanadi. Natijada 10Gbps gacha bo'lgan tezliklarda minimal CPU yuklamasi ta'minlanadi.

---

## 5. OpenVPN vs WireGuard Benchmark Tahlili

| Ko'rsatkich | OpenVPN (AES-256-GCM) | WireGuard (ChaCha20-Poly1305) | Yutuq |
|---|:---:|:---:|:---:|
| **Ulanish Vaqti (Handshake)** | 3 - 8 soniya | **< 100 millisoniya** | 50x tezroq |
| **O'tkazuvchanlik (1Gbps kanal)**| ~180 - 250 Mbps | **~850 - 950 Mbps** | 4x tezroq |
| **CPU Yuklamasi (Yuklama ostida)**| 85 - 100% | **15 - 25%** | 4x yengilroq |
| **Roaming (Wi-Fi -> LTE)** | Ulanish uziladi (Re-auth) | **Uzluksiz davom etadi** | Choksiz |
