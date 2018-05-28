# -*- coding: utf-8 -*-
# © 2018, Clovis NZOUENDJOU <nzouendjou@cam-network.org>
# © 2018 CAM NETWORK (www.cam-network.org)
{
    'name': 'NY Gestion',
    'version': '11.0',
    'license': 'AGPL-3',
    'category': 'custom',
    'author': 'CAM NETWORK',
    'maintainer': 'CAM NETWORK',
    'summary': "Module d'initialisation de l'instance Odoo pour NY Gestion",
    'website': 'http://www.cam-network.org',
    'images': [],
    'description': """

NY GESTION
==========

Module permettant d'installer et configurer tous les autres modules nécessaire
pour le fonctionnement de NY Gestion

Fonctionnalites:
----------------

* ACHATS
* VENTES
* COMPTABILITE
* RESSOURCES HUMAINES
* ...

    """,
    'depends': [
        'bi_website_support_ticket',
        'project_start_stop',
        'employee_document',
        'print_project_report',
        'project_kanban',
    ],
    'data': [
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
}
