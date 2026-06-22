"use client";

import { FormEvent, useEffect, useMemo, useState, type CSSProperties } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  ChevronUp,
  CircleHelp,
  Copy,
  Eraser,
  LoaderCircle,
  MailCheck,
  Moon,
  ShieldCheck,
  Sun,
  Wrench,
  XCircle,
} from "lucide-react";

import type {
  AggregateResult,
  BulkComplianceItem,
  CheckListResult,
  CheckResult,
  ErrorResult,
  ManualCheckResult,
} from "@/lib/checker-types";
import { trackEvent } from "@/lib/analytics";
import { buildLeadCaptureUrl } from "@/lib/lead-capture";
import type { CheckerPageConfig } from "@/lib/page-config";
import { buildDeveloperReport, toneFromStatus } from "@/lib/report";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_MAILAUTHCHECK_API_URL ?? "http://127.0.0.1:8000";
const SHOW_LOCALE_SELECTOR = process.env.NEXT_PUBLIC_SHOW_LOCALE_SELECTOR === "true";

type Locale = "en" | "es" | "pt";
type Theme = "light" | "dark";

type RecentCheckItem = {
  id: string;
  domain: string;
  espProvider: string | null;
  path: string;
  resultSnapshot: AggregateResult;
  savedAt: string;
  source: "api_result";
};

const RECENT_CHECKS_STORAGE_KEY = "mailauthcheck.recentChecks.v1";
const RECENT_CHECKS_TTL_MS = 24 * 60 * 60 * 1000;
const RECENT_CHECKS_LIMIT = 10;

const localeLabels: Record<Locale, string> = {
  en: "EN",
  es: "ES",
  pt: "PT",
};

const chromeCopy = {
  en: {
    language: "Language",
    themeLight: "Light",
    themeDark: "Dark",
    publicDns: "Public DNS checks",
    noAccount: "No account needed",
    noInbox: "No inbox guarantee",
    domain: "Domain",
    esp: "Sending platform (optional)",
    helper:
      "Enter a domain like example.com. Choose a sending platform only if you know it; the domain is enough to start.",
    loading: "Checking public DNS records...",
    liveChecker: "Live checker",
    runCheck: "Check readiness",
    ready: "Ready",
    needsAttention: "Needs attention",
    notReady: "Not ready",
    resultCards: "Result cards",
    manualChecks: "Manual checks",
    manualTitle: "Manual review required",
    manualIntro:
      "These items cannot be verified from DNS alone. Review them inside your ESP, message headers or provider dashboards before treating a campaign as ready.",
    bulkChecklist: "Bulk checklist",
    gmailChecklistTitle: "Gmail bulk sender checklist",
    yahooChecklistTitle: "Yahoo bulk sender checklist",
    manualStatus: "manual",
    nextSteps: "Next steps",
    nextTitle: "Fix the most important issues first",
    nextIntro:
      "The result starts with plain language, then keeps technical details and raw DNS records visible for developers and agencies who need them.",
    howLabel: "How it works",
    howTitle: "What you can click on this page",
    howScanTitle: "Run the checker",
    howScan:
      "Type a domain, optionally choose the sending platform, and click the main check button. The domain is the main input.",
    howReportTitle: "Copy a technical report",
    howReport:
      "After a scan, copy the result summary and raw records so you can send them to your developer or agency.",
    howHelpTitle: "Request assisted setup",
    howHelp:
      "After a scan, the help CTA opens a lightweight contact flow. There is no login, checkout or dashboard.",
    helpLabel: "Assisted setup CTA",
    helpTitle: "Need this fixed before your next campaign?",
    helpIntro:
      "We can review your SPF, DKIM and DMARC setup and send you the exact DNS changes to apply.",
    helpButton: "Need this fixed before your next campaign?",
    helpUnavailable: "Run a scan to request help",
    copyReport: "Copy report for my developer",
    copyCopied: "Technical report copied",
    copyFailed: "Copy failed",
    copyUnavailable: "Run a scan to copy report",
    clearResult: "Clear result",
    backToTop: "Back to top",
    recentLabel: "Recent checks",
    recentTitle: "Recent checks",
    recentIntro: "Saved on this device only. Open a saved result without making a new DNS request.",
    recentShowHistory: "Show history",
    recentHideHistory: "Hide history",
    recentEmpty: "No saved checks yet. Run a scan to keep the latest result here.",
    recentSavedNote: "Saved result. DNS may have changed.",
    recentOpenSaved: "Open saved result",
    recentCheckAgain: "Check again",
    recentRemove: "Remove",
    recentClearHistory: "Clear history",
    helpNoteResult:
      "This opens a simple external contact form and pre-fills the domain and main issues.",
    helpNoteEmpty: "Run a scan first to unlock the help request and technical report.",
    guaranteeNote:
      "It can help with visible DNS authentication issues, but it does not guarantee inbox placement.",
    relatedLabel: "Related tools",
    relatedTitle: "Focused tools for one check at a time",
    guidesLabel: "Guides",
    guidesTitle: "Practical setup guides",
    guidesIntro:
      "These guides explain the manual parts that public DNS alone cannot prove.",
    faqLabel: "FAQ",
    faqTitle: "Clear answers",
    disclaimer: "Disclaimer:",
    footer: "A focused utility for SPF, DKIM, DMARC, MX and bulk sender-readiness basics.",
    noRawRecord: "No raw record to show for this check.",
  },
  es: {
    language: "Idioma",
    themeLight: "Claro",
    themeDark: "Oscuro",
    publicDns: "Verificacion DNS publica",
    noAccount: "Sin cuenta",
    noInbox: "Sin garantia de entrega",
    domain: "Dominio",
    esp: "Plataforma de envio (opcional)",
    helper:
      "Escribe un dominio como example.com. Elige una plataforma solo si la conoces; el dominio basta para empezar.",
    loading: "Consultando DNS publicos...",
    liveChecker: "Verificador en vivo",
    runCheck: "Comprobar preparacion",
    ready: "Listo",
    needsAttention: "Necesita atencion",
    notReady: "No listo",
    resultCards: "Resultados",
    manualChecks: "Revisiones manuales",
    manualTitle: "Revision manual requerida",
    manualIntro:
      "Estos puntos no se pueden verificar solo con DNS. Revisalos dentro de tu ESP, cabeceras de mensajes o paneles del proveedor antes de tratar una campana como lista.",
    bulkChecklist: "Checklist de envio masivo",
    gmailChecklistTitle: "Checklist de remitente masivo para Gmail",
    yahooChecklistTitle: "Checklist de remitente masivo para Yahoo",
    manualStatus: "manual",
    nextSteps: "Proximos pasos",
    nextTitle: "Corrige primero lo mas importante",
    nextIntro:
      "El resultado empieza con lenguaje claro y deja los detalles tecnicos y registros DNS visibles para developers y agencias.",
    howLabel: "Como funciona",
    howTitle: "Que puedes hacer en esta pagina",
    howScanTitle: "Ejecutar el verificador",
    howScan:
      "Escribe un dominio, elige opcionalmente la plataforma de envio y pulsa el boton principal. El dominio es la entrada principal.",
    howReportTitle: "Copiar reporte tecnico",
    howReport:
      "Despues de un scan, copia el resumen y los registros para enviarlos a un developer o agencia.",
    howHelpTitle: "Pedir ayuda asistida",
    howHelp:
      "Despues de un scan, el CTA de ayuda abre un flujo ligero de contacto. No hay login, checkout ni dashboard.",
    helpLabel: "CTA de ayuda",
    helpTitle: "Necesitas resolver esto antes de tu proxima campana?",
    helpIntro:
      "Podemos revisar tu SPF, DKIM y DMARC y decirte exactamente que cambios DNS aplicar.",
    helpButton: "Necesitas resolver esto antes de tu proxima campana?",
    helpUnavailable: "Ejecuta un scan para pedir ayuda",
    copyReport: "Copiar reporte para mi developer",
    copyCopied: "Reporte tecnico copiado",
    copyFailed: "No se pudo copiar",
    copyUnavailable: "Ejecuta un scan para copiar reporte",
    clearResult: "Limpiar resultado",
    backToTop: "Volver arriba",
    recentLabel: "Checks recientes",
    recentTitle: "Checks recientes",
    recentIntro: "Guardado solo en este dispositivo. Abre un resultado guardado sin hacer una nueva consulta DNS.",
    recentShowHistory: "Mostrar historial",
    recentHideHistory: "Ocultar historial",
    recentEmpty: "Todavia no hay checks guardados. Ejecuta un scan para guardar el ultimo resultado aqui.",
    recentSavedNote: "Resultado guardado. DNS puede haber cambiado.",
    recentOpenSaved: "Abrir resultado guardado",
    recentCheckAgain: "Verificar otra vez",
    recentRemove: "Eliminar",
    recentClearHistory: "Limpiar historial",
    helpNoteResult:
      "Esto abre un formulario externo simple y completa el dominio y los problemas principales.",
    helpNoteEmpty: "Ejecuta un scan primero para activar ayuda y reporte tecnico.",
    guaranteeNote:
      "Puede ayudar con problemas visibles de autenticacion DNS, pero no garantiza inbox placement.",
    relatedLabel: "Herramientas relacionadas",
    relatedTitle: "Herramientas enfocadas, una verificacion cada vez",
    guidesLabel: "Guias",
    guidesTitle: "Guias practicas de configuracion",
    guidesIntro:
      "Estas guias explican las partes manuales que DNS publico no puede comprobar.",
    faqLabel: "FAQ",
    faqTitle: "Respuestas claras",
    disclaimer: "Disclaimer:",
    footer: "Una herramienta enfocada en SPF, DKIM, DMARC, MX y readiness para remitentes masivos.",
    noRawRecord: "No hay registro raw para mostrar en este check.",
  },
  pt: {
    language: "Idioma",
    themeLight: "Claro",
    themeDark: "Escuro",
    publicDns: "Verificacao DNS publica",
    noAccount: "Sem conta",
    noInbox: "Sem garantia de entrega",
    domain: "Dominio",
    esp: "Plataforma de envio (opcional)",
    helper:
      "Digite um dominio como example.com. Escolha uma plataforma so se souber qual e; o dominio e suficiente para comecar.",
    loading: "Consultando DNS publicos...",
    liveChecker: "Verificador ao vivo",
    runCheck: "Verificar preparacao",
    ready: "Pronto",
    needsAttention: "Precisa de atencao",
    notReady: "Nao pronto",
    resultCards: "Resultados",
    manualChecks: "Revisoes manuais",
    manualTitle: "Revisao manual obrigatoria",
    manualIntro:
      "Estes itens nao podem ser verificados apenas por DNS. Revise isso no ESP, nos headers da mensagem ou nos paineis do provedor antes de considerar uma campanha pronta.",
    bulkChecklist: "Checklist de envio em massa",
    gmailChecklistTitle: "Checklist de remetente em massa para Gmail",
    yahooChecklistTitle: "Checklist de remetente em massa para Yahoo",
    manualStatus: "manual",
    nextSteps: "Proximos passos",
    nextTitle: "Corrija primeiro o que importa",
    nextIntro:
      "O resultado comeca em linguagem simples e mantem detalhes tecnicos e registros DNS visiveis para developers e agencias.",
    howLabel: "Como funciona",
    howTitle: "O que voce pode fazer nesta pagina",
    howScanTitle: "Executar o verificador",
    howScan:
      "Digite um dominio, escolha opcionalmente a plataforma de envio e clique no botao principal. O dominio e a entrada principal.",
    howReportTitle: "Copiar relatorio tecnico",
    howReport:
      "Depois de um scan, copie o resumo e os registros para enviar a um developer ou agencia.",
    howHelpTitle: "Pedir setup assistido",
    howHelp:
      "Depois de um scan, o CTA de ajuda abre um fluxo leve de contato. Nao ha login, checkout ou dashboard.",
    helpLabel: "CTA de ajuda",
    helpTitle: "Precisa resolver isso antes da sua proxima campanha?",
    helpIntro:
      "Podemos revisar seu SPF, DKIM e DMARC e indicar exatamente quais mudancas DNS aplicar.",
    helpButton: "Precisa resolver isso antes da sua proxima campanha?",
    helpUnavailable: "Rode um scan para pedir ajuda",
    copyReport: "Copiar relatorio para meu developer",
    copyCopied: "Relatorio tecnico copiado",
    copyFailed: "Falha ao copiar",
    copyUnavailable: "Rode um scan para copiar relatorio",
    clearResult: "Limpar resultado",
    backToTop: "Voltar ao topo",
    recentLabel: "Checks recentes",
    recentTitle: "Checks recentes",
    recentIntro: "Salvo apenas neste dispositivo. Abra um resultado salvo sem fazer uma nova consulta DNS.",
    recentShowHistory: "Mostrar historico",
    recentHideHistory: "Ocultar historico",
    recentEmpty: "Ainda nao ha checks salvos. Rode um scan para guardar o ultimo resultado aqui.",
    recentSavedNote: "Resultado salvo. O DNS pode ter mudado.",
    recentOpenSaved: "Abrir resultado salvo",
    recentCheckAgain: "Verificar novamente",
    recentRemove: "Remover",
    recentClearHistory: "Limpar historico",
    helpNoteResult:
      "Isso abre um formulario externo simples e preenche dominio e principais problemas.",
    helpNoteEmpty: "Rode um scan primeiro para liberar ajuda e relatorio tecnico.",
    guaranteeNote:
      "Pode ajudar com problemas visiveis de autenticacao DNS, mas nao garante inbox placement.",
    relatedLabel: "Ferramentas relacionadas",
    relatedTitle: "Ferramentas focadas, uma verificacao por vez",
    guidesLabel: "Guias",
    guidesTitle: "Guias praticos de configuracao",
    guidesIntro:
      "Estes guias explicam as partes manuais que DNS publico nao consegue provar.",
    faqLabel: "FAQ",
    faqTitle: "Respostas claras",
    disclaimer: "Disclaimer:",
    footer: "Uma ferramenta focada em SPF, DKIM, DMARC, MX e readiness para remetentes em massa.",
    noRawRecord: "Nao ha registro raw para mostrar neste check.",
  },
} satisfies Record<Locale, Record<string, string>>;

const pageCopy: Record<Locale, Record<string, Partial<CheckerPageConfig>>> = {
  en: {},
  es: {
    "/": {
      eyebrow: "Preparacion para remitentes masivos en Gmail y Yahoo",
      h1: "Verificador de preparacion para email masivo",
      buttonLabel: "Comprobar preparacion",
      intro:
        "Comprueba si tu dominio tiene los requisitos basicos para enviar email masivo a Gmail y Yahoo. Revisa SPF, DKIM, DMARC, MX, SPF lookups y checks manuales como unsubscribe y spam rate.",
      previewSummary:
        "Ejecuta el checker para ver senales DNS automaticas y checks manuales en un solo lugar.",
      resultsHeading: "Senales DNS automaticas y checks manuales",
      resultsIntro:
        "Revisa primero el resultado general y despues inspecciona cards, confianza y registros DNS raw.",
    },
    "/spf-checker": {
      eyebrow: "Herramienta SPF",
      h1: "Verificador de registro SPF",
      buttonLabel: "Comprobar SPF",
      intro:
        "Comprueba si tu dominio publica un unico registro SPF valido, revisa el TXT raw y detecta errores comunes.",
      previewSummary: "Ejecuta el checker para inspeccionar SPF y el conteo de DNS lookups.",
      resultsHeading: "Resultado SPF enfocado",
      resultsIntro: "Esta pagina se centra en calidad de SPF y presion de DNS lookups.",
      faqs: [
        {
          question: "Puedo tener varios registros SPF?",
          answer:
            "No. Un dominio debe publicar un unico registro SPF TXT. Varios SPF pueden causar fallos de autenticacion.",
        },
        {
          question: "Que significa ~all?",
          answer:
            "~all es soft fail. Se usa a menudo mientras el remitente valida su politica SPF final.",
        },
        {
          question: "Que significa -all?",
          answer:
            "-all es hard fail. Indica que servidores fuera de la politica SPF deberian fallar SPF.",
        },
      ],
      relatedTools: [
        { href: "/dmarc-checker", label: "DMARC checker" },
        { href: "/spf-lookup-counter", label: "SPF lookup counter" },
      ],
    },
    "/dmarc-checker": {
      eyebrow: "Herramienta DMARC",
      h1: "Verificador de registro DMARC",
      buttonLabel: "Comprobar DMARC",
      intro:
        "Valida si tu dominio publica DMARC, revisa la politica activa y entiende que corregir despues.",
      previewSummary:
        "Ejecuta el checker para inspeccionar la politica DMARC publicada y el modo de enforcement.",
      resultsHeading: "Resultado DMARC enfocado",
      resultsIntro: "Esta pagina se centra en presencia de DMARC, politica y siguiente paso.",
      faqs: [
        {
          question: "Que es p=none?",
          answer:
            "p=none significa solo monitoreo. Permite recopilar reportes antes de subir el enforcement.",
        },
        {
          question: "Debo usar quarantine o reject?",
          answer:
            "Empieza con p=none, confirma que los remitentes legitimos pasan autenticacion y despues endurece la politica.",
        },
        {
          question: "DMARC requiere SPF o DKIM?",
          answer:
            "Si. DMARC depende de SPF o DKIM y de alineacion con el dominio visible en From.",
        },
      ],
      relatedTools: [
        { href: "/spf-checker", label: "SPF checker" },
        { href: "/spf-lookup-counter", label: "SPF lookup counter" },
      ],
    },
    "/mx-record-checker": {
      eyebrow: "Herramienta MX",
      h1: "Verificador de registros MX",
      buttonLabel: "Comprobar MX",
      intro:
        "Inspecciona si tu dominio recibe email correctamente, incluyendo hosts MX, prioridades y casos Null MX.",
      previewSummary:
        "Ejecuta el checker para revisar registros MX, prioridades y comportamiento Null MX.",
      resultsHeading: "Resultado MX enfocado",
      resultsIntro: "Esta pagina se centra en ruteo de email, hosts MX y dominios sin correo entrante.",
      faqs: [
        {
          question: "Que es un registro MX?",
          answer:
            "Un registro MX indica a otros sistemas de email donde entregar mensajes entrantes para tu dominio.",
        },
        {
          question: "Necesito MX para enviar email?",
          answer:
            "No siempre para enviar, pero la mayoria de dominios de negocio lo necesitan para recibir email.",
        },
        {
          question: "Por que faltan registros MX?",
          answer:
            "El dominio puede no estar configurado para recibir email o el setup del proveedor puede estar incompleto.",
        },
      ],
      relatedTools: [
        { href: "/spf-checker", label: "SPF checker" },
        { href: "/dmarc-checker", label: "DMARC checker" },
      ],
    },
    "/spf-lookup-counter": {
      eyebrow: "Herramienta SPF lookup",
      h1: "Contador de lookups SPF",
      buttonLabel: "Contar SPF lookups",
      intro:
        "Estima cuantos DNS lookups activa tu politica SPF y detecta registros cerca o por encima del limite.",
      previewSummary:
        "Ejecuta el contador para estimar SPF DNS lookups antes de llegar al limite.",
      resultsHeading: "Resultado enfocado de SPF lookups",
      resultsIntro: "Esta pagina se centra en politicas SPF pesadas y el limite de 10 lookups.",
      faqs: [
        {
          question: "Por que existe el limite de 10 lookups?",
          answer:
            "SPF tiene un limite duro de 10 DNS lookups para evitar recursion excesiva y abuso.",
        },
        {
          question: "Que cuenta como DNS lookup SPF?",
          answer:
            "include, a, mx, ptr, exists y redirect pueden consumir lookups durante la evaluacion SPF.",
        },
        {
          question: "Como reduzco los SPF lookups?",
          answer:
            "Elimina proveedores que ya no envian, evita includes duplicados y consolida servicios cuando sea posible.",
        },
      ],
      relatedTools: [
        { href: "/spf-checker", label: "SPF checker" },
        { href: "/dmarc-checker", label: "DMARC checker" },
      ],
    },
    "/bulk-email-readiness-checker": {
      eyebrow: "Preparacion DNS para remitentes masivos",
      h1: "Verificador de preparacion para email masivo",
      buttonLabel: "Comprobar preparacion",
      intro:
        "Ejecuta un check enfocado antes de una newsletter, campana o automatizacion. Revisa SPF, DKIM, DMARC, MX, SPF lookups y requisitos manuales.",
      previewSummary:
        "Ejecuta el checker para separar checks DNS automaticos de requisitos manuales de bulk sender.",
      resultsHeading: "Senales de readiness para bulk senders",
      resultsIntro:
        "Usa primero el score de autenticacion DNS y despues revisa los checks manuales antes de enviar campanas.",
    },
    "/gmail-bulk-sender-requirements": {
      eyebrow: "Checklist de requisitos de Gmail",
      h1: "Verificador de requisitos de Gmail para remitentes masivos",
      buttonLabel: "Comprobar preparacion para Gmail",
      intro:
        "Comprueba las senales DNS que Gmail espera de bulk senders y revisa requisitos manuales como unsubscribe y spam rate fuera de DNS.",
      previewSummary:
        "Ejecuta el checker para ver que requisitos de Gmail son automaticos y cuales necesitan confirmacion manual.",
      resultsHeading: "Checklist de readiness para Gmail",
      resultsIntro:
        "SPF, DKIM y DMARC pueden revisarse por DNS. Spam rate y unsubscribe necesitan revision del proveedor o del mensaje.",
    },
    "/dmarc-policy-bulk-email": {
      eyebrow: "Guia de politica DMARC",
      h1: "Politica DMARC para email masivo",
      buttonLabel: "Comprobar politica DMARC",
      intro:
        "Revisa la politica DMARC de tu dominio y entiende que significan p=none, quarantine y reject antes de campanas bulk.",
      previewSummary:
        "Ejecuta el checker para ver la politica actual y decidir si monitoreo o enforcement es el siguiente paso correcto.",
      resultsHeading: "Estado de politica DMARC y siguiente paso",
      resultsIntro:
        "Esta pagina interpreta DMARC para bulk sending. SPF y DKIM siguen importando, pero aqui la pregunta principal es la politica DMARC.",
    },
    "/guides/mailchimp-gmail-compliance": {
      eyebrow: "Guia de setup Mailchimp",
      h1: "Guia de cumplimiento de Gmail para Mailchimp",
      buttonLabel: "Comprobar configuracion de Mailchimp",
      intro:
        "Usa esta guia si envias campanas desde Mailchimp y quieres confirmar DNS basico mas los checks manuales de Gmail.",
      previewSummary:
        "Ejecuta el checker con Mailchimp seleccionado para revisar DKIM, DMARC, SPF, MX y checks manuales.",
      resultsHeading: "Readiness del dominio para Mailchimp",
      resultsIntro:
        "Esta pagina reutiliza el checker principal, pero encuadra el resultado alrededor de Mailchimp y requisitos de Gmail.",
    },
  },
  pt: {
    "/": {
      eyebrow: "Preparacao para remetentes em massa no Gmail e Yahoo",
      h1: "Verificador de preparacao para email em massa",
      buttonLabel: "Verificar preparacao",
      intro:
        "Verifique se seu dominio tem os requisitos basicos para envio em massa para Gmail e Yahoo. Revise SPF, DKIM, DMARC, MX, SPF lookups e checks manuais como unsubscribe e spam rate.",
      previewSummary:
        "Rode o checker para ver sinais DNS automaticos e checks manuais em um so lugar.",
      resultsHeading: "Sinais DNS automaticos e checks manuais",
      resultsIntro:
        "Revise primeiro o resultado geral e depois inspecione cards, confianca e registros DNS raw.",
    },
    "/spf-checker": {
      eyebrow: "Ferramenta SPF",
      h1: "Verificador de registro SPF",
      buttonLabel: "Verificar SPF",
      intro:
        "Verifique se seu dominio publica um unico registro SPF valido, veja o TXT raw e encontre erros comuns.",
      previewSummary: "Rode o checker para inspecionar SPF e a estimativa de DNS lookups.",
      resultsHeading: "Resultado SPF focado",
      resultsIntro: "Esta pagina fica focada na qualidade do SPF e no limite de DNS lookups.",
      faqs: [
        {
          question: "Posso ter varios registros SPF?",
          answer:
            "Nao. Um dominio deve publicar um unico registro SPF TXT. Varios SPF podem causar falhas de autenticacao.",
        },
        {
          question: "O que significa ~all?",
          answer:
            "~all e soft fail. E comum enquanto o remetente ainda valida a politica SPF final.",
        },
        {
          question: "O que significa -all?",
          answer:
            "-all e hard fail. Indica que emails de servidores fora da politica SPF devem falhar SPF.",
        },
      ],
      relatedTools: [
        { href: "/dmarc-checker", label: "DMARC checker" },
        { href: "/spf-lookup-counter", label: "SPF lookup counter" },
      ],
    },
    "/dmarc-checker": {
      eyebrow: "Ferramenta DMARC",
      h1: "Verificador de registro DMARC",
      buttonLabel: "Verificar DMARC",
      intro:
        "Valide se seu dominio publica DMARC, veja a politica ativa e entenda o proximo ajuste.",
      previewSummary:
        "Rode o checker para inspecionar a politica DMARC publicada e o modo de enforcement.",
      resultsHeading: "Resultado DMARC focado",
      resultsIntro: "Esta pagina fica focada em presenca de DMARC, politica e proximo passo.",
      faqs: [
        {
          question: "O que e p=none?",
          answer:
            "p=none significa apenas monitoramento. Permite coletar relatorios antes de aumentar o enforcement.",
        },
        {
          question: "Devo usar quarantine ou reject?",
          answer:
            "Comece com p=none, confirme que remetentes legitimos passam autenticacao e depois endureca a politica.",
        },
        {
          question: "DMARC exige SPF ou DKIM?",
          answer:
            "Sim. DMARC depende de SPF ou DKIM e de alinhamento com o dominio visivel no From.",
        },
      ],
      relatedTools: [
        { href: "/spf-checker", label: "SPF checker" },
        { href: "/spf-lookup-counter", label: "SPF lookup counter" },
      ],
    },
    "/mx-record-checker": {
      eyebrow: "Ferramenta MX",
      h1: "Verificador de registros MX",
      buttonLabel: "Verificar MX",
      intro:
        "Inspecione se seu dominio recebe email corretamente, incluindo hosts MX, prioridades e casos Null MX.",
      previewSummary:
        "Rode o checker para revisar registros MX, prioridades e comportamento Null MX.",
      resultsHeading: "Resultado MX focado",
      resultsIntro: "Esta pagina fica focada em roteamento de email, hosts MX e dominios sem email de entrada.",
      faqs: [
        {
          question: "O que e um registro MX?",
          answer:
            "Um registro MX informa a outros sistemas de email onde entregar mensagens recebidas para seu dominio.",
        },
        {
          question: "Preciso de MX para enviar email?",
          answer:
            "Nem sempre para enviar, mas a maioria dos dominios de negocio precisa de MX para receber email.",
        },
        {
          question: "Por que faltam registros MX?",
          answer:
            "O dominio pode nao estar configurado para receber email ou o setup do provedor pode estar incompleto.",
        },
      ],
      relatedTools: [
        { href: "/spf-checker", label: "SPF checker" },
        { href: "/dmarc-checker", label: "DMARC checker" },
      ],
    },
    "/spf-lookup-counter": {
      eyebrow: "Ferramenta SPF lookup",
      h1: "Contador de lookups SPF",
      buttonLabel: "Contar SPF lookups",
      intro:
        "Estime quantos DNS lookups sua politica SPF aciona e identifique registros perto ou acima do limite.",
      previewSummary:
        "Rode o contador para estimar SPF DNS lookups antes de atingir o limite.",
      resultsHeading: "Resultado focado de SPF lookups",
      resultsIntro: "Esta pagina fica focada em politicas SPF pesadas e no limite de 10 lookups.",
      faqs: [
        {
          question: "Por que existe o limite de 10 lookups?",
          answer:
            "SPF tem um limite rigido de 10 DNS lookups para evitar recursao excessiva e abuso.",
        },
        {
          question: "O que conta como DNS lookup SPF?",
          answer:
            "include, a, mx, ptr, exists e redirect podem consumir lookups durante a avaliacao SPF.",
        },
        {
          question: "Como reduzo os SPF lookups?",
          answer:
            "Remova provedores que nao enviam mais, evite includes duplicados e consolide servicos quando possivel.",
        },
      ],
      relatedTools: [
        { href: "/spf-checker", label: "SPF checker" },
        { href: "/dmarc-checker", label: "DMARC checker" },
      ],
    },
    "/bulk-email-readiness-checker": {
      eyebrow: "Preparacao DNS para remetentes em massa",
      h1: "Verificador de preparacao para email em massa",
      buttonLabel: "Verificar preparacao",
      intro:
        "Rode um check focado antes de uma newsletter, campanha ou automacao. Revise SPF, DKIM, DMARC, MX, SPF lookups e requisitos manuais.",
      previewSummary:
        "Rode o checker para separar checks DNS automaticos de requisitos manuais de bulk sender.",
      resultsHeading: "Sinais de readiness para bulk senders",
      resultsIntro:
        "Use primeiro o score de autenticacao DNS e depois revise os checks manuais antes de enviar campanhas.",
    },
    "/gmail-bulk-sender-requirements": {
      eyebrow: "Checklist de requisitos do Gmail",
      h1: "Verificador de requisitos do Gmail para remetentes em massa",
      buttonLabel: "Verificar preparacao para Gmail",
      intro:
        "Confira os sinais DNS que o Gmail espera de bulk senders e revise requisitos manuais como unsubscribe e spam rate fora do DNS.",
      previewSummary:
        "Rode o checker para ver quais requisitos do Gmail sao automaticos e quais precisam de confirmacao manual.",
      resultsHeading: "Checklist de readiness para Gmail",
      resultsIntro:
        "SPF, DKIM e DMARC podem ser revisados via DNS. Spam rate e unsubscribe precisam de revisao no provedor ou na mensagem.",
    },
    "/dmarc-policy-bulk-email": {
      eyebrow: "Guia de politica DMARC",
      h1: "Politica DMARC para email em massa",
      buttonLabel: "Verificar politica DMARC",
      intro:
        "Revise a politica DMARC do seu dominio e entenda p=none, quarantine e reject antes de campanhas bulk.",
      previewSummary:
        "Rode o checker para ver a politica atual e decidir se monitoramento ou enforcement e o proximo passo correto.",
      resultsHeading: "Estado da politica DMARC e proximo passo",
      resultsIntro:
        "Esta pagina interpreta DMARC para bulk sending. SPF e DKIM ainda importam, mas aqui a pergunta principal e a politica DMARC.",
    },
    "/guides/mailchimp-gmail-compliance": {
      eyebrow: "Guia de setup Mailchimp",
      h1: "Guia de conformidade do Gmail para Mailchimp",
      buttonLabel: "Verificar configuracao do Mailchimp",
      intro:
        "Use este guia se voce envia campanhas pelo Mailchimp e quer confirmar DNS basico mais os checks manuais do Gmail.",
      previewSummary:
        "Rode o checker com Mailchimp selecionado para revisar DKIM, DMARC, SPF, MX e checks manuais.",
      resultsHeading: "Readiness do dominio para Mailchimp",
      resultsIntro:
        "Esta pagina reutiliza o checker principal, mas enquadra o resultado em Mailchimp e requisitos do Gmail.",
    },
  },
};

const espProviders = [
  { id: "", name: "I do not know / Other" },
  { id: "mailchimp", name: "Mailchimp" },
  { id: "brevo", name: "Brevo" },
  { id: "klaviyo", name: "Klaviyo" },
  { id: "sendgrid", name: "SendGrid" },
  { id: "mailgun", name: "Mailgun" },
  { id: "resend", name: "Resend" },
  { id: "amazon_ses", name: "Amazon SES" },
  { id: "hubspot", name: "HubSpot" },
];

function StatusIcon({ tone }: { tone: "ok" | "warn" | "error" }) {
  if (tone === "ok") {
    return <CheckCircle2 aria-hidden="true" />;
  }

  if (tone === "error") {
    return <XCircle aria-hidden="true" />;
  }

  return <AlertTriangle aria-hidden="true" />;
}

function loadRecentChecks(): RecentCheckItem[] {
  if (typeof window === "undefined") {
    return [];
  }

  const now = Date.now();
  try {
    const raw = window.localStorage.getItem(RECENT_CHECKS_STORAGE_KEY);
    if (!raw) {
      return [];
    }

    const parsed = JSON.parse(raw) as RecentCheckItem[];
    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed
      .filter((item) => item && typeof item.savedAt === "string")
      .filter((item) => now - new Date(item.savedAt).getTime() <= RECENT_CHECKS_TTL_MS)
      .slice(0, RECENT_CHECKS_LIMIT);
  } catch {
    return [];
  }
}

function saveRecentChecks(items: RecentCheckItem[]) {
  if (typeof window === "undefined") {
    return;
  }

  try {
    window.localStorage.setItem(RECENT_CHECKS_STORAGE_KEY, JSON.stringify(items));
  } catch {
    // Ignore storage failures in the browser; history is a convenience only.
  }
}

function dedupeRecentChecks(items: RecentCheckItem[]) {
  const seen = new Set<string>();
  const deduped: RecentCheckItem[] = [];

  for (const item of items) {
    const key = `${item.domain}|${item.espProvider || ""}|${item.path}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    deduped.push(item);
  }

  return deduped.slice(0, RECENT_CHECKS_LIMIT);
}

function contextualStatusLabel(status: AggregateResult["status"], config: CheckerPageConfig) {
  return config.statusLabels[status];
}

function contextualHelpButtonLabel(locale: Locale, espProvider: string) {
  if (locale === "en") {
    if (espProvider === "mailchimp") {
      return "Need help fixing Mailchimp domain authentication?";
    }
    if (espProvider === "brevo") {
      return "Need help fixing Brevo SPF/DKIM/DMARC?";
    }
    if (espProvider === "sendgrid") {
      return "Need help fixing SendGrid domain authentication?";
    }
    return chromeCopy.en.helpButton;
  }

  if (locale === "es") {
    if (espProvider === "mailchimp") {
      return "Necesitas ayuda con la autenticacion de dominio en Mailchimp?";
    }
    if (espProvider === "brevo") {
      return "Necesitas ayuda con SPF/DKIM/DMARC en Brevo?";
    }
    if (espProvider === "sendgrid") {
      return "Necesitas ayuda con la autenticacion de dominio en SendGrid?";
    }
    return "Necesitas ayuda para corregirlo?";
  }

  if (espProvider === "mailchimp") {
    return "Precisa de ajuda com a autenticacao de dominio no Mailchimp?";
  }
  if (espProvider === "brevo") {
    return "Precisa de ajuda com SPF/DKIM/DMARC no Brevo?";
  }
  if (espProvider === "sendgrid") {
    return "Precisa de ajuda com a autenticacao de dominio no SendGrid?";
  }
  return "Precisa de ajuda para corrigir isso?";
}

function ScoreFlags({ result, locale }: { result: AggregateResult; locale: Locale }) {
  const topFlags = result.checks
    .filter((check) => check.status !== "ok")
    .slice(0, 2)
    .map((check) => `${check.checkName}: ${check.summary}`);

  if (topFlags.length === 0) {
    topFlags.push(
      locale === "es"
        ? "Checks DNS principales saludables"
        : locale === "pt"
          ? "Checks DNS principais saudaveis"
          : "Core DNS checks look healthy",
      locale === "es"
        ? "Listo para la siguiente revision"
        : locale === "pt"
          ? "Pronto para a proxima revisao"
          : "Ready for the next review step",
    );
  }

  return (
    <div className="score-flags">
      {topFlags.map((flag) => (
        <span key={flag}>
          <ShieldCheck aria-hidden="true" />
          {flag}
        </span>
      ))}
    </div>
  );
}

function ManualChecksPanel({
  checks,
  copy,
}: {
  checks: ManualCheckResult[];
  copy: typeof chromeCopy.en;
}) {
  if (checks.length === 0) {
    return null;
  }

  return (
    <section className="manual-band">
      <div className="shell">
        <div className="section-heading">
          <p className="eyebrow">{copy.manualChecks}</p>
          <h2>{copy.manualTitle}</h2>
          <p>{copy.manualIntro}</p>
        </div>
        <div className="manual-grid">
          {checks.map((check) => (
            <article className="manual-card" key={check.checkName}>
              <div className="card-title">
                <AlertTriangle aria-hidden="true" />
                <div>
                  <h3>{check.checkName}</h3>
                  <span>{check.summary}</span>
                </div>
              </div>
              <p>{check.whyItMatters}</p>
              <p>{check.howToVerify}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function BulkChecklistPanel({
  title,
  items,
  label,
  manualStatus,
}: {
  title: string;
  items: BulkComplianceItem[];
  label: string;
  manualStatus: string;
}) {
  if (items.length === 0) {
    return null;
  }

  return (
    <section className="checklist-band">
      <div className="shell">
        <div className="section-heading">
          <p className="eyebrow">{label}</p>
          <h2>{title}</h2>
        </div>
        <div className="checklist-list">
          {items.map((item) => (
            <article key={`${item.provider}-${item.item}`}>
              <span className={`checklist-status ${toneFromStatus(item.status)}`}>
                {item.status === "manual_check" ? manualStatus : item.status.replace("_", " ")}
              </span>
              <div>
                <h3>{item.item}</h3>
                <p>{item.explanation}</p>
                {item.howToVerify ? <p>{item.howToVerify}</p> : null}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

export function DomainChecker({ config }: { config: CheckerPageConfig }) {
  const [locale, setLocale] = useState<Locale>("en");
  const [theme, setTheme] = useState<Theme>("light");
  const [apiBaseUrl, setApiBaseUrl] = useState(API_BASE_URL);
  const [domain, setDomain] = useState("");
  const [espProvider, setEspProvider] = useState(
    config.pathname === "/guides/mailchimp-gmail-compliance" ? "mailchimp" : "",
  );
  const [result, setResult] = useState<AggregateResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [copyLabel, setCopyLabel] = useState(chromeCopy.en.copyReport);
  const [showBackToTop, setShowBackToTop] = useState(false);
  const [recentChecks, setRecentChecks] = useState<RecentCheckItem[]>([]);
  const [recentChecksExpanded, setRecentChecksExpanded] = useState(false);
  const [showAllRecentChecks, setShowAllRecentChecks] = useState(false);

  const effectiveLocale: Locale = SHOW_LOCALE_SELECTOR ? locale : "en";
  const copy = chromeCopy[effectiveLocale];
  const localizedConfig = {
    ...config,
    ...(pageCopy[effectiveLocale][config.pathname] ?? {}),
  };
  const activeHelpLabel = result
    ? contextualHelpButtonLabel(effectiveLocale, espProvider)
    : copy.helpUnavailable;

  useEffect(() => {
    if (SHOW_LOCALE_SELECTOR) {
      const savedLocale = window.localStorage.getItem("mailauthcheck.locale");
      if (savedLocale === "en" || savedLocale === "es" || savedLocale === "pt") {
        setLocale(savedLocale);
      }
    } else {
      setLocale("en");
    }

    const savedTheme = window.localStorage.getItem("mailauthcheck.theme");
    if (savedTheme === "light" || savedTheme === "dark") {
      setTheme(savedTheme);
    }
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("mailauthcheck.theme", theme);
  }, [theme]);

  useEffect(() => {
    setApiBaseUrl(resolveRuntimeApiBaseUrl(API_BASE_URL));
  }, []);

  useEffect(() => {
    const nextLocale = SHOW_LOCALE_SELECTOR ? locale : "en";
    window.localStorage.setItem("mailauthcheck.locale", nextLocale);
    setCopyLabel(chromeCopy[nextLocale].copyReport);
  }, [locale]);

  useEffect(() => {
    setRecentChecks(loadRecentChecks());
  }, []);

  useEffect(() => {
    setShowAllRecentChecks(false);
  }, [recentChecks.length]);

  useEffect(() => {
    const onScroll = () => {
      setShowBackToTop(window.scrollY > 520);
    };

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const scoreTone = useMemo(() => {
    if (!result) {
      return localizedConfig.placeholderResult.score;
    }
    return Math.max(0, Math.min(100, result.score));
  }, [localizedConfig.placeholderResult.score, result]);

  const displayResult = result ?? localizedConfig.placeholderResult;
  const displayedChecks = displayResult.automatedChecks ?? displayResult.checks;
  const manualChecks = displayResult.manualChecks ?? [];
  const gmailChecklist = displayResult.gmailBulkChecklist ?? [];
  const yahooChecklist = displayResult.yahooBulkChecklist ?? [];
  const leadCaptureUrl = result
    ? buildLeadCaptureUrl(result, espProvider || undefined, {
        buttonLabel: contextualHelpButtonLabel(effectiveLocale, espProvider),
        toolName: localizedConfig.reportToolName,
        toolPath: config.pathname,
      })
    : null;
  const leadCaptureChannel =
    leadCaptureUrl?.startsWith("mailto:") ? "mailto" : leadCaptureUrl ? "external_form" : null;
  const visibleRecentChecks = showAllRecentChecks ? recentChecks : recentChecks.slice(0, 3);
  const hiddenRecentChecks = Math.max(0, recentChecks.length - visibleRecentChecks.length);

  function persistRecentCheck(nextResult: AggregateResult) {
    const savedAt = new Date().toISOString();
    const nextItem: RecentCheckItem = {
      id: `${nextResult.domain}|${espProvider || ""}|${config.pathname}`,
      domain: nextResult.domain,
      espProvider: espProvider || null,
      path: config.pathname,
      resultSnapshot: nextResult,
      savedAt,
      source: "api_result",
    };

    setRecentChecks((current) => {
      const nextItems = [
        nextItem,
        ...current.filter(
          (item) =>
            !(item.domain === nextItem.domain && item.espProvider === nextItem.espProvider && item.path === nextItem.path),
        ),
      ];
      const pruned = dedupeRecentChecks(
        nextItems.filter((item) => Date.now() - new Date(item.savedAt).getTime() <= RECENT_CHECKS_TTL_MS),
      );
      saveRecentChecks(pruned);
      return pruned;
    });
  }

  function openRecentCheck(item: RecentCheckItem) {
    setResult(item.resultSnapshot);
    setErrorMessage(null);
    setDomain(item.domain);
    setEspProvider(item.espProvider || "");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function removeRecentCheck(id: string) {
    setRecentChecks((current) => {
      const nextItems = current.filter((item) => item.id !== id);
      saveRecentChecks(nextItems);
      return nextItems;
    });
  }

  function clearRecentChecks() {
    setRecentChecks([]);
    setShowAllRecentChecks(false);
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(RECENT_CHECKS_STORAGE_KEY);
    }
  }

  function toggleRecentChecksExpanded() {
    setRecentChecksExpanded((value) => {
      const nextExpanded = !value;
      if (!nextExpanded) {
        setShowAllRecentChecks(false);
      }
      return nextExpanded;
    });
    if (recentChecksExpanded) {
      setShowAllRecentChecks(false);
    }
  }

  async function runCheck(nextDomain: string, nextEspProvider: string, nextSource: "form" | "history") {
    const normalizedDomain = nextDomain.trim().toLowerCase();
    trackEvent("scan_started", {
      tool: config.pathname,
      domain_entered: normalizedDomain.length > 0,
      esp_selected: nextEspProvider.length > 0,
      esp_provider: nextEspProvider || null,
      source: nextSource,
    });
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const requestUrl =
        config.apiPath === "/api/check-domain"
          ? `${apiBaseUrl}${config.apiPath}`
          : `${apiBaseUrl}${config.apiPath}?domain=${encodeURIComponent(normalizedDomain)}`;

      const response = await fetch(
        requestUrl,
        config.apiPath === "/api/check-domain"
          ? {
              method: "POST",
              headers: {
                "content-type": "application/json",
              },
              body: JSON.stringify({
                domain: nextDomain,
                mode: "bulk_sender",
                espProvider: nextEspProvider || null,
              }),
            }
          : undefined,
      );

      const payload = (await response.json()) as
        | AggregateResult
        | CheckListResult
        | ErrorResult;

      if (!response.ok) {
        setResult(null);
        const errorText =
          response.status === 429
            ? "You reached the temporary rate limit. You can open a saved result below if one exists."
            : "message" in payload
              ? payload.message
              : "The DNS check could not be completed right now.";
        setErrorMessage(errorText);
        trackEvent("scan_failed", {
          tool: config.pathname,
          domain: normalizedDomain || null,
          error:
            "error" in payload && typeof payload.error === "string"
              ? payload.error
              : "request_failed",
          status_code: response.status,
          source: nextSource,
        });
        return;
      }

      if ("score" in payload) {
        const aggregateResult = payload as AggregateResult;
        setResult(aggregateResult);
        persistRecentCheck(aggregateResult);
        trackEvent("scan_completed", {
          tool: config.pathname,
          domain: aggregateResult.domain,
          status: aggregateResult.status,
          score: aggregateResult.score,
          esp_provider: nextEspProvider || null,
          source: nextSource,
        });
      } else {
        const normalizedResult = normalizeCheckListResult(payload as CheckListResult);
        setResult(normalizedResult);
        persistRecentCheck(normalizedResult);
        trackEvent("scan_completed", {
          tool: config.pathname,
          domain: normalizedResult.domain,
          status: normalizedResult.status,
          score: normalizedResult.score,
          esp_provider: nextEspProvider || null,
          source: nextSource,
        });
      }
    } catch {
      setResult(null);
      setErrorMessage(
        "The checker could not reach the API. Make sure the FastAPI service is running.",
      );
      trackEvent("scan_failed", {
        tool: config.pathname,
        domain: normalizedDomain || null,
        error: "network_error",
        esp_provider: nextEspProvider || null,
        source: nextSource,
      });
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runCheck(domain, espProvider, "form");
  }

  async function handleCopyReport() {
    if (!result) {
      return;
    }

    const report = buildDeveloperReport(result, {
      toolName: localizedConfig.reportToolName,
      scope: localizedConfig.reportScope,
      statusLabels: localizedConfig.statusLabels,
    });

    try {
      if (!navigator.clipboard?.writeText) {
        throw new Error("clipboard_unavailable");
      }

      await navigator.clipboard.writeText(report);
      setCopyLabel(copy.copyCopied);
      window.setTimeout(() => setCopyLabel(copy.copyReport), 1800);
      trackEvent("cta_clicked", {
        tool: config.pathname,
        cta: "send_to_dev",
        cta_type: "copy_report",
        domain: result.domain,
        status: result.status,
      });
      trackEvent("cta_send_to_dev_clicked", {
        tool: config.pathname,
        cta_type: "copy_report",
        domain: result.domain,
        status: result.status,
      });
    } catch {
      setCopyLabel(copy.copyFailed);
      window.setTimeout(() => setCopyLabel(copy.copyReport), 1800);
      trackEvent("cta_clicked", {
        tool: config.pathname,
        cta: "send_to_dev",
        cta_type: "copy_report",
        domain: result.domain,
        status: result.status,
        outcome: "copy_failed",
      });
    }
  }

  function handleHelpClick() {
    if (!result) {
      return;
    }

    trackEvent("cta_clicked", {
      tool: config.pathname,
      cta: "help",
      cta_type: "assisted_setup",
      domain: result.domain,
      status: result.status,
      lead_channel: leadCaptureChannel,
      esp_provider: espProvider || null,
    });
    trackEvent("cta_help_clicked", {
      tool: config.pathname,
      cta_type: "assisted_setup",
      domain: result.domain,
      status: result.status,
      lead_channel: leadCaptureChannel,
      esp_provider: espProvider || null,
    });
    trackEvent("lead_form_started", {
      tool: config.pathname,
      domain: result.domain,
      status: result.status,
      lead_channel: leadCaptureChannel,
      esp_provider: espProvider || null,
    });
  }

  function handleClearResult() {
    setResult(null);
    setErrorMessage(null);
    setCopyLabel(copy.copyReport);
    trackEvent("cta_clicked", {
      tool: config.pathname,
      cta: "clear_result",
      cta_type: "reset_result",
      had_result: Boolean(result),
      had_error: Boolean(errorMessage),
    });
  }

  function refreshRecentCheck(item: RecentCheckItem) {
    void runCheck(item.domain, item.espProvider || "", "history");
  }

  function handleBackToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <main>
      <section className="hero">
        <div className="shell hero-grid">
          <div className="hero-copy">
            <div className="topbar">
              <Link className="brand" href="/" aria-label="MailAuthCheck home">
                <MailCheck aria-hidden="true" />
                <span>MailAuthCheck</span>
              </Link>
              <div className="site-controls" aria-label="Site preferences">
                {SHOW_LOCALE_SELECTOR ? (
                  <div className="segmented" aria-label={copy.language}>
                    {(Object.keys(localeLabels) as Locale[]).map((item) => (
                      <button
                        type="button"
                        key={item}
                        className={item === locale ? "active" : undefined}
                        aria-pressed={item === locale}
                        onClick={() => setLocale(item)}
                      >
                        {localeLabels[item]}
                      </button>
                    ))}
                  </div>
                ) : null}
                <button
                  type="button"
                  className="theme-toggle"
                  aria-label={theme === "dark" ? copy.themeLight : copy.themeDark}
                  onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                >
                  {theme === "dark" ? <Sun aria-hidden="true" /> : <Moon aria-hidden="true" />}
                  <span>{theme === "dark" ? copy.themeLight : copy.themeDark}</span>
                </button>
              </div>
            </div>
            <p className="eyebrow">{localizedConfig.eyebrow}</p>
            <h1>{localizedConfig.h1}</h1>
            <p className="hero-text">{localizedConfig.intro}</p>

            <div className="trust-strip" aria-label="Product guardrails">
              <span>
                <ShieldCheck aria-hidden="true" />
                {copy.publicDns}
              </span>
              <span>
                <CheckCircle2 aria-hidden="true" />
                {copy.noAccount}
              </span>
              <span>
                <AlertTriangle aria-hidden="true" />
                {copy.noInbox}
              </span>
            </div>

            <form className="domain-form" aria-label="Domain checker" onSubmit={handleSubmit}>
              <label htmlFor="domain">{copy.domain}</label>
              <div className={`input-row ${localizedConfig.showEspSelector ? "" : "single-input"}`}>
                <input
                  id="domain"
                  name="domain"
                  placeholder="example.com"
                  value={domain}
                  onChange={(event) => setDomain(event.target.value)}
                />
                {localizedConfig.showEspSelector ? (
                  <select
                    id="espProvider"
                    name="espProvider"
                    aria-label={copy.esp}
                    value={espProvider}
                    onChange={(event) => setEspProvider(event.target.value)}
                  >
                    {espProviders.map((provider) => (
                      <option key={provider.id || "unknown"} value={provider.id}>
                        {provider.name}
                      </option>
                    ))}
                  </select>
                ) : null}
                <button type="submit" disabled={isLoading}>
                  {isLoading ? <LoaderCircle aria-hidden="true" className="spin" /> : null}
                  <span>{isLoading ? copy.loading : localizedConfig.buttonLabel}</span>
                  {!isLoading ? <ArrowRight aria-hidden="true" /> : null}
                </button>
              </div>
              <p>
                {errorMessage ?? copy.helper}
              </p>
              {result || errorMessage ? (
                <div className="result-actions">
                  <button
                    className="clear-result-button"
                    type="button"
                    onClick={handleClearResult}
                    disabled={isLoading}
                  >
                    <Eraser aria-hidden="true" />
                    {copy.clearResult}
                  </button>
                </div>
              ) : null}
            </form>

            <section className={`recent-checks ${recentChecksExpanded ? "expanded" : "collapsed"}`} aria-label="Recent checks">
              <div className="recent-header">
                <div className="section-heading">
                  <p className="eyebrow">{copy.recentLabel}</p>
                  <h2>{copy.recentTitle}</h2>
                  <p>{copy.recentIntro}</p>
                </div>
                <button
                  type="button"
                  className="recent-toggle"
                  onClick={toggleRecentChecksExpanded}
                  aria-expanded={recentChecksExpanded}
                >
                  {recentChecksExpanded ? copy.recentHideHistory : copy.recentShowHistory}
                </button>
              </div>
              <div className="recent-checks-body" aria-hidden={!recentChecksExpanded}>
                {recentChecks.length === 0 ? (
                  <p className="recent-empty">{copy.recentEmpty}</p>
                ) : (
                  <div className="recent-list">
                    {visibleRecentChecks.map((item) => (
                      <article className="recent-item" key={item.id}>
                        <div className="recent-item-copy">
                          <h3>{item.domain}</h3>
                          <p className="recent-meta">
                            {item.espProvider ? item.espProvider : "No ESP selected"} · {new Date(item.savedAt).toLocaleString()}
                          </p>
                          <p className="recent-summary">
                            Status: {item.resultSnapshot.status} · Score: {item.resultSnapshot.score}
                          </p>
                          <p className="recent-saved-note">{copy.recentSavedNote}</p>
                        </div>
                        <div className="recent-actions">
                          <button type="button" onClick={() => openRecentCheck(item)}>
                            {copy.recentOpenSaved}
                          </button>
                          <button type="button" onClick={() => refreshRecentCheck(item)}>
                            {copy.recentCheckAgain}
                          </button>
                          <button type="button" onClick={() => removeRecentCheck(item.id)}>
                            {copy.recentRemove}
                          </button>
                        </div>
                      </article>
                    ))}
                  </div>
                )}
                {hiddenRecentChecks > 0 ? (
                  <button
                    type="button"
                    className="recent-show-more"
                    onClick={() => setShowAllRecentChecks((value) => !value)}
                  >
                    {showAllRecentChecks ? "Show fewer" : `Show ${hiddenRecentChecks} more`}
                  </button>
                ) : null}
                {recentChecks.length > 0 ? (
                  <button type="button" className="clear-history-button" onClick={clearRecentChecks}>
                    {copy.recentClearHistory}
                  </button>
                ) : null}
              </div>
            </section>
          </div>

          <aside className="score-panel" aria-label="Scan result">
            <div className="score-topline">
              <span>{result ? result.domain : copy.liveChecker}</span>
              <strong>
                {result ? contextualStatusLabel(result.status, localizedConfig) : copy.runCheck}
              </strong>
            </div>
            <div
              className="score-ring"
              aria-label={`Score ${result ? `${result.score} out of 100` : "not available yet"}`}
              style={
                {
                  "--score-progress": `${scoreTone}%`,
                } as CSSProperties
              }
            >
              <span>{result ? result.score : "?"}</span>
              <small>{result ? "/100" : "score"}</small>
            </div>
            <p>
              {result
                ? result.summary
                : localizedConfig.previewSummary}
            </p>
            <ScoreFlags result={displayResult} locale={effectiveLocale} />
          </aside>
        </div>
      </section>

      <section className="results-band">
        <div className="shell">
          <div className="section-heading">
            <p className="eyebrow">{copy.resultCards}</p>
            <h2>{localizedConfig.resultsHeading}</h2>
            <p>{localizedConfig.resultsIntro}</p>
          </div>

          <div className="cards-grid">
            {displayedChecks.map((check) => {
              const tone = toneFromStatus(check.status);
              return (
                <article className={`check-card ${tone}`} key={check.checkName}>
                  <div className="card-title">
                    <StatusIcon tone={tone} />
                    <div>
                      <h3>{check.checkName}</h3>
                      <span>{check.summary}</span>
                    </div>
                  </div>
                  <p>{check.technicalDetails ?? check.summary}</p>
                  <span className="raw-record-label">Raw DNS record</span>
                  {check.rawRecords.length > 0 ? (
                    <code>{check.rawRecords.join("\n")}</code>
                  ) : (
                    <p className="raw-record-empty">{copy.noRawRecord}</p>
                  )}
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <ManualChecksPanel checks={manualChecks} copy={copy} />

      <BulkChecklistPanel
        title={copy.gmailChecklistTitle}
        items={gmailChecklist}
        label={copy.bulkChecklist}
        manualStatus={copy.manualStatus}
      />

      <BulkChecklistPanel
        title={copy.yahooChecklistTitle}
        items={yahooChecklist}
        label={copy.bulkChecklist}
        manualStatus={copy.manualStatus}
      />

      <section className="next-steps">
        <div className="shell steps-grid">
          <div>
            <p className="eyebrow">{copy.nextSteps}</p>
            <h2>{copy.nextTitle}</h2>
            <p>{copy.nextIntro}</p>
          </div>
          <ol>
            {displayResult.nextSteps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </div>
      </section>

      <section className="how-band">
        <div className="shell">
          <div className="section-heading">
            <p className="eyebrow">{copy.howLabel}</p>
            <h2>{copy.howTitle}</h2>
          </div>
          <div className="how-grid">
            <article>
              <CheckCircle2 aria-hidden="true" />
              <h3>{copy.howScanTitle}</h3>
              <p>{copy.howScan}</p>
            </article>
            <article>
              <Copy aria-hidden="true" />
              <h3>{copy.howReportTitle}</h3>
              <p>{copy.howReport}</p>
            </article>
            <article>
              <Wrench aria-hidden="true" />
              <h3>{copy.howHelpTitle}</h3>
              <p>{copy.howHelp}</p>
            </article>
          </div>
        </div>
      </section>

      <section className="help-band">
        <div className="shell help-grid">
          <div>
            <p className="eyebrow">{copy.helpLabel}</p>
            <h2>{copy.helpTitle}</h2>
            <p>{copy.helpIntro}</p>
          </div>
          <div className="cta-actions">
            {result && leadCaptureUrl ? (
              <a
                href={leadCaptureUrl}
                target="_blank"
                rel="noreferrer"
                onClick={handleHelpClick}
              >
                <Wrench aria-hidden="true" />
                {activeHelpLabel}
              </a>
            ) : (
              <button className="inactive-action" type="button" disabled>
                <Wrench aria-hidden="true" />
                {activeHelpLabel}
              </button>
            )}
            <button
              className="secondary"
              type="button"
              onClick={handleCopyReport}
              disabled={!result}
            >
              <Copy aria-hidden="true" />
              {result ? copyLabel : copy.copyUnavailable}
            </button>
          </div>
          <p className="cta-note">
            {result ? copy.helpNoteResult : copy.helpNoteEmpty}
          </p>
          <p className="cta-note">{copy.guaranteeNote}</p>
        </div>
      </section>

      <section className="tools-band">
        <div className="shell">
          <div className="section-heading">
            <p className="eyebrow">{copy.relatedLabel}</p>
            <h2>{copy.relatedTitle}</h2>
          </div>
          <div className="link-grid">
            {config.relatedTools.map((tool) => (
              <Link className="tool-link" href={tool.href} key={tool.href}>
                <span>{tool.label}</span>
                <ArrowRight aria-hidden="true" />
              </Link>
            ))}
          </div>
        </div>
      </section>

      {config.guidePreviews.length > 0 ? (
        <section className="guides-band">
          <div className="shell">
            <div className="section-heading">
              <p className="eyebrow">{copy.guidesLabel}</p>
              <h2>{copy.guidesTitle}</h2>
              <p>{copy.guidesIntro}</p>
            </div>
            <div className="guides-grid">
              {config.guidePreviews.map((guide) => (
                <article className="guide-card" key={guide.title}>
                  <h3>{guide.title}</h3>
                  <p>{guide.summary}</p>
                </article>
              ))}
            </div>
          </div>
        </section>
      ) : null}

      <section className="faq-band">
        <div className="shell">
          <div className="section-heading">
            <p className="eyebrow">{copy.faqLabel}</p>
            <h2>{copy.faqTitle}</h2>
          </div>
          <div className="faq-list">
            {config.faqs.map((faq) => (
              <article key={faq.question}>
                <CircleHelp aria-hidden="true" />
                <div>
                  <h3>{faq.question}</h3>
                  <p>{faq.answer}</p>
                </div>
              </article>
            ))}
          </div>
          <p className="disclaimer">
            {copy.disclaimer} {displayResult.disclaimer}
          </p>
        </div>
      </section>

      <footer className="site-footer">
        <div className="shell footer-grid">
          <div>
            <Link className="brand" href="/" aria-label="MailAuthCheck home">
              <MailCheck aria-hidden="true" />
              <span>MailAuthCheck</span>
            </Link>
            <p>{copy.footer}</p>
          </div>
          <nav className="footer-links" aria-label="Footer">
            <Link href="/">Home</Link>
            <Link href="/bulk-email-readiness-checker">Bulk readiness</Link>
            <Link href="/gmail-bulk-sender-requirements">Gmail requirements</Link>
            <Link href="/dmarc-policy-bulk-email">DMARC policy</Link>
            <Link href="/guides/mailchimp-gmail-compliance">Mailchimp guide</Link>
            <Link href="/spf-checker">SPF checker</Link>
            <Link href="/dmarc-checker">DMARC checker</Link>
            <Link href="/mx-record-checker">MX checker</Link>
            <Link href="/spf-lookup-counter">SPF lookup counter</Link>
          </nav>
        </div>
      </footer>
      {showBackToTop ? (
        <button
          type="button"
          className="back-to-top-button"
          onClick={handleBackToTop}
          aria-label={copy.backToTop}
        >
          <ChevronUp aria-hidden="true" />
          <span>{copy.backToTop}</span>
        </button>
      ) : null}
    </main>
  );
}

function resolveRuntimeApiBaseUrl(configuredBaseUrl: string) {
  if (typeof window === "undefined") {
    return configuredBaseUrl;
  }

  try {
    const parsed = new URL(configuredBaseUrl);
    const isLocalHost = parsed.hostname === "localhost" || parsed.hostname === "127.0.0.1";
    const pageHostIsLocal =
      window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

    if (isLocalHost && !pageHostIsLocal) {
      return `${window.location.protocol}//${window.location.hostname}:8000`;
    }

    return parsed.origin;
  } catch {
    if (
      configuredBaseUrl.includes("localhost") ||
      configuredBaseUrl.includes("127.0.0.1")
    ) {
      return `${window.location.protocol}//${window.location.hostname}:8000`;
    }

    return configuredBaseUrl.replace(/\/$/, "");
  }
}

function normalizeCheckListResult(payload: CheckListResult): AggregateResult {
  const derivedStatus = deriveAggregateStatus(payload.checks);
  const score =
    derivedStatus === "ready"
      ? 100
      : derivedStatus === "needs_attention"
        ? 68
        : 20;

  const nextSteps = payload.checks
    .map((check) => check.recommendedFix)
    .filter((value): value is string => Boolean(value));

  return {
    domain: payload.domain,
    score,
    status: derivedStatus,
    summary:
      payload.checks[0]?.summary ??
      "The domain returned a focused result for this checker.",
    checks: payload.checks,
    nextSteps:
      nextSteps.length > 0
        ? Array.from(new Set(nextSteps)).slice(0, 3)
        : ["Review the returned technical details before making DNS changes."],
    disclaimer:
      "This is a DNS/authentication check and does not guarantee inbox placement.",
  };
}

function deriveAggregateStatus(checks: CheckResult[]): AggregateResult["status"] {
  if (checks.some((check) => check.status === "error" || check.status === "missing")) {
    return "not_ready";
  }

  if (checks.some((check) => check.status === "warning")) {
    return "needs_attention";
  }

  return "ready";
}
