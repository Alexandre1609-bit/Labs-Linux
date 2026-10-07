# Lab Linux

## Objectifs

L'objectif principal derrière ces labs est d'apprendre comment fonctionne réellement Linux, dans sa globalité.

L'un des objectifs est d'approfondir mes connaissances Linux afin de pouvoir les transposer plus tard :

- professionnellement (stage, alternance, travail) ;
- personnellement (homelab, projets) ;
- académiquement (TP, SAE, etc.).

Les objectifs sont multiples. En plus d'être intrinsèquement bénéfique à mon parcours, cela me permet d'approfondir mes connaissances, de mieux comprendre les systèmes que j'utilise et de monter progressivement en compétences.

L'objectif n'est pas simplement d'apprendre à utiliser des commandes Linux, mais de comprendre ce qui se passe réellement derrière celles-ci et les mécanismes sur lesquels repose le système.

## Méthode

Ces labs seront réalisés principalement par la pratique.

L'idée est de partir de situations concrètes, d'observer le comportement du système, de formuler des hypothèses, de les vérifier et de documenter les résultats.

La démarche sera autant que possible :

1. Comprendre le concept.
2. Manipuler le système.
3. Observer son comportement.
4. Provoquer volontairement certaines situations ou erreurs.
5. Diagnostiquer le problème.
6. Comprendre pourquoi cela fonctionne de cette manière.
7. Documenter ce qui a été appris.

Une attention particulière sera portée au raisonnement de diagnostic plutôt qu'à la simple mémorisation de commandes.

## Thèmes abordés

Le contenu évoluera au fur et à mesure de l'avancement.

### Système

- Processus et threads
- Mémoire et mémoire virtuelle
- Système de fichiers
- Stockage
- Partitions et systèmes de fichiers
- Inodes
- LVM
- RAID
- Permissions et propriétaires
- Utilisateurs et groupes
- ACL
- `/proc` et `/sys`
- Services et systemd
- Logs et journalisation
- Démarrage du système
- Kernel et appels système

### Réseau

- Interfaces réseau
- Adressage IP
- Routage
- ARP / NDP
- TCP / UDP
- Sockets
- DNS
- Firewall
- Network namespaces
- Outils de diagnostic réseau

### Conteneurs

- Namespaces
- Cgroups
- Filesystem et couches
- Isolation
- Réseau des conteneurs
- Volumes
- Capabilities
- Docker
- containerd
- Lien entre Linux, Docker et Kubernetes

## Troubleshooting

Une partie importante des labs sera consacrée au diagnostic de problèmes.

Exemples :

- Un disque semble plein.
- Il reste de l'espace mais il est impossible de créer un fichier.
- Un processus consomme trop de CPU.
- Un service ne démarre plus.
- Une machine ne répond plus en SSH.
- Un programme rencontre un `Permission denied`.
- Un processus continue d'occuper de l'espace après la suppression d'un fichier.
- Un programme écoute sur un port mais reste inaccessible.
- Un conteneur fonctionne mais ne peut pas communiquer avec le réseau.

L'objectif est progressivement d'être capable de partir d'un symptôme et de remonter jusqu'à la cause.

## Documentation

Les notes sont organisées en plusieurs catégories :

```text

notes/ Contient les notions étudiées et les connaissances acquises.

labs/ Contient les manipulations et expérimentations réalisées.

troubleshooting/ Contient les problèmes rencontrés, les hypothèses, les investigations et les solutions.

```

## Relation avec mes autres projets

Ces labs sont indépendants de mes projets personnels, mais certaines connaissances pourront ensuite être réutilisées dans ceux-ci.

Par exemple, les connaissances acquises sur :

- les namespaces;
- les cgroups;
- le réseau Linux;
- le stockage;
- les processus;
- systemd;

pourront être mises en pratique dans mon homelab Kubernetes et dans d'autres projets.

L'objectif reste cependant de comprendre Linux dans un contexte général et pas uniquement à travers Kubernetes.

_n.b: Fiche de route réalisée avec l'IA, documentation par moi-même_
