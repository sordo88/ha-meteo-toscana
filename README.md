# Meteo Toscana

Integrazione personalizzata per Home Assistant che rende disponibili le previsioni meteorologiche delle località toscane pubblicate dal Consorzio LaMMA.

## Funzionalità

- configurazione tramite Config Flow;
- selezione della località dall'elenco ufficiale LaMMA;
- supporto a più località configurate contemporaneamente;
- previsioni orarie e giornaliere;
- aggiornamento dei dati ogni 60 minuti per ciascuna località.

## Dati meteorologici e attribuzione

Dati meteorologici forniti da **Consorzio LaMMA** (https://www.lamma.toscana.it), distribuiti tramite il catalogo Open Data di Regione Toscana (https://dati.toscana.it/organization/lamma-toscana) con licenza Creative Commons Attribuzione 4.0 (CC-BY).

L'integrazione scarica e rielabora i file XML delle previsioni pubblicati dal Consorzio LaMMA, convertendoli nel formato utilizzato da Home Assistant. I dati mostrati nell'interfaccia e nelle previsioni sono quindi dati rielaborati a partire dalle pubblicazioni LaMMA.

La licenza **CC BY 4.0** si applica ai dati meteorologici; il codice sorgente di questa integrazione è invece distribuito con la licenza **MIT**.

## Stato del progetto e disclaimer

**Meteo Toscana è un progetto open source sviluppato da terzi.**

Non è un prodotto ufficiale del Consorzio LaMMA e non è patrocinato, certificato, approvato o affiliato al Consorzio. Il nome del Consorzio è citato esclusivamente per attribuire la fonte dei dati.

Il progetto **non utilizza il logo o il marchio grafico del Consorzio LaMMA**.

I dati sono forniti **“così come sono”** e hanno esclusivamente scopo informativo. Il Consorzio LaMMA non è responsabile per eventuali inesattezze delle previsioni, per la loro interpretazione o per l'indisponibilità del servizio.

I file XML utilizzati dall'integrazione non costituiscono un'API versionata e formale: struttura, URL o formato possono cambiare senza preavviso. L'integrazione gestisce gli errori di rete, i timeout e i dati XML non validi mantenendo Home Assistant informato del mancato aggiornamento.

## Licenza

Il codice dell'integrazione è distribuito con licenza MIT. I dati meteorologici di origine sono distribuiti dal Consorzio LaMMA tramite il catalogo Open Data della Regione Toscana con licenza CC BY 4.0.

Per i dettagli, vedere `LICENSE`.


## Installazione

### Installazione tramite HACS

L'integrazione può essere installata tramite [HACS](https://www.hacs.xyz/).

Se **Meteo Toscana** non è ancora disponibile nell'elenco predefinito di HACS:

1. Aprire **HACS → Integrazioni**.
2. Selezionare il menu **⋮ → Repository personalizzati**.
3. Inserire nel campo **Repository**:

   `sordo88/ha-meteo-toscana`

4. Selezionare **Integration** come tipo di repository.
5. Aggiungere la repository e installare **Meteo Toscana**.
6. Riavviare Home Assistant.

Dopo il riavvio, andare in **Impostazioni → Dispositivi e servizi → Aggiungi integrazione**, cercare **Meteo Toscana** e seguire la procedura guidata per selezionare la località desiderata.

### Installazione manuale

Scaricare la repository:

`https://github.com/sordo88/ha-meteo-toscana`

e copiare la directory:

```text
custom_components/lamma
