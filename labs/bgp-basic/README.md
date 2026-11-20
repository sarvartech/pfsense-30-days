## Topologiya

```
pc1 10.1.0.10 ── r1 (AS65001) ══ eBGP 172.16.0.0/30 ══ r2 (AS65002) ── pc2 10.2.0.10
                 10.1.0.1                                10.2.0.1
```

## Topshiriqlar

1. **r1** (vtysh):
   ```
   configure terminal
   router bgp 65001
    bgp router-id 192.0.2.1
    no bgp ebgp-requires-policy
    neighbor 172.16.0.2 remote-as 65002
    neighbor 172.16.0.2 description ISP-B
    address-family ipv4 unicast
     network 10.1.0.0/24
    exit-address-family
   end
   write memory
   ```
2. **r2** da ko'zgu konfiguratsiya: AS65002, neighbor `172.16.0.1 remote-as 65001`, `network 10.2.0.0/24`.
3. `show bgp summary`, `show bgp ipv4 unicast` — AS_PATH ustunini tahlil qiling.
4. pc1 (`3`) dan: `ping 10.2.0.10`, `traceroute 10.2.0.10`.
5. **Qo'shimcha (production amaliyot):** `no bgp ebgp-requires-policy` ni olib tashlab, prefix-list + route-map bilan faqat o'z prefiksingizni e'lon qiling.
