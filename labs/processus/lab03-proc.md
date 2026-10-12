# lab 3 - Cycle de vie d'un processus

L'objectif de se lab est de comprendre comment un processus se termine, de quelle manière peut-on terminer un processus, comment un parent et / ou un enfant réagissent à la fermeture de l'un des deux ? Je vais essayer de creuser de comprendre les signaux: observer un processus qui reçoit une commande d'arrêt (SIGTERM, SIGKILL...), les zombies: essayer de comprendre pourquoi et comment un processus terminé peut encore apparaître dans `ps`, et quel rôle peut jouer le syscall `wait()` pour son parent, et enfin les orphelin: observer ce qui arrive à un processus lorsque son parent se termine avant lui.

---

# Expérience 1: Les signaux

Le but ici est d'observer les interaction processus <-> signaux, voir comment un processus réagit à différent signaux, comment sont-ils interprétés...

Pour ce faire nous allons d'abord lancer un processus en arrière plan qui reste actif:

```bash
sleep 300 &
```

Enfin on récupère son Pid:

```bash
jobs -l
```

Nous obtenons le PID `386372`

Avant de faire quoi que ce soit essayons de voir la différence entre `SIGTERM` et `SIGKILL`

### Hypothèses:

1. SIGTERM: SIGTERM demande au processus de se terminer. Un processus peut, lorsqu'il intercepte ce signal, effectuer un nettoyage, sauvegarder des données, fermer ses fichiers puis quitter. En d'autre termes, une fermeture "propre". Cependant il peut aussi ignorer le signal et ne pas se terminer immédiatement.

2. SIGKILL: SIGKILL force le noyau à arrêter le processus. Celui-ci ne peut ni intercepter, ni ignorer ce signal. Par conséquent un processus ciblé par SIGKILL ne peut pas prendre le temps de faire un arrêt "propre".

_À noter: Ces deux points présentent mes hypothèse, rien de concret. Nous ne savons pas si SIGTERM garantie la sauvegarde d'un procesuss, si SIGKILL implique que toutes les données soient perdues..._

Essayons maintenant de terminer notre processus via un signal `SIGTERM` et observons ce qu'il se passe:

```bash
kill -TERM 386372
```

Directement après avoir lancé la commande le processus s'est arrêté.

```bash
➜  linux-labs git:(main) ✗ ps -o pid,ppid,stat,cmd -p 386372
    PID    PPID STAT CMD
```

Cette fermeture rapide n'est pas innatendue: sleep n'a pas de traitement particulier pour sauvegarder son état, de ce fait sa fermeture est quasi-insantanée.

Afin de mener au mieux notre expérience nous allons crée un petit processus qui attend volontairement avant de se fermer. À noter ici que le `time.sleep` ne représente pas une véritable sauvegarde ou quelconque autre fonctionnalité. Il sert juste à en simuler une afin de rendre le comportement voulu observable.

```python
import signal
import time
import os

def handle_SIGTERM(signum, frame):
    print("SIGTERM reçu : nettoyage en cours...", flush=True)
    time.sleep(10)
    print("Nettoyage terminé.", flush=True)
    exit(0)

signal.signal(signal.SIGTERM, handle_SIGTERM)

print(f"PID : {os.getpid()}", flush=True)

while True:
    time.sleep(1)
```

quand nous lançons le script nous obtenons:

```bash
➜  Code git:(main) ✗ python3 signal_test.py
PID : 390421
```

Le but est de lançer le script plusieurs fois et d'observer la réaction obtenue avec `SIGTERM` et `SIGKILL`.

En terminant le processus avec le sgnal `SIGTERM` nous obtenons:

```bash
➜  Code git:(main) ✗ python3 signal_test.py
PID : 390421
SIGTERM reçu : nettoyage en cours...
Nettoyage terminé.
```

Le processus à un délais avant sa fermeture définitive. Il n'est pas fermé brusquement et à le temps de se fermer proprement (cf: hypothèse ci-dessus.)

Cette fois-ci observons avec `SIGKILL`

```bash
➜  Code git:(main) ✗ python3 signal_test.py
PID : 393115
[1]    393115 killed     python3 signal_test.py
```

Ici le processus s'arrête immédiatement, sans temps délais.

Cette petite expérience nous permet de vérifier en partie nos hypothèses principales : `SIGTERM` laisse au processus la possibilité de réagir au signal et d'exécuter un traitement avant de se terminer, tandis que `SIGKILL` ne lui laisse aucune possibilité d'intercepter le signal pour effectuer ce traitement.

Comme observé avec notre script Python, le processus a pu afficher un message, attendre dix secondes, puis se terminer après avoir reçu `SIGTERM`. Avec `SIGKILL`, il s'est terminé sans exécuter ce traitement.

**À noter :** Ce lab se limite à quelques expériences et ne cherche pas à couvrir tous les comportements possibles de ces signaux. Il reste notamment à explorer les situations dans lesquelles un processus ne réagit pas immédiatement à `SIGTERM`, ainsi que les conséquences concrètes d'une terminaison forcée.

---

# Expérience 2: Les processus zombies

## Hypothèse de départ

Un processus peut avoir terminer son exécution mais pour autant il peut encore apparâitre dans la liste des processus via `ps`. Nous chercherons ici à comprendre pourquoi et comment cela se produit.

## Observations

Nous allons nous servir du script suivant afin de mieux observer ce qu'il se passe:

```python
import os
import time

pid = os.fork()

if pid == 0:
    # Processus enfant
    print(f"Enfant : PID={os.getpid()}, fin immédiate.", flush=True)
    os._exit(0)

else:
    # Processus parent
    print(f"Parent : PID={os.getpid()}", flush=True)
    print(f"Enfant : PID={pid}", flush=True)
    print("Le parent attend 60 secondes sans récupérer le statut de l'enfant.", flush=True)
    time.sleep(60)
```

Résultats obtenus:

```bash
➜  ~ ps -o pid,ppid,stat,cmd -p 402951 402952
    PID    PPID STAT CMD
 402951  377034 S+   python3 zombie_test.py
 402952  402951 Z+   [python3] <defunct>
```

Ces résultats sont très intéressants. Premièrerment notons les codes d'états affichés **"S+"** et **"Z+"**. (_Après renseignement le "+" signifie que le processus est en premier plan_). En se référant au man de `ps` nous obtenons ces informations:

```text
D en sommeil non interruptible (normalement entrées et sorties) ;
I fil inactif du noyau ;
R s'exécutant ou pouvant s'exécuter (dans la file d'exécution) ;
S en sommeil interruptible (en attente d'un événement pour finir) ;
T arrêté par le signal de contrôle de la tâche ;
t arrêté par le débogueur lors du traçage ;
W pagination (non valable depuis le noyau 2.6.xx) ;
X tué (ne devrait jamais être vu) ;
Z processus zombie (<defunct>), terminé mais pas détruit par son
parent.
```

En se basant sur ces explications nous déterminons que notre processus parent (PID=402951) est dans l'état S, qui signifie qu'il est en sommeil, qu'il attend une action, un évènement pour se terminer.

Ensuite, encore plus intéressant, l'enfant: il est dans l'état "Z", processus zombie. La documentation nous dit clairement que le processus est **terminé** mais non détruit par son parent, pourquoi ?

On sait que l'enfant a fini d'exécuter son programme, il est terminé. On sait aussi que le parent, lui, continu de fonctionner. Pourquoi l'enfant ne disparaît-il donc pas immédiatement ? Y-a-t il un lien entre parent et enfant lors de la terminaison d'un processus ? Mon hypothèse est que le parent doit attendre de recevoir des informations de l'enfant (Code d'erreur ? Bien terminé... ?) mais dans quel but ? Aussi, quid du parent qui se terminerais avant d'avoir pu récupérer les informations de son enfant ? Un processus zombie sans parent réel resterait donc indéfiniement dans cet état ?

Pour le prochain test je vais relancer notre script mais cette fois-ci je vais envoyer un signal `SIGKILL` au parent pendant ses 60 secondes de `sleep`. Ainsi nous pourrons espérer observer ce qu'il advient d'un enfant quand son parent est interrompu.

**WIP, suite à venir, stay tuned !**
