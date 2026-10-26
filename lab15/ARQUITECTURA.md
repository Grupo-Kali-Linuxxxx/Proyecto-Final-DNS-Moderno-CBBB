# Arquitectura de Infraestructura y Servicios de Red — Proyecto Socioformativo

**Organización Beneficiaria:** Colegio Bautista Boliviano Brasileño (CBBB)  
**Dominio Público Real:** `cbautistabb.edu.bo` | **Dominio de Laboratorio:** `cbbb.example`  
**Dominio Interno Seguro:** `cbbb.internal`  
**Diseño de Arquitectura y Consultoría:** Ketfer Gianella Salazar y Equipo de Proyecto (UPDS)  
**Asignatura:** Tecnología Web I (SIS-0150) — Docente: M.Sc. Ing. Jimmy Nataniel Requena Llorentty  

---

## 1. Plan de Nombres de Dominio (DNS Híbrido)

La arquitectura de nombres adopta el modelo **DNS Híbrido y Desacoplado**, dividiendo las responsabilidades lógicas entre zonas privadas y zonas públicas para blindar la seguridad institucional:

| Zona DNS | Tipo de Zona | Quién la Consulta | Servidores Autoritativos | Función en la Organización |
|---|---|---|---|---|
| **`cbbb.internal`** | Interna (*Split-Horizon*) | Exclusivamente estaciones y servidores dentro del campus escolar (10.10.10.0/24 y 127.0.0.0/8). | `ns1` (Primario BIND 9)<br>`ns2` (Secundario TSIG) | Resolución de servicios privados protegidos: portal académico de notas (`portal.cbbb.internal`), API de avisos (`api.cbbb.internal`), almacenamiento de circulares, bases de datos y buzones locales. |
| **`10.10.10.in-addr.arpa`** | Inversa (*PTR*) | Red interna del colegio y resolutor recursivo. | `ns1` (Primario)<br>`ns2` (Secundario TSIG) | Mapeo unívoco de direcciones IP a nombres FQDN. Permite validación FCrDNS de servidores de correo, filtros antispam y auditoría precisa en los registros de seguridad. |
| **`cbbb.example`** *(proyectada a `cbautistabb.edu.bo`)* | Pública (Firmada con DNSSEC) | Internet, comunidad escolar externa, tutores y público en general (0.0.0.0/0 vía vista externa). | `ns1` (BIND 9 con *inline-signing*)<br>Configuración como código en **DNSControl** | Sitio web informativo público (`www.cbbb.example`), servidores de transporte de correo MX (`mail.cbbb.example`), registros de validación criptográfica SPF (`-all`), claves públicas OpenDKIM de 2048 bits (`mail._domainkey`), políticas DMARC (`p=quarantine`) y registros de control de certificados CAA. |

---

## 2. Plan de Direccionamiento IP y Topología de Red (7 Nodos)

El sistema opera sobre un entorno de contenedores Linux interconectados mediante dos redes virtuales aisladas: `tw1-dns_cbbb` (Red Interna 10.10.10.0/24) y `tw1-externo_cbbb` (Red Pública Simulada 172.30.0.0/24):

| Nodo | IP Interna | IP Externa (Internet) | Rol y Pila Tecnológica en Ejecución |
|---|---|---|---|
| **`ns1`** | `10.10.10.2` | `172.30.0.2` | **Servidor DNS Autoritativo Primario (BIND 9.18):** Motor de vistas (*Split-Horizon*), firmado dinámico DNSSEC (`dnssec-policy`), replicación TSIG con NOTIFY, ocultación de versión y control de acceso ACL. |
| **`ns2`** | `10.10.10.3` | — | **Servidor DNS Autoritativo Secundario (BIND 9.18):** Alta disponibilidad interna, sincronización automática vía AXFR protegida con clave secreta compartida HMAC-SHA256 (`tsig-key`). |
| **`resolutor`** | `10.10.10.4` | — | **Servidor DNS Recursivo/Caché (Unbound 1.19):** Desacoplado de los autoritativos, validación local de DNSSEC, privacidad ascendente mediante **DNS sobre TLS (DoT en puerto 853)** y filtrado de navegación por lista **RPZ** (*Response Policy Zones*). |
| **`servidor-web`** | `10.10.10.20` | — | **Servidor Web y Aplicaciones (Nginx 1.24 + PHP 8.3 FPM):** HTTPS forzado con TLS 1.3, HSTS, CSP, acceso remoto SSH blindado solo con claves Ed25519, SFTP enjaulado (`chroot`), firewall UFW, métricas con GoAccess y respaldos automáticos con Restic. |
| **`mail`** | `10.10.10.25` | — | **Servidor de Correo Institucional (Postfix 3.8 + Dovecot 2.3 + OpenDKIM):** Buzones Maildir, acceso IMAPS seguro (puerto 993, puerto 143 cerrado), envío autenticado SASL por puerto 587 (*Submission*) y control anti-spoofing con tabla PCRE. |
| **`cliente`** | `10.10.10.50` | — | **Estación de Trabajo Interna (Auditoría TI y Operaciones):** Simula las computadoras de los laboratorios del colegio; contiene las herramientas de auditoría (`dig`, `swaks`, `openssl`, `curl`, `delv`). |
| **`externo`** | — | `172.30.0.100` | **Estación Externa de Auditoría Pública:** Simula un usuario en Internet; se utiliza para auditar que los nombres `.internal` no se filtren hacia afuera y que la firma DNSSEC sea validada como auténtica con `delv`. |

---

## 3. Diagrama de Arquitectura y Flujos de Comunicación

```text
                  +-------------------------------------------------------------+
                  |               INTERNET / USUARIO EXTERNO                    |
                  |                Nodo: externo (172.30.0.100)                 |
                  +------------------------------+------------------------------+
                                                 |
                               Peticiones DNS    | Consultas HTTPS hacia
                               a zona pública    | portal del colegio
                                                 v
                  +-------------------------------------------------------------+
                  |          ns1 (Interfaz Externa Pública: 172.30.0.2)         |
                  |      Vista Externa: cbbb.example (DNSSEC Firmado NSEC3)     |
                  +------------------------------+------------------------------+
                                                 |
                                   FIREWALL PERIMETRAL UFW
                          (Solo puertos 22/SSH, 80/HTTP y 443/HTTPS)
                                                 |
      ===========================================+===========================================
                      RED INTERNA COLEGIO CBBB (Subred: 10.10.10.0/24)
      ===========================================+===========================================
           |                      |                      |                      |
           v                      v                      v                      v
    +---------------+      +---------------+      +---------------+      +---------------+
    |      ns1      |      |      ns2      |      |   resolutor   |      |  servidor-web |
    | (10.10.10.2)  |<====>| (10.10.10.3)  |      | (10.10.10.4)  |      | (10.10.10.20) |
    | BIND 9 Prim.  | TSIG | BIND 9 Sec.   |      | Unbound Local |      | Nginx HTTPS   |
    | Vista Interna | NOTIFY Zona Interna  |      | DoT Puerto 853|      | PHP 8.3 FPM   |
    | cbbb.internal |      | cbbb.internal |      | RPZ Antivirus |      | SSH Ed25519   |
    +---------------+      +---------------+      +---------------+      +---------------+
                                                         ^                      |
                                           Consultas DNS | Tráfico de           |
                                           de estaciones | Aplicación           |
                                           y servidores  +----------+-----------+
                                                         |          |
                                   +---------------------+          |
                                   |                                v
                            +---------------+               +---------------+
                            |     mail      |               |    cliente    |
                            | (10.10.10.25) |               | (10.10.10.50) |
                            | Postfix / Dove|               | Auditoría C3  |
                            | IMAPS 993/587 |               | Verificadores |
                            | DKIM / DMARC  |               | Thunderbird   |
                            +---------------+               +---------------+
```

---

## 4. Matriz de Decisiones Técnicas Justificadas (5 Decisiones Clave)

| Decisión Arquitectónica | Alternativas Descartadas | Justificación Técnica de Seguridad, Disponibilidad y Rendimiento |
|---|---|---|
| **1. DNS con Vistas Separadas (Split-Horizon)** | • Publicar un solo archivo de zona que resuelva todo.<br>• Usar dominios públicos distintos sin vista interna. | **Confidencialidad y Eficiencia de Ancho de Banda:** Los equipos del campus escolar resuelven `cbbb.internal` apuntando directamente a IPs privadas locales (10.10.10.x), evitando saturar el enlace de internet escolar. Para internet, la vista externa solo publica registros públicos indispensables (`www`, `mail`, `MX`), devolviendo `REFUSED` o `NXDOMAIN` para cualquier nombre interno, impidiendo que ciberdelincuentes descubran la topología privada del colegio. |
| **2. Resolutor Recursivo Independiente (Unbound) con DoT y RPZ** | • Habilitar recursión directamente en los autoritativos BIND 9.<br>• Usar los DNS públicos en claro de las operadoras (Tigo/Entel). | **Mitigación de Envenenamiento y Protección Estudiantil:** Separar los servidores autoritativos del resolutor recursivo es el estándar de oro de IETF. Unbound realiza validación DNSSEC estricta en memoria, protege la privacidad de la navegación escolar cifrando las consultas externas mediante **DNS sobre TLS (DoT en puerto 853)** contra espionaje en el ISP, y bloquea dominios peligrosos o malware mediante listas **RPZ**. |
| **3. Autoridad Certificadora (CA) Raíz Institucional Propia** | • Pagar certificados comerciales de alto costo para nombres internos.<br>• Usar certificados autofirmados individuales sin CA común. | **Confianza Centralizada y Cero Costo de Licencias:** Las autoridades públicas (Let's Encrypt / DigiCert) no emiten certificados para dominios `.internal`. Construir una Autoridad Certificadora institucional permite emitir certificados X.509 de 2048 bits para HTTPS (`portal.cbbb.internal`), API y correos IMAPS/Submission. La clave raíz de la CA se custodia fuera de línea y su certificado público se instala en los navegadores del colegio, garantizando candado verde sin advertencias. |
| **4. Inyección de Correo por Submission (587) con SASL y Anti-Spoofing** | • Permitir envíos por el puerto estándar 25 autenticado.<br>• Permitir retransmisión de correo basada únicamente en IP (`mynetworks`). | **Trazabilidad y Bloqueo Total de Suplantación Interna:** El puerto 25 se reserva para recibir correos de otros servidores del mundo. El puerto 587 (*Submission*) exige cifrado TLS 1.3 obligatorio antes de la autenticación (`smtpd_tls_auth_only = yes`). La directiva `reject_sender_login_mismatch` con tabla PCRE impide que un alumno o administrativo autenticado con su cuenta envíe un correo haciéndose pasar por el Director (`direccion@cbautistabb.edu.bo`). |
| **5. Respaldos Cifrados en Origen con Restic y Temporizadores Systemd** | • Copias manuales con scripts bash `tar` o `rsync` sin cifrar.<br>• Soluciones complejas con agentes comerciales pesados. | **Inviolabilidad Criptográfica y Recuperación Rápida (DRP):** Restic divide los archivos en bloques deduplicados y los cifra en origen con AES-256-GCM antes de escribir al disco. Incluso si un respaldo es sustraído físicamente, la información de notas y datos familiares es inaccesible sin la clave maestra. Los temporizadores systemd garantizan ejecución desatendida nocturna y verificación matemática de integridad (`restic check`). |

---

## 5. Plus de Nivel Estratégico (Criterios 1 y 2 de la Rúbrica)

1. **Gestión de Zona Pública como Código con DNSControl:**  
   La zona externa del colegio se define formalmente en `dnsconfig.js` mediante la herramienta de infraestructura como código **DNSControl**, permitiendo un ciclo de despliegue auditable:
   - `dnscontrol check`: Validación sintáctica del código.
   - `dnscontrol preview`: Inspección diferencial de registros a modificar.
   - `dnscontrol push`: Publicación automatizada sin intervención manual.

2. **Procedimiento Formal de Cambios y Plan de Migración DNS:**  
   Documentado en [`PROCEDIMIENTO_CAMBIOS_DNS.md`](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/PROCEDIMIENTO_CAMBIOS_DNS.md), estableciendo la regla estricta de incremento de serial SOA (`YYYYMMDDnn`), tiempos de vida TTL escalonados y migración hacia un modelo híbrido Anycast (Cloudflare + BIND9 local).

3. **Servicio Investigado Integrado al Dominio:**  
   Documentado en [`SERVICIO_INVESTIGADO_DNS01_NSUPDATE.md`](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/SERVICIO_INVESTIGADO_DNS01_NSUPDATE.md), detallando la automatización de certificados SSL/TLS mediante el desafío **DNS-01 (RFC 8555 / ACME)** y la actualización dinámica de registros con **`nsupdate` (RFC 2136)** autenticado por firma TSIG.
