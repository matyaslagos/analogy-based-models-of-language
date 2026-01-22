#!/usr/bin/env python3
"""Tests for Radix Trie V3 (compact implementation with single freq integers)."""

import syntax_model as syn
import radix_trie_v3 as radix_v3


def test_basic_insertion():
    print("\n=== Test 1: Basic Insertion ===")

    standard = syn.FreqTrie()
    radix = radix_v3.RadixFreqTrie()

    seq = ('<', 'the', 'cat', '>')
    standard._insert(seq)
    radix._insert(seq)

    test_cases = [(), ('<',), ('<', 'the'), ('<', 'the', 'cat'), ('<', 'the', 'cat', '>'),
                  ('the',), ('the', 'cat'), ('cat',), ('cat', '>'), ('>',)]

    all_passed = True
    for s in test_cases:
        std_f = standard.freq(s)
        rad_f = radix.freq(s)
        match = "✓" if std_f == rad_f else "✗"
        if std_f != rad_f:
            all_passed = False
        print(f"{match} freq({s}): standard={std_f}, v3={rad_f}")

    return all_passed


def test_multiple_insertions():
    print("\n=== Test 2: Multiple Insertions ===")

    standard = syn.FreqTrie()
    radix = radix_v3.RadixFreqTrie()

    sequences = [
        ('<', 'the', 'cat', '>'),
        ('<', 'the', 'dog', '>'),
        ('<', 'the', 'cat', 'ran', '>'),
        ('<', 'a', 'dog', '>'),
    ]

    for seq in sequences:
        standard._insert(seq)
        radix._insert(seq)

    test_cases = [('<',), ('<', 'the'), ('<', 'the', 'cat'), ('<', 'the', 'dog'),
                  ('the',), ('the', 'cat'), ('cat', 'ran'), ('dog', '>')]

    all_passed = True
    for s in test_cases:
        std_f = standard.freq(s)
        rad_f = radix.freq(s)
        match = "✓" if std_f == rad_f else "✗"
        if std_f != rad_f:
            all_passed = False
        print(f"{match} freq({s}): standard={std_f}, v3={rad_f}")

    return all_passed


def test_small_corpus():
    print("\n=== Test 3: Small Corpus ===")

    standard = syn.FreqTrie()
    radix = radix_v3.RadixFreqTrie()

    standard.setup('syntax/corpora/small_test_corpus.txt')
    radix.setup('syntax/corpora/small_test_corpus.txt')

    test_cases = [('<',), ('<', 'some'), ('<', 'some', 'dog'), ('dog',), ('dog', 'was'),
                  ('was',), ('was', 'barking'), ('the',), ('the', 'street'), ('around', 'the')]

    all_passed = True
    for s in test_cases:
        std_f = standard.freq(s)
        rad_f = radix.freq(s)
        match = "✓" if std_f == rad_f else "✗"
        if std_f != rad_f:
            all_passed = False
        print(f"{match} freq({s}): standard={std_f}, v3={rad_f}")

    return all_passed


def test_right_neighbors():
    print("\n=== Test 4: Right Neighbors ===")

    standard = syn.FreqTrie()
    radix = radix_v3.RadixFreqTrie()

    sequences = [
        ('<', 'the', 'cat', 'ran', '>'),
        ('<', 'the', 'cat', 'jumped', '>'),
        ('<', 'the', 'dog', 'ran', '>'),
    ]

    for seq in sequences:
        standard._insert(seq)
        radix._insert(seq)

    test_seq = ('<', 'the', 'cat')
    std_neighbors = sorted(list(standard.right_neighbors(test_seq)))
    rad_neighbors = sorted(list(radix.right_neighbors(test_seq)))

    print(f"Standard: {std_neighbors}")
    print(f"V3:       {rad_neighbors}")

    passed = std_neighbors == rad_neighbors
    print(f"{'✓' if passed else '✗'} Right neighbors match")
    return passed


def test_left_neighbors():
    print("\n=== Test 5: Left Neighbors ===")

    standard = syn.FreqTrie()
    radix = radix_v3.RadixFreqTrie()

    sequences = [
        ('<', 'the', 'cat', 'ran', '>'),
        ('<', 'a', 'cat', 'ran', '>'),
        ('<', 'the', 'dog', 'ran', '>'),
    ]

    for seq in sequences:
        standard._insert(seq)
        radix._insert(seq)

    test_seq = ('cat', 'ran')
    std_neighbors = sorted(list(standard.left_neighbors(test_seq)))
    rad_neighbors = sorted(list(radix.left_neighbors(test_seq)))

    print(f"Standard: {std_neighbors}")
    print(f"V3:       {rad_neighbors}")

    passed = std_neighbors == rad_neighbors
    print(f"{'✓' if passed else '✗'} Left neighbors match")
    return passed


def test_shared_right_neighbors():
    print("\n=== Test 6: Shared Right Neighbors ===")

    standard = syn.FreqTrie()
    radix = radix_v3.RadixFreqTrie()

    sequences = [
        ('<', 'the', 'cat', 'ran', 'fast', '>'),
        ('<', 'the', 'cat', 'jumped', 'high', '>'),
        ('<', 'the', 'dog', 'ran', 'fast', '>'),
        ('<', 'the', 'dog', 'jumped', 'high', '>'),
    ]

    for seq in sequences:
        standard._insert(seq)
        radix._insert(seq)

    seq1, seq2 = ('<', 'the', 'cat'), ('<', 'the', 'dog')
    std_shared = sorted(list(standard.shared_right_neighbors(seq1, seq2)))
    rad_shared = sorted(list(radix.shared_right_neighbors(seq1, seq2)))

    print(f"Standard: {std_shared}")
    print(f"V3:       {rad_shared}")

    passed = std_shared == rad_shared
    print(f"{'✓' if passed else '✗'} Shared right neighbors match")
    return passed


def test_shared_left_neighbors():
    print("\n=== Test 7: Shared Left Neighbors ===")

    standard = syn.FreqTrie()
    radix = radix_v3.RadixFreqTrie()

    sequences = [
        ('<', 'the', 'big', 'cat', 'ran', '>'),
        ('<', 'a', 'big', 'cat', 'ran', '>'),
        ('<', 'the', 'big', 'dog', 'ran', '>'),
        ('<', 'a', 'big', 'dog', 'ran', '>'),
    ]

    for seq in sequences:
        standard._insert(seq)
        radix._insert(seq)

    seq1, seq2 = ('cat', 'ran'), ('dog', 'ran')
    std_shared = sorted(list(standard.shared_left_neighbors(seq1, seq2)))
    rad_shared = sorted(list(radix.shared_left_neighbors(seq1, seq2)))

    print(f"Standard: {std_shared}")
    print(f"V3:       {rad_shared}")

    passed = std_shared == rad_shared
    print(f"{'✓' if passed else '✗'} Shared left neighbors match")
    return passed


def test_edge_compression():
    print("\n=== Test 8: Edge Compression ===")

    radix = radix_v3.RadixFreqTrie()

    seq = ('<', 'this', 'is', 'a', 'very', 'long', 'unique', 'sequence', '>')
    radix._insert(seq)

    test_cases = [
        ('<', 'this'),
        ('<', 'this', 'is', 'a'),
        ('<', 'this', 'is', 'a', 'very', 'long'),
        ('<', 'this', 'is', 'a', 'very', 'long', 'unique', 'sequence', '>'),
    ]

    all_passed = True
    for s in test_cases:
        freq = radix.freq(s)
        expected = 1
        match = "✓" if freq == expected else "✗"
        if freq != expected:
            all_passed = False
        print(f"{match} freq({s[-2:]}...): expected={expected}, got={freq}")

    # Check compression
    node = radix.fw_root
    if '<' in node.children:
        child = node.children['<']
        edge_len = len(child.edge_label)
        print(f"\nFirst edge has {edge_len} tokens: {child.edge_label[:3]}...")
        print(f"{'✓' if edge_len > 1 else '○'} Edge compression active: {edge_len > 1}")

    return all_passed


def test_length_constraints():
    print("\n=== Test 9: Length Constraints ===")

    standard = syn.FreqTrie()
    radix = radix_v3.RadixFreqTrie()

    sequences = [
        ('<', 'a', 'b', 'c', 'd', '>'),
        ('<', 'a', 'x', '>'),
        ('<', 'a', 'y', 'z', '>'),
    ]

    for seq in sequences:
        standard._insert(seq)
        radix._insert(seq)

    base = ('<', 'a')
    std_neighbors = sorted(list(standard.right_neighbors(base, min_length=2, max_length=3)))
    rad_neighbors = sorted(list(radix.right_neighbors(base, min_length=2, max_length=3)))

    print(f"Standard: {std_neighbors}")
    print(f"V3:       {rad_neighbors}")

    passed = std_neighbors == rad_neighbors
    print(f"{'✓' if passed else '✗'} Length constraints match")
    return passed


def test_repeated_insertions():
    print("\n=== Test 10: Repeated Insertions ===")

    standard = syn.FreqTrie()
    radix = radix_v3.RadixFreqTrie()

    seq = ('<', 'hello', 'world', '>')
    for _ in range(5):
        standard._insert(seq)
        radix._insert(seq)

    test_cases = [('<', 'hello'), ('<', 'hello', 'world'), ('hello',), ('world',)]

    all_passed = True
    for s in test_cases:
        std_f = standard.freq(s)
        rad_f = radix.freq(s)
        match = "✓" if std_f == rad_f else "✗"
        if std_f != rad_f:
            all_passed = False
        print(f"{match} freq({s}): standard={std_f}, v3={rad_f}")

    return all_passed


def run_all_tests():
    print("=" * 60)
    print("RADIX TRIE V3 TEST SUITE")
    print("=" * 60)

    tests = [
        ("Basic Insertion", test_basic_insertion),
        ("Multiple Insertions", test_multiple_insertions),
        ("Small Corpus", test_small_corpus),
        ("Right Neighbors", test_right_neighbors),
        ("Left Neighbors", test_left_neighbors),
        ("Shared Right Neighbors", test_shared_right_neighbors),
        ("Shared Left Neighbors", test_shared_left_neighbors),
        ("Edge Compression", test_edge_compression),
        ("Length Constraints", test_length_constraints),
        ("Repeated Insertions", test_repeated_insertions),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    print("=" * 60)

    return passed_count == total_count


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
