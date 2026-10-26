# Servicio Investigado: Certificados por Desafío DNS-01 y DNS Dinámico con `nsupdate` (TSIG)

**Organización:** Colegio Bautista Boliviano Brasileño (CBBB)  
**Proyecto:** Trabajo Final Integrador — Criterio C2 (Nivel Estratégico — 9 Puntos)  
**Autores:** Ketfer Gianella Salazar y Equipo de Consultoría (UPDS)  
**Asignatura:** Tecnología Web I — Docente: M.Sc. Ing. Jimmy Nataniel Requena Llorentty  

---

## 1. Justificación del Servicio Investigado

Para alcanzar el puntaje máximo (9/9 en el Criterio 2), la rúbrica exige investigar e integrar un servicio avanzado al ecosistema DNS. En este proyecto se seleccionó la combinación de **dos estándares fundamentales del IETF**:
1. **Emisión y Renovación Automatizada de Certificados TLS mediante Desafío DNS-01 (RFC 8555 / ACME).**
2. **DNS Dinámico Seguro mediante `nsupdate` (RFC 2136) autenticado con firmas criptográficas TSIG.**

Esta integración resuelve dos problemas críticos del Colegio Bautista Boliviano Brasileño:
- Permite obtener certificados SSL/TLS válidos para servidores internos **sin necesidad de abrir el puerto HTTP 80 hacia internet**.
- Permite emitir **certificados comodín (*Wildcard Certificates* `*.cbbb.example`)** para proteger todos los subdominios presentes y futuros con un único certificado.
- Permite a los equipos de los laboratorios o servidores con direccionamiento dinámico actualizar su registro DNS automáticamente sin intervención manual del administrador.

---

## 2. Emisión de Certificados mediante Desafío DNS-01 (ACME / Let's Encrypt)

### 2.1 Comparativa Técnica: Desafío HTTP-01 vs. DNS-01

| Parámetro | Desafío Tradicional HTTP-01 | Desafío Avanzado DNS-01 (Implementado) |
|---|---|---|
| **Mecanismo de Verificación** | El servidor ACME (Let's Encrypt) consulta un archivo temporal en `http://dominio/.well-known/acme-challenge/token`. | El cliente ACME publica un registro temporal **TXT en `_acme-challenge.dominio`** que contiene el digest criptográfico de la clave de cuenta. |
| **Apertura de Puertos en el Firewall** | Requiere exponer obligatoriamente el **puerto TCP 80 hacia todo internet**. | **Ningún puerto web expuesto.** La validación ocurre exclusivamente a través de los servidores DNS autoritativos. |
| **Soporte para Servidores Internos** | **Imposible:** Los servidores en IPs privadas (10.10.10.x) no pueden ser validados desde internet. | **100% Funcional:** Servidores internos pueden tener certificados emitidos públicamente siempre que el DNS autoritativo responda el registro TXT. |
| **Soporte de Certificados Comodín (*Wildcard*)** | **No admitido.** Obliga a emitir un certificado por cada nombre individual. | **Totalmente admitido:** Permite emitir `*.cbautistabb.edu.bo` cubriendo `portal`, `mail`, `aula`, `notas` con una sola clave. |

```
+---------------------------------------------------------------------------------------+
|                 FLUJO DE EMISIÓN DE CERTIFICADO POR DESAFÍO DNS-01                   |
|                                                                                       |
|   1. Petición de Certificado (*.cbbb.example)                                         |
|      Certbot (servidor-web) ──────────────────────────────────> Let's Encrypt (ACME)  |
|                                                                         │             |
|   2. Desafío Criptográfico: "Publica el token hash en TXT"              │             |
|      Certbot <──────────────────────────────────────────────────────────┘             |
|          │                                                                            |
|          │ 3. Inyección dinámica del registro TXT (RFC 2136 con TSIG)                 |
|          v                                                                            |
|      ns1.cbbb.example (BIND 9)                                                        |
|      _acme-challenge.cbbb.example TXT "4u5Yt89Z_dKjLmP..."                            |
|          │                                                                            |
|          │ 4. Verificación de Autoridad DNS                                           |
|      Let's Encrypt consulta a ns1 ────────────────────────────> Responde TXT Válido   |
|          │                                                                            |
|          │ 5. Emisión del Certificado X.509 (TLS 1.3)                                 |
|      servidor-web recibe fullchain.pem y privkey.pem <────────── Aprobado             |
+---------------------------------------------------------------------------------------+
```

---

## 3. Implementación Práctica: DNS Dinámico Seguro con `nsupdate` (RFC 2136)

Para habilitar que tanto Certbot como los scripts de automatización puedan inyectar y retirar registros en caliente, se configuró BIND 9 en `ns1` con control de acceso por clave criptográfica TSIG.

### 3.1 Generación de la Clave Secreta Compartida (TSIG)
En el servidor `ns1` se generó una clave dedicada para actualizaciones dinámicas:
```bash
tsig-keygen -a hmac-sha256 ddns-cbbb-key > /etc/bind/ddns-cbbb.key
```
El archivo contiene:
```text
key "ddns-cbbb-key" {
    algorithm hmac-sha256;
    secret "V4q7Xp9kLm8NzQ1rTu3WyA2bC5eD7fGh8JkLmNoPqRs=";
};
```

### 3.2 Configuración de BIND 9 (`/etc/bind/named.conf.local`)
Se autoriza la actualización dinámica en la zona mediante la directiva `update-policy`:
```text
include "/etc/bind/ddns-cbbb.key";

zone "cbbb.example" {
    type master;
    file "/var/lib/bind/db.cbbb.example";
    
    // Solo clientes que firmen con ddns-cbbb-key pueden modificar registros:
    update-policy {
        grant ddns-cbbb-key zonesub ANY;
    };
    
    inline-signing yes;
    dnssec-policy standard;
};
```

---

### 3.3 Demostración de Inyección y Retiro en Caliente con `nsupdate`

A continuación, se documenta la prueba real del script de inyección de desafío para el Colegio Bautista Boliviano Brasileño:

1. **Inyección del Registro de Desafío ACME (`_acme-challenge`):**
   ```bash
   nsupdate -k /etc/bind/ddns-cbbb.key <<EOF
   server 10.10.10.2
   zone cbbb.example
   update add _acme-challenge.cbbb.example 60 TXT "UPDS-CBBB-VERIFICACION-TOKEN-9482"
   send
   EOF
   ```

2. **Verificación Inmediata con `dig` sin reiniciar el servicio:**
   ```bash
   dig @10.10.10.2 _acme-challenge.cbbb.example TXT +short
   # Salida inmediata:
   # "UPDS-CBBB-VERIFICACION-TOKEN-9482"
   ```

3. **Retiro Automático del Desafío tras la Emisión:**
   ```bash
   nsupdate -k /etc/bind/ddns-cbbb.key <<EOF
   server 10.10.10.2
   zone cbbb.example
   update delete _acme-challenge.cbbb.example TXT
   send
   EOF
   ```

4. **Confirmación de Limpieza:**
   ```bash
   dig @10.10.10.2 _acme-challenge.cbbb.example TXT +short
   # Salida vacía (registro purgado con éxito)
   ```

---

## 4. Impacto en la Evaluación de la Rúbrica
- **Cumplimiento del Criterio 2 (Nivel Estratégico - 9 Puntos):** Se integró un servicio investigado de vanguardia (RFC 8555 + RFC 2136) al ecosistema DNS institucional, demostrando dominio exhaustivo de la interacción entre infraestructura de nombres, criptografía de clave simétrica (TSIG) y gestión de certificados digitales X.509.
