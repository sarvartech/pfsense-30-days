---
title: IPv4 adreslash va subnetting
duration: 50
quiz:
  - q: 192.168.10.0/26 subnetida nechta foydalanish mumkin bo'lgan (host) manzil bor?
    options: ["64", "62", "30", "126"]
    answer: 1
    explain: "2^(32-26) = 64, minus network va broadcast = 62."
  - q: 10.0.0.77/27 qaysi tarmoqqa tegishli?
    options: ["10.0.0.64/27", "10.0.0.32/27", "10.0.0.77/27", "10.0.0.96/27"]
    answer: 0
    explain: "/27 bloki 32 dan: 0, 32, 64, 96… 77 → 64–95 oralig'ida."
  - q: Quyidagilardan qaysi biri RFC 1918 xususiy (private) manzil EMAS?
    options: ["10.20.30.40", "172.20.1.1", "192.168.0.1", "172.32.0.1"]
    answer: 3
    explain: "172.16.0.0/12 → 172.16.0.0 – 172.31.255.255. 172.32.x.x ommaviy."
  - q: 100.64.0.0/10 diapazoni nima uchun ishlatiladi?
    options: ["Loopback", "CGNAT (provayder ichki NAT)", "Multicast", "Link-local"]
    answer: 1
    explain: Agar uy routeringiz WAN IP si 100.64–100.127 oralig'ida bo'lsa — siz CGNAT ortidasiz va tashqaridan to'g'ridan-to'g'ri kira olmaysiz.
  - q: "/30 maska odatda nima uchun ishlatiladi?"
    options: ["Katta ofis LAN", "Point-to-point (ikki router orasidagi) link", "Broadcast domen", "Loopback"]
    answer: 1
---

# IPv4 adreslash va subnetting

## 1. IPv4 manzil tuzilishi

32 bit, 4 oktet: `192.168.10.25` = `11000000.10101000.00001010.00011001`.
Prefiks (`/24`) — nechta bit **tarmoq** qismi ekanini bildiradi, qolgani — **xost** qismi.

| Prefiks | Maska | Manzillar | Xostlar |
|---|---|---|---|
| /24 | 255.255.255.0 | 256 | 254 |
| /25 | 255.255.255.128 | 128 | 126 |
| /26 | 255.255.255.192 | 64 | 62 |
| /27 | 255.255.255.224 | 32 | 30 |
| /28 | 255.255.255.240 | 16 | 14 |
| /29 | 255.255.255.248 | 8 | 6 |
| /30 | 255.255.255.252 | 4 | 2 |
| /31 | 255.255.255.254 | 2 | 2 (RFC 3021, p2p) |
| /32 | 255.255.255.255 | 1 | 1 (loopback, host route) |

## 2. Tezkor subnetting usuli — "blok o'lchami"

1. Blok = `256 − maskaning qiziqarli okteti`. `/27` → `256 − 224 = 32`.
2. Tarmoqlar: `0, 32, 64, 96, 128, 160, 192, 224`.
3. Manzil qaysi blokka tushsa — o'sha tarmoq. Broadcast = keyingi blok − 1.

**Misol:** `172.16.5.130/26` → blok 64 → tarmoqlar 0, 64, 128, 192 → **172.16.5.128/26**,
xostlar `.129–.190`, broadcast `.191`.

## 3. Maxsus diapazonlar

| Diapazon | Vazifasi |
|---|---|
| 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 | Xususiy (RFC 1918) |
| 100.64.0.0/10 | CGNAT — provayder ichki NAT (RFC 6598) |
| 127.0.0.0/8 | Loopback |
| 169.254.0.0/16 | Link-local (DHCP ishlamaganda APIPA) |
| 224.0.0.0/4 | Multicast |
| 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24 | Hujjatlar uchun (TEST-NET) |

## 4. VLSM — real loyiha

Ofisga `10.10.0.0/22` berildi. Kerak: 300 xodim, 100 Wi-Fi mehmon, 20 server, 4 ta p2p link.

| Segment | Kerak | Prefiks | Tarmoq |
|---|---|---|---|
| Xodimlar | 300 | /23 (510) | 10.10.0.0/23 |
| Mehmon | 100 | /25 (126) | 10.10.2.0/25 |
| Serverlar | 20 | /27 (30) | 10.10.2.128/27 |
| P2P linklar | 4×2 | /30 | 10.10.2.160/30 … 10.10.2.172/30 |

Qoida: **eng kattasidan boshlab** joylashtiring — shunda bo'shliqlar qolmaydi.

## 5. Linuxda tekshirish

```bash
ipcalc 10.0.0.77/27          # yoki: python3 -c "import ipaddress as i; print(i.ip_interface('10.0.0.77/27').network)"
ip -4 addr show
```

## 6. Sizning uy tarmog'ingiz

PPPoE routeringiz WAN manzilini ko'ring. U `100.64.x.x` bo'lsa — CGNAT ortidasiz. Aynan shuning uchun platformamiz
home server ni **VPS orqali** (WireGuard tunnel) internetga chiqaradi — bu haqda VPN kursida batafsil.
