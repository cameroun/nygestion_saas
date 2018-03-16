from os.path import exists
from fabric.api import env, local, cd, sudo, puts, abort, run
from fabric.colors import green
from fabric.contrib.console import prompt
from fabric.decorators import roles
from ConfigParser import SafeConfigParser
from .api import multiline_question, promptlist


env.roledefs['buildbot'] = ['buildbot.anybox.fr']
env.roledefs['privbot'] = ['privbot.anybox.fr']

STANDARD_BUILDER = '''
[{account}-{builder_type}]
buildout = {vcs_type} {vcs_url} {revision} buildout.cfg
build-category = {build_category}
buildout-part = {odoo}
build-for = {build_for}
build-requires = {build_requires}
openerp-addons = {openerp_addons}
post-buildout-steps = {post_buildout_steps}
db-steps = {db_steps}
auto-watch = true
'''

NOSE = '''nose.tests = {nose_test_dirs} --logging-level INFO
nose.coverage = true
'''

FLAKE8 = '''static-analysis.flake-directories = {static_analysis_dirs}
'''

RELEASE_BUILDER = '''
[{account}-{builder_type}]
buildout = {vcs_type}tag {vcs_url} unextracted-latest-release.cfg
build-category = {build_category}
buildout-part = {odoo}
build-for = {build_for}
build-requires = {build_requires}
post-dl-steps = packaging
post-buildout-steps = {post_buildout_steps}
db-steps = {db_steps}
packaging.parts = {odoo}
packaging.prefix = {account}-{odoo}
packaging.upload-dir = {account}
auto-watch = false
watch =

'''

PRIVATE_REPOSITORY = 'https://rhode.anybox.fr/Anybox/buildbot/priv_buildouts'
PUBLIC_REPOSITORY = 'ssh://hg@bitbucket.org/anybox/public_buildbot_buildouts'


def samples(option):
    """returns examples found in the manifest"""
    if env.host.split('.')[0] == 'privbot':
        which = 'private'
    if env.host.split('.')[0] == 'buildbot':
        which = 'public'
    manifest = SafeConfigParser()
    manifest.read('{}_buildbot/MANIFEST.cfg'.format(which))
    ex = set()
    for section in manifest.sections():
        if manifest.has_option(section, option):
            ex = ex.union([v.strip() for v in manifest.get(section, option).splitlines()])
    return ' / '.join(ex)


def local_clone():
    """ Clone the buildbot for modification"""
    if not env.host:
        abort('No roles specified')
    if env.host.split('.')[0] == 'privbot':
        if not exists('private_buildbot'):
            local('hg clone {} private_buildbot'.format(PRIVATE_REPOSITORY))
    if env.host.split('.')[0] == 'buildbot':
        if not exists('public_buildbot'):
            local('hg clone {} public_buildbot'.format(PUBLIC_REPOSITORY))


def create_builder():
    """Ask relevant questions and prints a builder config for the MANIFEST"""
    # first clone the relevant repository
    local_clone()
    if env.host.split('.')[0] == 'privbot':
        which = 'private'
    if env.host.split('.')[0] == 'buildbot':
        which = 'public'
    local('cd {}_buildbot && hg pull && hg up -C'.format(which))

    builder_type = promptlist('What kind of builder?', ('test', 'release'))
    test_type = True
    if builder_type == 'release':
        test_type = prompt('Test before releasing? [y]n ',
                           default='y', validate='[yYnN]').lower() == 'y'
    test_type = promptlist('What kind of test?', ('test-odoo', 'nose')) if test_type else None
    openerp_addons = ','.join(multiline_question('Odoo addon to test: ')) if test_type else None
    static_analysis = prompt('Run flake8 analysis? y[n] ',
                             default='n', validate='[yYnN]').lower() == 'y'
    build_category = prompt('Existing categories: {}\nBuild category: '
                            .format(samples('build-category')))
    build_for = multiline_question('Build for what?', example=samples('build-for'))
    build_requires = multiline_question('Build requires what?', example=samples('build-requires'))
    if builder_type == 'release':
        build_requires = set(build_requires).union(['release'])
    static_analysis_dirs = (multiline_question(
        'Path (relative to the buildout) on which to perform static analysis: ')
        if static_analysis else [])
    nose_test_dirs = ' '.join(multiline_question(
        'Path (relative to the buildout) where nose should search and run tests: '
        )) if test_type == 'nose' else None
    post_buildout_steps = []
    post_buildout_steps += ['static-analysis'] if static_analysis else []
    post_buildout_steps += [test_type] if test_type else []
    post_buildout_steps += ['packaging'] if builder_type == 'release' else []
    db_steps = ['simple_create'] if test_type else []

    template = STANDARD_BUILDER if builder_type == 'test' else RELEASE_BUILDER
    template += NOSE if test_type == 'nose' else ''
    template += FLAKE8 if static_analysis else ''

    config = template.format(
        account=env.account,
        builder_type=builder_type,
        vcs_type=env.vcs_type,
        vcs_url=env.vcs_url,
        revision=env.get('revision', ''),
        odoo=env.odoo,
        build_category=build_category,
        build_for=('\n'+12*' ').join(build_for),
        build_requires=('\n'+17*' ').join(build_requires),
        openerp_addons=openerp_addons,
        post_buildout_steps=('\n'+22*' ').join(post_buildout_steps),
        db_steps=('\n'+11*' ').join(db_steps),
        static_analysis_dirs=('\n'+36*' ').join(static_analysis_dirs),
        nose_test_dirs=nose_test_dirs,
    )

    puts('\nAdd this configuration in the MANIFEST.cfg of the buildbot, commit, push, then '
         'reconfig the buildbot with: fab buildbot.reconfig\n{}'.format(green(config)))
    puts('Please also read the doc: '
         'http://docs.anybox.fr/anybox.buildbot.openerp/current/py-modindex.html')


@roles('buildbot')
def reconfig():
    """ reconfigure the buildbot to reflect builder changes """
    if env.host.split('.')[0] == 'privbot':
        with cd('~privbot'):
            run('sudo -u privbot bin/pull_reconfig')
    if env.host.split('.')[0] == 'buildbot':
        with cd('~buildbot'):
            sudo('hg pull -u --cwd anybox_pub_buildouts/', user='buildbot')
            sudo('bin/buildbot reconfig public_master', user='buildbot')
