# server.py

Server zaisťuje preklad doménových mien, použitím HTTP protokolu. Pre preklad mien server používa lokálnu resolver stanicu na ktorej beží s použitím API, ktoré poskytuje operačný systém.

# Server podporuje 2 operácie:

  - GET
 Táto operácia preloží jeden dotaz, ktorý bude špecifikovaný, ako parameter URL požiadavku.


 - POST
Metoda POST pbsahuje v tele požiadavku zoznam dotazov, každý na samostatnom riadku.


Server je implementovaný ako IPv4 server. Je napísaný v jazyku Python, s použitím funkcií knižnice socket. Server beží v nekonečnom cyklea čaká pri tom na požiadavky generované pomocou nástroja cURL. Po obdržaní formálne správneho požiadavku server požiadavok vyhodnotí, a odošle príslušnú odpoveď.

# Príklady implementovaných typov požiadaviek:

# GET

curl localhost:5353/resolve?name=www.fit.vutbr.cz\&type=A

# POST

curl --data-binary @queries.txt -X POST http://localhost:5353/dns-query

# Autor :

- Damián Krajňák (xkrajn03)