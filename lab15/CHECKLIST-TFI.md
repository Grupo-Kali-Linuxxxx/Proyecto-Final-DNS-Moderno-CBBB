# Lista de Verificación y Rúbrica Oficial de Evaluación (Trabajo Final Integrador)

**Organización Beneficiaria:** Colegio Bautista Boliviano Brasileño (CBBB)  
**Dominio Interno:** `cbbb.internal` | **Dominio Público:** `cbautistabb.edu.bo` (`cbbb.example`)  
**Equipo de Estudiantes:**
1. Ketfer Gianella Salazar
2. Charles Yourdan Conde
3. Brian Calás
4. Marco Barriga
5. Adaniel Balderrama Orellana

**Asignatura:** Tecnología Web I (SIS-0150) — Sexto Semestre  
**Docente Titular:** M.Sc. Ing. Jimmy Nataniel Requena Llorentty  
**Calificación Objetivo:** **30 / 30 Puntos (Nivel Estratégico Máximo)**  

---

## 1. Criterio 1: DNS de la Organización: Diseño e Implementación (9 / 9 Puntos)

| Requisito de la Rúbrica | Estado | Evidencia Técnica Documentada en el Repositorio |
|---|:---:|---|
| **Plan de nombres estructurado y funcional** | [x] | Zonas directa interna (`cbbb.internal`), inversa (`10.10.10.in-addr.arpa`) y externa (`cbbb.example` proyectada a `cbautistabb.edu.bo`) resolviendo sin errores en `ns1` y `ns2`. |
| **BIND 9 primario y secundario con Vistas Split-Horizon** | [x] | Vistas `interna` y `externa` configuradas con directiva `match-clients`. Clientes internos resuelven servicios privados en 10.10.10.x; clientes externos reciben `REFUSED` para nombres privados. |
| **Replicación segura TSIG con avisos NOTIFY** | [x] | Transferencias de zona AXFR protegidas con clave secreta compartida HMAC-SHA256 (`transferencia.key`). Incremento de serial SOA notificado y replicado en `ns2` en menos de 2 segundos. |
| **Zona pública descrita como código en DNSControl** | [x] | Archivo declarativo `dnsconfig.js` auditado con el ciclo completo: `dnscontrol check` → `dnscontrol preview` → `dnscontrol push` sin discrepancias sintácticas. |
| **PLUS ESTRATÉGICO (9/9): Procedimiento de cambios y Plan de migración a DNS gestionado/híbrido** | [x] | Documentado en [`PROCEDIMIENTO_CAMBIOS_DNS.md`](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/PROCEDIMIENTO_CAMBIOS_DNS.md). Prueba documentada de incremento de serial SOA (`YYYYMMDDnn`), gestión de TTLs (300s previo a cambios, 86400s en producción) y plan de adopción de Anycast híbrido (Cloudflare/Route53 + BIND 9 local) para el CBBB. |

---

## 2. Criterio 2: Seguridad del DNS e Integración de Servicios (9 / 9 Puntos)

| Requisito de la Rúbrica | Estado | Evidencia Técnica Documentada en el Repositorio |
|---|:---:|---|
| **Zona pública firmada con DNSSEC y validada con `delv`** | [x] | Automatización con `dnssec-policy standard`. Validación criptográfica positiva desde nodo externo con `delv` arrojando `; fully validated`. Validación negativa de inexistencia blindada con `NSEC3`. |
| **Resolutor Unbound con DNS sobre TLS (DoT) y RPZ escolar** | [x] | Unbound (`10.10.10.4`) canaliza consultas externas cifradas hacia el puerto TCP 853 (demostrado con `tcpdump: nada por el 53`). Lista de filtrado RPZ activa bloqueando dominios de apuestas y malware escolar (`NXDOMAIN`). |
| **Sitio Web HTTPS con TLS 1.3, HSTS y CSP** | [x] | Nginx en `10.10.10.20` con certificados emitidos por la CA institucional (vigencia > 80 días), redirección 301 obligatoria, HSTS (`max-age=31536000`), CSP y X-Content-Type-Options: nosniff. |
| **Acceso Remoto SSH blindado y Fail2ban** | [x] | OpenSSH 9.6 configurado con solo claves asimétricas Ed25519, `PermitRootLogin no`, `PasswordAuthentication no`, jaula SFTP en `/srv/cbbb` propiedad de `root:root (755)` y Fail2ban activo en `nftables`. |
| **Servicio de Correo Institucional Criptográfico** | [x] | Postfix 3.8 con buzones Maildir, Dovecot IMAPS 993 (puerto 143 cerrado), Submission 587 autenticado con SASL y anti-spoofing con tabla PCRE. Registros MX, SPF estricto (`-all`), DKIM RSA 2048 y DMARC `p=quarantine`. Envíos recibidos con `dkim=pass`, `spf=pass` y `dmarc=pass`. |
| **PLUS ESTRATÉGICO (9/9): Servicio investigado integrado al dominio** | [x] | Documentado en [`SERVICIO_INVESTIGADO_DNS01_NSUPDATE.md`](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/SERVICIO_INVESTIGADO_DNS01_NSUPDATE.md). Implementación de **certificados comodín SSL por desafío DNS-01 (RFC 8555 / ACME)** y actualización dinámica de registros con **`nsupdate` (RFC 2136) y firmas TSIG**. |

---

## 3. Criterio 3: Administración, Seguridad y Documentación Operativa (12 / 12 Puntos)

| Requisito de la Rúbrica | Estado | Evidencia Técnica Documentada en el Repositorio |
|---|:---:|---|
| **Firewall perimetral UFW con auditoría Nmap** | [x] | Política por defecto `deny (incoming)`. Escaneo Nmap desde internet confirma únicamente puertos **22 (SSH con rate-limiting), 80 (HTTP) y 443 (HTTPS)** abiertos. |
| **Reportes GoAccess y Respaldos Restic probados** | [x] | Panel de análisis web GoAccess protegido con HTTP Basic (`ti:Reportes2026!`). Respaldos automáticos programados con temporizador systemd; script `probar_restauracion.sh` certifica restauración idéntica con huella SHA-256 intacta. |
| **Auditoría interna ≥ 90% y externa al 100%** | [x] | Verificador `auditar_infraestructura.sh` superó **29 de 29 comprobaciones (100%)** y `auditar_publico.sh` superó **7 de 7 comprobaciones (100%)** documentadas en [`INFORME_AUDITORIA.md`](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/INFORME_AUDITORIA.md). |
| **Manual de Operación integral y DRP** | [x] | Documentado en [`MANUAL_OPERACION.md`](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/MANUAL_OPERACION.md), detallando tareas frecuentes paso a paso, mantenimiento periódico, matriz de resolución de incidentes y DRP para reconstruir el servidor en 20-25 minutos. |
| **PLUS ESTRATÉGICO (12/12): Plan de adopción real (costos, riesgos y migración) y solvencia oral** | [x] | Documentado en [`PLAN_ADOPCION_CBBB.md`](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/PLAN_ADOPCION_CBBB.md) con análisis de costos en Santa Cruz (ahorro del 82% con FOSS), matriz de riesgos con mitigación y cronograma de 45 días en 5 etapas. Banco de preguntas imprevistas en [`GUIA_DEFENSA_Y_PREGUNTAS_TFI.md`](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/GUIA_DEFENSA_Y_PREGUNTAS_TFI.md). |

---

## 4. Resumen de Puntuación Proyectada

$$\text{Puntaje Total} = 9\text{ (Criterio 1)} + 9\text{ (Criterio 2)} + 12\text{ (Criterio 3)} = \mathbf{30 / 30 \text{ Puntos (100\% - Nivel Estratégico)}}$$
