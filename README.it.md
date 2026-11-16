# Integrazione Zyxel Router per Home Assistant

[English](README.md) · **Italiano**

Un'integrazione locale e in sola lettura per Home Assistant che rileva i dispositivi Wi-Fi collegati ai router Zyxel. Il primo modello supportato è **Zyxel DX54C**.

> **Stato dello sviluppo: sperimentale.** La procedura di autenticazione del DX54C e l'endpoint della tabella dei dispositivi Wi-Fi sono stati verificati con un client Python indipendente. Il codice dell'integrazione Home Assistant è in fase di sviluppo e non è ancora stato collaudato su un'installazione Home Assistant reale. Il ramo `main` non deve essere considerato una versione stabile.

## Funzionalità attualmente implementate

- Comunicazione locale con il router, senza servizi cloud.
- Configurazione tramite interfaccia di Home Assistant: indirizzo del router, nome utente e password.
- Interrogazioni asincrone tramite il coordinator di Home Assistant.
- Creazione dinamica di device tracker per gli indirizzi MAC rilevati.
- Sensori per ogni dispositivo: RSSI, SNR, velocità del collegamento e livello del segnale.
- Recupero del nome del dispositivo dalla tabella ARP in sola lettura del router, quando disponibile, tramite associazione con il MAC.
- Intervallo di aggiornamento configurabile da 30 a 600 secondi (60 secondi predefiniti).
- Diagnostica senza password, token di sessione o indirizzi MAC dei client.

## Protocollo del router verificato finora

- Autenticazione: `GET /getRSAPublickKey`, seguito da `POST /UserLogin` con dati cifrati.
- Tabella dei dispositivi Wi-Fi: richiesta semplice `GET /cgi-bin/WLANTable_handle`, utilizzando la stessa sessione HTTP e i relativi cookie.
- L'endpoint Wi-Fi è in sola lettura: non viene modificata alcuna impostazione del router.
- La tabella restituisce i dispositivi collegati alle reti a 2,4 GHz e 5 GHz, con MAC, velocità del collegamento, RSSI, SNR e livello del segnale.
- Una seconda richiesta in sola lettura a `GET /cgi-bin/ARPTable_handle` recupera le associazioni IP/MAC/nome; i nomi vengono associati ai client Wi-Fi tramite MAC. Se il router non conosce il nome o la richiesta ARP non riesce, il rilevamento Wi-Fi continua normalmente e viene mantenuto il nome di ripiego basato sul MAC.

## Limiti del rilevamento della presenza

Il device tracker indica se un indirizzo MAC risulta attualmente associato alla rete Wi-Fi del router. Non è una misurazione della distanza Bluetooth, non identifica la stanza in cui si trova un dispositivo e non dimostra che una persona sia fisicamente in casa. I dispositivi che utilizzano indirizzi MAC privati o casuali possono comparire come client distinti.

## Installazione

Non è ancora disponibile una versione stabile tramite HACS. Prima di installare questa integrazione su un'istanza Home Assistant in uso quotidiano, attendere la pubblicazione di una versione contrassegnata (tag) e delle relative istruzioni di installazione.

Per lo sviluppo, la cartella dell'integrazione è `custom_components/zyxel_dx54c`.

## Sicurezza e privacy

- Non pubblicare mai password del router, cookie, token di sessione, chiavi AES o dati di sessione del browser.
- Non includere indirizzi MAC dei dispositivi non anonimizzati nelle segnalazioni pubbliche.
- La diagnostica riporta intenzionalmente il numero di dispositivi per banda, senza elencarne gli identificativi.
- Utilizzare una password amministratore del router robusta e non riutilizzata.

## Sviluppo e test

I test del parser si trovano nella cartella `tests/`. Prima della prima versione stabile verranno aggiunti test automatici per il flusso di configurazione e il coordinator di Home Assistant.

## Prossimi obiettivi

1. Verificare autenticazione e aggiornamento dei dati da Home Assistant con un DX54C reale.
2. Aggiungere il recupero automatico dopo la scadenza della sessione e una gestione più robusta delle risposte del firmware.
3. Completare i test automatici per Home Assistant e la pipeline CI.
4. Aggiungere il supporto ad altri modelli Zyxel solo dopo averne verificato il protocollo.
5. Pubblicare una versione contrassegnata e una guida per l'installazione tramite HACS.
