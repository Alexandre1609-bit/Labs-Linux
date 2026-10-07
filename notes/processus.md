# Les processus

Dans ce premier chapitre, je reviendrai sur ce que j'ai pu revoir, apprendre et approfondir sur les processus Linux. Le but est de dégager un maximum de connaissances et de les remettre au propre.

## 1. Cheminement commande - retour commande

Dans les grandes lignes, de ce que je comprends, lorsque l'on tape une commande dans notre shell, ce dernier va consulter la liste des dossiers qu'il connaît via son **PATH** (consultable depuis la variable d'environnement `$PATH`) et va voir si un binaire associé à notre demande existe.

Si l'on devait résumer cela rapidement, on obtiendrait la chose suivante :

````text
tapes "ls"

      |

Le shell cherche "ls" dans $PATH

      |

Il trouve /usr/bin/ls

      |

Un processus est créé pour exécuter ls

      |

Le programme s'exécute

      |

Le processus se termine
```

Il est important de noter la différence entre un processus et un programme.
Un programme peut se traduire par un fichier exécutable présent sur le disque.
Un processus, lui, est une instance en cours d'exécution d'un programme.

Donc :

```text
/usr/bin/ls

    │
    │ lancement

Processus PID 12345

    │
    │ exécution

affiche le contenu du répertoire

    │

fin du processus
````

Mais cela va plus loin que ça. Nous pouvons déjà dégager plusieurs hypothèses : le shell lui-même est-il impliqué dans la création d'un processus ? Qui crée ce processus ? Le kernel ? Le shell ? Comment un processus fraîchement créé passe-t-il de « processus du shell » à « processus qui exécute réellement /usr/bin/ls ?

De ce que j'ai pu comprendre, cela découle principalement de deux mécanismes Linux fondamentaux : fork() et exec().

Ma théorie initiale est que le shell lui-même est impliqué, car un processus lancé dépend de son parent (notre shell), et que fork() lierait un processus à une instance puis exec() lancerait ce processus.

Cette théorie est en partie vraie, mais pas assez précise. En me renseignant, j'ai découvert que fork() faisait une copie du processus du shell, créant un nouveau processus (i.e. : bash PID 1000 → fork() → bash PID 1000 et bash PID 1001).

Ensuite, avoir une copie d'un processus existant n'est pas vraiment ce que l'on veut. C'est là qu'exec() interviendrait : il remplace le programme exécuté par le processus. Notre copie est donc amenée à changer.

On pourrait résumer cela par le schéma suivant :

```text
PID 1001
 bash
  │
  │ exec("/usr/bin/ls")
  |

PID 1001
  ls
```

À noter qu'après la « transformation », le PID reste le même. exec() ne crée pas un nouveau processus, il remplace essentiellement le programme chargé dans ce processus par celui demandé.

De ce fait, nous avons deux nouvelles connaissances : fork() crée une copie, donc un nouveau processus, et exec() remplace le programme exécuté par notre nouvelle copie.

Notre shell initial reste vivant pour nous permettre de continuer à l'utiliser !

Donc, un schéma plus détaillé serait :

```text
            SHELL
        bash PID 1000

              │

              │ fork()
        processus PID 1001

              │

              │ exec()

          /usr/bin/ls

              │

        affiche le contenu

              │

        processus terminé
```

Cependant, il nous manque encore des expérimentations pour le prouver. Jusque-là, nous avons vu la partie théorique. Dans la prochaine partie, un lab sera mis en place afin d'essayer d'observer les comportements désirés et d'en déduire leur fonctionnement réel.
