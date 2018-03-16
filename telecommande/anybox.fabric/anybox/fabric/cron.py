from fabric.api import env, sudo
from anybox.fabric import systemuser
from random import randint

BACKUP = 'anybox-pg-backup'


def enable_backup():
    shinken = ('--shinken-enable --shinken-host {customer}_prod'
               .format(customer=env.account)
               if any([r.startswith('prod') for r in env.effective_roles])
               else '')
    sudo("crontab -l | grep -v '{cmd}' "
         "| {{ cat; echo '{m} {h} * * * {cmd} {shinken} {db}'; }} | crontab -"
         .format(m=randint(0, 59), h=randint(0, 7), db=env.db,
                 cmd=BACKUP, shinken=shinken),
         user=env.account)


def disable_backup():
    if systemuser.exists():
        sudo("crontab -l | grep -v '{cmd}' | crontab -"
             .format(m=randint(0, 59), h=randint(0, 7), db=env.db, cmd=BACKUP),
             user=env.account)
