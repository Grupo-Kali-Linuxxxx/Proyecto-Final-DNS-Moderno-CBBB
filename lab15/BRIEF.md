# Brief de la Organización — Proyecto Socioformativo (Trabajo Final Integrador)

**Asignatura:** Tecnología Web I (SIS-0150) — Sexto Semestre  
**Docente Titular:** M.Sc. Ing. Jimmy Nataniel Requena Llorentty  
**Institución Académica:** Universidad Privada Domingo Savio (UPDS), Sede Santa Cruz de la Sierra  
**Equipo de Proyecto (Consultores):**
1. Ketfer Gianella Salazar
2. Charles Yourdan Conde
3. Brian Calás
4. Marco Barriga
5. Adaniel Balderrama Orellana

**Fecha:** 26 de Octubre de 2026  
**Criterio Evaluado:** C3 (40% de la materia — 30 Puntos)  

---

## 1. Ficha Técnica de la Organización Real

| Campo | Información Institucional Verificada |
|---|---|
| **Organización y Rubro** | **Colegio Bautista Boliviano Brasileño (CBBB)** — Institución de Educación Regular (Nivel Inicial, Primaria y Secundaria Comunitaria Productiva). |
| **Ubicación Geográfica** | Av. Beni, entre Calle Los Tureres y Calle Bibosi (Tercer Anillo Interno), Santa Cruz de la Sierra, Bolivia (a 5 minutos del campus UPDS). |
| **Contacto Entrevistado (Cargo)** | Lic. Roberto Da Silva (Coordinador del Área de Tecnología Educativa y Sistemas). |
| **Dominio Público Oficial** | **`cbautistabb.edu.bo`** (Registrado ante NIC Bolivia / ADSIB). |
| **Infraestructura Web Actual** | Esquema fragmentado: Dominio raíz en servidor VPS (`148.113.159.58` en proveedor Nemabol / OVH); el subdominio `www.cbautistabb.edu.bo` apunta a Google Sites (`64.233.190.121`). |
| **Sistema de Correo Actual** | Google Workspace for Education (`ASPMX.L.GOOGLE.COM`), utilizado por docentes y dirección. |
| **Dimensión y Carga de Red** | • 52 docentes regulares.<br>• 16 funcionarios administrativos y de apoyo.<br>• ~920 estudiantes matriculados y sus familias/tutores.<br>• 75 equipos de cómputo fijos en laboratorios y oficinas.<br>• Red Wi-Fi con más de 300 dispositivos móviles concurrentes. |
| **Servicios Internos en Uso** | Sistema de control de notas escolar en PHP, servidor de archivos de circulares en PDF, reloj biométrico de asistencia, cámaras de seguridad IP y servicios de impresión en red. |
| **Problemas Críticos Detectados** | 1. Inexistencia total de política DMARC (vulnerabilidad crítica de suplantación/phishing).<br>2. SPF laxo e inconsistente (`~all` sin incluir servidores de Google).<br>3. Dominio público sin firmas DNSSEC (expuesto a envenenamiento de caché).<br>4. Inexistencia de registros CAA para controlar la emisión de certificados SSL.<br>5. Falta de separación de vistas DNS (Split-Horizon), exponiendo servicios internos o saturando enlaces externos.<br>6. Servidor con DNS inverso (PTR) genérico de hosting (`host.nemabol.net`). |
| **Personal Responsable de TI** | El Departamento de Cómputo y Soporte Técnico del Colegio Bautista Boliviano Brasileño, asistido por el Manual de Operación y DRP entregado en este proyecto. |

---

## 2. Diagnóstico Técnico en Vivo del Dominio Actual (`cbautistabb.edu.bo`)

En cumplimiento de las normas éticas del proyecto socioformativo, se ejecutó una radiografía no invasiva utilizando exclusivamente **consultas DNS públicas** sobre el dominio oficial:

```text
================================================================================
RADIOGRAFÍA DNS EN VIVO — DOMINIO: cbautistabb.edu.bo
Fecha y Hora de Auditoría: 2026-10-26 15:16 UTC-4
Resolutores Públicos de Consulta: 1.1.1.1 (Cloudflare) / 8.8.8.8 (Google)
================================================================================

[+] Servidores de Nombres Autoritativos (NS):
    • ns1.nemabol.net (Delegación en NIC Bolivia)
    • ns2.nemabol.net (Delegación en NIC Bolivia)
    -> Estado: Autoritativos delegados en proveedor de hosting compartido.

[+] Registro de Inicio de Autoridad (SOA):
    • Serial: 2026090504
    • Servidor Primario (MNAME): ns1.nemabol.net.
    • Correo Responsable (RNAME): nemabol.hotmail.com.
    -> Observación: El correo de contacto técnico utiliza un buzón gratuito comercial (Hotmail).

[+] Direcciones IP del Sitio Web Institucional:
    • Dominio raíz (cbautistabb.edu.bo A): 148.113.159.58
    • Prefijo www (www.cbautistabb.edu.bo A): 64.233.190.121 (Google Sites)
    • IPv6 (AAAA): Inexistente.

[+] Servidores de Transporte de Correo (MX):
    • Prioridad 1:  ASPMX.L.GOOGLE.COM
    • Prioridad 5:  ALT1.ASPMX.L.GOOGLE.COM
    • Prioridad 5:  ALT2.ASPMX.L.GOOGLE.COM
    • Prioridad 10: ALT3.ASPMX.L.GOOGLE.COM
    • Prioridad 10: ALT4.ASPMX.L.GOOGLE.COM
    -> Estado: Entrega delegada en plataforma Google Workspace.

[+] Evaluación Criptográfica de Registros TXT (SPF, DKIM, DMARC):
    • SPF: "v=spf1 ip4:148.113.159.58 ip4:72.251.3.93 +a +mx +ip4:147.135.64.154 ~all"
      -> DIAGNÓSTICO SPF: INCONSISTENTE Y LAXO.
         - Calificador ~all (SoftFail) permite envíos fraudulentos sin bloqueo inmediato.
         - NO CONTIENE la cláusula obligatoria "include:_spf.google.com", a pesar de que el
           colegio opera su correo en Google. Esto provoca que envíos legítimos de profesores
           puedan ser penalizados por filtros de spam (Gmail/Outlook).
    • DMARC: NO EXISTE (_dmarc.cbautistabb.edu.bo devuelve NXDOMAIN).
      -> DIAGNÓSTICO DMARC: VULNERABILIDAD CRÍTICA.
         - Cualquier atacante en internet puede emitir correos fraudulentos suplantando a
           direccion@cbautistabb.edu.bo o secretaria@cbautistabb.edu.bo para cobrar cuotas falsas
           a padres de familia sin que los servidores receptores sospechen del remitente.

[+] Validación Criptográfica DNSSEC:
    • Registro DS en zona padre (.bo): INEXISTENTE.
    • Registros DNSKEY en zona: INEXISTENTES.
    -> DIAGNÓSTICO: Dominio NO firmado con DNSSEC. Vulnerable a ataques de spoofing/envenenamiento.

[+] Restricción de Autoridades Certificadoras (CAA):
    • Registro CAA: INEXISTENTE.
    -> DIAGNÓSTICO: Cualquier CA pública puede emitir certificados SSL para cbautistabb.edu.bo.

[+] Resolución Inversa de Servidor Web (PTR / FCrDNS):
    • 148.113.159.58 PTR -> host.nemabol.net.
    -> DIAGNÓSTICO: Reverse DNS desalineado respecto al nombre de host del colegio.

[+] Prueba de Transferencia de Zona (AXFR):
    • ns1.nemabol.net: Transferencia rechazada (NOTAUTH / REFUSED). [CORRECTO]
    • ns2.nemabol.net: Transferencia rechazada (NOTAUTH / REFUSED). [CORRECTO]
================================================================================
```

---

## 3. Objetivos Medibles del Proyecto Socioformativo

Para transformar y blindar integralmente la infraestructura tecnológica del Colegio Bautista Boliviano Brasileño, se establecen los siguientes **4 objetivos técnicos cuantitativos**:

1. **Objetivo 1 (DNS Híbrido con Vistas y DNSSEC):**  
   Implementar una arquitectura DNS de alto rendimiento con BIND 9.18 separando matemáticamente la vista interna (`cbbb.internal` y zona inversa `10.10.10.in-addr.arpa`) de la vista externa (`cbbb.example`, proyectada a `cbautistabb.edu.bo`). La zona pública se firmará automáticamente con **DNSSEC (`dnssec-policy`)** alcanzando validación criptográfica estricta con `delv` (`fully validated`), y el servidor secundario (`ns2`) sincronizará zonas mediante claves criptográficas **TSIG** con avisos inmediatos **NOTIFY**.
   - *Meta Medible:* 0% de fuga de nombres internos en consultas externas y 100% de consultas DNSSEC validadas.

2. **Objetivo 2 (Resolutor Endurecido con DoT y RPZ Escolar):**  
   Desplegar un resolutor recursivo local Unbound desacoplado de los autoritativos, canalizando consultas externas mediante **DNS sobre TLS (DoT en puerto TCP 853)** demostrado con `tcpdump`, e integrando una zona de política de respuestas (**RPZ**) con al menos 3 reglas activas para bloquear navegación hacia dominios maliciosos, estafas y contenido peligroso en la red de estudiantes.
   - *Meta Medible:* 100% del tráfico DNS hacia internet cifrado y resolución inmediata `NXDOMAIN` para sitios listados en RPZ.

3. **Objetivo 3 (Seguridad Integral de Correo y Autenticación Criptográfica):**  
   Configurar el servidor de correo institucional Postfix y Dovecot en buzones Maildir con TLS 1.3 forzado, eliminando el puerto 143 en claro (`port = 0`), forzando envío autenticado SASL por el puerto 587 (*Submission*) con control anti-spoofing por tabla PCRE, y publicando la tríada criptográfica DNS completa: **SPF estricto (`v=spf1 mx -all`)**, firma **DKIM RSA de 2048 bits** y política **DMARC en modo cuarentena (`p=quarantine; adkim=s; aspf=s`)**.
   - *Meta Medible:* Verificación `dkim=pass`, `spf=pass` y `dmarc=pass` en correos recibidos, y tasa de rechazo del 100% ante intentos de suplantación interna (código SMTP 553).

4. **Objetivo 4 (Operación Confiable, Respaldo Cifrado y Plan de Adopción Real):**  
   Endurecer el servidor web institucional con Nginx, HTTPS obligatorio (TLS 1.3, HSTS y CSP), SSH blindado exclusivamente por claves Ed25519 con Fail2ban sobre `nftables`, cortafuegos perimetral UFW, análisis de registros con GoAccess y respaldos automatizados deduplicados y cifrados con **Restic** con restauración probada. Entregar al colegio el manual operativo con DRP y un plan de adopción real (costos, riesgos y migración).
   - *Meta Medible:* Superar con 100% de éxito los scripts oficiales de auditoría interna (29/29) y externa (7/7), garantizando una recuperación total ante desastres en menos de 25 minutos.
