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

_WIP, suite à venir ! :)_
