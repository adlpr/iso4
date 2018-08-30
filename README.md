# iso4

Implementation of [ISO-4](https://www.iso.org/standard/3569.html) (Rules for the abbreviation of title words and titles of publications) / [CIEPS LTWA](http://www.issn.org/services/online-services/access-to-the-ltwa/) (ISSN International Centre's List of Title Word Abbreviations) as a Python library.

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

## Notes

* Known issues:
  * Python's built-in `str.title()` treats NFKD'd strings badly, resulting in wonky capitalization on conversion:
```python
>>> import unicodedata, iso4
>>> unicodedata.normalize('NFKD', "Bücherei des Orthopäden").title()
'BüCherei Des OrthopäDen'
>>> iso4.abbreviate("Bücherei des Orthopäden")
'BüCh. Orthop.'
```
* Potential future improvements:
  * stricter treatment of language in general
  * better fuzzy matching with diacritics
  * conversion from non-Latin scripts
* Consider this function fairly hacky as is; **do not expect 100% accuracy!**
