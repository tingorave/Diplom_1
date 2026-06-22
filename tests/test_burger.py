import sys
from pathlib import Path

import pytest
from unittest.mock import Mock

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from burger import Burger


@pytest.fixture
def bun_mock():
    bun = Mock()
    bun.get_price.return_value = 100
    bun.get_name.return_value = "Булка с кунжутом"
    return bun


@pytest.fixture
def ingredient_mock():
    ing = Mock()
    ing.get_price.return_value = 50
    ing.get_name.return_value = "Соус фирменный"
    ing.get_type.return_value = "SAUCE"
    return ing


@pytest.fixture
def burger(bun_mock):
    burger = Burger()
    burger.set_buns(bun_mock)
    return burger


def test_burger_is_initially_without_bun():
    burger = Burger()
    assert burger.bun is None


def test_burger_is_initially_without_ingredients():
    burger = Burger()
    assert burger.ingredients == []


def test_set_buns_sets_bun(bun_mock):
    burger = Burger()
    burger.set_buns(bun_mock)

    assert burger.bun is bun_mock


def test_add_ingredient_appends_to_list(burger, ingredient_mock):
    burger.add_ingredient(ingredient_mock)

    assert ingredient_mock in burger.ingredients
    assert len(burger.ingredients) == 1


def test_remove_ingredient_removes_by_index(burger, ingredient_mock):
    other_ing = Mock()
    burger.add_ingredient(ingredient_mock)
    burger.add_ingredient(other_ing)

    burger.remove_ingredient(0)

    assert len(burger.ingredients) == 1
    assert ingredient_mock not in burger.ingredients
    assert burger.ingredients[0] is other_ing


def test_remove_ingredient_invalid_index_raises_index_error(burger):
    with pytest.raises(IndexError):
        burger.remove_ingredient(0)


def test_move_ingredient_moves_item_to_new_position(burger):
    ing1 = Mock(name="ing1")
    ing2 = Mock(name="ing2")
    ing3 = Mock(name="ing3")

    burger.add_ingredient(ing1)
    burger.add_ingredient(ing2)
    burger.add_ingredient(ing3)

    burger.move_ingredient(0, 2)

    assert burger.ingredients == [ing2, ing3, ing1]


def test_move_ingredient_invalid_index_raises_index_error(burger):
    ing = Mock()
    burger.add_ingredient(ing)

    with pytest.raises(IndexError):
        burger.move_ingredient(5, 0)


@pytest.mark.parametrize(
    "bun_price, ingredient_prices, expected_price",
    [
        (100, [], 200),                    # только булка
        (50, [20], 120),                   # булка + 1 ингредиент
        (30, [10, 20, 40], 2*30+10+20+40)  # булка + 3 ингредиента
    ]
)
def test_get_price_calculates_correct_total(bun_price, ingredient_prices, expected_price):
    burger = Burger()

    bun = Mock()
    bun.get_price.return_value = bun_price
    bun.get_name.return_value = "Булка"
    burger.set_buns(bun)

    for price in ingredient_prices:
        ing = Mock()
        ing.get_price.return_value = price
        ing.get_name.return_value = "Ингредиент"
        ing.get_type.return_value = "FILLING"
        burger.add_ingredient(ing)

    assert burger.get_price() == expected_price


def test_get_price_without_bun_raises_attribute_error():
    burger = Burger()

    with pytest.raises(AttributeError):
        burger.get_price()


def test_get_receipt_contains_bun_and_price(burger, ingredient_mock):
    burger.add_ingredient(ingredient_mock)

    receipt = burger.get_receipt()
    lines = receipt.split("\n")

    assert lines[0] == f"(==== {burger.bun.get_name()} ====)"

    assert lines[-1] == f"Price: {burger.get_price()}"


def test_get_receipt_contains_ingredient_line(burger):
    ing = Mock()
    ing.get_name.return_value = "Соус фирменный"
    ing.get_type.return_value = "SAUCE"
    ing.get_price.return_value = 50
    burger.add_ingredient(ing)

    receipt = burger.get_receipt()
    lines = receipt.split("\n")

    expected_line = "= sauce Соус фирменный ="
    assert expected_line in lines


def test_get_receipt_without_bun_raises_attribute_error():
    burger = Burger()

    with pytest.raises(AttributeError):
        burger.get_receipt()            
