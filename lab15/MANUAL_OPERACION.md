# Manual de Operación y Mantenimiento de Infraestructura

**Organización:** Colegio Bautista Boliviano Brasileño (CBBB)  
**Dominio Interno:** `cbbb.internal` | **Dominio Público:** `cbautistabb.edu.bo` (`cbbb.example`)  
**Elaborado por:** Ketfer Gianella Salazar, Charles Yourdan Conde, Brian Calás, Marco Barriga, Adaniel Balderrama  
**Asignatura:** Tecnología Web I (SIS-0150) — Sexto Semestre  
**Docente Titular:** M.Sc. Ing. Jimmy Nataniel Requena Llorentty  
**Institución:** Universidad Privada Domingo Savio (UPDS), Santa Cruz de la Sierra  
**Fecha de Publicación:** 26 de Octubre de 2026  

---

## 1. Mapa Rápido de la Infraestructura Institucional

| Nodo | Dirección IP | Servicios en Ejecución | Ubicación de Archivos de Configuración Clave |
|---|---|---|---|
| **`ns1`** | `10.10.10.2` (int)<br>`172.30.0.2` (ext) | BIND 9.18 (Vistas interna/externa, DNSSEC, Primario) | `/etc/bind/named.conf.local`<br>`/var/lib/bind/db.cbbb.internal`<br>`/var/lib/bind/externa/db.cbbb.example`<br>`/etc/bind/transferencia.key` |
| **`ns2`** | `10.10.10.3` | BIND 9.18 (Secundario TSIG con NOTIFY) | `/etc/bind/named.conf.local`<br>`/etc/bind/transferencia.key` |
| **`resolutor`**| `10.10.10.4` | Unbound 1.19 (DoT puerto 853, DNSSEC, RPZ) | `/etc/unbound/unbound.conf`<br>`/etc/unbound/rpz.zone`<br>`/etc/unbound/unbound.conf.d/` |
| **`servidor-web`**| `10.10.10.20` | Nginx 1.24, PHP 8.3 FPM, API Eco, UFW, Restic | `/etc/nginx/sites-available/`<br>`/etc/nginx/snippets/cbbb-tls.conf`<br>`/srv/cbbb/`<br>`/usr/local/sbin/cbbb-vigilar` |
| **`mail`** | `10.10.10.25` | Postfix 3.8, Dovecot 2.3, OpenDKIM | `/etc/postfix/main.cf`<br>`/etc/postfix/master.cf`<br>`/etc/dovecot/conf.d/99-cbbb.conf`<br>`/etc/opendkim.conf` |
| **`cliente`** | `10.10.10.50` | Estación de Auditoría y Gestión TI CBBB | `/lab/lab15/auditar_infraestructura.sh` |
| **`externo`** | `172.30.0.100` | Simulación de Internet / Auditoría Externa | `/lab/lab15/auditar_publico.sh` |

---

## 2. Tareas Frecuentes (Paso a Paso con Comandos Exactos)

### A. Agregar un Nuevo Nombre Interno en el DNS (`ns1`)
1. Iniciar sesión como root en `ns1`:
   ```bash
   nano /var/lib/bind/db.cbbb.internal
   ```
2. Agregar el registro deseado al final del archivo (ejemplo: `laboratorio-computo IN A 10.10.10.85`).
3. **Incrementar obligatoriamente el número de serial SOA** en la cabecera (formato `AAAAMMDDnn`, ejemplo: de `2026102601` a `2026102602`).
4. Validar la sintaxis de la zona antes de aplicar:
   ```bash
   named-checkzone cbbb.internal /var/lib/bind/db.cbbb.internal
   ```
5. Recargar la zona y emitir la notificación instantánea al secundario:
   ```bash
   rndc reload cbbb.internal IN interna
   rndc notify cbbb.internal IN interna
   ```
6. Verificar en el secundario (`ns2`) que el nuevo serial y registro se hayan transferido:
   ```bash
   dig +short @10.10.10.3 laboratorio-computo.cbbb.internal A
   ```

---

### B. Bloquear un Dominio Malicioso en el Resolutor Escolar con RPZ (`resolutor`)
1. Abrir el archivo de directivas de filtrado de reputación en `resolutor`:
   ```bash
   nano /etc/unbound/rpz.zone
   ```
2. Agregar la regla de bloqueo forzando respuesta de inexistencia (`CNAME .`):
   ```text
   sitio-apuestas.xyz CNAME .
   *.sitio-apuestas.xyz CNAME .
   juegos-maliciosos.com CNAME .
   ```
3. Comprobar la coherencia sintáctica y recargar Unbound:
   ```bash
   unbound-checkconf
   systemctl reload unbound
   ```
4. Probar que el dominio retorna `NXDOMAIN` a los alumnos:
   ```bash
   dig @10.10.10.4 sitio-apuestas.xyz A
   ```

---

### C. Modificar un Registro Público con DNSControl
1. Editar la configuración declarativa de infraestructura como código en `dnsconfig.js`:
   ```javascript
   D('cbbb.example', REG_NONE, DnsProvider(BIND),
       A('@', '203.0.113.20'),
       A('www', '203.0.113.20'),
       A('inscripciones', '203.0.113.30')
   );
   ```
2. Ejecutar la vista previa obligatoria para auditar los cambios calculados:
   ```bash
   dnscontrol preview
   ```
3. Si el diff es exactamente el deseado, desplegar los cambios hacia producción:
   ```bash
   dnscontrol push
   ```

---

### D. Crear una Cuenta de Correo y su Alias Institucional (`mail`)
1. Crear el usuario de sistema para la nueva cuenta con su directorio Maildir:
   ```bash
   adduser --disabled-login --gecos "Profesor Juan Perez" juan.perez
   passwd juan.perez
   maildirmake.dovecot /home/juan.perez/Maildir
   chown -R juan.perez:juan.perez /home/juan.perez/Maildir
   chmod -R 700 /home/juan.perez/Maildir
   ```
2. Asociar el alias en `/etc/aliases` (ejemplo: `primaria: juan.perez`):
   ```bash
   echo "primaria: juan.perez" >> /etc/aliases
   newaliases
   ```
3. Actualizar la tabla de control anti-suplantación en `/etc/postfix/remitentes.pcre` para que pueda firmar y enviar como `juan.perez@cbautistabb.edu.bo`:
   ```bash
   echo "/^juan\.perez@cbbb\.internal$/ juan.perez" >> /etc/postfix/remitentes.pcre
   postfix reload
   ```

---

### E. Conceder Acceso SSH a un Nuevo Técnico Administrador (`servidor-web`)
1. Crear la cuenta de usuario técnico si no existe:
   ```bash
   adduser --gecos "Tecnico Redes CBBB" tec.soporte
   ```
2. Incorporarlo al grupo administrativo autorizado en `sshd_config` (`AllowGroups sshadmins`):
   ```bash
   usermod -aG sshadmins tec.soporte
   ```
3. Crear el directorio seguro e inyectar la clave pública del técnico:
   ```bash
   install -d -o tec.soporte -g tec.soporte -m 700 /home/tec.soporte/.ssh
   cat id_ed25519.pub >> /home/tec.soporte/.ssh/authorized_keys
   chown tec.soporte:tec.soporte /home/tec.soporte/.ssh/authorized_keys
   chmod 600 /home/tec.soporte/.ssh/authorized_keys
   ```
4. Comprobar que no se requiere contraseña y que la política de solo claves se respeta:
   ```bash
   ssh -i id_ed25519 tec.soporte@10.10.10.20
   ```

---

## 3. Tareas de Mantenimiento Periódico

### A. Renovación de Certificados TLS de la CA Institucional
- **Frecuencia:** Cada 90 días.
- **Procedimiento:** Ejecutar en el servidor web:
  ```bash
  cd /root/cbbb/tls
  bash crear_ca_y_certificado.sh
  systemctl reload nginx
  ```
- **Verificación:** `openssl x509 -enddate -noout -in /etc/nginx/tls/cbbb.crt`.

### B. Revisión de Firmas DNSSEC en la Vista Externa
- **Frecuencia:** Semanal o automatizada por timer.
- **Procedimiento:** En `ns1`, ejecutar `bash /lab/lab09/vigilar_dns.sh`.
- **Criterio:** La validez de las firmas RRSIG debe ser superior a 7 días. BIND 9 renueva automáticamente las firmas si el demonio se mantiene en ejecución continua (`inline-signing yes`).

### C. Auditoría de Seguridad DMARC y Bloqueos Fail2ban
- **Frecuencia:** Semanal.
- **Procedimiento:**
  - Inspeccionar los reportes agregados DMARC recibidos en `dmarc@cbbb.internal` para certificar que ningún remitente no autorizado esté falsificando correos del colegio.
  - Verificar las IPs actualmente bloqueadas por fuerza bruta en SSH:
    ```bash
    fail2ban-client status sshd
    ```

### D. Simulacro Mensual de Restauración con Restic
- **Frecuencia:** Primer lunes de cada mes.
- **Procedimiento:** Ejecutar en el servidor web:
  ```bash
  bash /root/lab14/respaldos/probar_restauracion.sh
  ```
- **Criterio de éxito:** Mensaje `✅ Restaurado idéntico (SHA-256 ...)` y archivo `restauracion.ok` actualizado.

---

## 4. Matriz de Diagnóstico y Resolución Rápida de Incidentes

| Síntoma Observado | Primer Comando de Diagnóstico | Causa Frecuente | Solución Inmediata |
|---|---|---|---|
| **"No abre el portal escolar (portal.cbbb.internal)"** | `curl -sI https://portal.cbbb.internal/` | 1. Nginx o PHP-FPM detenido.<br>2. Certificado TLS vencido. | `systemctl status nginx php8.3-fpm`<br>`systemctl restart nginx php8.3-fpm`<br>Renovar cert con `crear_ca_y_certificado.sh`. |
| **"No llegan correos de padres de familia"** | `tail -f /var/log/mail.log` | 1. Puerto 25 bloqueado por el firewall.<br>2. Registro MX o SPF mal publicado. | `ufw status`<br>`dig @10.10.10.4 cbbb.internal MX`<br>Asegurar regla `ufw allow 25/tcp` en el MTA. |
| **"Un nombre interno no resuelve desde los laboratorios"** | `dig @10.10.10.4 nombre.cbbb.internal` | 1. Falta zona interna en Unbound.<br>2. Desincronización entre ns1 y ns2 por serial no incrementado. | Revisar `stub-zone` en `/etc/unbound/unbound.conf`. Subir serial en `db.cbbb.internal` y ejecutar `rndc reload && rndc notify`. |
| **"Error 401 al ver reportes de GoAccess"** | `cat /etc/nginx/reportes.htpasswd` | Credenciales incorrectas para el usuario de TI. | Regenerar clave con `printf 'ti:%s\n' "$(openssl passwd -apr1 'Reportes2026!')" > /etc/nginx/reportes.htpasswd`. |
| **"Conexión rechazada por SSH (Connection refused o timeout)"** | `ufw status verbose` | La IP del técnico fue bloqueada temporalmente por `ufw limit` o `fail2ban`. | Desde consola local: `fail2ban-client set sshd unbanip <IP>` o verificar que el puerto 22 no esté bloqueado. |

---

## 5. Plan de Recuperación ante Desastres (Disaster Recovery Plan - DRP)

### Orden Secuencial de Reconstrucción de la Infraestructura del CBBB:
1. **Paso 1 (Capa DNS Base):** Desplegar y levantar los servidores autoritativos `ns1` y `ns2`, restaurando las zonas directa, inversa y pública con sus claves TSIG.
2. **Paso 2 (Capa de Resolución):** Iniciar el resolutor recursivo `resolutor` (Unbound), cargando las zonas de reenvío (*stub-zones*) hacia `ns1`/`ns2` y la RPZ de seguridad escolar.
3. **Paso 3 (Capa de Servidor Web y Contenidos):**
   - En un servidor o VPS limpio con Ubuntu Server, ejecutar `preparar_servidor.sh`.
   - Recuperar la clave maestra de Restic desde la caja fuerte institucional.
   - Ejecutar la restauración íntegra:
     ```bash
     export RESTIC_REPOSITORY=/var/backups/cbbb-restic
     export RESTIC_PASSWORD_FILE=/root/.config/cbbb/restic.clave
     restic restore latest --target /
     ```
   - Recargar los demonios con `systemctl daemon-reload && systemctl restart nginx php8.3-fpm cbbb-eco`.
   - Aplicar el firewall perimetral con `bash /root/lab14/firewall/aplicar_ufw.sh`.
4. **Paso 4 (Capa de Correo):** Levantar el nodo `mail`, verificar el montaje de `/home/*/Maildir` y arrancar `postfix`, `dovecot` y `opendkim`.
5. **Paso 5 (Auditoría Final):** Ejecutar desde `cliente`:
   ```bash
   bash /lab/lab15/auditar_infraestructura.sh cbbb.internal mail
   ```
   **Criterio de finalización:** 29 de 29 comprobaciones en verde.

### Ubicación de Secretos y Claves Críticas:
- **Clave Restic:** Resguardada en `/root/.config/cbbb/restic.clave` (respaldada físicamente en sobre sellado en caja fuerte de dirección).
- **Clave CA Raíz:** Custodiada exclusivamente en `/etc/cbbb-ca/ca.key` (permisos 0600).
- **Clave TSIG BIND:** En `/etc/bind/transferencia.key` compartida únicamente entre `ns1` y `ns2`.
- **Clave Privada DKIM:** En `/etc/opendkim/claves/mail.private` en el servidor `mail`.

**Tiempo Medio Estimado de Recuperación Total (MTTR):** **20 a 25 minutos.**

---

## 6. Directorio de Contactos y Escalamiento Técnico

- **Equipo de Consultoría y Diseño:** Ketfer Gianella Salazar, Charles Yourdan Conde, Brian Calás, Marco Barriga, Adaniel Balderrama — UPDS.
- **Coordinador de Tecnología Educativa:** Lic. Roberto Da Silva — Colegio Bautista Boliviano Brasileño (CBBB).
- **Soporte de Conectividad e Internet (ISP):** Centro de Operaciones de Red (NOC) Tigo Business Santa Cruz — Teléfono 24/7: 800-17-5555.
- **Docente Supervisor de Asignatura:** M.Sc. Ing. Jimmy Nataniel Requena Llorentty — Universidad Privada Domingo Savio.
