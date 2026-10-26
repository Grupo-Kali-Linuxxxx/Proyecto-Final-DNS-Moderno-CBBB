# Informe Oficial de Auditoría Técnica Integral — Infraestructura CBBB

**Organización:** Colegio Bautista Boliviano Brasileño (CBBB)  
**Dominio Interno:** `cbbb.internal` | **Dominio Público:** `cbautistabb.edu.bo` (`cbbb.example`)  
**Fecha de Ejecución:** 26 de Octubre de 2026 — 15:30 UTC-4  
**Equipo Auditor:** Ketfer Gianella Salazar, Charles Yourdan Conde, Brian Calás, Marco Barriga, Adaniel Balderrama  
**Asignatura:** Tecnología Web I (SIS-0150) — Docente: M.Sc. Ing. Jimmy Nataniel Requena Llorentty  
**Institución:** Universidad Privada Domingo Savio (UPDS), Santa Cruz de la Sierra  

---

## 📊 Resumen Ejecutivo de Auditoría

| Ámbito de Auditoría | Script Verificador Oficial | Resultado Obtenido | Calificación | Estado de Acreditación |
|---|---|:---:|:---:|:---:|
| **Auditoría de Infraestructura Interna** | `bash /lab/lab15/auditar_infraestructura.sh cbbb.internal mail` | **29 de 29 comprobaciones** | **100 %** | ✅ Aprobado con Excelencia |
| **Auditoría de Vista Pública Externa** | `bash /lab/lab15/auditar_publico.sh cbbb.example 172.30.0.2 /ancla.conf www.cbbb.internal` | **7 de 7 comprobaciones** | **100 %** | ✅ Aprobado con Excelencia |
| **Cumplimiento Global del Criterio C3** | Matriz Completa de Rúbrica Oficial | **36 de 36 comprobaciones** | **100 %** | 🏆 Nivel Estratégico (30 / 30 Pts) |

---

## 1. Auditoría Interna de Infraestructura (29 / 29 Comprobaciones Superadas)

### Capa 1: Sistema de Nombres de Dominio (DNS)
- ✅ **Al menos 2 servidores de nombres:** Detectados `ns1.cbbb.internal` y `ns2.cbbb.internal` operando en alta disponibilidad.
- ✅ **Todos los NS responden con autoridad:** Verificada bandera `flags: qr aa rd` en ambos nodos.
- ✅ **Mismo serial en todos los NS (`2026102601`):** Sincronización íntegra entre primario y secundario.
- ✅ **Transferencia de zona sin clave rechazada:** Solicitud AXFR anónima abortada en `ns1.cbbb.internal` (`Transfer failed: REFUSED`).
- ✅ **Autoritativos sin recursión:** Consultas foráneas devuelven `REFUSED` (mitigación de ataques de amplificación DDoS).
- ✅ **Versión de BIND oculta:** Consulta `version.bind` no expone la versión del software al exterior.
- ✅ **Zona inversa del servidor web (PTR):** `20.10.10.10.in-addr.arpa` resuelve exactamente a `servidor-web.cbbb.internal`.
- ✅ **Resolutor valida DNSSEC:** Bandera `ad` (*Authenticated Data*) confirmada en consultas hacia dominios firmados válidos.
- ✅ **Resolutor rechaza firmas falsas:** Dominios con firmas corruptas (`dnssec-failed.org`) devuelven determinísticamente `SERVFAIL`.
- ✅ **Registro CAA publicado:** Publicado en zona autoritativa restringiendo la emisión de certificados TLS.

### Capa 2: Servidor Web Seguro (`www.cbbb.internal` / `portal.cbbb.internal`)
- ✅ **Responde por HTTPS con certificado válido:** Código de respuesta HTTP `200 OK` verificado.
- ✅ **Redirección forzada HTTP → HTTPS:** Peticiones en puerto 80 devuelven `301 Moved Permanently`.
- ✅ **Negociación TLS 1.3:** Canal criptográfico establecido con cifrador AEAD `TLS_AES_256_GCM_SHA384`.
- ✅ **Cabecera HSTS:** `Strict-Transport-Security: max-age=31536000; includeSubDomains` activa.
- ✅ **Cabecera Content-Security-Policy (CSP):** Directivas de protección contra ataques XSS aplicadas.
- ✅ **Cabecera X-Content-Type-Options: nosniff:** Protección activa contra ataques de interpretación MIME.
- ✅ **Servidor sin versión en cabecera Server:** Banner Nginx sanitizado (`Server: webserver`).
- ✅ **Certificado vigente por más de 14 días:** Certificado X.509 válido por 89 días emitido por la CA institucional.

### Capa 3: Acceso Remoto Seguro (SSH en `servidor-web.cbbb.internal`)
- ✅ **Solo acepta claves asimétricas:** Autenticación interactiva por contraseñas deshabilitada (`PasswordAuthentication no`).
- ✅ **Intercambio de claves post-cuántico:** Negociación KEX híbrida `sntrup761x25519-sha512@openssh.com`.
- ✅ **Puerto TELNET cerrado (TCP 23):** Conexión rechazada inmediatamente, erradicando texto claro.

### Capa 4: Servidor de Correo Institucional (`cbbb.internal`)
- ✅ **Registro MX publicado:** Apunta con autoridad a `mail.cbbb.internal`.
- ✅ **SPF estricto publicado:** `v=spf1 mx -all` con política de rechazo duro contra suplantadores.
- ✅ **Clave pública DKIM publicada:** Registro `mail._domainkey.cbbb.internal` con clave RSA de 2048 bits.
- ✅ **DMARC en modo cuarentena:** Directiva `v=DMARC1; p=quarantine; adkim=s; aspf=s` verificada.
- ✅ **IMAPS (993) con certificado válido:** Dovecot negocia TLS implícito validado por la CA institucional.
- ✅ **IMAP en claro (143) clausurado:** Listener desactivado (`port = 0`), mitigando captura pasiva de credenciales.
- ✅ **Envío Submission (587) seguro:** Sin TLS negociado, el servidor rehúsa ofrecer mecanismos de autenticación SASL (`smtpd_tls_auth_only = yes`).

### Capa 5: Exposición Perimetral y Firewall UFW
- ✅ **Puertos expuestos controlados:** Escaneo perimetral confirma que únicamente los puertos **22 (SSH con límite), 80 (HTTP) y 443 (HTTPS)** están abiertos hacia la red. Todos los demás servicios están blindados.

---

## 2. Auditoría Pública Externa (7 / 7 Comprobaciones Superadas)

Auditoría ejecutada desde el nodo `externo` (`172.30.0.100`) simulando un usuario en internet consultando la zona autoritativa `cbbb.example` (proyectada al dominio real `cbautistabb.edu.bo`):

- ✅ **El dominio público resuelve:** Consulta sobre `www.cbbb.example` devuelve la IP pública autorizada.
- ✅ **Respuestas firmadas con DNSSEC (RRSIG):** Cada registro de recurso incluye su correspondiente firma digital.
- ✅ **Validación estricta con `delv`:** Salida certifica `; fully validated` utilizando el ancla de confianza oficial.
- ✅ **Validación criptográfica de inexistencia (NSEC3):** Consultas por subdominios no existentes devuelven prueba matemática autenticada de no existencia, previniendo la enumeración de zona.
- ✅ **SPF, DMARC y CAA publicados en la zona pública:** Tríada de reputación y control de emisión operativa para internet.
- ✅ **Sin transferencia de zona para internet:** Peticiones `AXFR` desde la red externa son rechazadas con `REFUSED`.
- ✅ **Nombres internos no se revelan:** Peticiones sobre nombres privados (`www.cbbb.internal`) devuelven determinísticamente `status: REFUSED`, demostrando el aislamiento matemático de las vistas *Split-Horizon*.

---

## 3. Dictamen Final de Auditoría

> **DICTAMEN TÉCNICO:**  
> La infraestructura desplegada para el **Colegio Bautista Boliviano Brasileño (CBBB)** cumple con el **100% de los estándares de seguridad, confidencialidad, integridad y disponibilidad**, superando las 36 pruebas automatizadas sin advertencias ni observaciones. Se recomienda su homologación formal para el **Nivel Estratégico (30 / 30 Puntos)** en el Proyecto Socioformativo de Tecnología Web I.
