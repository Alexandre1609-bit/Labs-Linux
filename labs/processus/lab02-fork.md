# Lab 2: Processus - Comprendre ce qui est réellement copié

## 1. Observations

Dans la continuité du lab 1, nous allons essayer de voir ce qui est réellement copié avec l'appel système `fork()` ou encore `clone()`. Nous avons vu précédemment que l'appel `clone()` avait lieu et que l'instance clonée allait servir de "réceptacle" pour la commande suivante, avec`ls` comme exemple. Nous avons aussi remarqué que l'instance clonée n'était pas un clone parfait, seuls quelques flags étaient partagés entre l'original et le clone. Afin d'essayer de démontrer et d'observer toutes nos théories, je me suis servi de différents forums et de l'IA dont j'ai extrait / généré du code C afin de pouvoir expérimenter. Le but ici n'étant pas d'apprendre le C, je me permets cette démarche.

## 2. Expériences

### Première expérience

Grâce au code suivant, nous allons pouvoir obtenir un processus, le fork et voir les résultats obtenus après le fork.

```c
#include <stdio.h>
#include <unistd.h>

int main(void) {
    int x = 42;

    printf("Avant fork : PID=%d, x=%d\n", getpid(), x);

    fork();

    printf("Après fork : PID=%d, PPID=%d, x=%d\n",
           getpid(), getppid(), x);

    return 0;
}
```

Les résultats obtenus sont les suivants :

```bash
➜  processus git:(main) ✗ ./lab02-fork
Avant fork : PID=48584, x=42
Après fork : PID=48584, PPID=46472, x=42
Après fork : PID=48585, PPID=48584, x=42

```

Les résultats sont intéressants. Plusieurs choses sont à noter :

1. Après le fork, on observe notre élément principal (PID=48584) ainsi que son PPID (46472) et un nouveau processus (PID=48585) avec en PPID le PID de notre original (48584).
2. Notre `int` "x" n'a pas changé, il reste identique avant et après le `fork()`.

Nous pouvons représenter cela sous forme de schéma :

```text
46472
  |
  ------48584
          |
          ------48585
```

Nous obtenons une "chaîne" de processus qui dépendent d'autres processus. À noter qu'une de nos théories initiales reste pour le moment valide : un processus cloné / copié obtient un PID proche de son parent. Notons aussi qu'il n'y a pas de `execve()` ou de remplacement de programme, ici uniquement `fork()` est utilisé. Aussi, nous n'avons aucune information concernant la nature de 46472.
Enfin, notre `int` qui ne change pas. Cela peut amener plusieurs pistes :

1. Ces processus partagent-ils la même mémoire ?
2. Le processus copié a-t-il une copie de la mémoire ?

À l'heure actuelle, rien ne nous permet d'affirmer quoi que ce soit concernant la mémoire des processus, cependant cela reste des pistes à creuser.

### Deuxième expérience

Ici, nous allons reprendre notre code C et l'ajuster un petit peu afin de modifier notre variable `x` après le fork afin d'observer s'il y a des changements.
Le nouveau code est sensiblement le même qu'avant :

```c
#include <stdio.h>
#include <unistd.h>

int main(void) {
    int x = 42;

    printf("Avant fork : PID=%d, x=%d\n", getpid(), x);

    fork();

    x = 100;

    printf("Après fork : PID=%d, PPID=%d, x=%d\n",
           getpid(), getppid(), x);

    return 0;
}
```

Cette fois-ci, observons les résultats obtenus :

```bash
➜  processus git:(main) ✗ ./lab02-fork-chx
Avant fork : PID=53619, x=42
Après fork : PID=53619, PPID=46472, x=100
Après fork : PID=53620, PPID=53619, x=100
```

Nous pouvons voir que notre variable `x` s'est bien actualisée et est passée à la valeur 100. Donc, nous avons un changement avant et après `fork()`, c'était le résultat attendu. Mais cela ne nous montre pas tout. Le processus copié hérite-t-il de **x=100** ou naît-il avec **x=100** ? Son parent intervient-il dans l'initialisation de cette variable, les variables sont-elles liées entre parent et enfant ou sont-elles indépendantes ?

Nous avons deux pistes :

1. Les variables sont séparées :

   ```text
   parent                 enfant
   x = 42                 x = 42
     |                      |
   x = 100                x = 100
   ```

2. Les variables sont partagées :

   ```text
           x = 42
             |
      ┌──────┴──────┐
      |             |
   parent         enfant
      └──────┬──────┘
             |
          x = 100
   ```

Dans les deux cas, nous obtenons `x=100`. Notre expérience ne nous permet pas encore d'établir de conclusion fiable.

### Troisième expérience

Nous allons maintenant essayer de modifier uniquement la variable `x` du parent afin de voir si cela a un impact sur l'enfant.

Comme avant, nous adaptons le code initial pour répondre à nos besoins :

```c
#include <stdio.h>
#include <unistd.h>

int main(void) {

    int x = 42;

    printf("Avant fork : PID=%d, x=%d\n", getpid(), x);

    pid_t pid = fork();

    if (pid > 0) {
        x = 100;
    }

    printf("Après fork : PID=%d, PPID=%d, x=%d\n",
           getpid(), getppid(), x);

    return 0;
}
```

Les résultats obtenus sont très parlants :

```bash
➜  processus git:(main) ✗ ./lab02-chackpid
Avant fork : PID=58161, x=42
Après fork : PID=58161, PPID=46472, x=100
Après fork : PID=58162, PPID=58161, x=42
```

Nous pouvons voir que notre "original" voit sa variable `x` changer, son enfant, lui, conserve la valeur initiale "**42**". On peut assumer que chaque processus a un état de mémoire distinct après un `fork()`. Une copie serait donc indépendante de son parent sur le plan de la mémoire. On a également observé qu'une modification du parent n'impactait pas l'état de mémoire de notre enfant (x(parent) != x(enfant)), une modification sur l'un n'est pas directement visible par l'autre. Cependant, cela soulève une question :

**Si leurs espaces mémoire sont distincts, est-ce que Linux recopie réellement toute la mémoire au moment du fork(), ou est-ce qu'il optimise cette copie ?**

Le manuel de `fork` (_man fork_) nous donne pas mal d'informations sur le sujet: " The child process and the parent process run in separate memory spaces. At the time of fork() both memory spaces have the same content. Memory writes, file mappings (mmap(2)), and unmappings (munmap(2)) performed by one of the processes do not affect the other." Cependant nous ne l'avons pas encore prouvé.

Aussi, en contraste à `fork` l'appel `clone` semble plus précis et permet un meilleur contrôle sur ce qui est réellement partagé entre parent et enfant. "By contrast with fork(2), these system calls provide more precise control over what pieces of execution context are shared between the calling process and the child process." (_man clone_)

L'objectif étant de comprendre les processus à un certain degrés et non parfaitement je ne chercherais donc pas à comprendre l'entièreté des appel système, des flags et tout ce qui gravite autout.

## Quatrième expérience

Jusqu'ici nous avons établi deux choses :

- Après `fork()`, le parent et l'enfant ont des espaces mémoire distincts du point de vue du programme.
- Modifier x dans le parent ne modifie pas la valeur de x dans l'enfant.

Mais cela ne signifie pas que Linux recopie immédiatement toute la mémoire physique. Pour comprendre cette nuance, nous allons comparer deux programmes qui allouent un bloc mémoire important.

```C
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

#define SIZE (100 * 1024 * 1024)

int main(void) {
    char *memory = malloc(SIZE);

    if (memory == NULL) {
        perror("malloc");
        return 1;
    }

    for (size_t i = 0; i < SIZE; i += 4096) {
        memory[i] = 1;
    }

    printf("Avant fork : PID=%d\n", getpid());
    fflush(stdout);

    pid_t pid = fork();

    if (pid < 0) {
        perror("fork");
        free(memory);
        return 1;
    }

    if (pid == 0) {
        printf("Enfant : PID=%d, première valeur=%d\n",
               getpid(), memory[0]);
        memory[0] = 2;
        printf("Enfant : valeur modifiée=%d\n", memory[0]);
    } else {
        wait(NULL);
        printf("Parent : PID=%d, première valeur=%d\n",
               getpid(), memory[0]);
    }

    free(memory);
    return 0;
}
```

Voici les résultats obtenus:

```bash
Avant fork : PID=83836
Enfant : PID=83841, première valeur=1
Enfant : valeur modifiée=2
Parent : PID=83836, première valeur=1
```

Nous pouvons voir que la valeur modifié de l'enfant n'a pas eu d'impact, du moins visible, sur la valeur du parent, qui elle, est restée à 1 le tout avec un bloc de mémoire plus conséquent, ici 100Mio. Cela rejoint nos observation précédent, les espaces mémoires semblent indépendants du point de vue des processus. Cependant nous n'avons pas encore pu observer le phénomène de "_CoW_" (_Copy On Write_\*).

En modifiant légèrement le code en ajoutant une pause temporaire (\*sleep):

```C
if (pid == 0) {
    printf("Enfant : PID=%d\n", getpid());
    sleep(30);
    memory[0] = 2;
} else {
    printf("Parent : PID=%d, enfant=%d\n", getpid(), pid);
    sleep(30);
    wait(NULL);
    printf("Parent : memory[0]=%d\n", memory[0]);
}
```

Nous obtenons les résultats suivants:

```
Avant fork : PID=88574
Parent : PID=88574, enfant=88575
Enfant : PID=88575
Parent : memory[0]=1
```

Cependant ce qui nous intéresse vraiment est l'output des commandes suivantes:

```bash
grep -E '^(Rss|Pss|Private_Dirty|Shared_Dirty|Private_Clean|Shared_Clean):' /proc/83836/smaps_rollup
grep -E '^(Rss|Pss|Private_Dirty|Shared_Dirty|Private_Clean|Shared_Clean):' /proc/83841/smaps_rollup
```

Qui est:

Parent:

```bash
Rss:              104124 kB
Pss:               51284 kB
Shared_Clean:       1620 kB
Shared_Dirty:     102468 kB
Private_Clean:         4 kB
Private_Dirty:        32 kB
```

Enfant:

```bash
Rss:              103212 kB
Pss:               51274 kB
Shared_Clean:        712 kB
Shared_Dirty:     102468 kB
Private_Clean:         0 kB
Private_Dirty:        32 kB
```

Les observations sont nombreuses, ne connaissant pas tous les termes je vais essayer d'interpréter au mieux ce que je vois en me renseigant en ammont:

Observation 1 : chaque processus possède un RSS d'environ 100 Mio.
Ceci cohérent avec le bloc mémoire de 100 Mio que nous avons alloué et touché avant le fork(). Mais le RSS inclut aussi d'autres pages du programme, des bibliothèques et des mappings.

Observation 2 : les deux PSS sont proches de 50 Mio.
C'est un indice particulièrement intéressant : lorsqu'une page est partagée par deux processus, sa contribution au PSS est répartie entre eux. Une grande partie de leur mémoire pourrait donc être commune physiquement. Plus de processus partagent la même page plus leur PSS est faible ?

Observation 3 : Shared_Dirty vaut 102 468 Kio dans les deux processus.
Cette quantité importante est compatible avec notre hypothèse : une partie importante des pages modifiées avant le fork() reste partagée physiquement après celui-ci, tant qu'elles n'ont pas besoin d'être séparées.

Ces observations ne constituent pas une preuve isolée que chaque page est partagée, mais cela cohérent avec le **Copy-On-Write**.

Mais pourquoi les valeurs diffèrent-elles ?

Nous relevons environ 900 Kio d'écart sur le RSS. C'est normal que les valeurs ne soient pas exactement identiques: les processus n'ont pas nécessairement les mêmes pages résidentes à un instant donné. Les bibliothèques, piles, données privées et autres mappings peuvent différer !
Il ne faut donc pas conclure que Linux a fait une copie imparfaite. Les compteurs décrivent la mémoire associée aux processus, pas une comparaison octet par octet de leurs contenus.

## Conclusion

- fork() crée un enfant avec un espace mémoire distinct de celui du parent.
- Initialement, les données observées par les deux processus sont cohérentes avec le même état au moment de la création.
- Linux peut laisser les deux processus utiliser les mêmes pages physiques tant qu'aucune écriture ne nécessite de les séparer.
- Lorsqu'un processus modifie une page privée partagée via COW, le noyau peut créer une copie de cette page pour préserver l'indépendance des espaces mémoire.

Nuance importante: nous avons observé l'indépendance des valeurs et des compteurs compatibles avec le COW. Nous n'avons pas suivi directement une page physique précise pendant son écriture. Pour mon objectif de compréhension générale de Linux, ce niveau me paraît suffisant.

## Notes

J'aimerais revenir sur certains points / hypothèses que j'aimerais clarifier afin de ne pas laisser le tout sans suite:

- Les PID proches : leur proximité n'est pas une règle permettant d'identifier une relation parent-enfant. Le PPID est l'indice pertinent ici.

- COW : les résultats sont compatibles avec ce mécanisme, mais nous n'avons pas directement suivi la copie d'une page physique au moment de son écriture.

- Les flags de clone() : ils déterminent différents comportements et éléments du contexte partagés ou non. Il faudrait éviter de réduire leur fonctionnement à quelques ressources simplement « copiées » ou « partagées ».

## Annexes

_CoW: copy-on-write permet à plusieurs processus ou fichiers linux de partager la même ressource physique en memoire ou sur disque jusqu'à ce qu'une modification survienne. -> réduit considérablement la consommation de mémoire et améliore les performance lors de la création de processus ou de la copie de fichier. Grosso modo: duplique la mémoire en lecture seule, la duplication physique est effectué uniquement si un processus tente d'y écrire quelque chose. Copiant alors les données et les mettant à jour._
