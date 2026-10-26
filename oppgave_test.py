"""Automatisk retting av 1T-02-likningssett.

Hver sjekk i SJEKKER er én deltest, og poengene fordeles likt på dem.
De samme sjekkene ligger i "Test løsningen din"-cellen nederst i notebooken.
"""
import pytest

from notebook_loader import last_notebook

def naer(a, b, rel=1e-3):
    """Sant hvis tallet a er innenfor rel (relativt) av b."""
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if b == 0:
        return abs(a) < 1e-9
    return abs(a - b) <= rel * abs(b)


def S(tekst):
    """Gjør tekst om til et sympy-uttrykk, f.eks. S("x**2 - 1")."""
    import sympy
    return sympy.sympify(tekst, locals={n: sympy.Symbol(n) for n in ("N", "O", "Q", "S")})


def lik(a, b):
    """Sant hvis a og b er matematisk like.

    Lister og mengder sammenlignes uten hensyn til rekkefølge, tupler (koordinater) i rekkefølge.
    """
    import sympy
    if a is None:
        return False
    if isinstance(b, tuple):
        if not isinstance(a, (tuple, list, sympy.Tuple)) or len(a) != len(b):
            return False
        return all(lik(x, y) for x, y in zip(a, b))
    if isinstance(b, (list, set)):
        if isinstance(a, sympy.FiniteSet):
            a = list(a)
        if not isinstance(a, (list, tuple, set)) or len(a) != len(b):
            return False
        rest = list(a)
        for y in b:
            for i, x in enumerate(rest):
                if lik(x, y):
                    del rest[i]
                    break
            else:
                return False
        return True
    if isinstance(b, dict):
        if not isinstance(a, dict) or len(a) != len(b):
            return False
        a = {str(k): v for k, v in a.items()}
        return all(str(k) in a and lik(a[str(k)], v) for k, v in b.items())
    try:
        a, b = sympy.sympify(a), sympy.sympify(b)
    except (sympy.SympifyError, TypeError):
        return False
    vanlige = lambda u: u.subs({s: sympy.Symbol(s.name) for s in u.free_symbols})
    a, b = vanlige(a), vanlige(b)
    if isinstance(a, sympy.Set) or isinstance(b, sympy.Set):
        return a == b
    if getattr(b, "is_Relational", False):
        return a == b
    try:
        return sympy.simplify(a - b) == 0
    except TypeError:
        return a == b

oppgave = last_notebook("oppgave")

SJEKKER = [
    ('1a', 'losning_1a skal være x = 2, y = 3', "lik(losning_1a, {'x': 2, 'y': 3})"),
    ('1b', 'losning_1b skal være x = 1, y = 2, z = 3', "lik(losning_1b, {'x': 1, 'y': 2, 'z': 3})"),
    ('3', 'honer og kuer skal være 30 og 20', 'lik(honer, 30) and lik(kuer, 20)'),
    ('4_en', 'antall_losninger(1, 1, 2, 1, -1, 0) skal gi 1', 'antall_losninger(1, 1, 2, 1, -1, 0) == 1'),
    ('4_ingen', 'antall_losninger(1, 1, 2, 1, 1, 5) skal gi 0 (parallelle linjer)', 'antall_losninger(1, 1, 2, 1, 1, 5) == 0'),
    ('4_uendelig', "antall_losninger(1, 1, 2, 2, 2, 4) skal gi 'uendelig' (samme linje)", "antall_losninger(1, 1, 2, 2, 2, 4) == 'uendelig'"),
    ('4_vannrett', 'antall_losninger(0, 1, 3, 1, 0, 2) skal gi 1', 'antall_losninger(0, 1, 3, 1, 0, 2) == 1'),
    ('5', 'skjaering_5 skal være punktene (-1, -3) og (3, 5)', 'lik(skjaering_5, [(-1, -3), (3, 5)])'),
    ('6', 'bolle, kaffe og juice skal koste 20, 30 og 25 kr', 'lik(bolle, 20) and lik(kaffe, 30) and lik(juice, 25)'),
]


@pytest.mark.parametrize(
    "beskrivelse,uttrykk", [s[1:] for s in SJEKKER], ids=[s[0] for s in SJEKKER]
)
def test_sjekk(beskrivelse, uttrykk):
    navnerom = {**vars(oppgave), "naer": naer, "lik": lik, "S": S}
    assert eval(uttrykk, navnerom), beskrivelse
