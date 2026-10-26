# Bitácora de Uso y Aplicación de Inteligencia Artificial (Formato APA v7)

**Proyecto Socioformativo — Trabajo Final Integrador (Criterio C3 — 30 Puntos)**  
**Organización Beneficiaria:** Colegio Bautista Boliviano Brasileño (CBBB)  
**Dominio:** `cbautistabb.edu.bo` (`cbbb.example`) / `cbbb.internal`  
**Asignatura:** Tecnología Web I (SIS-0150) — Sexto Semestre  
**Docente Titular:** M.Sc. Ing. Jimmy Nataniel Requena Llorentty  
**Institución Académica:** Universidad Privada Domingo Savio (UPDS), Santa Cruz de la Sierra  
**Equipo de Proyecto:**
1. **Ketfer Gianella Salazar**
2. **Charles Yourdan Conde**
3. **Brian Calás**
4. **Marco Barriga**
5. **Adaniel Balderrama Orellana**

**Fecha de Elaboración:** 26 de Octubre de 2026  
**Repositorio Oficial del Proyecto (GitHub):**  
[https://github.com/Grupo-Kali-Linuxxxx/Proyecto-Final-DNS-Moderno-CBBB](https://github.com/Grupo-Kali-Linuxxxx/Proyecto-Final-DNS-Moderno-CBBB)  

---

## 1. Declaración Ética y Propósito Metodológico

En estricto cumplimiento del *Reglamento de Integridad Académica* de la Universidad Privada Domingo Savio y las directrices del docente de la asignatura, el equipo declara el uso responsable, transparente y crítico de herramientas de Inteligencia Artificial generativa (**Antigravity / Google DeepMind Advanced AI Coding Assistant**) como acelerador de ingeniería y consultoría para:

1. **Automatización de consultas y análisis de radiografía DNS:** Desarrollo del script en Python con `dnspython` para auditar registros públicos del dominio real `cbautistabb.edu.bo` respetando las normas éticas (cero escaneos invasivos, solo peticiones DNS públicas).
2. **Diseño de la matriz de decisiones arquitectónicas:** Evaluación comparativa de estándares IETF (RFC 1035, RFC 2136, RFC 4033, RFC 8555) y directivas de configuración en BIND 9.18 y Unbound.
3. **Formulación del Servicio Investigado de Nivel Estratégico:** Modelado del flujo de emisión de certificados SSL comodín mediante el desafío **DNS-01 (ACME)** y actualizaciones dinámicas con **`nsupdate` TSIG**.
4. **Estructuración económica del Plan de Adopción Real:** Proyección de presupuestos CAPEX/OPEX y matriz de riesgos tecnológicos contextualizada en el mercado de telecomunicaciones de Santa Cruz de la Sierra.

Ninguna directiva de configuración, script o parámetro criptográfico propuesto por el modelo de IA fue integrado a la infraestructura sin previa validación experimental en la terminal, revisión de compatibilidad de sintaxis y verificación exhaustiva mediante los verificadores oficiales del curso.

---

## 2. Registro Cronológico de Prompts y Adaptaciones Técnicas

### Registro 1: Radiografía DNS en Vivo del Dominio `cbautistabb.edu.bo`
- **Fecha y Hora:** 26/10/2026 15:10:00
- **Herramienta de IA:** Antigravity (DeepMind Advanced Coding Assistant).
- **Prompt Enviado:**
  > *"Diseña un script en Python utilizando la librería dnspython para auditar de forma no invasiva el dominio real de un colegio de Santa Cruz (cbautistabb.edu.bo). Debe verificar NS delegados, SOA serial y RNAME, direcciones A/www, servidores MX, registro SPF, DMARC, DNSSEC (DS/DNSKEY), CAA, y resolución inversa (PTR). Imprime el resultado en consola."*
- **Respuesta de la IA:**
  La IA generó el script `radiografia_real.py`, configurando resolutores públicos (1.1.1.1 y 8.8.8.8) y capturando excepciones para registrar cuando un registro no existe en DNS.
- **Evaluación Crítica y Adaptación del Equipo:**
  Al ejecutar el script en Windows, se detectó un error de codificación con caracteres Unicode en terminales CP1252. El equipo modificó el script integrando `codecs.getwriter('utf-8')` y ejecutó la auditoría, descubriendo que el colegio opera sin DMARC, con SPF sin incluir a Google Workspace y sin DNSSEC. Estos datos empíricos se plasmaron en el `BRIEF.md` como base del proyecto.

---

### Registro 2: Procedimiento de Cambios y Plan de Migración Anycast (Criterio 1 Plus)
- **Fecha y Hora:** 26/10/2026 15:18:30
- **Herramienta de IA:** Antigravity (DeepMind Advanced Coding Assistant).
- **Prompt Enviado:**
  > *"Para cumplir el nivel Estratégico del Criterio 1 en la rúbrica del Trabajo Final Integrador, se requiere documentar y probar un procedimiento de cambios de zona (serial SOA, TTL, Git) y un plan de migración a DNS híbrido/gestionado para el Colegio Bautista Boliviano Brasileño. Propón la regla de serial, los tiempos TTL escalonados y el diagrama de migración hacia Anycast con TSIG."*
- **Respuesta de la IA:**
  La IA propuso el estándar de serial `YYYYMMDDnn`, la política de TTL corto (300s) previo a cambios de IP y 86400s en operación, y un plan en 5 fases para transformar el BIND 9 local en un *Hidden Master* que replica hacia redes Anycast mundiales mediante claves TSIG.
- **Evaluación Crítica y Adaptación del Equipo:**
  El equipo adaptó el plan a la realidad de conectividad cruceña, señalando los proveedores de fibra óptica locales (Tigo Business / Entel Empresas) y la necesidad de mantener el servidor local para la zona privada `cbbb.internal`, documentando la simulación completa del cambio en [`PROCEDIMIENTO_CAMBIOS_DNS.md`](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/PROCEDIMIENTO_CAMBIOS_DNS.md).

---

### Registro 3: Servicio Investigado: Desafío DNS-01 y `nsupdate` con TSIG (Criterio 2 Plus)
- **Fecha y Hora:** 26/10/2026 15:21:00
- **Herramienta de IA:** Antigravity (DeepMind Advanced Coding Assistant).
- **Prompt Enviado:**
  > *"La rúbrica del Criterio 2 exige agregar un servicio investigado integrado al dominio (DNS dinámico con nsupdate o certificados por desafío DNS-01). Diseña cómo integrar ambos estándares: cómo Certbot solicita el desafío _acme-challenge y cómo nsupdate con clave TSIG lo inyecta dinámicamente en BIND 9 sin reiniciar el servicio."*
- **Respuesta de la IA:**
  La IA explicó la ventaja de DNS-01 sobre HTTP-01 (soporte para certificados wildcard `*.cbbb.example` y validación de servidores internos sin abrir el puerto 80). Proporcionó la sintaxis de BIND 9 con `update-policy { grant ddns-cbbb-key zonesub ANY; };` y los comandos exactos de `nsupdate` con bloques heredoc.
- **Evaluación Crítica y Adaptación del Equipo:**
  Se verificó la sintaxis en la documentación oficial de BIND 9.18 y se documentó paso a paso la inyección y posterior retiro del registro TXT temporal en [`SERVICIO_INVESTIGADO_DNS01_NSUPDATE.md`](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/SERVICIO_INVESTIGADO_DNS01_NSUPDATE.md).

---

### Registro 4: Plan de Adopción Real, Costos y Riesgos en Santa Cruz (Criterio 3 Plus)
- **Fecha y Hora:** 26/10/2026 15:22:45
- **Herramienta de IA:** Antigravity (DeepMind Advanced Coding Assistant).
- **Prompt Enviado:**
  > *"Para el Criterio 3 de la rúbrica (12 puntos), se debe entregar a la organización un plan de adopción real (costos reales, matriz de riesgos y cronograma de migración). Estructura el presupuesto de un servidor físico en Santa Cruz, enlace de fibra simétrica local, costo de dominio .edu.bo en ADSIB, y compara el costo de software libre vs licencias comerciales de Microsoft/Google. Incluye matriz de riesgos con mitigación de cortes de energía en el 3er anillo."*
- **Respuesta de la IA:**
  La IA formuló una tabla comparativa CAPEX/OPEX detallando hardware Dell PowerEdge R250, licencias Windows Server y CALs ($us 14,366 comercial vs $us 2,600 FOSS, logrando 82% de ahorro). Diseñó la matriz de 5 riesgos con mitigaciones técnicas (UPS online de doble conversión, respaldos 3-2-1 con Restic y failover) y un cronograma de 45 días en 5 etapas.
- **Evaluación Crítica y Adaptación del Equipo:**
  Se cotejaron los precios con cotizaciones del mercado tecnológico de Santa Cruz (Av. Brasil / Chiriguano y cotizaciones corporativas de Tigo/Entel). Se incorporó el documento completo en [`PLAN_ADOPCION_CBBB.md`](file:///c:/Users/Ketfer/Desktop/Tecnologia%20Web%201/lab15/PLAN_ADOPCION_CBBB.md).

---

## 3. Matriz de Síntesis del Aporte Humano vs. Aporte de IA

| Componente del Proyecto Final | Contribución de la Inteligencia Artificial | Validación, Ajuste y Ejecución por el Equipo |
|---|---|---|
| **Diagnóstico del Dominio Real** | Estructuración inicial del script de consulta multirregistro con `dnspython`. | Identificación de la institución educativa, resolución de problemas de encoding en Windows y ejecución en vivo de la radiografía. |
| **Diseño del DNS Híbrido** | Recomendación de directivas de vistas BIND 9 (`match-clients`) y sintaxis de Unbound. | Adaptación de archivos de zona, validación de transferencia TSIG en contenedores y eliminación de advertencias sintácticas. |
| **Servicio Investigado (DNS-01)** | Propuesta teórica del flujo ACME RFC 8555 e inyección dinámica con `nsupdate` (RFC 2136). | Generación de clave TSIG HMAC-SHA256, prueba de inyección en vivo en `ns1` y verificación con `dig`. |
| **Plan Económico y Operativo** | Plantilla de desglose de costos CAPEX/OPEX y matriz de riesgos de infraestructura. | Ajuste a tarifas bolivianas (ADSIB 140 Bs/año, enlaces simétricos en Santa Cruz y autonomía de UPS). |
| **Documentación y Guía Oral** | Generación de plantillas Markdown APA 7 y banco de preguntas técnicas imprevistas. | Redacción final de la defensa oral, división de roles por bloques de tiempo y verificación de coherencia técnica integral. |

---

## 4. Reflexión Crítica sobre la IA en la Ingeniería de Sistemas

El desarrollo del Proyecto Socioformativo evidenció que la Inteligencia Artificial actúa como un catalizador de productividad de alto calibre cuando es guiada por profesionales con sólida base conceptual. En la administración de infraestructura de redes críticas, la IA puede sugerir configuraciones complejas en segundos; sin embargo, carece de la capacidad de comprender las restricciones físicas del entorno local (como los cortes de energía en Santa Cruz, la latencia de los proveedores locales o la rigidez de las políticas de NIC Bolivia).

La competencia determinante del futuro Ingeniero de Sistemas no radica en memorizar la sintaxis de archivos de configuración, sino en poseer el **criterio arquitectónico** para interrogar a los modelos de lenguaje, auditar rigurosamente cada línea de código generado, comprobar experimentalmente los resultados mediante herramientas de diagnóstico empírico (`dig`, `delv`, `openssl`, `swaks`) y articular soluciones tecnológicas éticas, seguras y económicamente viables para la sociedad.
