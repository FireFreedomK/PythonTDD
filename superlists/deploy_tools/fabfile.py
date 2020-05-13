from fabric.contrib.files import append,exists,sed
from fabric.api import env,local,run
import random

REPO_URL='https://github.com/FireFreedomK/PythonTDD.git'

def deploy():
    site_folder = '/home/%s/sites/%s' % (env.user, env.host)        #用于放置项目的文件夹
    source_folder = site_folder + '/source'                         #用于防止项目源代码的文件夹
    _create_directory_structure_if_necessary(site_folder)           #在服务器中创建项目的目录结构
    _get_latest_source(source_folder)                               #从GitHub中拉取源代码到服务器中
    _update_settings(source_folder, env.host)                       #更新项目的settings.py，设置DEBUG=False，设置允许访问项目的IP
    _update_virtualenv(source_folder)                               #创建或更新项目环境
    _update_static_files(source_folder)                             #创建或更新项目静态文件
    _update_database(source_folder)                                 #迁移或更新项目数据库

def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('database','static','virtualenv','source'):
        run(f'mkdir -p {site_folder}/{subfolder}')

def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        run('cd %s && git fetch' % (source_folder,))
    else:
        run('git clone %s  %s' % (REPO_URL, source_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd %s && git reset --hard %s' % (source_folder, current_commit))

def _update_settings(source_folder,site_name):
    settings_path=source_folder+'/superlists/superlists/settings.py'
    sed(settings_path,"DEBUG=True","DEBUG=False")
    sed(settings_path,
        'ALLOWED_HOSTS=.+$',
        f'ALLOWED_HOSTS=["{site_name}"]'
        )
    secret_key_file=source_folder+'/superlists/secret_key.py'
    if not exists(secret_key_file):
        chars='qazwsxedcrfvtgb1234567890-='
        key=''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file,f'SECRET_KEY="{key}"')
    append(settings_path,'\nfrom .secret_key import SECRET_KEY')

def _update_virtualenv(source_folder):
    virtualenv_folder=source_folder+'/../virtualenv'
    if not exists(virtualenv_folder+'/bin/pip'):
        run(f'python3.7 -m venv {virtualenv_folder}')

    run(f'{virtualenv_folder}/bin/pip install -r {source_folder}/requirements.txt')

def _update_static_files(source_folder):
    run('cd %s && ../virtualenv/bin/python  ./superlists/manage.py collectstatic --noinput' % (
        source_folder,
    ))

def _update_database(source_folder):
    run(f'cd {source_folder}'
        ' && ../virtualenv/bin/python ./superlists/manage.py migrate --noinput')    