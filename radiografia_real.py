import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
import dns.resolver
import dns.query
import dns.zone
import dns.message
import dns.rdatatype
import datetime

dom = 'cbautistabb.edu.bo'
res = dns.resolver.Resolver()
res.nameservers = ['1.1.1.1', '8.8.8.8']

print(f"Radiografía DNS de {dom} — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("─" * 60)

# 1. NS
try:
    ns_ans = res.resolve(dom, 'NS')
    ns_list = sorted([str(r.target).lower().rstrip('.') for r in ns_ans])
    print(f"[+] Servidores de nombres (NS): {ns_list}")
except Exception as e:
    print(f"[-] Error NS: {e}")
    ns_list = []

# 2. SOA
try:
    soa_ans = res.resolve(dom, 'SOA')
    for r in soa_ans:
        print(f"[+] SOA Serial: {r.serial} | MNAME: {r.mname} | RNAME: {r.rname}")
except Exception as e:
    print(f"[-] Error SOA: {e}")

# 3. A y www
try:
    a_ans = res.resolve(dom, 'A')
    print(f"[+] A (IPv4): {[str(r) for r in a_ans]}")
except Exception as e:
    print(f"[-] A: {e}")

try:
    w_ans = res.resolve('www.' + dom, 'A')
    print(f"[+] www.{dom}: {[str(r) for r in w_ans]}")
except Exception as e:
    print(f"[-] www.{dom}: {e}")

# 4. MX
try:
    mx_ans = res.resolve(dom, 'MX')
    mx_list = [f"{r.preference} {str(r.exchange).rstrip('.')}" for r in mx_ans]
    print(f"[+] MX (Servidores de Correo): {mx_list}")
except Exception as e:
    print(f"[-] MX: {e}")

# 5. TXT / SPF
has_spf = False
try:
    txt_ans = res.resolve(dom, 'TXT')
    for r in txt_ans:
        txt = b"".join(r.strings).decode('utf-8', errors='ignore')
        if 'v=spf1' in txt.lower():
            print(f"[+] SPF: {txt}")
            has_spf = True
    if not has_spf:
        print("[-] SPF: No encontrado")
except Exception as e:
    print(f"[-] TXT/SPF: {e}")

# 6. DMARC
try:
    dmarc_ans = res.resolve('_dmarc.' + dom, 'TXT')
    for r in dmarc_ans:
        print(f"[+] DMARC: {b''.join(r.strings).decode('utf-8', errors='ignore')}")
except Exception as e:
    print(f"[-] DMARC: NO EXISTE (_dmarc.{dom} - Error: {e})")

# 7. CAA
try:
    caa_ans = res.resolve(dom, 'CAA')
    print(f"[+] CAA: {[str(r) for r in caa_ans]}")
except Exception as e:
    print("[-] CAA: NO TIENE REGISTRO CAA (Cualquier CA puede emitir certificados)")

# 8. DNSSEC
try:
    ds_ans = res.resolve(dom, 'DS')
    print(f"[+] DS (DNSSEC en padre): {[str(r) for r in ds_ans]}")
except Exception as e:
    print("[-] DNSSEC: NO FIRMADO (Sin registro DS en la delegación de .bo)")

# 9. PTR
try:
    ip_web = str(a_ans[0])
    ptr_ans = res.resolve_address(ip_web)
    print(f"[+] PTR IP {ip_web}: {[str(r).rstrip('.') for r in ptr_ans]}")
except Exception as e:
    print(f"[-] PTR: {e}")

# 10. AXFR Check
print("\n[+] Prueba de Transferencia de Zona (AXFR):")
for ns in ns_list:
    try:
        ns_ip = str(res.resolve(ns, 'A')[0])
        z = dns.zone.from_xfr(dns.query.xfr(ns_ip, dom, timeout=3))
        print(f"  [!] ALERTA CRÍTICA: AXFR PERMITIDO en {ns} ({ns_ip})")
    except Exception as e:
        print(f"  [✓] AXFR rechazado/bloqueado en {ns} ({e})")
