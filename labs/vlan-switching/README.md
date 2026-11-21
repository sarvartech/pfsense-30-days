## Topologiya

```
               ┌──────── sw1 (br0) ────────┐
          eth1 │ VLAN10    eth2 VLAN10   eth3 VLAN20
             pc10a        pc10b          pc20
       192.168.10.11  192.168.10.12  192.168.10.21
```

Uchala PC **bir xil subnetda**, lekin pc20 boshqa VLAN da bo'lgani uchun unga yetib bo'lmasligi kerak.

## Topshiriqlar (sw1 da)

```bash
ip link add br0 type bridge vlan_filtering 1
for p in eth1 eth2 eth3; do ip link set $p master br0; ip link set $p up; done
ip link set br0 up

bridge vlan del dev eth1 vid 1; bridge vlan add dev eth1 vid 10 pvid untagged
bridge vlan del dev eth2 vid 1; bridge vlan add dev eth2 vid 10 pvid untagged
bridge vlan del dev eth3 vid 1; bridge vlan add dev eth3 vid 20 pvid untagged
bridge vlan show
```

So'ng pc10a dan `ping 192.168.10.12` (ishlashi kerak) va `ping 192.168.10.21` (ishlamasligi kerak).
`bridge fdb show br br0` bilan MAC jadvalini o'rganing.
