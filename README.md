# fadder.nabla.no #

Dette er Nablas system for automatisk fordeling til faddergruppene basert på fadderbarnas ønsker. Dette gjøres med en enkel Django-nettside og optimering via GLPK (GNU Linear Programming Kit).

## Installasjon

Prosjektet bruker [Pipfile](https://github.com/pypa/pipfile), slik at alle nødvendige Python-pakker blir installert vha. `pipenv install`. Det eneste som kan være litt vrient er å få med GLPK-støtte. Dette burde inkluderes med `cvxopt` både for Windows og Linux, men på Windows ser det ut som man også trenger en `numpy+mkl` binary. Dette kan skaffes f.eks. [her](https://www.lfd.uci.edu/~gohlke/pythonlibs/).

Påmeldingsskjemaet bruker Google reCAPTCHA v2 Invisible, så man trenger en site key (i `groupfixer/templates/mainpage.html`) og secret key (i `fadder/settings/base.py`) fra Google for å få den til å fungere. For øyeblikket brukes et sett med nøkkler jeg (Kristoffer A.) har hardkoded inn, men de burde heller lastes inn fra en `.env` fil, slik som MySQL brukernavn/passordet gjøres i production.

## Fordelingsmetoden

Alle fadderbarnene blir bedt på index-siden om å oppgi navn, kjønn og velge 3 faddergrupper i prioritert rekkefølge. Etter påmeldingen er stengt av administrator fra kontrollpanelet (på URL-bane `/control`) blir fadderbanene delt inn med hensyn på min/max gruppestørrelse og kjønnsfordeling. Dette optimeres som et integer programming (IP) problem.

###Optimeringsalgoritme

Vi vil maksimere en funksjon basert på ønskene til fadderbarnene. Slik vi har definert det så blir 10 poeng gitt for hvert fadderbarn som får sitt førstevalg, 8 poeng for hvert andrevalg, 5 poeng for hvert tredjevalg og 0 poeng ellers. Hvis det er plass til alle på førstevalgene så er den optimale fordelingen triviell, men ellers må en ["branch and bound"](https://en.wikipedia.org/wiki/Branch_and_bound) algoritme brukes.

For `N` fadderbarn og `M` faddergrupper bruker vi en `N x M` lang binær valgvektor (eg. `x = [0,0,0,1,0, 0,0,1,0,0, ...]`), hvor vi ønsker å maksimere prikkproduktet med en poengvektor vi konstruerer fra prioriteringene (eg. `c = [5,0,0,10,8, 8,0,10,5,0, ...]`). Optimeringen blir gjort med hensyn begresninger slik at

* hvert fadderbarn er plassert i kun én gruppe (`Ax = [1,1,1,1,...]` hvor `A` er en matrise som teller hvor mange grupper hver fadderbarn er i),
* hver faddergruppe er innenfor størrelseskravet (eg. `Bx <= [20,20,20,...]` og `Bx >= [10,10,10,...]` hvor `B` er en matrise som teller antall barn i hver faddergruppe),
* hver faddergruppe er innenfor kjønnsfordelingskravet (eg. `Cx <= 0.65*Dx` og `Cx >= 0.35*Dx` hvor `C` er en matrise som teller antall kvinner og `D` er en matrise som teller antall kvinner og menn i hver gruppe. Vi eksluderer altså fadderbarnene som ikke har oppgitt kjønn/valg annet fra beregningene).

###Implementasjon

Dette problemet forumleres  ved hjelp av `numpy`-matriser/vektorer og `cvxpy` og sendes til GLPK for å finne en løsning. Dette løses typisk ganske raskt (i løpet av et par sekunder), men den kan også ende opp med en eksponensielt økende mengde noder som må undersøkes. Dette er ikke så farlig, ettersom vi kun gir GLPK 30 sekunder på å løse problemet, og på den tiden vil den alltid ha funnet en løsning som ligger svært tett opp mot den øvre grensen.

###Eksportering av fordeling

Fordelingen presenteres i kontrollpanelet, hvor man kan se hvilken priotiering hvert fadderbarn fikk. Gruppene kan også eksporteres som et `.csv`-regneark ved å trykke på "Eksporter til regneark".

## Testing

Med `Debug=True` kan faddergrupper og fadderbarn bli generert med tilfeldig valgte prioriteringer. `python manage.py make_faddergrupper` lager 8 faddergrupper med navn basert på fadderpeioden 2018. `python manage.py make_fadderbarn -n N -p P` genererer `N` fadderbarn med jenteandel `P` (mellom 0.0 og 1.0). Deretter kan de fordeles fra kontrollpanelet.