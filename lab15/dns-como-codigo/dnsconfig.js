// dnsconfig.js — Zona PÚBLICA del Colegio Bautista Boliviano Brasileño (CBBB) descrita como Código (DNSControl)
// Proyecto Socioformativo - Tecnología Web I (SIS-0150) - UPDS Santa Cruz
// Equipo: Ketfer Gianella Salazar, Charles Yourdan Conde, Brian Calás, Marco Barriga, Adaniel Balderrama
//
// Flujo profesional de cambios en Git:
// 1. Editar dnsconfig.js en rama 'feature/cambio-dns'
// 2. dnscontrol check   (validar sintaxis JS)
// 3. dnscontrol preview (calcular diff contra el proveedor DNS)
// 4. Pull Request y code-review de 2 integrantes
// 5. dnscontrol push    (aplicar a BIND 9 local o Cloudflare Anycast)

var REG_NINGUNO = NewRegistrar("none");
var DNS_BIND    = NewDnsProvider("bind");
// Para migración híbrida a Cloudflare Anycast, descomentar:
// var DNS_CLOUDFLARE = NewDnsProvider("cloudflare");

var IP_WEB_CBBB  = "203.0.113.20";   // Rango reservado para documentación RFC 5737 (proyectado a 148.113.159.58)
var IP_MAIL_CBBB = "203.0.113.25";   // Servidor Postfix institucional

// ============================================================================
// Zona Pública del Colegio Bautista Boliviano Brasileño
// ============================================================================
D("cbbb.example", REG_NINGUNO, DnsProvider(DNS_BIND),
    DefaultTTL(3600),

    // SOA con serial semántico YYYYMMDDnn y tiempos RFC 1982 / RFC 2182
    SOA("@", "ns1.cbbb.example.", "soporte-ti.cbautistabb.edu.bo.", 3600, 600, 1209600, 300),

    // Servidores de Nombres Autoritativos Redundantes
    NAMESERVER("ns1.cbbb.example."),
    NAMESERVER("ns2.cbbb.example."),
    A("ns1", "203.0.113.2"),
    A("ns2", "198.51.100.3"),                 // Secundario en segmento de red independiente (RFC 2182)

    // Servicio Web Institucional
    A("@",   IP_WEB_CBBB),
    A("www", IP_WEB_CBBB),
    CNAME("portal", "www"),
    CNAME("aulavirtual", "www"),
    CNAME("inscripciones", "www"),

    // Servicio de Correo Institucional (MTA Postfix + Google Workspace Híbrido)
    MX("@", 10, "mail"),
    A("mail", IP_MAIL_CBBB),

    // SPF Endurecido: Autoriza servidores institucionales y Google Workspace sin relé abierto (-all)
    SPF_BUILDER({
        label: "@",
        parts: [
            "v=spf1",
            "mx",
            "include:_spf.google.com",
            "ip4:203.0.113.25",
            "-all"
        ]
    }),

    // DMARC Estricto con Reportes Agregados (RUA) y Forenses (RUF)
    DMARC_BUILDER({
        policy: "quarantine",
        subdomainPolicy: "reject",
        rua: ["mailto:dmarc-reports@cbautistabb.edu.bo"],
        ruf: ["mailto:seguridad-ti@cbautistabb.edu.bo"],
        percent: 100
    }),

    // Clave Pública DKIM (Selector mail._domainkey) 2048 bits
    TXT("mail._domainkey", "v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0FvLqP+4gW7uK8hZt2...CBBB...IDAQAB"),

    // Restricción CAA (RFC 8659): Solo Let's Encrypt puede emitir certificados, prohibiendo wildcards no autorizados
    CAA_BUILDER({
        issue: ["letsencrypt.org"],
        issuewild: ["none"],
        iodef: ["mailto:seguridad-ti@cbautistabb.edu.bo"]
    }),

    // Token de Verificación Institucional
    TXT("@", "cbbb-institucional-verification=UPDS-SIS0150-TF-2026")
);
