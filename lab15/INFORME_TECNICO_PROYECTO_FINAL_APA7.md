# Informe Técnico Final: DNS Moderno e Infraestructura Web Segura para el Colegio Bautista Boliviano Brasileño (CBBB)

**Proyecto Socioformativo — Trabajo Final Integrador (Criterio C3 — 30 Puntos)**  
**Asignatura:** Tecnología Web I (SIS-0150) — Sexto Semestre  
**Docente Titular:** M.Sc. Ing. Jimmy Nataniel Requena Llorentty  
**Institución Académica:** Universidad Privada Domingo Savio (UPDS), Sede Santa Cruz de la Sierra  
**Equipo de Consultoría e Ingeniería:**
1. **Ketfer Gianella Salazar**
2. **Charles Yourdan Conde**
3. **Brian Calás**
4. **Marco Barriga**
5. **Adaniel Balderrama Orellana**

**Fecha de Publicación:** 26 de Octubre de 2026  
**Repositorio Oficial del Proyecto (GitHub):**  
[https://github.com/Grupo-Kali-Linuxxxx/Proyecto-Final-DNS-Moderno-CBBB](https://github.com/Grupo-Kali-Linuxxxx/Proyecto-Final-DNS-Moderno-CBBB)  

---

## Resumen Ejecutivo

El presente informe técnico documenta el diseño, aprovisionamiento, endurecimiento y auditoría empírica de una infraestructura de red moderna y desacoplada para el **Colegio Bautista Boliviano Brasileño (CBBB)**, una institución educativa de referencia en Santa Cruz de la Sierra ubicada sobre el Tercer Anillo Interno y Av. Beni. Con el **Sistema de Nombres de Dominio (DNS)** como columna vertebral de seguridad y encaminamiento, se integraron los tres criterios cardinales del programa académico: Servidores Web Seguros (C1), Acceso Remoto Endurecido y Correo Institucional Criptográfico (C2), y DNS Híbrido con Seguridad Criptográfica (C3).

A partir de un diagnóstico inicial no invasivo ejecutado sobre el dominio público real del colegio (**`cbautistabb.edu.bo`**), se identificaron fallas de seguridad críticas: ausencia absoluta de registros DMARC, política SPF laxa e inconsistente que penaliza correos legítimos, falta de firmas criptográficas DNSSEC y resolución inversa desalineada. Para resolver de raíz estas deficiencias, se diseñó e implementó una arquitectura de 7 nodos en contenedores Linux: un cluster DNS con BIND 9.18 estructurado en **vistas divididas (*Split-Horizon*)** que aísla los servicios privados (`cbbb.internal`) del internet público (`cbbb.example` / `cbautistabb.edu.bo`), replicación secundaria protegida con claves **TSIG**, firmado automático **DNSSEC (`dnssec-policy`)** validado estrictamente con `delv` (`fully validated`), y un resolutor recursivo local **Unbound** que cifra sus consultas externas mediante **DNS sobre TLS (DoT en puerto 853)** e incorpora filtrado de reputación **RPZ** para salvaguardar la navegación de los estudiantes.

Sobre esta base, se acoplaron los servicios institucionales: portal web Nginx con **HTTPS obligatorio (TLS 1.3, HSTS y CSP)**, acceso administrativo OpenSSH 9.6 blindado con **claves asimétricas Ed25519**, jaula SFTP (`chroot`) y **Fail2ban sobre `nftables`**, y servidor de correo Postfix/Dovecot con **buzones Maildir, IMAPS 993, Submission 587 autenticado con SASL y control anti-suplantación PCRE**. Para alcanzar el **Nivel Estratégico (30/30 puntos)**, se incorporó un procedimiento formal de cambios de zona con control en Git, el diseño de migración a un modelo híbrido Anycast, la integración del servicio investigado de **certificados comodín por desafío DNS-01 (RFC 8555) y DNS dinámico con `nsupdate` (RFC 2136)**, y un **Plan de Adopción Real** con análisis de costos en el mercado cruceño (82% de ahorro frente a licencias comerciales), matriz de riesgos y cronograma de 45 días. Las auditorías automatizadas certificaron el **100% de cumplimiento: 29 de 29 comprobaciones en la red interna y 7 de 7 en la vista pública externa**.

---

## 1. Contexto de la Organización y Diagnóstico del Dominio Real

### 1.1 Ficha Institucional del Colegio Bautista Boliviano Brasileño (CBBB)
El Colegio Bautista Boliviano Brasileño es una institución educativa de formación regular fundada en Santa Cruz de la Sierra, que atiende a más de 920 estudiantes en los niveles Inicial, Primaria y Secundaria, contando con una planta de 52 docentes y 16 funcionarios administrativos. Su campus principal se sitúa en la Av. Beni, entre Calle Los Tureres y Bibosi, en las inmediaciones del Tercer Anillo Interno, próximo al campus central de la UPDS.

### 1.2 Radiografía DNS del Dominio Oficial (`cbautistabb.edu.bo`)
En estricto cumplimiento de las normas éticas (utilizando únicamente consultas DNS públicas sobre servidores de internet), se ejecutó una radiografía técnica sobre el dominio institucional. Los hallazgos confirmaron un estado de vulnerabilidad severo:

| Parámetro Evaluado | Estado Detectado en Producción | Impacto y Vulnerabilidad Identificada |
|---|---|---|
| **Servidores de Nombres (NS)** | `ns1.nemabol.net`<br>`ns2.nemabol.net` | Autoritativos delegados en un proveedor de hosting compartido de bajo costo, sin redundancia geográfica ni mitigación contra ataques de denegación de servicio (DDoS). |
| **Sitio Web Institucional** | `cbautistabb.edu.bo` $\to$ `148.113.159.58`<br>`www` $\to$ `64.233.190.121` (Google Sites) | Fragmentación de servicios: el dominio raíz apunta a una IP de hosting básica, mientras que el portal de comunicación redirige a una plantilla genérica de Google Sites. |
| **DNS Inverso (PTR / FCrDNS)** | `58.159.113.148.in-addr.arpa` $\to$ `host.nemabol.net` | **Desalineación Crítica:** La IP no resuelve al nombre del colegio (*Forward-Confirmed Reverse DNS* roto), lo que provoca penalizaciones inmediatas de reputación en filtros antispam. |
| **Servidores de Correo (MX)** | Google Workspace (`ASPMX.L.GOOGLE.COM`) | Recepción delegada en servidores de Google. |
| **Registro SPF** | `v=spf1 ip4:148.113.159.58 ... ~all` | **Inconsistencia Crítica:** Termina en `~all` (SoftFail) y **NO incluye** la directiva `include:_spf.google.com`, lo que genera que los correos que los docentes envían desde sus cuentas institucionales de Gmail sean catalogados como Spam en destinos como Hotmail o Yahoo. |
| **Registro DMARC** | **Inexistente** (`_dmarc.cbautistabb.edu.bo` NXDOMAIN) | **Riesgo Crítico de Phishing:** Cualquier ciberdelincuente puede falsificar correos fingiendo ser `direccion@cbautistabb.edu.bo` para emitir circulares falsas o solicitudes de pago a tutores de familia sin que los filtros detecten el fraude. |
| **Firmas DNSSEC** | **Sin firmar** (Sin registro DS en NIC Bolivia) | **Vulnerabilidad a Spoofing:** Las respuestas DNS pueden ser interceptadas o envenenadas en la red de los proveedores locales (*DNS Cache Poisoning*). |
| **Registros CAA** | **Inexistente** | Cualquier CA del mundo puede emitir certificados SSL para el colegio. |

---

## 2. Objetivos Cuantitativos y Medibles del Proyecto

1. **Objetivo 1 (Aislamiento de Zonas y DNSSEC):** Implementar BIND 9 con vistas *Split-Horizon*, garantizando 0% de fuga de nombres internos (`cbbb.internal`) hacia el exterior y 100% de validación criptográfica DNSSEC en la zona pública (`cbbb.example`).
2. **Objetivo 2 (Resolución Segura y Filtrado Escolar):** Desplegar Unbound con DoT (puerto 853) para cifrar el 100% de las consultas externas, e integrar una lista RPZ escolar que bloquee de forma inmediata (`NXDOMAIN`) sitios de malware y apuestas en las aulas de cómputo.
3. **Objetivo 3 (Autenticación Criptográfica de Correo):** Configurar Postfix y Dovecot eliminando el puerto en claro 143, forzando Submission 587 con TLS y SASL, e implementando la tríada SPF `-all`, DKIM RSA 2048 y DMARC `quarantine`, certificando `dkim=pass` en destino y 100% de bloqueo a la suplantación de remitente (anti-spoofing).
4. **Objetivo 4 (Operación Confiable y DRP):** Proteger el servidor web con HTTPS TLS 1.3 (HSTS y CSP), SSH endurecido solo con claves Ed25519, Fail2ban, UFW y respaldos deduplicados con Restic, alcanzando una tasa de éxito $\ge 90\%$ interna y 100% externa en las auditorías, con un tiempo de recuperación ante desastres menor a 25 minutos.

---

## 3. Arquitectura del Sistema y Topología de Red

La infraestructura opera en dos redes desacopladas de contenedores: la red interna del campus (`tw1-dns_cbbb` en subred `10.10.10.0/24`) y la red pública externa (`tw1-externo_cbbb` en subred `172.30.0.0/24`):

```
                  +-------------------------------------------------------------+
                  |               INTERNET / USUARIO EXTERNO                    |
                  |                Nodo: externo (172.30.0.100)                 |
                  +------------------------------+------------------------------+
                                                 |
                               Peticiones DNS    | Peticiones Web HTTPS
                               a zona pública    | hacia portal del colegio
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

### 3.1 Plan de Direccionamiento de los 7 Nodos
- **`ns1` (10.10.10.2 / 172.30.0.2):** DNS autoritativo primario BIND 9.18 con vistas divididas, DNSSEC y TSIG.
- **`ns2` (10.10.10.3):** DNS autoritativo secundario BIND 9.18 con sincronización AXFR autenticada.
- **`resolutor` (10.10.10.4):** Servidor recursivo Unbound con DoT (853) y filtrado de reputación RPZ.
- **`servidor-web` (10.10.10.20):** Nginx HTTPS, PHP-FPM, SSH solo claves, Fail2ban, UFW y respaldos Restic.
- **`mail` (10.10.10.25):** MTA Postfix + Dovecot IMAPS 993, Submission 587 autenticado SASL y OpenDKIM.
- **`cliente` (10.10.10.50):** Estación de gestión y auditoría interna de TI del colegio.
- **`externo` (172.30.0.100):** Estación de auditoría pública externa para verificación DNSSEC con `delv`.

---

## 4. Matriz de Decisiones Técnicas Justificadas

1. **DNS con Vistas Separadas (*Split-Horizon*):** Permite que los estudiantes y docentes en el campus resuelvan nombres institucionales apuntando directamente a IPs privadas locales (10.10.10.x), optimizando el ancho de banda y garantizando que los servidores y bases de datos internas sean invisibles (`REFUSED`) para atacantes en internet.
2. **Resolutor Recursivo Desacoplado (Unbound) con DoT y RPZ:** Separar la autoridad de la recursión previene ataques de envenenamiento de caché y amplificación DDoS. Unbound valida firmas DNSSEC en memoria, protege la privacidad escolar cifrando las peticiones hacia internet con DoT (853) y bloquea páginas de apuestas y malware mediante RPZ.
3. **Autoridad Certificadora (CA) Institucional Propia:** Los certificados para nombres `.internal` no pueden emitirse por CAs públicas como Let's Encrypt. La CA propia emite certificados X.509 de 2048 bits para la web y el correo sin costo de licencias, distribuyendo la clave pública en los navegadores del colegio.
4. **Envío de Correo por Submission (587) con SASL y Anti-Spoofing PCRE:** El puerto 25 se reserva para la recepción inter-servidor. El puerto 587 exige TLS y autenticación de usuario. La directiva `reject_sender_login_mismatch` cruza las credenciales del usuario con el remitente del mensaje, bloqueando el fraude interno (error SMTP 553).
5. **Respaldos Cifrados en Origen con Restic y Temporizadores:** Restic aplica deduplicación por bloques y cifra la información en origen con AES-256-GCM antes de escribir al disco. Incluso si un respaldo es sustraído físicamente, la información de notas y datos familiares es inaccesible sin la clave maestra.

---

## 5. Plus de Nivel Estratégico (Criterios 1, 2 y 3 de la Rúbrica)

### 5.1 Criterio 1 Plus: Procedimiento de Cambios y Plan de Migración Anycast
- **Procedimiento de Cambios:** Documentado y probado en [`PROCEDIMIENTO_CAMBIOS_DNS.md`](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/PROCEDIMIENTO_CAMBIOS_DNS.md). Establece el formato estricto de serial SOA (`YYYYMMDDnn`), gestión de TTL escalonado (300 segundos previo a migraciones y 86400 segundos en operación estable), validación sintáctica con `named-checkzone` y control de versiones en Git con Pull Requests.
- **Plan de Migración a DNS Híbrido:** Diseño para integrar el BIND 9 primario del colegio como *Hidden Master*, transfiriendo zonas protegidas con claves TSIG hacia una red Anycast mundial (Cloudflare/Route53), garantizando 99.999% de disponibilidad y mitigación DDoS terabit.

### 5.2 Criterio 2 Plus: Servicio Investigado Integrado al Dominio
Documentado en [`SERVICIO_INVESTIGADO_DNS01_NSUPDATE.md`](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/SERVICIO_INVESTIGADO_DNS01_NSUPDATE.md):
- **Certificados por Desafío DNS-01 (RFC 8555 / ACME):** Permite emitir certificados válidos y certificados comodín (*Wildcard* `*.cbautistabb.edu.bo`) sin necesidad de abrir el puerto HTTP 80 hacia internet.
- **DNS Dinámico Seguro con `nsupdate` (RFC 2136):** Configuración en BIND 9 con directiva `update-policy` y firmas criptográficas TSIG (`ddns-cbbb-key`), permitiendo inyectar y retirar registros en caliente de forma automatizada.

### 5.3 Criterio 3 Plus: Plan de Adopción Real para el CBBB
Documentado en [`PLAN_ADOPCION_CBBB.md`](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/PLAN_ADOPCION_CBBB.md):
- **Análisis de Costos Reales:** La solución de código abierto representa un ahorro de **$us 11,766.00 (82% de ahorro en el Año 1)** frente a soluciones comerciales propietarias (Windows Server, CALs y appliances Infoblox), requiriendo únicamente un presupuesto operativo de $us 223/mes para fibra simétrica y soporte.
- **Matriz de Riesgos y Mitigación:** Respaldos 3-2-1 con Restic, UPS Online de 1500VA contra cortes de energía en el 3er anillo y enlace secundario de fibra.
- **Cronograma de Migración en 5 Etapas (45 Días):** Desde la preparación del servidor físico hasta la capacitación docente presencial y el corte definitivo.

---

## 6. Evidencias Gráficas de Auditoría y Verificación Oficial

Las pruebas de auditoría ejecutadas con los verificadores institucionales arrojaron resultados del 100% de cumplimiento:

### Figura 1: Auditoría Interna de Infraestructura (29 de 29 Comprobaciones Superadas)
![Auditoría Interna 29 de 29](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/screenshots/02_auditoria_infraestructura_29_de_29.png)  
*Ejecución oficial de `bash /lab/lab15/auditar_infraestructura.sh cbbb.internal mail` certificando la aprobación del 100% de las pruebas en DNS, Web HTTPS, SSH y Correo Criptográfico.*

---

### Figura 2: Auditoría de la Vista Pública Externa con Validación DNSSEC (7 de 7)
![Auditoría Externa 7 de 7](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/screenshots/03_auditoria_publica_externa_7_de_7.png)  
*Ejecución de `auditar_publico.sh` desde el nodo `externo`: confirmación de resolución pública, firmas RRSIG, validación DNSSEC estricta con delv, protección de inexistencia con NSEC3 y ocultación absoluta de nombres internos.*

---

### Figura 3: Validación Criptográfica Estricta de DNSSEC con `delv`
![Validación delv](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/screenshots/05_verificacion_dnssec_delv_fully_validated.png)  
*Demostración de resolución segura mediante la utilidad oficial `delv`: estado `; fully validated` con el ancla de confianza institucional, confirmando la autenticidad e integridad de la zona pública.*

---

### Figura 4: Monitoreo Continuo de Zonas DNS sin Alertas
![Monitoreo DNS](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/screenshots/04_monitoreo_vigilar_dns_sin_alertas.png)  
*Monitoreo con `vigilar_dns.sh`: sincronización de seriales entre primario y secundario en 0 ms, firmas válidas por más de 13 días y registro de consultas separadas por vista.*

---

## 7. Conclusiones y Recomendaciones Técnicas

1. **Cumplimiento Integral del Criterio C3:** La arquitectura implementada demuestra cómo la articulación de estándares abiertos (RFC 1035, RFC 2136, RFC 4033, RFC 8314, RFC 8555) permite al Colegio Bautista Boliviano Brasileño contar con una infraestructura de primer nivel que garantiza confidencialidad, alta disponibilidad y protección contra ataques cibernéticos modernos.
2. **Impacto Directo en la Seguridad Institucional:** La implementación de la tríada criptográfica DNS (SPF `-all`, DKIM 2048 y DMARC `quarantine`) erradica por completo la vulnerabilidad de suplantación de identidad detectada en el diagnóstico del dominio real `cbautistabb.edu.bo`.
3. **Sostenibilidad y Soberanía Tecnológica:** Al basar la solución en software libre de grado empresarial y documentación técnica reproducible mediante scripts idempotentes, el colegio reduce sus costos de licencias a cero dólares, conservando el control absoluto de sus datos, notas y comunicaciones.

---

## 8. Referencias Bibliográficas (Normas APA v7)

- Albitz, P., & Liu, C. (2001). *DNS and BIND* (4th ed.). O'Reilly Media.
- Arends, R., Austein, R., Larson, M., Massey, D., & Rose, S. (2005). *Protocol Modifications for the DNS Security Extensions* (RFC 4035). Internet Engineering Task Force. https://doi.org/10.17487/RFC4035
- Barnes, R., Iyengar, S., Sullivan, N., & Kario, E. (2019). *Automatic Certificate Management Environment (ACME)* (RFC 8555). Internet Engineering Task Force. https://doi.org/10.17487/RFC8555
- Crocker, D. (2011). *DomainKeys Identified Mail (DKIM) Signatures* (RFC 6376). Internet Engineering Task Force. https://doi.org/10.17487/RFC6376
- Kitterman, S. (2014). *Sender Policy Framework (SPF) for Authorizing Use of Domains in Email* (RFC 7208). Internet Engineering Task Force. https://doi.org/10.17487/RFC7208
- Kucherawy, M., & Zwicky, E. (2015). *Domain-based Message Authentication, Reporting, and Conformance (DMARC)* (RFC 7489). Internet Engineering Task Force. https://doi.org/10.17487/RFC7489
- Mockapetris, P. (1987). *Domain Names - Concepts and Facilities* (RFC 1034). Internet Engineering Task Force. https://doi.org/10.17487/RFC1034
- Rescorla, E. (2018). *The Transport Layer Security (TLS) Protocol Version 1.3* (RFC 8446). Internet Engineering Task Force. https://doi.org/10.17487/RFC8446
- Vixie, P., Thomson, S., Rekhter, Y., & Bound, J. (1997). *Dynamic Updates in the Domain Name System (DNS UPDATE)* (RFC 2136). Internet Engineering Task Force. https://doi.org/10.17487/RFC2136
