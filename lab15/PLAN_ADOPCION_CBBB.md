# Plan de Adopción Real: Costos, Matriz de Riesgos y Cronograma de Migración

**Organización Beneficiaria:** Colegio Bautista Boliviano Brasileño (CBBB)  
**Proyecto:** Trabajo Final Integrador — Criterio C3 (Nivel Estratégico — 12 Puntos)  
**Consultoría y Diseño:** Ketfer Gianella Salazar y Equipo de Ingeniería (UPDS)  
**Asignatura:** Tecnología Web I — Docente: M.Sc. Ing. Jimmy Nataniel Requena Llorentty  
**Fecha:** Octubre de 2026 — Santa Cruz de la Sierra, Bolivia  

---

## 1. Análisis Financiero y Estructura de Costos Reales (Mercado Local Santa Cruz)

Para que la adopción de la infraestructura sea viable y sostenible para el Directorio del Colegio Bautista Boliviano Brasileño, se proyectó una comparativa económica entre la **solución propuesta de código abierto (FOSS)** frente a **soluciones comerciales propietarias (Microsoft / Cisco / Google Enterprise)**:

### 1.1 Presupuesto de Inversión Inicial (CAPEX) — Año 1

| Componente | Detalle Técnico | Costo Solución Propuesta (FOSS) | Costo Solución Comercial Propietaria | Ahorro Institucional |
|---|---|---|---|---|
| **Servidor Físico Principal** | Servidor Rack 1U Dell PowerEdge R250 (Intel Xeon E-2336, 32GB RAM ECC, 2x 1TB SSD NVMe RAID 1). | **$us 1,850.00** | **$us 1,850.00** | $us 0.00 |
| **Licencias de Sistema Operativo** | Ubuntu Server 24.04 LTS (Kernel Linux Enterprise sin costo por licencia). | **$us 0.00** (Software Libre) | $us 1,020.00 (Windows Server 2022 Std) | $us 1,020.00 |
| **Licencias de Acceso Cliente (CALs)** | Acceso para 68 usuarios docentes y administrativos. | **$us 0.00** (Sin límites CAL) | $us 3,400.00 (68 User CALs a $50 c/u) | $us 3,400.00 |
| **Servidor DNS y Vistas** | BIND 9.18 + Unbound DoT + RPZ. | **$us 0.00** (FOSS) | $us 1,500.00 (Appliance Infoblox base) | $us 1,500.00 |
| **Plataforma de Correo y Antivirus** | Postfix + Dovecot IMAPS + OpenDKIM + Rspamd + ClamAV. | **$us 0.00** (FOSS) | $us 4,896.00 (Google Workspace Plus a $6/mes x 68 usuarios/año) | $us 4,896.00 |
| **Dominio Institucional `.edu.bo`** | Registro oficial ante ADSIB / NIC Bolivia (140 Bs/año). | **$us 20.00** | **$us 20.00** | $us 0.00 |
| **Sistema de Respaldo Cifrado** | Restic + Almacenamiento en disco secundario NAS 2TB. | **$us 250.00** (Hardware NAS) | $us 1,200.00 (Veeam Backup License) | $us 950.00 |
| **UPS y Protección Eléctrica** | UPS Online Doble Conversión 1500VA APC Smart-UPS con tarjeta de red. | **$us 480.00** | **$us 480.00** | $us 0.00 |
| **TOTAL CAPEX AÑO 1** | | **$us 2,600.00** | **$us 14,366.00** | **$us 11,766.00 (82% de ahorro)** |

---

### 1.2 Costos Operativos Recurrentes (OPEX) — Mensual y Anual

| Rubro Operativo | Proveedor Local (Santa Cruz) | Costo Mensual ($us) | Costo Anual ($us) |
|---|---|---|---|
| **Enlace de Fibra Óptica Simétrica** | Enlace corporativo simétrico 50 Mbps con 1 IP pública fija (Tigo Business / Entel Empresas). | $us 120.00 | $us 1,440.00 |
| **Mantenimiento y Auditoría Preventiva** | Contrato de soporte técnico preventivo externo (actualizaciones de seguridad, rotación de claves TSIG y revisión de logs GoAccess). | $us 100.00 | $us 1,200.00 |
| **Renovación Anual Dominio `.edu.bo`** | Agencia para el Desarrollo de la Sociedad de la Información en Bolivia (ADSIB). | -- | $us 20.00 |
| **Almacenamiento Off-site en Nube (Respaldos)** | Almacenamiento de respaldo secundario cifrado con Restic en Wasabi / Backblaze B2 (500 GB). | $us 3.00 | $us 36.00 |
| **TOTAL OPEX ESTIMADO** | | **$us 223.00 / mes** | **$us 2,696.00 / año** |

---

## 2. Matriz de Identificación, Evaluación y Mitigación de Riesgos

Se evaluaron los 5 riesgos de mayor impacto para la continuidad de la infraestructura del colegio:

| # | Riesgo Identificado | Probabilidad | Impacto | Nivel | Plan de Mitigación y Contingencia Técnica |
|---|---|---|---|---|---|
| **R1** | **Cortes de Energía Eléctrica Frecuentes** en el 3er Anillo de Santa Cruz (CRE). | Alta | Crítico | **Alto** | Instalación de **UPS Online de doble conversión** de 1500VA con autonomía de 45 minutos y apagado seguro desatendido mediante daemon `nut` (*Network UPS Tools*). Sincronización con el generador a diésel del campus. |
| **R2** | **Corte del Enlace Principal de Fibra Óptica** por rotura de cables o mantenimiento del ISP. | Media | Alto | **Alto** | Configuración de enlace secundario de respaldo con failover automático mediante módem LTE/5G institucional. **Arquitectura DNS Híbrida Anycast** para que los correos y el portal público sigan respondiendo fuera del colegio aunque la fibra local esté caída. |
| **R3** | **Ataque de Suplantación (*Phishing*) o Inclusión en Listas Negras (RBL)**. | Media | Crítico | **Alto** | Aplicación estricta de la tríada criptográfica: **SPF con `-all`**, **DKIM RSA 2048** y **DMARC `p=quarantine`**. En el servidor Postfix, activación de `reject_sender_login_mismatch` con tabla PCRE que anula la emisión de correos con remitentes ajenos. |
| **R4** | **Pérdida Catastrófica de Datos (Fallo de Disco o Ransomware)**. | Baja | Catastrófico | **Extremo** | Política de respaldos **3-2-1 con Restic**: 3 copias de los datos (producción, copia local en disco secundario y copia externa cifrada en la nube Wasabi), 2 soportes distintos y 1 fuera de las instalaciones. Restauración certificada en menos de 25 minutos con script de prueba. |
| **R5** | **Resistencia al Cambio o Fuga de Contraseñas del Personal Docente**. | Alta | Medio | **Medio** | Programa obligatorio de capacitación de 2 semanas con manual paso a paso de configuración en Thunderbird y dispositivos móviles. Política institucional de contraseñas de al menos 12 caracteres, prohibición de auto-forwarding hacia correos personales y clausura definitiva del puerto en claro 143. |

---

## 3. Cronograma Estratégico de Migración (Plan de 45 Días en 5 Etapas)

```
Semanas:     |  Semana 1  |  Semana 2  |  Semana 3  |  Semana 4  |  Semana 5-6  |
Etapas:      | [Etapa 1]  | [Etapa 2]  | [Etapa 3]  | [Etapa 4]  |  [Etapa 5]   |
Actividades:   Hardware y   DNS Híbrido  Web HTTPS    Capacitación   Convivencia
               Plataforma   y Seguridad  y Correo     y Migración    y Corte Final
```

### Detalle de las Etapas:

1. **Etapa 1: Preparación de Servidor y Red Base (Días 1 a 7):**
   - Montaje del servidor Dell PowerEdge en el rack del departamento de sistemas.
   - Configuración de arreglos de discos RAID 1 e instalación limpia de Ubuntu Server 24.04 LTS.
   - Despliegue de los contenedores de producción desacoplados (`ns1`, `ns2`, `resolutor`, `servidor-web`, `mail`).

2. **Etapa 2: Puesta en Marcha del DNS Híbrido y DNSSEC (Días 8 a 14):**
   - Configuración de BIND 9 con vistas interna (`cbbb.internal`) y externa (`cbautistabb.edu.bo`).
   - Sincronización segura con `ns2` mediante clave TSIG y avisos NOTIFY.
   - Activación de firmado automático DNSSEC (`dnssec-policy standard`).
   - Carga del registro DS en el portal de NIC Bolivia (`nic.bo`).
   - Despliegue de Unbound con DoT (puerto 853) y listas RPZ para protección de laboratorios escolares.

3. **Etapa 3: Integración de Servicios Web y Correo Seguro (Días 15 a 21):**
   - Puesta en marcha de Nginx con TLS 1.3 forzado, HSTS y CSP.
   - Endurecimiento de SSH con claves Ed25519 y jaula SFTP para los editores de circulares.
   - Aprovisionamiento de Postfix y Dovecot en buzones Maildir.
   - Publicación y verificación con `dig` de SPF `-all`, DKIM 2048 y DMARC `p=quarantine`.
   - Cierre irreversible del puerto 143 (`port = 0`).

4. **Etapa 4: Capacitación Docente y Migración de Históricos con IMAPSync (Días 22 a 28):**
   - Talleres presenciales en grupos pequeños (15 profesores por turno) para configuración de Thunderbird en sus laptops.
   - Instalación del certificado de la CA institucional.
   - Ejecución automatizada de `imapsync` para transferir carpetas históricas de correos anteriores hacia los nuevos buzones sin pérdida de información.

5. **Etapa 5: Período de Convivencia, Monitoreo y Corte Definitivo (Días 29 a 45):**
   - Ventana de convivencia de 15 días con auto-respuesta en los correos anteriores.
   - Monitoreo en tiempo real de tráfico y visitas mediante GoAccess.
   - Activación de temporizadores systemd para respaldos nocturnos con Restic a las 02:00 AM.
   - Ejecución de simulacro de recuperación ante desastres (DRP) validando tiempo de restauración.
   - Firma del acta de conformidad y entrega de la infraestructura a la Dirección del Colegio.
