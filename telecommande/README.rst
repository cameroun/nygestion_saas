************
Telecommande
************

Ce dépôt permet de gérer à distance les instances hébergées,
grâce à `Fabric <http://www.fabfile.org/>`_ 
et `anybox.fabric <https://bitbucket.org/anybox/anybox.fabric/>`_ :

Installation
============

L'installation se fait dans un répertoire sur sa propre machine ::

    hg clone https://rhode.anybox.fr/Anybox/telecommande
    cd telecommande
    python bootstrap.py
    bin/buildout
    source bin/activate  # à refaire à chaque utilisation

Un fabfile global est disponible à la racine du dépôt et permet des actions globales::

    fab help

Les sous-répertoires contiennent les fabfiles de chaque instance::

    cd saas/bdes/demo
    fab help

Fonctionnalités
===============

     - Gestion des comptes client (création, suppression, listage, espace disque)
     - Gestion des instances Odoo (installation, désinstallation, arrêt, démarrage, mise en sommeil, inspection)
     - Gestion des bases de données (dump, restore, déplacement depuis un autre serveur)
     - Génération de MANIFEST pour le buildbot
     - Plusieurs infrastructures possibles (Proxmox, etc.)
     - Plusieurs méthodes de déploiement possibles (vcs, tarball, paquet debian, etc.)
     - Génération de nouveau fabfile pour gérer une nouvelle prod ou recette
     - Prise en charge des erreurs (replay, savepoint, rollback, etc.)
     - Conception sur deux niveaux d'abstraction pour faciliter l'évolution de l'infra

Avantages en tant qu'utilisateur
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Aucune installation sur les serveurs (à part anybox-odoo-host)
    - On ne se connecte jamais soi-même sur les serveurs
    - On n'a pas besoin de se préoccuper de la réplication
    - On connait immédiatement la liste des commandes qu'on peut faire
    - Les commandes n'ont pas d'option, l'outil pose lui-même les questions
    - Les commandes sont les mêmes quel que soit le système, l'infra ou la méthode de déploiement
    - Tout est visible en clair pendant l'exécution
    - Mise à jour automatique (vérifiée pendant ``fab help``)

Avantages en tant que développeur
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - le code est disponible sous la main, facile à lire, à déboguer en local, et à enrichir
    - Possiblité d'ajouter des commandes spécifiques à une instance dans le fabfile

Exemples
========

Créer un nouveau fabfile ::

    cd telecommande
    mkdir nouveau_client
    fab fabfile.create
    edit fabfile.py  # ← modifier les options

Ajouter un builder sur le buildbot privé ::

    fab -R privbot buildbot.create_builder
    recopiez la sortie dans privbot/MANIFEST.cfg
    fab -R privbot buildbot.reconfig

Déployer une nouvelle instance ::

    fab -R recette customer.create
    fab -R recette instance.install
    fab -R recette instance.activate
    fab -R recette instance.start

Récupérer une base de prod en recette ::

    fab -R production db.backup
    fab -R recette db.transfer
    fab -R recette db.restore
    fab -R recette instance.restart

Récupérer une base de prod en local ::

    # si pas d'urgence et pas de filestore, utilisez plutôt pg_remote_copy
    fab -R recette db.download

Afficher le mot de passe superadmin de l'instance ::

    fab -R recette instance.admin_passwd

Modifier un mot de passe que vous ne connaissez pas ::

    fab -R recette db.reset_password

Voir la sortie du fichier de log ::

    fab -R recette instance.logfile

Démarrer un shell python Odoo sur l'instance distante ::

    fab -R recette instance.open_shell

Démarrer un shell SQL sur la base de données::

    fab -R recette db.inspect

Afficher un logo TEST sur une instance de recette ::

    # S'assurer que l'option testlogo est activée dans le fabfile, puis
    fab -R recette instance.activate

Limiter l'accès à la prod à certaines IP ::

    # ajouter les IPs dans le fabfile puis,
    fab -R recette instance.protect
    # Pour désactiver la protection :
    fab -R recette instance.unprotect
