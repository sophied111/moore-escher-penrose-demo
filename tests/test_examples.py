import examples


def test_families_match_method():
    assert examples.FAMILIES == ["conformal", "poles", "mobius", "square", "rimrings"]


def test_every_example_is_well_formed():
    assert len(examples.EXAMPLES) >= 3
    for row in examples.EXAMPLES:
        prompt, seed, family = row
        assert isinstance(prompt, str) and prompt.strip()
        assert isinstance(seed, int)
        assert family in examples.FAMILIES
