from morthal.vcs.url_utils import is_git_url, normalize_url


def test_is_git_url_protocol_prefixes():
    assert is_git_url('https://github.com/owner/repo') is True
    assert is_git_url('https://github.com/owner/repo.git') is True
    assert is_git_url('http://example.com/owner/repo') is True
    assert is_git_url('git@github.com:owner/repo.git') is True
    assert is_git_url('git://github.com/owner/repo.git') is True
    assert is_git_url('ssh://git@github.com/owner/repo.git') is True


def test_is_git_url_github_com_shorthand():
    assert is_git_url('github.com/owner/repo') is True
    assert is_git_url('github.com/owner') is True


def test_is_git_url_owner_repo_shorthand():
    assert is_git_url('owner/repo') is True


def test_is_git_url_local_paths_are_rejected():
    assert is_git_url('./repo') is False
    assert is_git_url('/abs/path/repo') is False
    assert is_git_url('../repo') is False


def test_is_git_url_no_slash_is_rejected():
    assert is_git_url('repo') is False


def test_is_git_url_too_many_slashes_without_known_prefix_is_rejected():
    assert is_git_url('owner/repo/branch') is False


def test_normalize_url_owner_repo_shorthand():
    assert normalize_url('owner/repo') == 'https://github.com/owner/repo'


def test_normalize_url_github_com_with_owner_and_repo():
    assert normalize_url('github.com/owner/repo') == 'https://github.com/owner/repo'


def test_normalize_url_full_urls_are_left_unchanged():
    assert normalize_url('https://github.com/owner/repo') == 'https://github.com/owner/repo'
    assert normalize_url('ssh://git@github.com/owner/repo.git') == 'ssh://git@github.com/owner/repo.git'


def test_normalize_url_scp_style_ssh_is_mistaken_for_owner_repo_shorthand():
    # 'git@github.com:owner/repo.git' has exactly one '/' and doesn't start
    # with '.' or '/', so it currently matches the owner/repo shorthand
    # branch instead of being left untouched.
    assert normalize_url('git@github.com:owner/repo.git') == \
        'https://github.com/git@github.com:owner/repo.git'


def test_normalize_url_local_paths_are_left_unchanged():
    assert normalize_url('./repo') == './repo'
    assert normalize_url('/abs/path/repo') == '/abs/path/repo'


def test_normalize_url_owner_only_hits_single_slash_branch_first():
    # 'github.com/owner' has exactly one '/', so it matches the owner/repo
    # shorthand branch before the 'github.com/' prefix branch is reached.
    assert normalize_url('github.com/owner') == 'https://github.com/github.com/owner'
