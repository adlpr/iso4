" iso4.vim
" Author: Robin Scheibler
" Created: Wed May 6 2020
" Requires: Vim Ver7.0+
" Version:  1.1
"
" Documentation:
"   This applies ISO4 shortening for publication title to a string
"
" History:
"  1.0:
"    - initial version

if v:version < 700 || !has('python3')
    echo "This script requires vim7.0+ with Python 3.6 support."
    finish
endif

if !exists("g:iso4_virtualenv")
  if has("nvim")
    let g:iso4_virtualenv = "~/.local/share/nvim/iso4"
  else
    let g:iso4_virtualenv = "~/.vim/iso4"
  endif
endif

python3 << endpython3
import os
import sys

import vim


def _get_python_binary(exec_prefix):
    try:
        default = vim.eval("g:pymode_python").strip()
    except vim.error:
        default = ""
    if default and os.path.exists(default):
        return default
    if sys.platform[:3] == "win":
        return exec_prefix / "python.exe"
    return exec_prefix / "bin" / "python3"


def _get_pip(venv_path):
    if sys.platform[:3] == "win":
        return venv_path / "Scripts" / "pip.exe"
    return venv_path / "bin" / "pip"


def _get_virtualenv_site_packages(venv_path, pyver):
    if sys.platform[:3] == "win":
        return venv_path / "Lib" / "site-packages"
    return venv_path / "lib" / f"python{pyver[0]}.{pyver[1]}" / "site-packages"


def _initialize_iso4_env(upgrade=False):
    pyver = sys.version_info[:2]
    if pyver < (3, 6):
        print("Sorry, iso4 requires Python 3.6+ to run.")
        return False

    from pathlib import Path
    import subprocess
    import venv

    virtualenv_path = Path(vim.eval("g:iso4_virtualenv")).expanduser()
    virtualenv_site_packages = str(
        _get_virtualenv_site_packages(virtualenv_path, pyver)
    )
    first_install = False
    if not virtualenv_path.is_dir():
        print("Please wait, one time setup for iso4.")
        _executable = sys.executable
        try:
            sys.executable = str(_get_python_binary(Path(sys.exec_prefix)))
            print(f"Creating a virtualenv in {virtualenv_path}...")
            print(
                "(this path can be customized in .vimrc by setting g:iso4_virtualenv)"
            )
            venv.create(virtualenv_path, with_pip=True)
        finally:
            sys.executable = _executable
        first_install = True
    if first_install:
        print("Installing iso4 with pip...")
    if upgrade:
        print("Upgrading iso4 with pip...")
    if first_install or upgrade:
        command = [
            str(_get_pip(virtualenv_path)),
            "install",
            "-U",
            "/Users/JP27024/.vim/bundle/iso4",
        ]
        out = subprocess.run(command, capture_output=True)
        if out.returncode == 0:
            print("DONE! You are all set, thanks for waiting ✨ 🍰 ✨")
        else:
            print("Error. Installation of iso4 failed with error")
            print("stdout:")
            print(out.stdout)
            print("stderr:")
            print(out.stderr)
    if first_install:
        print(
            "Pro-tip: to upgrade iso4 in the future, use the :ISO4Upgrade command and restart Vim.\n"
        )
    if virtualenv_site_packages not in sys.path:
        sys.path.append(virtualenv_site_packages)
    return True


if _initialize_iso4_env():
    import iso4


def ISO4():

    # get the current selection
    buf = vim.current.buffer
    (lnum1, col1) = buf.mark("<")
    (lnum2, col2) = buf.mark(">")

    if lnum1 > 0:
      # convert to python indices
      lnum1 -= 1
      col2 += 1

    else:
        lnum1, _ = vim.current.window.cursor
        lnum1 -= 1
        lnum2 = lnum1 + 1
        col1, col2 = 0, len(vim.current.line)

    # get the lines from the current buffer
    lines = vim.current.buffer[:]
    selection = [lines.pop(lnum1) for l in range(lnum1, lnum2)]

    # preserve what's before and after on the first and last lines
    head = selection[0][:col1]
    tail = selection[-1][col2:]

    if len(selection) == 1:
      selection[0] = selection[0][col1:col2]
    else:
      selection[0] = selection[0][col1:]
      selection[-1] = selection[-1][:col2]

    selection = " ".join(selection)

    # make the new content
    abrv = iso4.abbreviate(selection)
    lines.insert(lnum1, "".join([head, abrv, tail]))

    # Replace content of buffer
    vim.current.buffer[:] = lines


def ISO4Upgrade():
    _initialize_iso4_env(upgrade=True)
endpython3

command! ISO4Upgrade :py3 ISO4Upgrade()
command! -range ISO4 <line1>,<line2>py3 ISO4()
