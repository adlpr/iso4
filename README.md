# iso4

Implementation of [ISO-4](https://www.iso.org/standard/3569.html) (Rules for the abbreviation of title words and titles of publications) as a Python library.

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
