


<picture>
  <source media="(prefers-color-scheme: light)" srcset="./assets/bender_slackbot.png" width='100%'>
  <img alt="Project logo" src="/assets/" width="100%">
</picture>

<br>

[![tests](https://github.com/bojana-rankovic/bender-the-bot/actions/workflows/tests.yml/badge.svg)](https://github.com/bojana-rankovic/bender-the-bot)
[![PyPI](https://img.shields.io/pypi/v/bender-the-bot)](https://img.shields.io/pypi/v/bender-the-bot)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bender-the-bot)](https://img.shields.io/pypi/pyversions/bender-the-bot)
[![Documentation Status](https://readthedocs.org/projects/bender/badge/?version=latest)](https://bender.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Cookiecutter template from @bojana-rankovic](https://img.shields.io/badge/Cookiecutter-bojana-rankovic-blue)](https://github.com/bojana-rankovic/liac-repo)
[![Learn more @bojana-rankovic](https://img.shields.io/badge/Learn%20%0Amore-bojana-rankovic-blue)](https://bojana-rankovic.github.io)




<h1 align="center">
  bender
</h1>

### Note: functionality is split between branches: main and redirect_users 

<br>


## Check out the demo!


https://github.com/bojana-rankovic/bender-the-bot/assets/11743428/5be9b60f-0579-475f-b3f9-5f492c90bd36




Bender is the nicest bot! Use it in your Slack workspace to make your life easier.

## 🔥 Usage

> TODO show in a very small amount of space the **MOST** useful thing your package can do.
> Make it as short as possible! You have an entire set of docs for later.


## 👩‍💻 Installation

<!-- Uncomment this section after your first ``tox -e finish``
The most recent release can be installed from
[PyPI](https://pypi.org/project/bender/) with:

```shell
$ pip install bender
```
-->

The most recent code and data can be installed directly from GitHub with:

```bash
$ pip install git+https://github.com/bojana-rankovic/bender-the-bot.git
```




## 🛠️ For Developers


<details>
  <summary>See developer instructions</summary>



### 👐 Contributing

Contributions, whether filing an issue, making a pull request, or forking, are appreciated. See
[CONTRIBUTING.md](https://github.com/bojana-rankovic/bender-the-bot/blob/master/.github/CONTRIBUTING.md) for more information on getting involved.


### Development Installation

To install in development mode, use the following:

```bash
$ git clone git+https://github.com/bojana-rankovic/bender-the-bot.git
$ cd bender-the-bot
$ pip install -e .
```

### 🥼 Testing

After cloning the repository and installing `tox` with `pip install tox`, the unit tests in the `tests/` folder can be
run reproducibly with:

```shell
$ tox
```

Additionally, these tests are automatically re-run with each commit in a [GitHub Action](https://github.com/bojana-rankovic/bender-the-bot/actions?query=workflow%3ATests).

### 📖 Building the Documentation

The documentation can be built locally using the following:

```shell
$ git clone git+https://github.com/bojana-rankovic/bender-the-bot.git
$ cd bender-the-bot
$ tox -e docs
$ open docs/build/html/index.html
```

The documentation automatically installs the package as well as the `docs`
extra specified in the [`setup.cfg`](setup.cfg). `sphinx` plugins
like `texext` can be added there. Additionally, they need to be added to the
`extensions` list in [`docs/source/conf.py`](docs/source/conf.py).

### 📦 Making a Release

After installing the package in development mode and installing
`tox` with `pip install tox`, the commands for making a new release are contained within the `finish` environment
in `tox.ini`. Run the following from the shell:

```shell
$ tox -e finish
```

This script does the following:

1. Uses [Bump2Version](https://github.com/c4urself/bump2version) to switch the version number in the `setup.cfg`,
   `src/bender/version.py`, and [`docs/source/conf.py`](docs/source/conf.py) to not have the `-dev` suffix
2. Packages the code in both a tar archive and a wheel using [`build`](https://github.com/pypa/build)
3. Uploads to PyPI using [`twine`](https://github.com/pypa/twine). Be sure to have a `.pypirc` file configured to avoid the need for manual input at this
   step
4. Push to GitHub. You'll need to make a release going with the commit where the version was bumped.
5. Bump the version to the next patch. If you made big changes and want to bump the version by minor, you can
   use `tox -e bumpversion -- minor` after.
</details>
