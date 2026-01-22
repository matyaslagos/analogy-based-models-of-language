from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


Token = str
Sentence = Tuple[Token, ...]
Sequence = Tuple[Token, ...]
Context = Tuple[Token, ...]


class RadixTrieNode:
    """
    Radix-trie node with compressed, token-labeled edges.

    children[first_token] = edge_dict where:
        edge["label"] : Tuple[str,...]   # compressed label (>=1)
        edge["child"] : RadixTrieNode    # destination node
        edge["freq"]  : List[int]        # per-prefix frequencies for endpoints along label

    For an edge label L of length k, edge["freq"][i] stores the frequency of:
        path_to_owner + L[:i+1]
    """

    def __init__(self) -> None:
        self.children: Dict[Token, Dict[str, Any]] = {}


class RadixTrie:
    """
    Suffix radix trie for frequency and (variable-length) left/right contexts.

    - Insert all suffixes of each sentence into a forward trie.
    - Insert all suffixes of each reversed sentence into a reverse trie.

    Right contexts of seq:
        all non-empty continuations reachable from endpoint(seq) in forward trie,
        with count(context) = freq(seq + context).

    Left contexts of seq:
        right contexts of reversed(seq) in reverse trie, then reverse each context.
    """

    def __init__(self) -> None:
        self.root = RadixTrieNode()
        self.root_rev = RadixTrieNode()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def setup(self, corpus: List[Sentence]) -> None:
        for sentence in corpus:
            self.insert_sentence(sentence)

    def insert_sentence(self, sentence: Sentence) -> None:
        self._insert_all_suffixes(self.root, sentence)
        self._insert_all_suffixes(self.root_rev, tuple(reversed(sentence)))

    def frequency(self, seq: Sequence) -> int:
        pos = self._find_pos(self.root, seq)
        return 0 if pos is None else self._pos_freq(pos)

    def right_neighbors(self, seq: Sequence) -> Dict[Context, int]:
        pos = self._find_pos(self.root, seq)
        return {} if pos is None else self._enumerate_from_pos(pos)

    def left_neighbors(self, seq: Sequence) -> Dict[Context, int]:
        pos = self._find_pos(self.root_rev, tuple(reversed(seq)))
        if pos is None:
            return {}
        rev = self._enumerate_from_pos(pos)
        return {tuple(reversed(ctx)): c for ctx, c in rev.items()}

    def shared_right_neighbors(self, s1: Sequence, s2: Sequence) -> Dict[Context, Tuple[int, int]]:
        p1 = self._find_pos(self.root, s1)
        p2 = self._find_pos(self.root, s2)
        if p1 is None or p2 is None:
            return {}
        out: Dict[Context, Tuple[int, int]] = {}
        self._intersect(p1, p2, prefix=(), out=out)
        return out

    def shared_left_neighbors(self, s1: Sequence, s2: Sequence) -> Dict[Context, Tuple[int, int]]:
        p1 = self._find_pos(self.root_rev, tuple(reversed(s1)))
        p2 = self._find_pos(self.root_rev, tuple(reversed(s2)))
        if p1 is None or p2 is None:
            return {}
        rev_out: Dict[Context, Tuple[int, int]] = {}
        self._intersect(p1, p2, prefix=(), out=rev_out)
        return {tuple(reversed(ctx)): pair for ctx, pair in rev_out.items()}

    # ------------------------------------------------------------------
    # Insertion
    # ------------------------------------------------------------------

    def _insert_all_suffixes(self, root: RadixTrieNode, s: Sentence) -> None:
        for start in range(len(s)):
            self._insert_suffix(root, s, start)

    def _insert_suffix(self, root: RadixTrieNode, s: Sentence, start: int) -> None:
        node = root
        pos = start
        n = len(s)

        while pos < n:
            first = s[pos]
            edge = node.children.get(first)

            if edge is None:
                label = s[pos:]
                node.children[first] = {
                    "label": label,
                    "child": RadixTrieNode(),
                    "freq": [1] * len(label),
                }
                return

            label: Sequence = edge["label"]
            k = self._lcp(s, pos, label)

            if k == len(label):
                freq: List[int] = edge["freq"]
                for i in range(k):
                    freq[i] += 1
                node = edge["child"]
                pos += k
                continue

            # Split at k, then continue insertion from the new middle node.
            edge = self._split(node, first, k)

            freq = edge["freq"]
            for i in range(k):
                freq[i] += 1

            node = edge["child"]
            pos += k

    def _split(self, owner: RadixTrieNode, first: Token, k: int) -> Dict[str, Any]:
        edge = owner.children[first]
        L: Sequence = edge["label"]
        F: List[int] = edge["freq"]
        child: RadixTrieNode = edge["child"]

        pre, suf = L[:k], L[k:]
        preF, sufF = F[:k], F[k:]

        mid = RadixTrieNode()
        pre_edge = {"label": pre, "child": mid, "freq": preF}
        suf_edge = {"label": suf, "child": child, "freq": sufF}

        owner.children[first] = pre_edge
        mid.children[suf[0]] = suf_edge
        return pre_edge

    # ------------------------------------------------------------------
    # Lookup positions (compressed-edge aware)
    # ------------------------------------------------------------------
    # A position is (owner_node, edge_or_None, i)
    # - if edge is not None: the sequence ends at edge["label"][i]
    # - if edge is None: at a node boundary (used internally by advance())

    def _find_pos(
        self, root: RadixTrieNode, seq: Sequence
    ) -> Optional[Tuple[RadixTrieNode, Optional[Dict[str, Any]], int]]:
        if not seq:
            return None

        node = root
        i = 0
        m = len(seq)

        while i < m:
            edge = node.children.get(seq[i])
            if edge is None:
                return None

            label: Sequence = edge["label"]
            j = 0
            while i + j < m and j < len(label) and seq[i + j] == label[j]:
                j += 1

            if i + j == m:
                # Always return an inside-edge endpoint (even if j == len(label)).
                return (node, edge, j - 1)

            if j == len(label):
                node = edge["child"]
                i += j
                continue

            return None

        return None

    def _pos_freq(self, pos: Tuple[RadixTrieNode, Optional[Dict[str, Any]], int]) -> int:
        _owner, edge, i = pos
        if edge is None:
            return 0
        return int(edge["freq"][i])

    # ------------------------------------------------------------------
    # Two primitives: frontier(pos) and advance(...)
    # ------------------------------------------------------------------

    def _frontier(
        self, pos: Tuple[RadixTrieNode, Optional[Dict[str, Any]], int]
    ) -> Dict[Token, Tuple[RadixTrieNode, Dict[str, Any], int]]:
        """
        Return next-token choices from pos.

        Map: next_token -> (owner_node, edge, start_index_in_edge_label)

        - Mid-edge with remainder: exactly one forced next token.
        - Node boundary: all outgoing edges with start_index=0.
        """
        owner, edge, i = pos

        if edge is not None:
            label: Sequence = edge["label"]
            if i + 1 < len(label):
                nxt = label[i + 1]
                return {nxt: (owner, edge, i + 1)}
            # exactly at end of edge => node boundary at edge child
            node = edge["child"]
        else:
            node = owner

        return {tok: (node, e, 0) for tok, e in node.children.items()}

    def _advance(
        self, owner: RadixTrieNode, edge: Dict[str, Any], i: int
    ) -> Tuple[RadixTrieNode, Optional[Dict[str, Any]], int]:
        """
        Return new position after consuming up to edge["label"][i] (inclusive).
        """
        if i >= len(edge["label"]) - 1:
            return (edge["child"], None, -1)
        return (owner, edge, i)

    # ------------------------------------------------------------------
    # Enumerate contexts from an endpoint
    # ------------------------------------------------------------------

    def _enumerate_from_pos(
        self, pos: Tuple[RadixTrieNode, Optional[Dict[str, Any]], int]
    ) -> Dict[Context, int]:
        """
        Enumerate all non-empty contexts reachable from pos.
        context count is freq(seq + context), read from edge per-prefix freq arrays.
        """
        out: Dict[Context, int] = {}

        def dfs(p: Tuple[RadixTrieNode, Optional[Dict[str, Any]], int], prefix: Context) -> None:
            for tok, (owner, edge, si) in self._frontier(p).items():
                label: Sequence = edge["label"]
                freq: List[int] = edge["freq"]

                # Consume as much as possible on this edge: emit every prefix endpoint.
                # From start index si, the t-th emitted endpoint is at label[si:si+t].
                for end in range(si, len(label)):
                    ctx = prefix + label[si : end + 1]
                    out[ctx] = int(freq[end])

                # Continue below the child node with prefix extended by the full remainder.
                next_pos = self._advance(owner, edge, len(label) - 1)
                dfs(next_pos, prefix + label[si:])

        dfs(pos, ())
        return out

    # ------------------------------------------------------------------
    # Intersect contexts (shared neighbors) by synchronized traversal
    # ------------------------------------------------------------------

    def _intersect(
        self,
        p1: Tuple[RadixTrieNode, Optional[Dict[str, Any]], int],
        p2: Tuple[RadixTrieNode, Optional[Dict[str, Any]], int],
        prefix: Context,
        out: Dict[Context, Tuple[int, int]],
    ) -> None:
        """
        Synchronized intersection of continuation structures from p1 and p2.

        Emits each shared context C with (freq(seq1+C), freq(seq2+C)).
        Prunes any branch whose next token is not shared.
        """
        f1 = self._frontier(p1)
        f2 = self._frontier(p2)

        # Iterate over smaller frontier for fewer key lookups.
        if len(f1) <= len(f2):
            keys = [k for k in f1.keys() if k in f2]
        else:
            keys = [k for k in f2.keys() if k in f1]

        for k in keys:
            o1, e1, s1 = f1[k]
            o2, e2, s2 = f2[k]

            L1: Sequence = e1["label"]
            L2: Sequence = e2["label"]
            F1: List[int] = e1["freq"]
            F2: List[int] = e2["freq"]

            # Match token-by-token inside the (possibly long) compressed labels.
            m = 0
            while (s1 + m) < len(L1) and (s2 + m) < len(L2) and L1[s1 + m] == L2[s2 + m]:
                i1 = s1 + m
                i2 = s2 + m
                ctx = prefix + L1[s1 : i1 + 1]
                out[ctx] = (int(F1[i1]), int(F2[i2]))
                m += 1

            if m == 0:
                continue

            # Advance both positions to the last matched endpoint inside those edges.
            np1 = self._advance(o1, e1, s1 + m - 1)
            np2 = self._advance(o2, e2, s2 + m - 1)

            self._intersect(np1, np2, prefix + L1[s1 : s1 + m], out)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _lcp(s: Sentence, pos: int, label: Sequence) -> int:
        k = 0
        while pos + k < len(s) and k < len(label) and s[pos + k] == label[k]:
            k += 1
        return k


# -------------------------------------------------------------------------
# Example
# -------------------------------------------------------------------------
if __name__ == "__main__":
    corpus: List[Sentence] = [
        ("<", "this", "is", "a", "nice", "sentence", ">"),
        ("<", "this", "is", "another", "nice", "sentence", ">"),
        ("<", "this", "is", "a", "nice", "sentence", ">"),
    ]

    t = RadixTrie()
    for s in corpus:
        t.insert_sentence(s)

    seq = ("this", "is")
    print("freq", seq, "=", t.frequency(seq))

    rn = t.right_neighbors(seq)
    print("right contexts:")
    for ctx, c in sorted(rn.items()):
        print(" ", ctx, "->", c)

    sn = t.shared_right_neighbors(("a",), ("another",))
    print("shared right contexts of ('a',) and ('another',):")
    for ctx, pair in sorted(sn.items()):
        print(" ", ctx, "->", pair)
