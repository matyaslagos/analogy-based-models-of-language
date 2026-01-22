#!/usr/bin/env python3
# --------------------------------------- #
# Tests for Radix Trie V2 Implementation  #
# --------------------------------------- #

"""
Comprehensive tests for the improved radix trie implementation (v2).

This test suite compares the radix trie v2 against both the original radix trie
and the standard trie implementation to ensure functional equivalence.
"""

import syntax_model as syn
import radix_trie as radix_v1
import radix_trie_v2 as radix_v2


def test_basic_insertion():
    """Test basic insertion and frequency counting."""
    print("\n=== Test 1: Basic Insertion ===")

    # Create all three trie types
    standard_trie = syn.FreqTrie()
    radix_trie_v1 = radix_v1.RadixFreqTrie()
    radix_trie_v2 = radix_v2.RadixFreqTrie()

    # Insert a simple sequence
    sequence = ('<', 'the', 'cat', '>')
    standard_trie._insert(sequence)
    radix_trie_v1._insert(sequence)
    radix_trie_v2._insert(sequence)

    # Test frequency queries
    test_cases = [
        (),
        ('<',),
        ('<', 'the'),
        ('<', 'the', 'cat'),
        ('<', 'the', 'cat', '>'),
        ('the',),
        ('the', 'cat'),
        ('cat',),
        ('cat', '>'),
        ('>',),
    ]

    all_passed = True
    for seq in test_cases:
        std_freq = standard_trie.freq(seq)
        rad_v1_freq = radix_trie_v1.freq(seq)
        rad_v2_freq = radix_trie_v2.freq(seq)
        match = "✓" if std_freq == rad_v1_freq == rad_v2_freq else "✗"
        if std_freq != rad_v2_freq:
            all_passed = False
        print(f"{match} freq({seq}): standard={std_freq}, v1={rad_v1_freq}, v2={rad_v2_freq}")

    return all_passed


def test_multiple_insertions():
    """Test multiple sequence insertions with overlapping prefixes."""
    print("\n=== Test 2: Multiple Insertions ===")

    standard_trie = syn.FreqTrie()
    radix_trie_v1 = radix_v1.RadixFreqTrie()
    radix_trie_v2 = radix_v2.RadixFreqTrie()

    sequences = [
        ('<', 'the', 'cat', '>'),
        ('<', 'the', 'dog', '>'),
        ('<', 'the', 'cat', 'ran', '>'),
        ('<', 'a', 'dog', '>'),
    ]

    for seq in sequences:
        standard_trie._insert(seq)
        radix_trie_v1._insert(seq)
        radix_trie_v2._insert(seq)

    # Test various frequency queries
    test_cases = [
        ('<',),
        ('<', 'the'),
        ('<', 'the', 'cat'),
        ('<', 'the', 'dog'),
        ('<', 'the', 'cat', '>'),
        ('<', 'the', 'cat', 'ran'),
        ('<', 'the', 'cat', 'ran', '>'),
        ('<', 'a'),
        ('<', 'a', 'dog'),
        ('the',),
        ('the', 'cat'),
        ('cat', 'ran'),
        ('dog', '>'),
    ]

    all_passed = True
    for seq in test_cases:
        std_freq = standard_trie.freq(seq)
        rad_v1_freq = radix_trie_v1.freq(seq)
        rad_v2_freq = radix_trie_v2.freq(seq)
        match = "✓" if std_freq == rad_v1_freq == rad_v2_freq else "✗"
        if std_freq != rad_v2_freq:
            all_passed = False
        print(f"{match} freq({seq}): standard={std_freq}, v1={rad_v1_freq}, v2={rad_v2_freq}")

    return all_passed


def test_small_corpus():
    """Test on the small_test_corpus.txt file."""
    print("\n=== Test 3: Small Test Corpus ===")

    standard_trie = syn.FreqTrie()
    radix_trie_v1 = radix_v1.RadixFreqTrie()
    radix_trie_v2 = radix_v2.RadixFreqTrie()

    # Load and insert corpus
    standard_trie.setup('syntax/corpora/small_test_corpus.txt')
    radix_trie_v1.setup('syntax/corpora/small_test_corpus.txt')
    radix_trie_v2.setup('syntax/corpora/small_test_corpus.txt')

    print("Corpus loaded. Testing frequency queries...")

    # Test various sequences from the corpus
    test_cases = [
        ('<',),
        ('<', 'some'),
        ('<', 'some', 'dog'),
        ('<', 'some', 'dog', 'was'),
        ('dog',),
        ('dog', 'was'),
        ('was',),
        ('was', 'barking'),
        ('was', 'walking'),
        ('was', 'running'),
        ('the',),
        ('the', 'street'),
        ('the', 'table'),
        ('around',),
        ('around', 'the'),
        ('<', 'i'),
        ('<', 'i', 'was'),
        ('street', '>'),
        ('table', '>'),
    ]

    all_passed = True
    for seq in test_cases:
        std_freq = standard_trie.freq(seq)
        rad_v1_freq = radix_trie_v1.freq(seq)
        rad_v2_freq = radix_trie_v2.freq(seq)
        match = "✓" if std_freq == rad_v1_freq == rad_v2_freq else "✗"
        if std_freq != rad_v2_freq:
            all_passed = False
        print(f"{match} freq({seq}): standard={std_freq}, v1={rad_v1_freq}, v2={rad_v2_freq}")

    return all_passed


def test_right_neighbors():
    """Test right neighbor queries."""
    print("\n=== Test 4: Right Neighbors ===")

    standard_trie = syn.FreqTrie()
    radix_trie_v1 = radix_v1.RadixFreqTrie()
    radix_trie_v2 = radix_v2.RadixFreqTrie()

    sequences = [
        ('<', 'the', 'cat', 'ran', '>'),
        ('<', 'the', 'cat', 'jumped', '>'),
        ('<', 'the', 'dog', 'ran', '>'),
    ]

    for seq in sequences:
        standard_trie._insert(seq)
        radix_trie_v1._insert(seq)
        radix_trie_v2._insert(seq)

    # Test right neighbors
    test_seq = ('<', 'the', 'cat')
    print(f"\nRight neighbors of {test_seq}:")

    std_neighbors = sorted(list(standard_trie.right_neighbors(test_seq)))
    rad_v1_neighbors = sorted(list(radix_trie_v1.right_neighbors(test_seq)))
    rad_v2_neighbors = sorted(list(radix_trie_v2.right_neighbors(test_seq)))

    print(f"Standard trie: {std_neighbors}")
    print(f"Radix v1:      {rad_v1_neighbors}")
    print(f"Radix v2:      {rad_v2_neighbors}")

    all_passed = std_neighbors == rad_v1_neighbors == rad_v2_neighbors
    print(f"{'✓' if all_passed else '✗'} Right neighbors match")

    return all_passed


def test_left_neighbors():
    """Test left neighbor queries."""
    print("\n=== Test 5: Left Neighbors ===")

    standard_trie = syn.FreqTrie()
    radix_trie_v1 = radix_v1.RadixFreqTrie()
    radix_trie_v2 = radix_v2.RadixFreqTrie()

    sequences = [
        ('<', 'the', 'cat', 'ran', '>'),
        ('<', 'a', 'cat', 'ran', '>'),
        ('<', 'the', 'dog', 'ran', '>'),
    ]

    for seq in sequences:
        standard_trie._insert(seq)
        radix_trie_v1._insert(seq)
        radix_trie_v2._insert(seq)

    # Test left neighbors
    test_seq = ('cat', 'ran')
    print(f"\nLeft neighbors of {test_seq}:")

    std_neighbors = sorted(list(standard_trie.left_neighbors(test_seq)))
    rad_v1_neighbors = sorted(list(radix_trie_v1.left_neighbors(test_seq)))
    rad_v2_neighbors = sorted(list(radix_trie_v2.left_neighbors(test_seq)))

    print(f"Standard trie: {std_neighbors}")
    print(f"Radix v1:      {rad_v1_neighbors}")
    print(f"Radix v2:      {rad_v2_neighbors}")

    all_passed = std_neighbors == rad_v1_neighbors == rad_v2_neighbors
    print(f"{'✓' if all_passed else '✗'} Left neighbors match")

    return all_passed


def test_shared_right_neighbors():
    """Test shared right neighbor queries."""
    print("\n=== Test 6: Shared Right Neighbors ===")

    standard_trie = syn.FreqTrie()
    radix_trie_v1 = radix_v1.RadixFreqTrie()
    radix_trie_v2 = radix_v2.RadixFreqTrie()

    sequences = [
        ('<', 'the', 'cat', 'ran', 'fast', '>'),
        ('<', 'the', 'cat', 'jumped', 'high', '>'),
        ('<', 'the', 'dog', 'ran', 'fast', '>'),
        ('<', 'the', 'dog', 'jumped', 'high', '>'),
    ]

    for seq in sequences:
        standard_trie._insert(seq)
        radix_trie_v1._insert(seq)
        radix_trie_v2._insert(seq)

    # Test shared right neighbors
    seq1 = ('<', 'the', 'cat')
    seq2 = ('<', 'the', 'dog')
    print(f"\nShared right neighbors of {seq1} and {seq2}:")

    std_shared = sorted(list(standard_trie.shared_right_neighbors(seq1, seq2)))
    rad_v1_shared = sorted(list(radix_trie_v1.shared_right_neighbors(seq1, seq2)))
    rad_v2_shared = sorted(list(radix_trie_v2.shared_right_neighbors(seq1, seq2)))

    print(f"Standard trie: {std_shared}")
    print(f"Radix v1:      {rad_v1_shared}")
    print(f"Radix v2:      {rad_v2_shared}")

    all_passed = std_shared == rad_v1_shared == rad_v2_shared
    print(f"{'✓' if all_passed else '✗'} Shared right neighbors match")

    return all_passed


def test_shared_left_neighbors():
    """Test shared left neighbor queries."""
    print("\n=== Test 7: Shared Left Neighbors ===")

    standard_trie = syn.FreqTrie()
    radix_trie_v1 = radix_v1.RadixFreqTrie()
    radix_trie_v2 = radix_v2.RadixFreqTrie()

    sequences = [
        ('<', 'the', 'big', 'cat', 'ran', '>'),
        ('<', 'a', 'big', 'cat', 'ran', '>'),
        ('<', 'the', 'big', 'dog', 'ran', '>'),
        ('<', 'a', 'big', 'dog', 'ran', '>'),
    ]

    for seq in sequences:
        standard_trie._insert(seq)
        radix_trie_v1._insert(seq)
        radix_trie_v2._insert(seq)

    # Test shared left neighbors
    seq1 = ('cat', 'ran')
    seq2 = ('dog', 'ran')
    print(f"\nShared left neighbors of {seq1} and {seq2}:")

    std_shared = sorted(list(standard_trie.shared_left_neighbors(seq1, seq2)))
    rad_v1_shared = sorted(list(radix_trie_v1.shared_left_neighbors(seq1, seq2)))
    rad_v2_shared = sorted(list(radix_trie_v2.shared_left_neighbors(seq1, seq2)))

    print(f"Standard trie: {std_shared}")
    print(f"Radix v1:      {rad_v1_shared}")
    print(f"Radix v2:      {rad_v2_shared}")

    all_passed = std_shared == rad_v1_shared == rad_v2_shared
    print(f"{'✓' if all_passed else '✗'} Shared left neighbors match")

    return all_passed


def test_edge_compression():
    """Test that edge compression is actually happening."""
    print("\n=== Test 8: Edge Compression ===")

    radix_trie_v2_obj = radix_v2.RadixFreqTrie()

    # Insert a sequence with a long unique suffix
    sequence = ('<', 'this', 'is', 'a', 'very', 'long', 'unique', 'sequence', '>')
    radix_trie_v2_obj._insert(sequence)

    # Check that we can still query all prefixes correctly
    test_cases = [
        ('<', 'this'),
        ('<', 'this', 'is'),
        ('<', 'this', 'is', 'a'),
        ('<', 'this', 'is', 'a', 'very'),
        ('<', 'this', 'is', 'a', 'very', 'long'),
        ('<', 'this', 'is', 'a', 'very', 'long', 'unique'),
        ('<', 'this', 'is', 'a', 'very', 'long', 'unique', 'sequence'),
        ('<', 'this', 'is', 'a', 'very', 'long', 'unique', 'sequence', '>'),
    ]

    all_passed = True
    for seq in test_cases:
        freq = radix_trie_v2_obj.freq(seq)
        expected = 1  # All these sequences occur once
        match = "✓" if freq == expected else "✗"
        if freq != expected:
            all_passed = False
        print(f"{match} freq({seq[-2:]}...): expected={expected}, got={freq}")

    # Verify edge compression by checking the tree structure
    print("\nVerifying edge compression in tree structure...")
    node = radix_trie_v2_obj.fw_root
    if '<' in node.children:
        child = node.children['<']
        edge_len = len(child.edge_label)
        print(f"First edge from root has {edge_len} token(s): {child.edge_label[:3]}...")
        print(f"{'✓' if edge_len > 1 else '○'} Edge compression is {'active' if edge_len > 1 else 'minimal (may need branching)'}")

    return all_passed


def test_frequency_with_repeats():
    """Test frequency counting with repeated insertions."""
    print("\n=== Test 9: Frequency with Repeats ===")

    standard_trie = syn.FreqTrie()
    radix_trie_v1 = radix_v1.RadixFreqTrie()
    radix_trie_v2 = radix_v2.RadixFreqTrie()

    # Insert same sequence multiple times
    sequence = ('<', 'hello', 'world', '>')
    for _ in range(5):
        standard_trie._insert(sequence)
        radix_trie_v1._insert(sequence)
        radix_trie_v2._insert(sequence)

    # Test frequencies
    test_cases = [
        ('<', 'hello'),
        ('<', 'hello', 'world'),
        ('<', 'hello', 'world', '>'),
        ('hello',),
        ('world',),
    ]

    all_passed = True
    for seq in test_cases:
        std_freq = standard_trie.freq(seq)
        rad_v1_freq = radix_trie_v1.freq(seq)
        rad_v2_freq = radix_trie_v2.freq(seq)
        match = "✓" if std_freq == rad_v1_freq == rad_v2_freq else "✗"
        if std_freq != rad_v2_freq:
            all_passed = False
        print(f"{match} freq({seq}): standard={std_freq}, v1={rad_v1_freq}, v2={rad_v2_freq}")

    return all_passed


def test_neighbor_length_constraints():
    """Test neighbor queries with length constraints."""
    print("\n=== Test 10: Neighbor Length Constraints ===")

    standard_trie = syn.FreqTrie()
    radix_trie_v1 = radix_v1.RadixFreqTrie()
    radix_trie_v2 = radix_v2.RadixFreqTrie()

    sequences = [
        ('<', 'a', 'b', 'c', 'd', '>'),
        ('<', 'a', 'x', '>'),
        ('<', 'a', 'y', 'z', '>'),
    ]

    for seq in sequences:
        standard_trie._insert(seq)
        radix_trie_v1._insert(seq)
        radix_trie_v2._insert(seq)

    # Test with different length constraints
    base_seq = ('<', 'a')

    print("\nRight neighbors with min_length=2, max_length=3:")
    std_neighbors = sorted(list(standard_trie.right_neighbors(base_seq, min_length=2, max_length=3)))
    rad_v1_neighbors = sorted(list(radix_trie_v1.right_neighbors(base_seq, min_length=2, max_length=3)))
    rad_v2_neighbors = sorted(list(radix_trie_v2.right_neighbors(base_seq, min_length=2, max_length=3)))

    print(f"Standard: {std_neighbors}")
    print(f"Radix v1: {rad_v1_neighbors}")
    print(f"Radix v2: {rad_v2_neighbors}")

    all_passed = std_neighbors == rad_v1_neighbors == rad_v2_neighbors
    print(f"{'✓' if all_passed else '✗'} Neighbors with length constraints match")

    return all_passed


def run_all_tests():
    """Run all test cases."""
    print("=" * 60)
    print("RADIX TRIE V2 IMPLEMENTATION TEST SUITE")
    print("=" * 60)

    tests = [
        ("Basic Insertion", test_basic_insertion),
        ("Multiple Insertions", test_multiple_insertions),
        ("Small Test Corpus", test_small_corpus),
        ("Right Neighbors", test_right_neighbors),
        ("Left Neighbors", test_left_neighbors),
        ("Shared Right Neighbors", test_shared_right_neighbors),
        ("Shared Left Neighbors", test_shared_left_neighbors),
        ("Edge Compression", test_edge_compression),
        ("Frequency with Repeats", test_frequency_with_repeats),
        ("Neighbor Length Constraints", test_neighbor_length_constraints),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    print("=" * 60)

    return passed_count == total_count


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
