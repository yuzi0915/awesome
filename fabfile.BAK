import os,re
from datetime import datetime
from fabric.api import *

env.user = 'ubuntu'
env.sudo_user = 'root'
env.hosts = ['18.224.15.13']

db_user = 'root'
db_password = 'zjbaaa'

_TAR_FILE = 'dist-awesome.tar.gz'


def _current_path():
    return os.path.abspath('.')


def build():
    '''
    Build dist package.
    '''
    #includes = ['static', 'templates', 'transwarp', 'favicon.ico', '*.py']
    includes = ['static', 'templates', '*.py']
    excludes = ['test', '.*', '*.pyc', '*.pyo']
    local('rm -f dist/%s' % _TAR_FILE)
    with lcd(os.path.join(_current_path(), 'www')):
        local('rm -rf ../dist')
        local('mkdir ../dist')
        cmd = ['tar', '--dereference', '-czvf', '../dist/%s' % _TAR_FILE]
        cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
        cmd.extend(includes)
        local(' '.join(cmd))

_REMOTE_TEM_TAR = '/tmp/%s' % _TAR_FILE
_REMOTE_BASE_DIR = '/srv/awesome'

def deploy():
    newdir = 'www-%s' % datetime.now().strftime('%y-%m-%d_%H.%M.%S')

    run('rm -rf %s' % _REMOTE_TEM_TAR)
    put('dist/%s' % _TAR_FILE, _REMOTE_TEM_TAR)
    with cd(_REMOTE_BASE_DIR):
        sudo('mkdir %s' % newdir)
    with cd('%s/%s' % (_REMOTE_BASE_DIR,newdir)):
        sudo('tar -xzvf %s' % _REMOTE_TEM_TAR)
    with cd(_REMOTE_BASE_DIR):
        sudo('rm -rf www')
        sudo('ln -s %s www' % newdir)
        sudo('chown ubuntu:ubuntu www')
        sudo('chown -R ubuntu:ubuntu %s' %newdir)
    with settings(warn_only = True):
        sudo('supervisorctl stop awesome')
        sudo('supervisorctl start awesome')
        sudo('/etc/init.d/nginx reload')















