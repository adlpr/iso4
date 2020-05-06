# iso4

Implementation of [ISO 4](https://www.iso.org/standard/3569.html) (Rules for the abbreviation of title words and titles of publications) / [CIEPS LTWA](http://www.issn.org/services/online-services/access-to-the-ltwa/) (ISSN International Centre's List of Title Word Abbreviations) as a Python library.

## Usage

```python
>>> from iso4 import abbreviate

>>> abbreviate("Recent Advances in Studies on Cardiac Structure and Metabolism")
'Recent Adv. Stud. Card. Struct. Metab.'

>>> abbreviate("Journal of the American Academy of Dermatology", periods=False)
'J Am Acad Dermatol'

>>> abbreviate("Real Living with Multiple Sclerosis")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  ...
Exception: Ambiguous word in title: real; must disambiguate between langs: eng, fre, spa

>>> abbreviate("Real Living with Multiple Sclerosis", disambiguation_langs=['eng'])
'Real Living Mult. Scler.'

>>> abbreviate("Anales de la Real Academia de Farmacia", True, ['spa'])
'An. R. Acad. Farm.'
```

## VIM Plugin

A VIM plugin allows to abbreviate names directly from inside vim.

### Install with Vundle

The easiest way to install the plugin is via a vim plugin manager.
I use [vundle](https://github.com/VundleVim/Vundle.vim)
Then, just add the following to your `.vimrc` file.
```
Plugin  'adlpr/iso4'
```
Then run `:PluginInstall` from within VIM.

### Use

The following command will change the current line to its abbreviation
```
:ISO4
```
The command can also be used in visual mode.

## Notes

* Potential future improvements:
  * stricter treatment of language in general
  * better fuzzy matching with diacritics
  * conversion from non-Latin scripts
* Consider this function fairly hacky as is; **do not expect 100% accuracy!**
