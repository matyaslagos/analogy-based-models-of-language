#!/usr/bin/env python3
"""
Test to verify that all positions in compressed edges have identical frequencies.

According to the radix trie invariant: if all frequencies along an edge are not equal,
there must be a branching point, and the edge should have been split.
"""

import radix_trie as radix_v1
import radix_trie_v2 as radix_v2


def check_freqs_invariant_v1(node, path="root"):
    """Recursively check that all freqs in each edge are identical (v1)."""
    violations = []

    for first_token, child in node.children.items():
        edge_path = f"{path} -> {child.edge_label}"

        if len(child.freqs) > 1:
            # Check if all frequencies are the same
            if len(set(child.freqs)) > 1:
                violations.append({
                    'path': edge_path,
                    'edge_label': child.edge_label,
                    'freqs': child.freqs,
                    'unique_freqs': set(child.freqs)
                })

        # Recurse to children
        violations.extend(check_freqs_invariant_v1(child, edge_path))

    return violations


def check_freqs_invariant_v2(node, path="root"):
    """Recursively check that all freqs in each edge are identical (v2)."""
    violations = []

    for first_token, child in node.children.items():
        edge_path = f"{path} -> {child.edge_label}"

        if len(child.freqs) > 1:
            # Check if all frequencies are the same
            if len(set(child.freqs)) > 1:
                violations.append({
                    'path': edge_path,
                    'edge_label': child.edge_label,
                    'freqs': child.freqs,
                    'unique_freqs': set(child.freqs)
                })

        # Recurse to children
        violations.extend(check_freqs_invariant_v2(child, edge_path))

    return violations


def test_simple_sequences():
    """Test with simple endmarked sequences."""
    print("\n=== Test 1: Simple Endmarked Sequences ===")

    trie_v1 = radix_v1.RadixFreqTrie()
    trie_v2 = radix_v2.RadixFreqTrie()

    sequences = [
        ('<', 'the', '>'),
        ('<', 'the', 'cat', '>'),
        ('<', 'the', 'cat', 'ran', '>'),
    ]

    for seq in sequences:
        trie_v1._insert(seq)
        trie_v2._insert(seq)
        print(f"Inserted: {seq}")

    print("\nChecking V1 forward trie...")
    violations_v1_fw = check_freqs_invariant_v1(trie_v1.fw_root)

    print("Checking V1 backward trie...")
    violations_v1_bw = check_freqs_invariant_v1(trie_v1.bw_root)

    print("Checking V2 forward trie...")
    violations_v2_fw = check_freqs_invariant_v2(trie_v2.fw_root)

    print("Checking V2 backward trie...")
    violations_v2_bw = check_freqs_invariant_v2(trie_v2.bw_root)

    all_violations = violations_v1_fw + violations_v1_bw + violations_v2_fw + violations_v2_bw

    if all_violations:
        print(f"\n✗ FOUND {len(all_violations)} VIOLATIONS:")
        for v in all_violations:
            print(f"  Path: {v['path']}")
            print(f"  Edge: {v['edge_label']}")
            print(f"  Freqs: {v['freqs']}")
            print(f"  Unique values: {v['unique_freqs']}")
            print()
        return False
    else:
        print("\n✓ NO VIOLATIONS: All compressed edges have uniform frequencies")
        return True


def test_corpus():
    """Test with actual corpus."""
    print("\n=== Test 2: Small Corpus ===")

    trie_v1 = radix_v1.RadixFreqTrie()
    trie_v2 = radix_v2.RadixFreqTrie()

    try:
        trie_v1.setup('syntax/corpora/small_test_corpus.txt')
        trie_v2.setup('syntax/corpora/small_test_corpus.txt')
        print("Corpus loaded successfully")
    except FileNotFoundError:
        print("Corpus file not found, skipping")
        return True

    print("\nChecking V1 forward trie...")
    violations_v1_fw = check_freqs_invariant_v1(trie_v1.fw_root)

    print("Checking V1 backward trie...")
    violations_v1_bw = check_freqs_invariant_v1(trie_v1.bw_root)

    print("Checking V2 forward trie...")
    violations_v2_fw = check_freqs_invariant_v2(trie_v2.fw_root)

    print("Checking V2 backward trie...")
    violations_v2_bw = check_freqs_invariant_v2(trie_v2.bw_root)

    all_violations = violations_v1_fw + violations_v1_bw + violations_v2_fw + violations_v2_bw

    if all_violations:
        print(f"\n✗ FOUND {len(all_violations)} VIOLATIONS:")
        for v in all_violations[:10]:  # Show first 10
            print(f"  Path: {v['path']}")
            print(f"  Edge: {v['edge_label']}")
            print(f"  Freqs: {v['freqs']}")
            print(f"  Unique values: {v['unique_freqs']}")
            print()
        if len(all_violations) > 10:
            print(f"  ... and {len(all_violations) - 10} more violations")
        return False
    else:
        print("\n✓ NO VIOLATIONS: All compressed edges have uniform frequencies")
        return True


def test_specific_case():
    """Test the specific case from the discussion."""
    print("\n=== Test 3: Specific Case from Discussion ===")

    trie_v1 = radix_v1.RadixFreqTrie()

    # Insert "the" alone
    print("Inserting ('<', 'the', '>')")
    trie_v1._insert(('<', 'the', '>'))

    # Check state
    print("\nState after first insert:")
    if 'the' in trie_v1.fw_root.children:
        node = trie_v1.fw_root.children['the']
        print(f"  Node with first token 'the': edge={node.edge_label}, freqs={node.freqs}")

    # Insert "the cat"
    print("\nInserting ('<', 'the', 'cat', '>')")
    trie_v1._insert(('<', 'the', 'cat', '>'))

    # Check state
    print("\nState after second insert:")
    if 'the' in trie_v1.fw_root.children:
        node = trie_v1.fw_root.children['the']
        print(f"  Node with first token 'the': edge={node.edge_label}, freqs={node.freqs}")
        if node.children:
            print(f"  Children: {[(k, v.edge_label, v.freqs) for k, v in node.children.items()]}")

    violations = check_freqs_invariant_v1(trie_v1.fw_root)

    if violations:
        print(f"\n✗ FOUND {len(violations)} VIOLATIONS")
        for v in violations:
            print(f"  {v}")
        return False
    else:
        print("\n✓ NO VIOLATIONS")
        return True


if __name__ == '__main__':
    print("=" * 70)
    print("TESTING RADIX TRIE INVARIANT: Uniform Frequencies in Compressed Edges")
    print("=" * 70)

    results = []
    results.append(("Simple sequences", test_simple_sequences()))
    results.append(("Corpus", test_corpus()))
    results.append(("Specific case", test_specific_case()))

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("\n✓ INVARIANT HOLDS: All compressed edges have uniform frequencies")
        print("This suggests the freqs list could be replaced with a single integer!")
    else:
        print("\n✗ INVARIANT VIOLATED: Found edges with non-uniform frequencies")
        print("This suggests the current implementation is needed")
