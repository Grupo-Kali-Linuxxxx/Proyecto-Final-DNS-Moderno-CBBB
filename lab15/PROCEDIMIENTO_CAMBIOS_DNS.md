# Procedimiento de Gestión de Cambios DNS y Plan de Migración Híbrido

**Organización:** Colegio Bautista Boliviano Brasileño (CBBB)  
**Dominio:** `cbbb.internal` / `cbautistabb.edu.bo` (`cbbb.example`)  
**Proyecto:** Trabajo Final Integrador — Criterio C1 (Nivel Estratégico — 9 Puntos)  
**Autores:** Ketfer Gianella Salazar y Equipo Estudiantil (UPDS)  

---

## 1. Procedimiento Operativo Estándar para Cambios en Zonas DNS

Para evitar errores comunes como zonas desactualizadas en secundarios, caídas de servicio por errores tipográficos o caídas de reputación, todo cambio en las zonas del Colegio Bautista Boliviano Brasileño debe seguir estrictamente este flujo de 4 etapas:

```
[ Solicitud de Cambio ]
          │
          ▼
[ 1. Rama Git & Edición ] ──> Modificar archivo de zona o dnsconfig.js
          │                   • Aumentar Serial SOA (YYYYMMDDnn)
          │                   • Ajustar TTL según ventana de cambio
          ▼
[ 2. Validación Sintáctica ] ─> named-checkzone / dnscontrol check
          │                   • Si falla: Corrección inmediata en local
          ▼
[ 3. Revisión por Pares (PR) ]─> Aprobación en repositorio de Git
          │
          ▼
[ 4. Despliegue & NOTIFY ] ──> rndc reload && rndc notify
          │                   • Comprobación de sincronización en ns2
          ▼
[ Verificación Operativa ] ──> dig @ns1 y dig @ns2 confirmando nuevo serial
```

---

### 1.1 Regla Estricta del Número de Serie SOA (`serial`)
El número de serie del registro SOA en BIND 9 debe respetar obligatoriamente el formato estándar internacional:

$$\mathbf{YYYYMMDDnn}$$

- **`YYYY`:** Año corriente de 4 dígitos (ej. `2026`).
- **`MM`:** Mes de 2 dígitos (ej. `10` para Octubre).
- **`DD`:** Día del mes de 2 dígitos (ej. `26`).
- **`nn`:** Contador correlativo de cambio para ese día (iniciando en `01`, `02`, `03`... hasta `99`).

> [!CAUTION]
> Si se modifica un registro dentro del archivo de zona y **no se incrementa el serial SOA**, el servidor secundario (`ns2`) descartará el mensaje `NOTIFY` asumiendo que ya posee la versión más reciente, provocando que la mitad de los usuarios del colegio resuelvan información obsoleta (*split brain*).

---

### 1.2 Política de Gestión de Tiempos de Vida (TTL)

| Escenario Operativo | TTL Recomendado | Justificación Técnica |
|---|---|---|
| **Operación Normal y Estable** | **86400 s (24 horas)** o **14400 s (4 horas)** | Maximiza la tasa de aciertos en caché (*cache hit ratio*) de los clientes y proveedores de internet (Tigo, Entel, Cotas), reduciendo drásticamente la carga de CPU y consumo de ancho de banda sobre `ns1`. |
| **Previo a una Migración Planificada** | **300 s (5 minutos)** | Se debe reducir el TTL con **48 horas de anticipación** al cambio de IP del servidor. Esto garantiza que cuando se efectúe la migración física, los cachés de todo el mundo expiren en solo 5 minutos. |
| **Posterior a la Migración** | **14400 s (4 horas)** | Una vez comprobada la estabilidad del nuevo servidor durante 24 horas, se restablece el TTL a su valor operativo nominal. |

---

### 1.3 Prueba Práctica del Procedimiento de Cambio (Simulación Documentada)

A continuación, se documenta la prueba empírica de un cambio controlado agregando el nuevo subdominio académico `biblioteca.cbbb.internal` hacia la IP `10.10.10.22`:

1. **Paso 1: Edición del archivo de zona en `ns1` (`/etc/bind/db.cbbb.internal`):**
   ```dns
   ; Zona Interna Colegio Bautista Boliviano Brasileño
   $TTL 86400
   @   IN  SOA ns1.cbbb.internal. admin.cbbb.internal. (
                   2026102602  ; Serial incrementado (era 2026102601)
                   3600        ; Refresh (1 hora)
                   1800        ; Retry (30 minutos)
                   604800      ; Expire (1 semana)
                   86400 )     ; Negative Cache TTL (1 día)

   ; Nuevo registro agregado para el catálogo escolar:
   biblioteca  IN  A   10.10.10.22
   ```

2. **Paso 2: Validación sintáctica con `named-checkzone`:**
   ```bash
   named-checkzone cbbb.internal /etc/bind/db.cbbb.internal
   # Salida esperada:
   # zone cbbb.internal/IN: loaded serial 2026102602
   # OK
   ```

3. **Paso 3: Aplicación en vivo y notificación al secundario:**
   ```bash
   rndc reload cbbb.internal in interna
   # Salida: zone reload queued
   rndc notify cbbb.internal in interna
   # Salida: zone notify queued
   ```

4. **Paso 4: Auditoría de recepción en `ns2`:**
   ```bash
   # En ns2 se comprueba la transferencia inmediata en el log del sistema:
   journalctl -u named -n 10 --no-pager
   # Salida:
   # transfer of 'cbbb.internal/IN' from 10.10.10.2#53: Transfer status: success
   # transfer of 'cbbb.internal/IN' from 10.10.10.2#53: Transfer completed: 1 messages, 14 records, 482 bytes
   # zone cbbb.internal/IN (interna): loaded serial 2026102602
   ```

5. **Paso 5: Comprobación con `dig` desde la estación cliente:**
   ```bash
   dig @10.10.10.2 biblioteca.cbbb.internal +short
   # Devuelve: 10.10.10.22 (Confirmado en ns1)
   dig @10.10.10.3 biblioteca.cbbb.internal +short
   # Devuelve: 10.10.10.22 (Confirmado en ns2 con serial 2026102602)
   ```

---

## 2. Plan de Migración a un Modelo de DNS Gestionado o Híbrido

Actualmente, el Colegio Bautista Boliviano Brasileño depende de servidores DNS locales y del hosting básico de Nemabol. Ante un corte de energía eléctrica en el 3er Anillo o una falla de enlace de fibra óptica local, la institución quedaría completamente incomunicada en internet.

Se presenta el plan estratégico para migrar hacia una **Arquitectura de DNS Híbrido de Alta Disponibilidad Anycast**:

```
                              +-------------------------------------------+
                              |         NIC BOLIVIA (.edu.bo)             |
                              |         Delegación de Servidores NS       |
                              +---------------------+---------------------+
                                                    |
                                +-------------------+-------------------+
                                |                                       |
                                v                                       v
                 +-----------------------------+         +-----------------------------+
                 | CLOUD PRIVADO COLEGIO CBBB  |         |   RED MUNDIAL ANYCAST       |
                 | Servidor BIND 9 Primario    |         |   (Cloudflare / Route 53)   |
                 | • IP Estática Dedicada      |         | • 300+ Centros de Datos     |
                 | • Gestiona cbbb.internal    |         | • Mitigación DDoS Terabit   |
                 | • Emite firmado DNSSEC local|         | • Zona Pública cbautistabb  |
                 +--------------+--------------+         +--------------+--------------+
                                |                                       |
                                +================= TSIG ===============+
                                        Transferencia Secundaria Segura
```

### 2.1 Fases del Plan de Migración Híbrido

| Fase | Duración | Acciones Operativas | Criterio de Aceptación / Entregable |
|---|---|---|---|
| **Fase 1: Preparación y Auditoría** | Semana 1 | • Levantamiento de inventario completo de registros del dominio `cbautistabb.edu.bo`.<br>• Limpieza de registros obsoletos y validación de registros MX de Google Workspace.<br>• Creación de la cuenta institucional en la plataforma Anycast (Cloudflare Enterprise o AWS Route53). | Archivo de exportación de zona RFC 1035 (`bind-zonefile.txt`) verificado con `named-checkzone`. |
| **Fase 2: Configuración del Enlace Híbrido con TSIG** | Semana 2 | • Configuración de BIND 9 primario en el colegio como *Hidden Master* (maestro oculto).<br>• Generación de par de claves HMAC-SHA256 (`tsig-cbbb-cloud`).<br>• Habilitación de transferencias AXFR restringidas exclusivamente hacia las IPs autorizadas de la nube Anycast. | Prueba de transferencia AXFR exitosa desde la nube hacia el servidor local con clave TSIG. |
| **Fase 3: Implementación de DNSControl (Infraestructura como Código)** | Semana 3 | • Programación de la zona en `dnsconfig.js` mediante DNSControl.<br>• Integración de registros SPF estricto (`-all`), selector DKIM `mail._domainkey`, directiva DMARC `p=quarantine` y restricciones CAA para Let's Encrypt y Google Trust Services.<br>• Ejecución de `dnscontrol preview` para descartar discrepancias. | Pipeline de Git sincronizado con DNSControl aplicando cambios sin errores sintácticos. |
| **Fase 4: Cambio de Delegación en NIC Bolivia (Corte)** | Semana 4 | • Ingreso al portal de administración de dominios de NIC Bolivia (`nic.bo`).<br>• Sustitución de los servidores NS antiguos (`ns1/ns2.nemabol.net`) por los nuevos NS Anycast.<br>• Monitoreo continuo de propagación DNS a nivel global mediante herramientas como DNSChecker. | 100% de resolutores mundiales respondiendo desde la nueva red con resolución < 15 ms. |
| **Fase 5: Activación de DNSSEC en la Nube y Validación** | Semana 5 | • Generación de registro DS en la plataforma Anycast.<br>• Carga del registro DS (algoritmo 13 ECDSAP256SHA256 o RSA-SHA256) en NIC Bolivia.<br>• Comprobación de la cadena de confianza criptográfica con `delv` y DNSViz. | Validación global `fully validated` en todos los resolutores con soporte DNSSEC. |

### 2.2 Beneficios Estratégicos para el Colegio:
1. **Disponibilidad 99.999%:** El sitio web y los registros de correo del colegio siguen funcionando ininterrumpidamente aunque se corte el suministro eléctrico o la fibra óptica del colegio en Santa Cruz.
2. **Defensa contra Ataques DDoS:** Filtrado automático de tráfico malicioso volumétrico antes de que alcance el router institucional.
3. **Velocidad de Respuesta Ulrarrápida:** Los padres de familia en cualquier punto de la ciudad o del extranjero resuelven la página escolar en menos de 10 milisegundos gracias a la caché distribuida Anycast.
