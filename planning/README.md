# Introduzione al PDDL e ai Problemi di Planning

Questa directory contiene una serie di file scritti in **PDDL** (Planning Domain Definition Language), utilizzati per definire e risolvere problemi di _Automated Planning_ (Pianificazione Automatica) nell'ambito dell'Intelligenza Artificiale.

## 1. Cos'è il PDDL, come funziona e perché si usa

### Cos'è il PDDL?
Il **PDDL** (Planning Domain Definition Language) è un linguaggio standardizzato, originariamente sviluppato nel 1998 e basato sulla sintassi del LISP (da qui l'uso abbondante di parentesi tonde), per esprimere formalmente problemi di pianificazione. L'obiettivo dell'Intelligenza Artificiale in questo ambito è **non codificare** la soluzione algoritmica a un problema specifico (come un algoritmo di ricerca pathfinding customizzato), ma descrivere formalmente l'ambiente in cui ci troviamo per poi far trovare la soluzione (il "piano") a un motore software generale detto **Planner** o *Solver*.

### Come funziona la struttura PDDL
Qualsiasi problema di pianificazione viene rigorosamente scisso in due file logici separati:
1. **Il file di Dominio (Domain):** Rappresenta la "fisica" del nostro mondo. Definisce le regole generali, la tipologia degli oggetti (es. veicoli, container, locazioni), le proprietà che possono variare (i *predicati*) e le azioni o manovre consentite agli agenti.
2. **Il file del Problema (Problem):** È lo "scenario" d'impiego operativo. Descrive la precisa situazione della stanza (lo "stato iniziale"), precisa l'obiettivo finale da concretizzare (il *target abstract state*) e dichiara quali sono le vere istanze fisiche in gioco. 

Il *Planner* elabora poi assieme Dominio e Problema simulando internamente percorsi di ricerca in uno state-space virtuale, cercando una sequenza di **Azioni** che permetta la transizione verso il risultato, senza mai violare i vincoli (le cosiddette precondizioni).

---

## 2. I file di Dominio (`/Domini`)

Il Dominio contiene entità fondamentali come:
- **`:requirements`**: Estensioni logiche necessarie al solver (es. `:typing` per dichiarare gerarchie logiche nel codice, `:action-costs` per sommare i flussi di transazione, oppure `:negative-preconditions`).
- **`:predicates`**: Fatti logico/booleani che indicano qualcosa di intrinsecamente vero o falso come stato parziale. (Es: "La valigia è nel baule").
- **`:actions`**: Operazioni consentite regolamentate da *Precondizioni* (cosa serve affinché avvenga lo snap) ed *Effetti* (su cosa interviene).

Ecco i domini inclusi nel progetto:

### `blocksword.pddl` (Il mondo dei blocchi)
È il dominio accademico di base, noto universalmente come _Blocks World_. Simula i movimenti di base di un braccio robotico che sposta cubi sparsi su un banco di officina per impilarli correttamente.
- **Tipi:** Un unico blocco tipizzato `block`.
- **Predicati:** Tracciano dinamicamente tutto lo stato strutturale: se un blocco funge da tetto `(on)`, è radicato al suolo `(ontable)`, ha campo visivo libero sopra `(clear)` o se si attesta un blocco nella morsa robotica ed un check per morsa a riposo `(holding`, `handempty)`.
- **Azioni:** `pick-up` (solleva con la mano dal banco libero), `put-down` (sgancia blocco solitario sul desk), `unstack` (raccogli il primo in cima staccandolo dalla configurazione), `stack` (aggancia la scatola stretta su un bersaglio base sotto per far torre).

### `knights-tour.pddl` (Il cammino del cavallo)
Modelizza un problema della teoria dei grafi e matematica scacchistica pura: esplorare a salti "L" tutte le coordinate della griglia sfidandosi a toccare le celle unicamente per una volta.
- Rispetto ai domini di partenza, sfrutta un feature essenziale (`:negative-preconditions`) che verifica in precondizione passiva di un'azione che una cella sia in status "non toccato" `(not (visited ?to))`.
- **Azione base:** Viene permessa sola una singola transizione, `move`, vincolata dalla matrice delle probabilità valide `(valid_move)` mappate dalla sorgente o dall'utente e al divieto di ritorno sui propri passi.

### `linehaul-with-costs.pddl` (Logistica con calcolo del costo operativo)
Un dominio che strizza l'occhio ai flussi operations supply-chain dove si combinano beni termocontrollati (`refrigerated_truck`), veicoli standard ed enormi differenze di tragitti ed idrocarburo simulato su rete logistica.
- **Funzioni matematiche introdotte:** Sfrutta `:action-costs` istituendo funzioni reali attive `(:functions)` in grado di monitorare il tracciato `distance` implementando dinamicamente la metrica generatrice `total-cost`.
- **Aritmetica naturale per incrementi:** Dato che i parser PDDL di base fanno fatica a calcolare, per ovviare allo step di sottrazione di domanda clienti su container interi il dominio sfrutta funzioni in stile "assiomatiche standard". I link da un quantitativo all'altro (come un countdown 10... 9... 8...) vengono stabiliti in manuale col predicato transitorio costruttore `plus1`. Nel pratico scaricare nel processo `deliver_chilled` sfrutterà l'assegnazione relazionale scendendo da un blocco base d'inventario $N$ al limitrofo blocco d'inventario un'incirca inferiore o maggiore che fungerà di livello decrescente fin al parametro zero atteso.

---

## 3. I file di Problema (`/Problemi`)

Il file Problema definisce il setting della run, indicando per parametri specificati quantitativamente un numero "X" tutto quello che non era fissato.
- **`:objects`**: Stabilisce quali "variabili" del layer fisico entreranno nel frullatore iterativo, come i veri e propri identificativi (nomi dei veicoli "furgone bianco", o i riferimenti agli strati misurabili numericamente quali quantità limitanti).
- **`:init`**: Manda lo snapshot del momento T=0 inserendo in un attimo tutte quante le asimmetrie ed attivazioni esistite al decollo (es. camion allocato al deposito distretto C). 
- **`:goal`**: Forgia l'obiettivo logico `and / or` a raggiungimento garantito e perentorio che se non incrociato segnala un "Plan Fail". 
- **`:metric minimize`**: Ordina all'albero interno di procedere per diramazione in cerca del valore "minorato" per favorire l'economicità totale `(total-cost)` o in altre branche sui colpi delle azioni eseguite a pari efficienza.

### `blocksworld-example.pddl`
Prepara il tavolo virtuale e registra fisicamente quattro asset di tipo cubo (`red`, `yellow`, `blue`, `orange`). Per iniziare manda l'input con sparpagliamento globale e incastri prefissati. L'ordine del datore in fondo `goal` comanda e raggruppa forzatamente l'appoggio esclusivo di due cubetti (l'arancione poggiato solidamente sul colorato a base marina) ed invita la gru smontatrice ad abbandonare i rimanenti due componenti allo stato disciolto poggiato rasoterra sgombri. 

### `instance-8x8-A8.pddl`
Scenario dall'instanziazione enciclopedica e prolissa nel backend. Viene dichiarata a macchina e listata pezzo a pezzo una tipizzata griglia estesa tradizionale (`objects: da A1 a H8`) procedendo all'inizializzazione esplicita `init` dichiarando i singoli punti di scivolamento di una mossa cavallo. Fa atterrare per test iniziale l'icona sul vertice superiore alto-destrorso, l'A8. Impone come ordine di stop lo switch per il totalitarismo delle zone marcando ogni blocchetto di bandierina visitata garantendo path completi prima dello shut-down del core process.

### `linehaul-example.pddl`
Definisce la fornitura cittadina aziendale, impacchettata fisicamente in due flussi differenziati. 41 pseudo-numeri identificatori in stringhe gestiscono l'hardware dell'inventario (da 0 per vuoto o stop, scalo fino a tetto soglia tollerata volume 40 unita). 
Dichiara inoltre un network su 4 hubs e centralizzando "Depot" e "BW, E", e poi popola in un massivo frame i costi su mappa viaria assieme al contachilometri dei furgoni (doppiature o reefer trucks per il *chilled goods* ad 3.04/km o mezzi base *BDouble* a soli 2.59 di assorbimento costi operativi per lo spazio *ambient goods* in surplus logistico). 
Rientro per il check finale alla madre base richiesto al saldo delle distribuzioni finite azzerato sul conteggio per tutti tre i quartieri serviti assommando per l'ovvietà una "minorazione a ribasso dei ticket logistici".
