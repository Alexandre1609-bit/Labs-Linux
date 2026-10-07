# Lab 1: Processus - Comprendre le cheminement d'une commande: De sa saisie à son exécution

# 1. Observations

Comme vu dans nos notes, nous pensons qu'un processus est une copie d'un autre processus. Pour essayer d'observer cela nous allons invsetiguer sur ce qui tourne réellement sur une machine.

Tout d'abord nous pouvons essayer de lister les processus. Le but ici est d'obtenir le PID de notre shell actuel et aussi son PPID

```bash
➜  processus git:(main) ✗ ps -F
UID          PID    PPID  C    SZ   RSS PSR STIME TTY          TIME CMD
alex       40375   40367  0  4749 10224   5 15:10 pts/0    00:00:03 zsh
alex       58879   40375  0  3462  4856   3 15:59 pts/0    00:00:00 ps -F
```

Comme nous pouvons le voir ci-dessus, notre shell (ici zsh) a bien son PID 40375 et dépend d'un autre processus, avec un PPID assez proche 40367. Cela pourrait ajouter une preuve à notre hypothèse de départ (_cf:note1_): Un processus et enfait une copie d'un autre processus. Les deux PID étant proche l'un de l'autre nous ne pouvons pas écarter cette piste, cependant il est bon de noter que nous ne disposons, à l'heure actuelle d'aucune autre information capable d'alimenter cette théorie.

Afin de facilité l'avancement nous allons procéder par schéma, pour le moment nous avons:

```text
processus 40367
    |
    | parent de
    |
processus 40375 (zsh)
```

## 2. Expérience

```bash
➜  processus git:(main) ✗ ps -F
UID          PID    PPID  C    SZ   RSS PSR STIME TTY          TIME CMD
alex       40375   40367  0  4749 10224   5 15:10 pts/0    00:00:03 zsh
alex       58879   40375  0  3462  4856   3 15:59 pts/0    00:00:00 ps -F
```

Nous voyons que `ps -F` est un enfant de notre shell zsh. Il nous faut maintenant essayer de voir si `ps` est réellement une copie de zsh.

En lançant `sleep 100 &` et ensuite `ps -F` on valide une première observation:

```bash
➜  processus git:(main) ✗ ps -F
UID          PID    PPID  C    SZ   RSS PSR STIME TTY          TIME CMD
alex       40375   40367  0  4749 10224   2 15:10 pts/0    00:00:03 zsh
alex       65602   40375  0  2164  2368   4 16:27 pts/0    00:00:00 sleep 100
alex       65719   40375  0  3462  4852   4 16:27 pts/0    00:00:00 ps -F
```

`Sleep` partage le même PPID que `ps`, nous pouvons conclure que notre shell possède un processus enfant, qui correspond à la commande qu'on vient de lancer.
Cependant nous n'avons toujours pas observé comment le shell crée un processus enfant.

Afin d'essayer d'avancer et d'observer comment un processus est crée nous pouvons utiliser **strace**. (_trace system calls and signals_). Avec ce nouvel outil nous allons pouvoir voir si nos appels système `fork` et `exec` ont bien lieu.

Pour une première utilisation nous allons utiliser `strace -c ls`. Le flag "-c" (_summary-only_) nous permet d'avoir un résumé rapide des différents appels système utilisés ainsi que d'autres informations.

```bash
➜  processus git:(main) ✗ strace -c ls
lab01-proc.md
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 39,10    0,000226         226         1           execve
 20,24    0,000117           6        18           mmap
  6,75    0,000039           5         7           openat
  5,71    0,000033           6         5           mprotect
  4,50    0,000026           5         5           read
  4,33    0,000025           2         9           close
  3,81    0,000022           2         8           fstat
  2,25    0,000013          13         1           munmap
  1,90    0,000011           3         3           brk
  1,90    0,000011           5         2         2 statfs
  1,56    0,000009           4         2         2 access
  1,56    0,000009           4         2           getdents64
  1,38    0,000008           4         2           ioctl
  1,04    0,000006           6         1           write
  1,04    0,000006           3         2           pread64
  0,69    0,000004           4         1           arch_prctl
  0,52    0,000003           3         1           prlimit64
  0,52    0,000003           3         1           getrandom
  0,52    0,000003           3         1           rseq
  0,35    0,000002           2         1           set_tid_address
  0,35    0,000002           2         1           set_robust_list
------ ----------- ----------- --------- --------- ----------------
100,00    0,000578           7        74         4 total
```

Avec ce première exemple nous pouvons déjà voir plusieurs choses interéssantes: pour l'exécution d'une commande il y a pas mal d'appels système engagé et ce, dans un laps de temps extrêmement court. Ensuite, on peut voir ici l'appel `execve` (_execve - execute program_) qui demande au noyau de remplacer un programme actuellement exécuté par un autre programme.(_execve() executes the program referred to by pathname. This causes the program that is currently being run by the calling process to be replaced with a new program,_).

Avec cette première expérience nous obtenons quelque chose de la sorte :

```text
shell
  │
  │ ??? ← partie non tracée
  |
processus
  │
  │ execve("/usr/bin/ls", ...)
  |
ls
  │
  ├── mmap()
  ├── openat()
  ├── read()
  ├── ...
  └── write()
```

Notre strace commence donc réellement au niveau de ls et non avant. Nous allons maintenant essayer de faire la même commande mais cette fois-ci en l'utilisant de manière plus ciblée, en demandant explicitement le processus **zsh** (notre shell).

La commande suivante sera donc utilsée :`strace -f -e trace=process zsh -c 'ls'`

Le flag "-f" demande à strace de suivre les processus enfants: "_-f (--follow-forks: Trace child processes as they are created by currently traced processes as a result of the fork(2), vfork(2) and clone(2) system calls.)"_

Et "-e" demande d'afficher uniquement les appels liés à la gestion des processus.
"_Trace only the specified set of system calls. syscall_set is defined as [!]value[,value], and value can be one of the following:[...])_"

L'output obtenu est le suivant:

```bash
execve("/usr/bin/zsh", ["zsh", "-c", "ls"], ...) = 0
execve("/usr/bin/ls", ["ls"], ...) = 0
lab01-proc.md
exit_group(0) = ?
```

À partir de ce résultat nous pouvons affirmer plusieurs chose:

- Au départ strace lance `zsh -c 'ls` qui nous donne `execve("/usr/bin/zsh", ...)`. Cela signifie que le processus lancé par strace charge/exécute zsh. Enfin `execve("/usr/bin/ls", ["ls"], ...) ` montre que ce processus exécute ensuite `ls`.

- On obtient le schéma suivant pour cette expérience:

```text
    processus
    │
    ├── execve("/usr/bin/zsh")
    │
    |
   zsh
    │
    ├── execve("/usr/bin/ls")
    │
    |
    ls
```

- Le premier processus lancé, ici `zsh`, est remplacé par `ls`. À ce moment précis nous n'avons pas encore observé d'appel `fork()` ou d'équivalent comme `clone()`. Peut être que par optimisation cet appel peut être omis par le shell ?

Afin d'essayer plus de choses nous allons maintenant reprendre notre dernière commande mais y ajouter `echo`. L'objectif ici est de forcer notre shell à rester en vie après avoir lancé `ls` afin d'exécuter notre commande `echo`. Peut être aurons-nous des résultats plus interéssants ?

```bash
➜  processus git:(main) ✗ strace -f -e trace=process zsh -c 'ls; echo terminé'
execve("/usr/bin/zsh", ["zsh", "-c", "ls; echo termin\303\251"], 0x7ffdd74f5d08 /* 52 vars */) = 0
clone(child_stack=NULL, flags=CLONE_CHILD_CLEARTID|CLONE_CHILD_SETTID|SIGCHLD, child_tidptr=0x732080c3a590) = 78624
strace: Process 78624 attached
[pid 78624] execve("/usr/bin/ls", ["ls"], 0x7ffd9529e1e8 /* 52 vars */) = 0
lab01-proc.md
[pid 78624] exit_group(0)               = ?
[pid 78624] +++ exited with 0 +++
--- SIGCHLD {si_signo=SIGCHLD, si_code=CLD_EXITED, si_pid=78624, si_uid=1000, si_status=0, si_utime=0, si_stime=0} ---
wait4(-1, [{WIFEXITED(s) && WEXITSTATUS(s) == 0}], WNOHANG|WSTOPPED|WCONTINUED, {ru_utime={tv_sec=0, tv_usec=0}, ru_stime={tv_sec=0, tv_usec=1535}, ...}) = 78624
kill(-78624, 0)                         = -1 ESRCH (Aucun processus ayant ce numéro)
wait4(-1, 0x7ffd9529cd74, WNOHANG|WSTOPPED|WCONTINUED, 0x7ffd9529cd90) = -1 ECHILD (Aucun processus enfant)
terminé
exit_group(0)                           = ?
+++ exited with 0 +++
```

Ici notre expérience prend tout son sens. En analysant ligne par ligne nous nous rendons compte du cheminement pour la commande `ls`. Tout d'abord nbotre shell est crée `execve("/usr/bin/zsh"...` Ensuite, zsh crée un processus enfant, cloné depuis zsh, mais pas en intégralité: `clone(child_stack=NULL, flags=[...]= 78624`. Le processus enfant est cloné avec les "flag" `CLONE_CHILD_CLEARTID|CLONE_CHILD_SETTID|SIGCHLD, child_tidptr`. Ces flags seront les ressources qu'auront en communs notre processus parent et le clone crée. Cette ligne `strace: Process 78624 attached` nous montre qu'un nouveau processus a correctement été crée, qu'il existe réellement. Ensuite, notre processus devient `ls` via `execve()`: `[pid 78624] execve("/usr/bin/ls", ["ls"]`. Notre processus enfant, avec le PID 78624 vient d'être crée par `clone()` et devient le processus qui exécute `ls`. Notre schéma peut donc être actualisé:

```text
                 ZSH
                  │
                  │ clone()
                  |
              PID 78624
                  │
                  │ execve()
                  |
             /usr/bin/ls
                  │
                  |
              termine
```

Remarquons aussi que le pid du clone reste le même jusqu'à la fin ! Cela confirme une de nos observations: La création d'un processus et le remplacement du programme exécuté par ce processus. Avec tout cela nous pouvons affirmer, notamment grâce à nos observations, notre hypothèse: Le shell est probablement impliqué dans la création du processus

```text
zsh
 │
 │ clone()
 |
processus enfant PID 78624
 │
 │ execve("/usr/bin/ls")
 |
ls
 │
 │ exit
 |
SIGCHLD
 │
 |
zsh
 │
 │ wait4()
 |
continue
```
