# -*- python -*-
"""This is a template upgrade script.

The purpose is both to cover the most common use-case (updating all modules)
and to provide an example of how this works.
"""


def run(session, logger):
    """Update script"""
    if session.is_initialization:
        modules = [
            'account', 'crm', 'stock', 'account_invoicing',
            'sale_management', 'purchase', 'account_type_menu',
            'account_tag_menu', 'account_group_menu',
            'l10n_fr', 'l10n_fr_sale_closing', 'l10n_fr_department',
	    'l10n_fr_department_oversea', 'l10n_fr_state',
            'l10n_fr_certification', 'backend_theme_v11',
            'attachment_large_object', 'ny_gestion'
        ]
        logger.info(u"Fresh database - Installing modules %r" % modules)
        session.install_modules(modules)
        return

    if session.db_version <= '1.0':
        logger.info("ATTACHMENT LARGE OBJECT")
        install_module_if_not_already_done(
            session, logger, [
		'attachment_large_object', 'l10n_fr_department_oversea',
		'l10n_fr', 'l10n_fr_sale_closing', 'l10n_fr_department',
		'l10n_fr_certification', 'backend_theme_v11',
	    ])

        session.env['ir.config_parameter'].set_param(
            'ir_attachment.location', 'postgresql:lobject')
	
	session.db_version = '1.0'

    logger.info("Default upgrade procedure : updating all modules.")
    session.update_modules(['all'])

    session.cr.commit()


def install_module_if_not_already_done(session, logger, modules):
    logger.info("Installing modules %r if it is not already done" % modules)
    install_modules = []
    installed_modules = session.env['ir.module.module'].search([('state', '=', 'installed')])
    installed_modules_names = [m.name for m in installed_modules]
    for module in modules:
        if module in installed_modules_names:
            continue
        install_modules.append(module)
    if install_modules:
        session.install_modules(install_modules)
