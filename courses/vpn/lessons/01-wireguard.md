---
title: "WireGuard: zamonaviy, tez va sodda VPN"
duration: 45
lab: wireguard-p2p
quiz:
  - q: WireGuard qaysi transport protokolini ishlatadi?
    options: ["TCP", "UDP", "ESP", "GRE"]
    answer: 1
  - q: AllowedIPs parametri nima vazifani bajaradi?
    options:
      - Faqat firewall qoidasi
      - Ham chiquvchi marshrutlash (qaysi IP shu peerga), ham kiruvchi filtr (shu peerdan qaysi manba IP qabul qilinadi) — cryptokey routing
      - DNS sozlamasi
      - Faqat log uchun
    answer: 1
  - q: CGNAT ortidagi uy serveri VPS ga WireGuard bilan ulanadi. Tunnel uzilib qolmasligi uchun nima kerak?
    options: ["MTU 9000", "PersistentKeepalive = 25 (uy tomonida)", "TCP rejim", "Statik MAC"]
    answer: 1
    explain: Keepalive NAT jadvalidagi UDP yozuvini "tirik" ushlab turadi, shunda VPS istalgan paytda uyga paket yubora oladi.
  - q: WireGuard da kalit almashinuvi qaysi protokol asosida?
    options: ["IKEv2", "TLS 1.3", "Noise protokol freymvorki (Noise_IK)", "SSH"]
    answer: 2
---

# WireGuard

## 1. Nega WireGuard?

| | IPsec | OpenVPN | WireGuard |
|---|---|---|---|
| Kod hajmi | ~400 000 qator | ~100 000 | **~4 000** |
| Transport | ESP/UDP 500/4500 | UDP/TCP | UDP |
| Kriptografiya | Kelishiladi (ko'p variant) | TLS | Qat'iy: Curve25519, ChaCha20-Poly1305, BLAKE2s |
| Tezlik | Yuqori | O'rta | **Juda yuqori (kernel)** |
| Sozlash | Murakkab | O'rta | Sodda |

## 2. Asosiy tushunchalar

* Har bir tomonda **kalit juftligi** (private/public), SSH kalitlariga o'xshab.
* **Peer** = ochiq kalit + (ixtiyoriy) endpoint + **AllowedIPs**.
* **Cryptokey routing:** chiqishda — paket manzili qaysi peerning AllowedIPs iga tushsa, o'sha peerga shifrlab yuboriladi;
  kirishda — shifr ochilgandan keyin manba IP shu peerning AllowedIPs ida bo'lmasa, tashlanadi.
* WireGuard "jim" — handshake bo'lmaguncha hech narsa yubormaydi, skanerlarda ko'rinmaydi.

## 3. wg-quick konfiguratsiyasi

```ini
# /etc/wireguard/wg0.conf — VPS (public IP)
[Interface]
Address = 10.99.0.1/24
ListenPort = 51820
PrivateKey = <VPS_PRIVATE>

[Peer]
# home server (CGNAT ortida)
PublicKey = <HOME_PUBLIC>
AllowedIPs = 10.99.0.2/32
```

```ini
# /etc/wireguard/wg0.conf — Home server
[Interface]
Address = 10.99.0.2/24
PrivateKey = <HOME_PRIVATE>
MTU = 1412            # PPPoE (1492) − WireGuard overhead (80)

[Peer]
PublicKey = <VPS_PUBLIC>
Endpoint = vps.example.uz:51820
AllowedIPs = 10.99.0.1/32
PersistentKeepalive = 25
```

```bash
systemctl enable --now wg-quick@wg0
wg show
```

## 4. MTU — eng ko'p uchraydigan muammo

WireGuard overhead: IPv4 da 60 bayt, IPv6 da 80 bayt. PPPoE ustida: `1492 − 80 = 1412`. Noto'g'ri MTU belgisi:
ping ishlaydi, lekin SSH/HTTPS "osilib" qoladi.

## 5. Amaliyot

Labda ikki "filial" orasida qo'lda (wg-quick siz) tunnel ko'tarasiz — bu sizga har bir parametrni tushunishga yordam beradi.
