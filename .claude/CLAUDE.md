- Leggi tutti i file .md all'interno di @./notes . Questi file contengono molte informazioni che possono eseerti utili.
- A volte converseremo o ti darò istruzioni in italiano, ma tutto ciò che riguarda il codice, commenti inclusi, deve essere sempre in inglese.
- Aggiungi commenti non banali al codice quando necessario, spiegando il PERCHÈ dietro una determinata soluzione.
- quando vedi commenti vuoti nel codice, tipo "NOTE", non rimuoverli. Mi servono per ricordarmi di rivedere qualcosa di quel codice in seguito.
- Quando l'utente ti fornisce delle risorse web, path o di qualsiasi altra natura, fetchale/cercale attivamente.
- Quando spieghi il funzionamento di una api o di un concetto teorico, linka sempre la documentazione.

## Code

- Usa nomi espressivi per le variabili, non importa se vengono fuori lunghi.

<bad-example>
a
v_long
</bad-example>

<good-example>
apple
very_variable_long_name
</good-example>

- mai chiamare una variabile `data`.

## Dependencies

### Python

- usiamo uv come package manager, ricorda di attivare il venv in @./backend con `source .venv/bin/activate` quando esegui uno script o simili.

## Direttive provvisorie

- Concentriamoci sulle funzionalità, allo styling e alla sua coerenza penseremo dopo. Utilizza lo styling necessario per rendere il gioco fruibile anche se in fase di sviluppo.