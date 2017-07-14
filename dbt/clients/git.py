import os.path

from dbt.clients.system import run_cmd, rmdir
from dbt.logger import GLOBAL_LOGGER as logger
import dbt.exceptions


def clone(repo, cwd, dirname=None, remove_git_dir=False):
    clone_cmd = ['git', 'clone', '--depth', '1', repo]

    if dirname is not None:
        clone_cmd.append(dirname)

    result = run_cmd(cwd, clone_cmd)

    if remove_git_dir:
        rmdir(os.path.join(dirname, '.git'))

    return result


def list_tags(cwd):
    out, err = run_cmd(cwd, ['git', 'tag', '--list'])
    tags = set(out.decode('utf-8').strip().split("\n"))
    return tags


def checkout(cwd, repo, branch=None):
    if branch is None:
        branch = 'master'

    logger.info('  Checking out branch {}.'.format(branch))

    run_cmd(cwd, ['git', 'remote', 'set-branches', 'origin', branch])
    run_cmd(cwd, ['git', 'fetch', '--tags', '--depth', '1', 'origin', branch])

    tags = list_tags(cwd)

    # Prefer tags to branches if one exists
    if branch in tags:
        spec = 'tags/{}'.format(branch)
    else:
        spec = 'origin/{}'.format(branch)

    out, err = run_cmd(cwd, ['git', 'reset', '--hard', spec])
    stderr = err.decode('utf-8').strip()

    if stderr.startswith('fatal:'):
        dbt.exceptions.bad_package_spec(repo, branch, stderr)
    else:
        return out, err


def get_current_sha(cwd):
    out, err = run_cmd(cwd, ['git', 'rev-parse', 'HEAD'])

    return out.decode('utf-8')


def remove_remote(cwd):
    return run_cmd(cwd, ['git', 'remote', 'rm', 'origin'])
