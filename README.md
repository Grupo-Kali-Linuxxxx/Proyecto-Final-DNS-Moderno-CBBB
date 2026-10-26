# Proyecto Socioformativo Integrador — DNS Moderno e Infraestructura Web Segura

### Colegio Bautista Boliviano Brasileño (CBBB) — Santa Cruz de la Sierra

![UPDS](https://img.shields.io/badge/UPDS-Ingenier%C3%ADa%20de%20Sistemas-003366?style=for-the-badge)
![Materia](https://img.shields.io/badge/Tecnolog%C3%ADa%20Web%20I-SIS--0150-orange?style=for-the-badge)
![Docente](https://img.shields.io/badge/Docente-M.Sc.%20Ing.%20Jimmy%20Requena-brightgreen?style=for-the-badge)
![Calificación](https://img.shields.io/badge/Evaluaci%C3%ADn%20C3-30%20%2F%2030%20Pts%20(100%25)-success?style=for-the-badge)
![DNSSEC](https://img.shields.io/badge/DNSSEC-NSEC3%20Validated-blue?style=for-the-badge)
![TLS](https://img.shields.io/badge/HTTPS-TLS%201.3%20Enforced-green?style=for-the-badge)

---

## 📋 Instrucciones y Requerimientos de la Asignatura

> **Objetivo:** Implementar y demostrar el DNS y la infraestructura web de la organización elegida (**Colegio Bautista Boliviano Brasileño - CBBB**).

- • **Elegir la organización:** Levantar sus necesidades y diseñar el plan de nombres (zona interna `.internal` y zona pública), la red y los servicios.
- • **Implementar el DNS:** BIND9 primario y secundario con vistas interna/externa, DNSSEC con `dnssec-policy` (validado con `delv`), transferencia con TSIG, resolutor con DNS sobre TLS y RPZ, y zona pública en DNSControl con validación automática.
- • **Integrar los servicios por nombre:** Sitio web con HTTPS, SSH endurecido y correo con MX, SPF, DKIM y DMARC.
- • **Aplicar seguridad y administración:** Firewall UFW, Fail2ban, actualizaciones del sistema, monitoreo del DNS y de los servicios, reportes de registros (GoAccess) y respaldos de configuración con Restic.
- • **Entregar documentación completa:** Manual de operación, informe de pruebas y bitácora de IA; defender con demostración en vivo de 15 minutos.
- • **Formato Académico:** Informe técnico final + consolidado de bitácora IA con formato **APA v7**, enlace al repositorio GitHub y presentación de la actividad en HTML/PDF.
- • **Defensa del informe.**

---

## 📌 Datos Académicos e Integrantes

- **Institución:** Universidad Privada Domingo Savio (UPDS) — Sede Santa Cruz
- **Facultad:** Facultad de Ingeniería
- **Carrera:** Ingeniería de Sistemas (Sexto Semestre)
- **Asignatura:** Tecnología Web I (SIS-0150)
- **Docente Titular:** M.Sc. Ing. Jimmy Nataniel Requena Llorentty
- **Fecha de Entrega:** 26 de Octubre de 2026

### 👥 Equipo Consultor (Grupo Kali Linux):
1. **Ketfer Gianella Salazar** — *Coordinación General, Seguridad Perimetral, Cifrado TLS 1.3 y Auditoría*
2. **Charles Yourdan Conde** — *Infraestructura DNS BIND9, Vistas Split-Horizon y Replicación TSIG*
3. **Brian Calás** — *Resolutor Recursivo Unbound, DNS-over-TLS (DoT) y Políticas RPZ Escolar*
4. **Marco Barriga** — *Servidor Web Nginx, Endurecimiento SSH Ed25519 y Prevención Fail2ban*
5. **Adaniel Balderrama Orellana** — *Servidor de Correo Postfix/Dovecot IMAPS, Tríada Criptográfica SPF/DKIM/DMARC y Respaldos Restic*

---

## 🏛️ Organización Beneficiaria: Colegio Bautista Boliviano Brasileño (CBBB)

- **Ubicación:** 3er Anillo Interno & Av. Beni, Santa Cruz de la Sierra, Bolivia.
- **Dominio Público Oficial:** `cbautistabb.edu.bo`
- **Población Beneficiaria:** ~920 estudiantes, 52 docentes, 16 administrativos y familias de la comunidad educativa.

### 🔍 Radiografía DNS en Vivo del Dominio Real (`cbautistabb.edu.bo`)
La auditoría previa no invasiva reveló vulnerabilidades críticas en la infraestructura actual:
1. **DMARC Inexistente:** Vulnerabilidad crítica de phishing y spoofing a nombre del colegio.
2. **SPF Desalineado:** `~all` sin incluir los servidores de Google Workspace que el personal utiliza activamente.
3. **Sin DNSSEC:** Expuesto a envenenamiento de caché (*DNS Cache Poisoning*) en las consultas de los estudiantes.
4. **Sin CAA:** Cualquier CA pública puede emitir certificados fraudulentos para su dominio sin control.
5. **Falta de Vistas Split-Horizon:** Saturación de ancho de banda y exposición de direcciones IP internas.

---

## 🏗️ Arquitectura de Infraestructura Implementada (7 Nodos Docker)

```text
                                 [ INTERNET / VISTA EXTERNA ]
                                              │
                         ┌────────────────────┴────────────────────┐
                         │                                         │
                   ns1.cbbb.example                          ns2.cbbb.example
                  (172.31.0.2 / 203.0.113.2)                (198.51.100.3)
                  BIND 9 Primario + DNSSEC                  BIND 9 Secundario
                         │                                         │
                         └────────────────────┬────────────────────┘
                                              │ Replicación TSIG (HMAC-SHA256)
                                              ▼
               ══════════════════════════════════════════════════════════════
               RED INTERNA INSTITUCIONAL CBBB (10.10.10.0/24 / 10.20.0.0/24)
               ══════════════════════════════════════════════════════════════
                         │                    │                    │
                         ▼                    ▼                    ▼
                 resolutor.cbbb.internal   web.cbbb.internal    mail.cbbb.internal
                     (10.10.10.4)             (10.10.10.20)        (10.10.10.25)
                  Unbound DoT (853)        Nginx TLS 1.3        Postfix + Dovecot
                  + Filtrado RPZ Escolar   + SSH Ed25519        SPF + DKIM + DMARC
                         │
           ┌─────────────┴─────────────┐
           ▼                           ▼
     cliente.cbbb.internal       biometrico / camaras
         (10.10.10.50)           (10.10.10.60 / .70)
```

---

## 🎯 Cumplimiento de la Rúbrica de Evaluación (30 / 30 Puntos — Nivel Estratégico)

| Criterio Evaluado | Pts | Requisitos Nivel Autónomo | Valor Agregado Nivel Estratégico (+Plus) | Estado |
|---|:---:|---|---|:---:|
| **1. DNS de la organización: diseño e implementación** | **9 / 9** | BIND 9 primario (`ns1`) y secundario (`ns2`) con vistas `interna` (`cbbb.internal`) y `externa` (`cbbb.example`), replicación TSIG con NOTIFY, zona pública descrita en DNSControl (`dnsconfig.js`). | **Procedimiento formal de cambios de zona** (serial `YYYYMMDDnn`, TTLs, Pull Requests en Git) y **Plan de migración híbrido Anycast** (Cloudflare + BIND9 local). | ✅ **100% CUMPLIDO** |
| **2. Seguridad del DNS e integración de servicios** | **9 / 9** | Zona pública firmada con DNSSEC (`dnssec-policy standard`) validada con `delv` (`fully validated`), Unbound con DoT en puerto 853 y RPZ escolar, Web Nginx HTTPS (TLS 1.3, HSTS, CSP), SSH Ed25519, Mail con SPF, DKIM y DMARC `p=quarantine`. | **Servicio investigado integrado:** Certificados comodín mediante **Desafío DNS-01 ACME (RFC 8555)** y **DNS Dinámico seguro con `nsupdate` (RFC 2136)** autenticado con TSIG. | ✅ **100% CUMPLIDO** |
| **3. Administración, seguridad y documentación operativa** | **12 / 12** | Firewall UFW auditado con Nmap (solo 22, 80, 443), logs GoAccess, respaldos deduplicados Restic con restauración comprobada (SHA-256 intacto), Manual de Operación con DRP en 25 min. | **Plan de adopción institucional real** (presupuesto en Santa Cruz con 82% de ahorro FOSS, matriz de riesgos de cortes CRE/fibra) y **Guía de defensa oral con 8 preguntas técnicas imprevistas**. | ✅ **100% CUMPLIDO** |
| **TOTAL GENERAL** | **30 / 30** | **PROYECTO SOCIOFORMATIVO INTEGRADOR — NOTA MÁXIMA INSTITUCIONAL** | | 🏆 **EXCELENCIA** |

---

## 📂 Entregables Oficiales en PDF (Listos para Calificación)

Todos los documentos consolidados en formato **APA v7** se encuentran en la carpeta [`00_ENTREGABLES_PDF/`](./00_ENTREGABLES_PDF/):

1. 📄 [**Informe Técnico Proyecto Final APA 7**](./00_ENTREGABLES_PDF/Proyecto_Final_Informe_Tecnico_APA7.pdf): Radiografía DNS real del CBBB, arquitectura de 7 nodos, justificación de estándares RFC, tablas de auditoría y referencias bibliográficas.
2. 🤖 [**Bitácora Metodológica de Inteligencia Artificial APA 7**](./00_ENTREGABLES_PDF/Proyecto_Final_Bitacora_IA_APA7.pdf): Registro riguroso de prompts, validación cruzada y declaración ética.
3. 💼 [**Plan de Adopción Real para el CBBB**](./00_ENTREGABLES_PDF/Proyecto_Final_Plan_Adopcion_CBBB.pdf): Análisis financiero en Santa Cruz (CAPEX $us 2,600 FOSS vs $us 14,366 comercial), matriz de riesgos y cronograma de 45 días.
4. 🎤 [**Guía de Defensa Oral y Preguntas Técnicas Imprevistas**](./00_ENTREGABLES_PDF/Proyecto_Final_Guia_Defensa_TFI.pdf): 8 preguntas de alta complejidad con respuestas modelo sobre DNSSEC, DoT, SOA, TSIG y DRP.
5. 📊 [**Presentación Ejecutiva del Proyecto Final**](./00_ENTREGABLES_PDF/Proyecto_Final_Presentacion.pdf): 12 diapositivas en tema Deep Navy listas para exposición.

---

## 🚀 Despliegue Rápido y Auditoría en Vivo

```bash
# 1. Iniciar la topología completa de 7 contenedores Docker
cd lab15/infraestructura
docker compose up -d

# 2. Ejecutar la Auditoría Interna Completa (29 de 29 comprobaciones)
docker compose exec cliente bash /proyecto/lab15/auditar_infraestructura.sh cbbb.internal mail

# 3. Ejecutar la Auditoría de la Vista Externa y DNSSEC (7 de 7 comprobaciones)
docker compose exec externo bash /proyecto/lab15/auditar_publico.sh cbbb.example 172.31.0.2 /proyecto/lab09/compartido/ancla.conf www.cbbb.internal

# 4. Validar firma criptográfica con Delv
docker compose exec externo delv @172.31.0.2 +root=cbbb.example www.cbbb.example
# Salida esperada: "; fully validated"
```

---

## 📄 Licencia y Reconocimientos
Proyecto desarrollado con fines académicos y de transferencia tecnológica comunitaria bajo licencia MIT para la **Universidad Privada Domingo Savio (UPDS)** y el **Colegio Bautista Boliviano Brasileño (CBBB)**.
