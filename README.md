<h1 align="center">Terminal UI for Reddit (TUIR)</h1>

<p align="center">
A text-based interface (TUI) to view and interact with Reddit from your terminal.<br>
</p>

<p align="center">
  <strong>TUIR is a fork of rtv, which was maintained by Michael Lazar in <a href="https://github.com/michael-lazar/rtv">this respository</a> until Jun 3, 2019.</strong><br>
</p>

<p align="center">
<img alt="title image" src="resources/title_image.png"/>
</p>

<p align="center">
  <a href="https://pypi.python.org/pypi/tuir/">
    <img alt="pypi" src="https://img.shields.io/pypi/v/tuir.svg?label=version"/>
  </a>
  <a href="https://gitlab.com/ajak/tuir/pipelines?ref=master">
    <img alt="gitlab-ci" src="https://gitlab.com/ajak/tuir/badges/master/build.svg"/>
  </a> 
  <img alt="coverage" src="https://gitlab.com/ajak/tuir/badges/master/coverage.svg"/>
  <a href="https://repology.org/project/tuir/versions">
    <img src="https://repology.org/badge/tiny-repos/tuir.svg" alt="Packaging status">
  </a>
</p>
<!--
  <a href="https://saythanks.io/to/michael-lazar">
    <img alt="say-thanks" src="https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg"/>
  </a>
</p> -->

## Table of Contents

* [Demo](#demo)  
* [Installation](#installation)  
* [Usage](#usage)  
* [Settings](#settings)
* [Themes](#themes)
* [FAQ](#faq)  
* [Contributing](#contributing)  
* [License](#license)  

## Demo

<p align="center">
<img alt="title image" src="resources/demo.gif"/>
</p>

<!-- You can use *telnet* or *ssh* to try out a lite version of RTV directly in your terminal, without needing to install it:

- ``$ telnet redditbox.us``
- ``$ ssh redditbox.us``

*[redditbox.us](https://redditbox.us/) is an independent project by Alex Jarmoszuk* -->

## Installation

### PyPI package

TUIR is available on [PyPI](https://pypi.python.org/pypi/tuir/) and can be installed with pip:

```bash
$ pip install tuir
```

#### Migration from RTV

If you are migrating from RTV to TUIR, you can simply rename your old config directory/config file:

```bash
$ mv ~/.config/rtv ~/.config/tuir
$ mv ~/.config/tuir/rtv.cfg ~/.config/tuir/tuir.cfg
```

Please take care to use the new API keys for Imgur and Reddit. To replace with sed:

```bash
$ sed -i 's/E2oEtRQfdfAfNQ/zjyhNI7tK8ivzQ/; s/93396265f59dec9/b33d69ac8931734/' ~/.config/tuir/tuir.cfg
```

### Distro packages

See [Repology](https://repology.org/metapackage/tuir/packages) for an up-to-date list of supported distro packages.

#### Arch

TUIR is available from the AUR with the package name `TUIR`.

<!-- ```bash
# macOS
$ brew install rtv

# Arch
$ pacman -S rtv

# Nix
$ nix-env -i rtv

# Debian
$ apt install rtv

# FreeBSD
$ pkg install rtv
```-->

### From source

```bash
$ git clone https://gitlab.com/ajak/tuir.git
$ cd tuir
$ python setup.py install
```

### Windows

TUIR is not supported on Windows, due to a lack of resources and interest. Sorry!

## Usage

To run the program, type:

```bash
$ tuir --help
```

### Controls

Move the cursor using either the arrow keys or *Vim* style movement:

- Press <kbd>▲</kbd> and <kbd>▼</kbd> to scroll through submissions
- Press <kbd>▶</kbd> to view the selected submission and <kbd>◀</kbd> to return
- Press <kbd>space-bar</kbd> to expand/collapse comments
- Press <kbd>u</kbd> to login (this requires a web browser for [OAuth](https://github.com/reddit-archive/reddit/wiki/oauth2))
- Press <kbd>?</kbd> to open the help screen

Press <kbd>/</kbd> to open the navigation prompt, where you can type things like:

- ``/front``
- ``/r/commandprompt+linuxmasterrace``
- ``/r/programming/controversial``
- ``/u/me``
- ``/u/multi-mod/m/art``
- ``/domain/github.com``

See [CONTROLS](CONTROLS.md) for the full list of commands.

## Settings

### Configuration File

Configuration files are stored in the ``{HOME}/.config/tuir/`` directory.

Check out [tuir.cfg](tuir/templates/tuir.cfg) for the full list of configurable options. You can clone this file into your home directory by running:

```bash
$ tuir --copy-config
```

### Viewing Media Links

You can use [mailcap](https://en.wikipedia.org/wiki/Media_type#Mailcap) to configure how TUIR will open different types of links.

<p align="center">
<img alt="title image" src="resources/mailcap.gif"/>
</p>

A mailcap file allows you to associate different MIME media types, like ``image/jpeg`` or ``video/mp4``, with shell commands. This feature is disabled by default because it takes a few extra steps to configure. To get started, copy the default mailcap template to your home directory.

```bash
$ tuir --copy-mailcap
```

This template contains examples for common MIME types that work with popular reddit websites like *imgur*, *youtube*, and *gfycat*. Open the mailcap template and follow the [instructions](tuir/templates/mailcap) listed inside.

Once you've setup your mailcap file, enable it by launching tuir with the ``tuir --enable-media`` flag (or set it in your **tuir.cfg**)

### Environment Variables

The default programs that TUIR interacts with can be configured through environment variables:

<table>
  <tr>
  <td><strong>$TUIR_EDITOR</strong></td>
  <td>A program used to compose text submissions and comments, e.g. <strong>vim</strong>, <strong>emacs</strong>, <strong>gedit</strong>
  <br/> <em>If not specified, will fallback to $VISUAL and $EDITOR in that order.</em></td>
  </tr>
  <tr>
  <td><strong>$TUIR_BROWSER</strong></td>
  <td>A program used to open links to external websites, e.g. <strong>firefox</strong>, <strong>google-chrome</strong>, <strong>w3m</strong>, <strong>lynx</strong>
  <br/> <em>If not specified, will fallback to $BROWSER, or your system's default browser.</em></td>
  </tr>
  <tr>
  <td><strong>$TUIR_URLVIEWER</strong></td>
  <td>A tool used to extract hyperlinks from blocks of text, e.g. <a href=https://github.com/sigpipe/urlview>urlview</a>, <a href=https://github.com/firecat53/urlscan>urlscan</a>
  <br/> <em>If not specified, will fallback to urlview if it is installed.</em></td>
  </tr>
</table>

### Clipboard

TUIR supports copying submission links to the OS clipboard.  Data being copied is piped into a command specified by the configuration option `clipboard_cmd`. If this option is not set, the command will default to `pbcopy w` on Darwin systems (OSX), and `xclip -selection clipboard` on Linux.

## Themes

Themes can be used to customize the look and feel of TUIR

<table>
  <tr>
    <td align="center">
      <p><strong>Solarized Dark</strong></p>
      <img src="resources/theme_solarized_dark.png"></img>
    </td>
    <td align="center">
      <p><strong>Solarized Light</strong></p>
      <img src="resources/theme_solarized_light.png"></img>
    </td>
  </tr>
  <tr>
    <td align="center">
      <p><strong>Papercolor</strong></p>
      <img src="resources/theme_papercolor.png"></img>
    </td>
    <td align="center">
      <p><strong>Molokai</strong></p>
      <img src="resources/theme_molokai.png"></img>
    </td>
  </tr>
</table>

You can list all installed themes with the ``--list-themes`` command, and select one with ``--theme``. You can save your choice permanently in your [tuir.cfg](tuir/templates/tuir.cfg) file. You can also use the <kbd>F2</kbd> & <kbd>F3</kbd> keys inside of TUIR to cycle through all available themes.

For instructions on writing and installing your own themes, see [THEMES.md](THEMES.md).

## FAQ

<details>
 <summary>Why am I getting an error during installation/when launching tuir?</summary>
 
  > If your distro ships with an older version of python 2.7 or python-requests,
  > you may experience SSL errors or other package incompatibilities. The
  > easiest way to fix this is to install tuir using python 3. If you
  > don't already have pip3, see http://stackoverflow.com/a/6587528 for setup
  > instructions. Then do
  >
  > ```bash
  > $ sudo pip uninstall tuir
  > $ sudo pip3 install -U tuir
  > ```

</details>
<details>
  <summary>Why do I see garbled text like <em>M-b~@M-"</em> or <em>^@</em>?</summary>
 
  > This type of text usually shows up when python is unable to render
  > unicode properly.
  >    
  > 1. Try starting TUIR in ascii-only mode with ``tuir --ascii``
  > 2. Make sure that the terminal/font that you're using supports unicode
  > 3. Try [setting the LOCALE to utf-8](https://perlgeek.de/en/article/set-up-a-clean-utf8-environment)
  > 4. Your python may have been built against the wrong curses library,
  >    see [here](stackoverflow.com/questions/19373027) and
  >    [here](https://bugs.python.org/issue4787) for more information

</details>
<details>
 <summary>How do I run the code directly from the repository?</summary>
 
  > This project is structured to be run as a python *module*. This means that
  > you need to launch it using python's ``-m`` flag. See the example below, which
  > assumes that you have cloned the repository into the directory **~/tuir_project**.
  >
  > ```bash
  > $ cd ~/tuir_project
  > $ python3 -m tuir
  > ```

</details>

## Contributing
All feedback and suggestions are welcome, just post an issue!

Before writing any code, please read the [Contributor Guidelines](CONTRIBUTING.rst).

## License
This project is distributed under the [MIT](LICENSE) license.
