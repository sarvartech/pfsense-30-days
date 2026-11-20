---
title: "iproute2: ip, ss, bridge — zamonaviy Linux tarmoq vositalari"
duration: 45
lab: linux-basics
quiz:
  - q: Interfeysga IP manzil qo'shuvchi buyruq?
    options: ["ifconfig eth1 add", "ip addr add 10.0.0.1/24 dev eth1", "ip route add 10.0.0.1 dev eth1", "ss -a eth1"]
    answer: 1
  - q: Tinglayotgan TCP portlarni jarayon nomi bilan ko'rsatadigan buyruq?
    options: ["ss -tlnp", "ip link", "netstat -r", "ip neigh"]
    answer: 0
  - q: "`ip route get 8.8.8.8` nima qiladi?"
    options: ["8.8.8.8 ga ping yuboradi", "Yadro aynan qaysi marshrut, interfeys va manba IP tanlashini ko'rsatadi", "DNS so'rov yuboradi", "Marshrut qo'shadi"]
    answer: 1
  - q: "`ip addr add` bilan berilgan manzil server qayta yuklanganda nima bo'ladi?"
    options: ["Saqlanadi", "Yo'qoladi — doimiy bo'lishi uchun netplan/systemd-networkd/NetworkManager konfiguratsiyasi kerak", "Faqat IPv6 saqlanadi", "DHCP ga o'tadi"]
    answer: 1
---

# iproute2 — zamonaviy Linux tarmoq vositalari

`ifconfig`, `route`, `arp`, `netstat` (net-tools) eskirgan. Bugungi standart — **iproute2**.

## 1. Asosiy buyruqlar xaritasi

| Vazifa | Eski | Yangi |
|---|---|---|
| Interfeyslar | `ifconfig -a` | `ip -br link` / `ip -br addr` |
| IP qo'shish | `ifconfig eth0 10.0.0.1/24` | `ip addr add 10.0.0.1/24 dev eth0` |
| Marshrutlar | `route -n` | `ip route` |
| ARP | `arp -n` | `ip neigh` |
| Soketlar | `netstat -tlnp` | `ss -tlnp` |
| Bridge | `brctl show` | `bridge link`, `ip link add br0 type bridge` |

## 2. Interfeyslar

```bash
ip -br link                      # qisqa ro'yxat
ip link set eth1 up              # yoqish
ip link set eth1 mtu 1492        # PPPoE uchun MTU
ip -s link show eth1             # statistika: RX/TX, xatolar, drop
```

## 3. Manzillar va marshrutlar

```bash
ip addr add 10.0.12.1/24 dev eth1
ip addr del 10.0.12.1/24 dev eth1
ip route add 192.168.50.0/24 via 10.0.12.2
ip route add default via 10.0.12.254
ip route get 192.168.50.10       # yadro qaysi yo'lni tanlaydi?
```

`ip route get` — eng foydali diagnostika buyrug'i: chiqish interfeysi, gateway va **manba IP** ni ko'rsatadi.

## 4. Qo'shnilar va soketlar

```bash
ip neigh                         # ARP/NDP jadvali
ip neigh flush dev eth1
ss -tunap                        # barcha TCP/UDP ulanishlar
ss -tlnp 'sport = :22'           # 22-portni kim tinglayapti
```

## 5. Doimiy konfiguratsiya

`ip` bilan qilingan o'zgarishlar **vaqtinchalik**. Doimiy qilish uchun distributivga qarab:

* Ubuntu: **netplan** (`/etc/netplan/*.yaml`) → systemd-networkd
* Debian: `/etc/network/interfaces` yoki systemd-networkd
* RHEL/Fedora: NetworkManager (`nmcli`)

## 6. Amaliyot

Laboratoriyada `host1` va `host2` ni ulang, so'ng qo'shimcha mashq: host1 ga `ip route add 192.168.99.0/24 via 10.0.12.2`
qo'shib, `ip route get 192.168.99.5` natijasini tahlil qiling.
