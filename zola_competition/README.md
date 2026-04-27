# Agente Zola - playerSmart.py

Questo progetto contiene l'implementazione di un agente intelligente per il gioco Zola, sviluppato per la competizione del corso magistrale di Intelligenza Artificiale.

## Logica dell'Euristica (Pesi)

La scelta dei pesi nella funzione di valutazione (euristica) definisce la "personalità" e le priorità dell'agente. In `playerSmart.py` è stata utilizzata una gerarchia di pesi basata sul principio del **Lexicographic Ordering (Ordinamento Lessicografico)**. L'obiettivo è fare in modo che una priorità inferiore non possa mai superare una priorità superiore.

I pesi utilizzati sono i seguenti:
* **Vantaggio materiale (Pezzi): `* 100`**
* **Potenziale di cattura (Mosse di cattura future): `* 10`**
* **Mobilità generale (Mosse totali): `* 1`**

Vediamo nel dettaglio il ragionamento:

### 1. Il Materiale è Re (`* 100`)
Zola è un gioco di eliminazione: vince chi mangia tutti i pezzi dell'avversario. Avere un pezzo in più garantisce un netto vantaggio, perché riduce le opzioni nemiche e aumenta le proprie. 
Dando peso `100` a una pedina, ci assicuriamo che l'agente **non sacrificherà mai un pezzo** solo per ottenere una posizione apparentemente più "mobile". 
Anche se sacrificare un pezzo ci facesse guadagnare 5 mosse di mobilità in più, perderemmo `100` punti e ne guadagneremmo solo `5` (con il peso `1`). Quindi, l'agente proteggerà sempre il materiale prima di tutto.

### 2. Le Catture Future (`* 10`)
Fra due o più mosse di cattura disponibili, l'agente preferisce quella che negli stati successivi consentirà di effettuare un'altra cattura. 
Per implementare questo requisito, è stato dato peso `10` alle "mosse di cattura disponibili".
Quando l'agente confronta due stati in cui il numero di pedine è identico (stesso punteggio per il materiale), il peso `10` funge da **primo spareggio decisivo**. Lo stato che offre più bersagli raggiungibili guadagnerà `10` punti extra per ogni bersaglio, spingendo l'agente verso posizioni "aggressive".

### 3. Mobilità Generale (`* 1`)
Questo è l'**ultimo spareggio**. Se a parità di materiale c'è anche lo stesso numero di catture potenziali (oppure zero catture per entrambi), l'agente preferirà la posizione che gli offre più libertà di movimento generale (mosse di fuga o posizionamento).
In giochi ristretti come Zola, avere molte mosse significa che l'avversario farà molta fatica a forzarti a fare l'unica mossa pessima rimasta a disposizione (*Zugzwang*).

---
*I pesi attuali (`100, 10, 1`) sono un ottimo punto di partenza logico e sicuro. Se l'agente dovesse risultare troppo difensivo, si potrebbe aumentare il peso delle catture future (es. a `20` o `30`).*
