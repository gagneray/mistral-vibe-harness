"""Tests de src/calcul.py."""

import pytest

from calcul import additionner, moyenne


def test_additionner_entiers():
    assert additionner(2, 3) == 5


def test_additionner_negatif():
    assert additionner(-1, 1) == 0


def test_moyenne():
    assert moyenne([1, 2, 3, 4]) == 2.5


def test_moyenne_un_element():
    assert moyenne([7.0]) == pytest.approx(7.0)
