## Topologiya

```
            r1 (1.1.1.1)
      eth1 /         \ eth2
 10.0.12.0/24       10.0.13.0/24
      eth1 /           \ eth1
   r2 (2.2.2.2) ──────── r3 (3.3.3.3)
          eth2  10.0.23.0/24  eth2
```

Interfeys IP manzillari va loopbacklar **oldindan berilgan**. Sizning vazifangiz — OSPF.

## Topshiriqlar

1. `1` → r1 ning **vtysh** konsoliga kiring. Holatni ko'ring:
   ```
   show interface brief
   show ip route
   ```
2. OSPF ni yoqing (har bir routerda router-id o'zining loopbackiga teng):
   ```
   configure terminal
   router ospf
    ospf router-id 1.1.1.1
    network 10.0.0.0/16 area 0
    network 1.1.1.1/32 area 0
    passive-interface lo
   end
   write memory
   ```
3. Xuddi shuni **r2** (2.2.2.2) va **r3** (3.3.3.3) da bajaring.
4. Qo'shnilar: `show ip ospf neighbor` — holat `Full` bo'lishi kerak.
5. LSDB va marshrutlar: `show ip ospf database`, `show ip route ospf`.
6. Linux shell (`1s`) dan tekshiring: `ping -I 1.1.1.1 3.3.3.3`.
7. **Qo'shimcha:** r1–r3 linkida `ip ospf cost 100` bering va `traceroute 3.3.3.3` yo'li qanday o'zgarganini kuzating.
