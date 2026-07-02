def is_git_url(value: str) -> bool:
    if value.startswith(('https://', 'http://', 'git@', 'git://', 'ssh://')):
        return True
    if value.startswith('github.com/') and value.count('/') >= 2:
        return True
    if '/' in value and not value.startswith(('.', '/')) and value.count('/') == 1:
        return True
    return False


def normalize_url(value: str) -> str:
    if value.count('/') == 1 and not value.startswith(('.', '/')):
        return f'https://github.com/{value}'
    if value.startswith('github.com/'):
        return f'https://{value}'
    return value
