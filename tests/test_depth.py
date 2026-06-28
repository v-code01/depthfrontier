from depth import chain_sum, correct, frontier, gen_chain, parse_int


def test_gen_chain_deterministic_and_single_digit():
    a = gen_chain(6, 5, seed=1)
    b = gen_chain(6, 5, seed=1)
    assert a == b                              # deterministic for a fixed seed
    assert len(a) == 5
    for chain in a:
        assert len(chain) == 6
        assert all(1 <= t <= 9 for t in chain)   # every term is a single digit


def test_gen_chain_length_independent_streams():
    # different chain lengths must not share the leading terms of the stream
    assert gen_chain(4, 5, seed=1) != gen_chain(8, 5, seed=1)[:5]


def test_chain_sum():
    assert chain_sum([1, 2, 3, 4]) == 10
    assert chain_sum([9]) == 9


def test_parse_int_last_line_last_integer():
    assert parse_int("42") == 42
    assert parse_int("1 + 2 + 3 = 6") == 6
    assert parse_int("running total...\nfinal: 37") == 37
    assert parse_int("with commas 1,234") == 1234
    assert parse_int("nothing") is None


def test_correct():
    assert correct(10, 10) is True
    assert correct(None, 10) is False
    assert correct(9, 10) is False


def test_frontier_contiguous_max_k():
    assert frontier({2: 1.0, 4: 0.65, 6: 0.25, 8: 0.05}, 0.5) == 4
    assert frontier({2: 0.4}, 0.5) == 0
    assert frontier({2: 1.0, 4: 1.0}, 0.5) == 4
    assert frontier({}, 0.5) == 0
