# Rule DSL for the metric polytope: grammar proposal (Phase 4b, NOT YET IMPLEMENTED)

Goal: rules are code. Each rule is a function of n, may call rules at smaller sizes, and compiles to
(a) a Python generator / predicate run by an exact interpreter and (b) a readable formula (Unicode and LaTeX).

Three acceptance checks (from review):
- **R1** every construction in `docs/literature.md`, including the sporadic vertices as explicit base cases, is
  written out in full (§7, no `...`);
- **R2** "apply moves until nothing new appears" is a built-in (`closure`, §6) — it is the coverage experiment;
- **R3** new moves and new primitives can be added without changing the grammar or the core (§9).

## 1. Design choices (please confirm)

| # | choice | proposal | alternative |
|---|---|---|---|
| D1 | Surface syntax | **S-expressions** in `rules/*.mpr`: trivial to parse, programs are data, easy to enumerate and mutate mechanically (Phase 8 searches over DSL programs). | Python-embedded combinators (no parser; programs are not data). |
| D2 | Point model | A point at size n is a symmetric n×n matrix with zero diagonal, exact rationals. Blocks are induced submatrices; the middle is the rectangular cross matrix. | — |
| D3 | Splits | Split by a **node subset T** (top-left = x\|_T, bottom-right = x\|_{T̄}, middle = T×T̄), so search is 2^n, not n!. | Split after a permutation. |
| D4 | Data sources | `(vertices n)`: full vertex set for n ≤ 6 (cdd, Phase 2); **orbit representatives only** for n = 7, 8 (Deza). Predicates over representatives must be G-invariant; the interpreter tests invariance on seeded random group images and refuses otherwise. | — |
| D5 | Non-unique constructions | Explicit deterministic choice (`min-over`, `extend :lexmin`, `fiber-vertices`) — never hidden choices. | — |
| D6 | Trust | Generative rules and moves only produce *candidates*; every output goes through the exact vertex test. | — |
| D7 | Collections | `for` builds an **ordered list** (duplicates kept); `distinct` dedupes by equality, `orbits` dedupes by canonical form. | Sets everywhere (loses order and multiplicity). |

## 2. Types

`Nat` · `Rat` · `Bool` · `Nodes` · `Perm` · `Point` · `Mid` (k×l rational matrix) · `Partial` (point with holes) ·
`Graph` · `List⟨T⟩` · `Tuple` · `Pattern` (±1 clause matrix) · `Move` · `Closure`.
Types are checked at load time from the registry signatures (§9); sizes are checked at run time.

## 3. Grammar (EBNF) — closed

```
file      := form*
form      := '(' 'define'     sig meta* expr ')'                      ; function or constant
           | '(' 'generative' NAME '(' NAME ')' meta* expr ')'        ; size param -> List⟨Point⟩
           | '(' 'structural' NAME '(' NAME ')' meta* expr ')'        ; size param -> Bool (+ witness)
           | '(' 'move'       NAME '(' NAME+ ')' meta* expr ')'       ; 1 or 2 Points -> List⟨Point⟩ (§6)
sig       := NAME | '(' NAME param* ')'
param     := NAME | '(' NAME ':' TYPE ')'
meta      := ':domain' '(' INT INT? ')' | ':source' STRING | ':doc' STRING | ':formula' STRING
           | ':grow' (INT | 'computed')                 ; moves only: output size − input size (≥ 0), or per-output
expr      := atom
           | '(' 'let' '(' bind+ ')' expr ')'
           | '(' 'if' expr expr expr ')'
           | '(' 'case' expr clause+ ('(' 'else' expr ')')? ')'     ; base cases on n
           | '(' 'for' '(' gen+ ')' where? expr ')'                 ; -> List
           | '(' ('forall' | 'exists') '(' gen+ ')' where? expr ')' ; -> Bool (+ witness)
           | '(' ('min-over' | 'max-over' | 'count') '(' gen+ ')' where? expr ')'
           | '(' 'closure' expr expr copt* ')'                      ; (closure SEEDS MOVES ...) -> Closure
           | '(' OP expr* ')'                                       ; every primitive / define / rule / move call
bind      := '(' (NAME | '(' NAME+ ')') expr ')'                      ; tuple destructuring for split etc.
gen       := '(' NAME expr ')'
where     := '(' 'where' expr ')'
clause    := '(' INT expr ')'
copt      := ':max-n' expr | ':max-rounds' expr | ':only-vertices' BOOL | ':checkpoint' STRING
atom      := INT | RAT | '#t' | '#f' | '{' INT* '}' | NAME
```

The grammar has **no production per primitive**: all vocabulary is called through `'(' OP expr* ')'` and resolved in a
name registry. This is what makes R3 hold.

Recursion: a rule may call any rule at a size that evaluates to **< n** (checked at run time). Results are memoised
per (rule, n) and cached on disk keyed by sha256(rule source, transitive dependencies, n, code version).

## 4. Kernel primitives (registered in `metricpoly/dsl/prims.py`)

Points: `(lit n D (a ...))` · `(pairs n default ((i j) q) ...)` · `(const n q)` · `(cut n S)` · `(entry x i j)` ·
`(size x)` · `(maxc x)` · `(scale q x)` · `(affine a b x)` (a·x + b).

Blocks: `(block A M B)` = [[A, M],[Mᵀ, B]] (A's nodes first) · `(split T x)` → (A, M, B) · `(restrict T x)` ·
`(col x i)` (n×1 column of distances from i, 0 at i) · `(mcol M j)` · `(mconst k l q)` · `(mset M i j q)` ·
`(mhcat M1 M2)` · `(mvcat M1 M2)` · `(rows M)` · `(cols M)` · `(mvalues M)` ·
`(mflip S1 S2 M)` (M_ij ↦ 1 − M_ij iff [i∈S1] ⊕ [j∈S2]: switching seen on the middle).

Symmetry and patterns: `(switch S x)` · `(perm p x)` · `(canon x)` · `(orbit-key x)` · `(switch-class x)` ·
`(pattern x)` · `(mid-canon M)`.

Graphs: `(graph n edges)` · `(order G)` · `(edges G)` (sorted tuples i<j) · `(gmetric G)` · `(triameter G)` ·
`(complement G)` · `(gminus G H)` · `(gunion G H)` · `(connected? G)` · `(level-graph x q)` · `(good? G)`.
Relabelling helpers: `(arrangements n k)` (ordered k-tuples of distinct nodes) · `(move-last t x)` / `(move-first t x)`
(relabel so the nodes of tuple t become the last / first k, others keep relative order).

Lists, sets, numbers: `list concat len nth fst snd elems sum distinct orbits in card nodes binom`,
`and or not implies = < <= + - * / min max`.

Domains: `(range a b)` · `(subsets n)` · `(subsets n k)` · `(perms n)` · `(switchings n)` · `(partitions n)` ·
`(graphs n :connected)` (non-isomorphic, networkx atlas, n ≤ 7) · `(trees n)` · `(vertices n)` · `(cuts n)` ·
`(cone-rays n)` (n ≤ 6).

Verification: `(feasible? x)` · `(vertex? x)` · `(incidence x)` · `(denominator x)` · `(integral? x)` ·
`(fully-fractional? x)` · `(adjacent? x y)` (rank of common tight set = C(n,2) − 1) · `(in-orbits? x L)` ·
`(produced-by? x R)`.

Partial points: `(glue x1 x2 k)` (last k nodes of x1 ≡ first k of x2; missing pairs are holes) ·
`(lift-partial v)` (new last node, all its pairs are holes) · `(fiber-vertices P)` (all vertices of
{x ∈ m_n : x agrees with P}, exact cdd) · `(extend P :lexmin)`.

Every primitive carries: a type signature, a formula template (Unicode + LaTeX), and an equivariance tag
(`equivariant` / `label-dependent`) used by `closure` (§6).

## 5. Rule kinds and what they compile to

- `generative R (n)` → `R.generate(n) -> list[Point]`; report per n: #candidates, #feasible, #vertices, orbit keys.
- `structural P (n)` → `P.check(n) -> (holds, witness)`; a failing `forall` returns the first counterexample in the
  deterministic domain order (Phase 7 saves it).
- `move M (x)` / `move M (x y)` → `M.apply(x[, y]) -> list[Point]`, plus its `:grow`.
- All compile to `.formula("unicode"|"latex")`; defined names print as names with a glossary entry.

## 6. Moves and closure (R2)

A **move** is a first-class, named map Point → List⟨Point⟩ (unary) or Point × Point → List⟨Point⟩ (binary), with a
declared size change `:grow`. Moves quantify *internally* over their label choices (which node to twin, which overlap
to glue on), so each move is **G-equivariant as a map on orbits**:
orbits(M(g·x)) = orbits(M(x)) for all g. This is what makes it sound to apply moves only to orbit representatives.
The interpreter verifies equivariance on seeded random group elements the first time a move is used on each size, and
refuses a move that fails (error names the move and the witness g).

`(closure SEEDS MOVES :max-n N :max-rounds R :only-vertices #t :checkpoint "name")`
- State: for each size n ≤ N, a table orbit-key → (representative, provenance), provenance = (move, parent keys,
  round). Seeds get provenance `seed`.
- Loop: take orbits added in the last round; apply every unary move to each, and every binary move to each pair
  (new × all known, both orders) whose output size ≤ N; keep vertex outputs (exact test) if `:only-vertices`;
  canonicalize; insert new keys.
- Stop when a round adds nothing (**saturated**) or a bound is hit (**truncated**; reported, never silent).
  Terminates because each size has finitely many orbits.
- Checkpointed like every long job (worklist, tables, seed, code version); `--resume` continues.
- Accessors: `(closure-orbits C n)`, `(provenance C x)`, `(saturated? C)`, `(uncovered C n)` =
  vertices of m_n (per D4) whose orbit is not in C. **`uncovered` is the list of mutation candidates.**

The coverage experiment is then two lines:
```lisp
(define C-lit (closure (list (cut 3 {})) (list twin radial dup lift-fiber glue) :max-n 8 :checkpoint "C-lit"))
(structural closure-covers (n) :domain (3 8) (forall ((x (vertices n))) (in-orbits? x (closure-orbits C-lit n))))
```

## 7. Every construction in docs/literature.md, in full (R1)

```lisp
;; ---------- helpers --------------------------------------------------------------
(define (all-but n i) (nodes (for ((j (range 0 n))) (where (not (= i j))) j)))
(define (perimeter x T) (let (((a b c) (elems T))) (+ (entry x a b) (entry x a c) (entry x b c))))
(define (new-node x) {(size x)})                                        ; label of the node a :grow 1 move adds

;; ---------- C1 cuts, C2 anticuts -------------------------------------------------
(generative cuts (n) :source "C1" (for ((S (subsets n))) (cut n S)))
(define (anticut n S) (switch S (const n 2/3)))
(generative anticuts (n) :domain (5) :source "C2" (for ((S (subsets n))) (anticut n S)))

;; ---------- C3 trivial extension: twin / antitwin of node i ----------------------
(define (twin-of i b x)
  (let ((y (block x (col x i) (const 1 0))))
    (if (= b 0) y (switch (new-node x) y))))
(move twin (x) :grow 1 :source "C3"
  (for ((i (range 0 (size x))) (b (range 0 2))) (twin-of i b x)))

;; ---------- C4 duplication with same denominator --------------------------------
(define (dup-at i x)
  (let ((a (min-over ((j (range 0 (size x)))) (where (not (= j i)))
             (min (* 2 (entry x i j)) (- 2 (* 2 (entry x i j)))))))
    (block x (mset (col x i) i 0 a) (const 1 0))))
(move dup (x) :grow 1 :source "C4" (for ((i (range 0 (size x)))) (dup-at i x)))

;; ---------- C5 radial extension (m = 1, 2, 3) ------------------------------------
(define (radial-m m alpha v) (block v (mconst (size v) m alpha) (const m (* 2 alpha))))
(define (radial-ext m v) (radial-m m (/ (maxc v) 2) v))
(move radial  (x) :grow 1 :source "C5 Thm 3.1" (list (radial-ext 1 x)))
(move radial2 (x) :grow 2 :source "C5 Thm 3.2" (list (radial-ext 2 x)))
(move radial3 (x) :grow 3 :source "C5 Thm 3.2" (if (<= (maxc x) 2/3) (list (radial-ext 3 x)) (list)))
(structural radial-good-is-vertex (n) :domain (4) :source "C5 Thm 3.1"
  (forall ((v (vertices (- n 1)))) (where (good? (level-graph v (maxc v))))
    (vertex? (radial-ext 1 v))))

;; ---------- C6 suspension of a tree ---------------------------------------------
(define (third-metric G) (scale 1/3 (gmetric G)))
(generative tree-suspensions (n) :domain (6) :source "C6 (SECONDARY)"
  (for ((T (trees (- n 1))))                    ; stars have disconnected complements: excluded, as in L96's "not a star"
    (where (and (connected? (complement T)) (= (maxc (third-metric (complement T))) 2/3)))   ; diameter 2
    (radial-ext 1 (third-metric (complement T)))))

;; ---------- C7 graphic vertices ---------------------------------------------------
(define (graphic G) (scale (/ 2 (triameter G)) (gmetric G)))
(generative graphic-all (n) :domain (3 7) :source "C7"
  (for ((G (graphs n :connected))) (graphic G)))
(define (C-on n s) (graph n (for ((k (range 0 (len s)))) (tuple (nth s k) (nth s (mod (+ k 1) (len s)))))))
(define (P-on n s) (graph n (for ((k (range 0 (- (len s) 1)))) (tuple (nth s k) (nth s (+ k 1))))))
(define (K n) (complement (graph n (list))))
(define ddf-v7  (third-metric (gminus (K 7) (gunion (C-on 7 (list 1 2 3)) (C-on 7 (list 4 5 6))))))
(define ddf-v8  (scale 2/5 (gmetric (gminus (K 7) (C-on 7 (list 0 1 2 3 4 5 6))))))
(define ddf-v9  (third-metric (gminus (K 7) (gunion (C-on 7 (list 0 1 2 3 4 5 6)) (P-on 7 (list 0 2))))))
(define ddf-v10 (third-metric (gminus (K 7) (gunion (gunion (C-on 7 (list 1 2 3)) (C-on 7 (list 4 5 6)))
                                                     (P-on 7 (list 3 4))))))

;; ---------- C8 complete multipartite ---------------------------------------------
(define (labels p) (for ((t (range 0 (len p))) (r (range 0 (nth p t)))) t))   ; node -> part index
(define (kparts p)
  (let ((lab (labels p)) (n (sum p)))
    (graph n (for ((i (range 0 n)) (j (range 0 n)))
               (where (and (< i j) (not (= (nth lab i) (nth lab j))))) (tuple i j)))))
(generative multipartite-third (n) :source "C8"
  (for ((p (partitions n))) (where (> (len p) 1)) (third-metric (kparts p))))
(generative multipartite-minus-edge (n) :source "C8 (DDF96 Prop 3.4)"
  (for ((p (partitions n)) (e (edges (kparts p)))) (where (> (len p) 1))
    (third-metric (gminus (kparts p) (graph n (list e))))))

;; ---------- C9 Avis doubling --------------------------------------------------------
(define (avis-double G)
  (let ((n (order G)) (E (edges G)) (m (len (edges G))))
    (graph (+ (* 2 n) m)
      (concat E
              (for ((e E)) (tuple (+ n (fst e)) (+ n (snd e))))
              (for ((i (range 0 n))) (tuple i (+ n i)))
              (for ((k (range 0 m))) (tuple (fst (nth E k)) (+ (* 2 n) k)))
              (for ((k (range 0 m))) (tuple (+ n (snd (nth E k))) (+ (* 2 n) k)))))))
(define (path-graph d) (P-on d (range 0 d)))
(generative avis-paths (n) :source "C9"                  ; vertex of m_{3d-1} with denominator d
  (for ((d (range 3 (+ n 1)))) (where (= (- (* 3 d) 1) n)) (graphic (avis-double (path-graph d)))))

;; ---------- C10 rays of the metric cone ------------------------------------------
(define (ray-to-vertex r) (scale (/ 2 (max-over ((T (subsets (size r) 3))) (perimeter r T))) r))
(generative ray-vertices (n) :domain (3 6) :source "C10" (for ((r (cone-rays n))) (ray-to-vertex r)))

;; ---------- C11 k-union gluing (binary move) + lift through the fiber --------------
(define (agree? x1 x2 k)
  (= (restrict (nodes (range (- (size x1) k) (size x1))) x1) (restrict (nodes (range 0 k)) x2)))
(move glue (x1 x2) :grow computed :source "C11"      ; output size = |x1| + |x2| − k
  (for ((k (range 1 (min (size x1) (size x2))))
        (t1 (arrangements (size x1) k)) (t2 (arrangements (size x2) k)))   ; ordered choice of overlap nodes
    (where (agree? (move-last t1 x1) (move-first t2 x2) k))               ; (equivariance: all choices tried)
    (extend (glue (move-last t1 x1) (move-first t2 x2) k) :lexmin)))
(move lift-fiber (x) :grow 1 :source "LP92 Lemma 2.2" (fiber-vertices (lift-partial x)))

;; ---------- C12 sporadic vertices as explicit base cases -----------------------------
(define lp-ex-2-14 (pairs 7 1/3 ((1 2) 2/3) ((1 3) 2/3) ((2 3) 2/3) ((2 5) 2/3) ((4 5) 2/3) ((4 6) 2/3) ((5 6) 2/3)))
(define lp-ex-2-13 (pairs 8 2/3 ((0 1) 1/3) ((0 3) 1/3) ((0 5) 1/3) ((1 2) 1/3) ((3 4) 1/3) ((5 6) 1/3)
                               ((0 7) 1/3) ((1 7) 1/3) ((2 7) 1/3) ((3 7) 1/3) ((4 7) 1/3) ((5 7) 1/3) ((6 7) 1/3)))
(define lp-ex-2-13-ext (block lp-ex-2-13 (mvcat-list (list 3/6 1/6 1/6 3/6 3/6 5/6 5/6 3/6)) (const 1 0)))
(define dfmv-451 (lit 8 15 (2 4 4 5 5 7 8 6 6 5 5 5 10 8 5 5 5 4 9 9 3 4 10 10 5 10 5 5)))
(define dfmv-531 (lit 8 9  (2 2 3 3 4 4 5 4 3 3 6 6 3 5 5 2 6 3 6 3 3 6 3 3 6 4 5 3)))
(define di-2005  (lit 9 9  (2 2 3 3 4 4 5 5 4 3 5 6 6 3 3 5 5 2 4 3 5 6 3 3 6 6 5 3 2 6 6 3 3 5 3 4)))
(generative sporadic (n) :source "C12"
  (case n (7 (list lp-ex-2-14 ddf-v7 ddf-v8 ddf-v9 ddf-v10))
          (8 (list lp-ex-2-13 dfmv-451 dfmv-531))
          (9 (list lp-ex-2-13-ext di-2005))
          (else (list))))
```
(`mvcat-list` builds a k×1 middle from a list; `gunion` is edge union on the same node set — both kernel list/graph
utilities. `:grow -1` marks a move whose output size is computed per output; closure reads the actual size.)

Structural facts S1–S18 are all `forall` / `exists` over `(vertices n)` with the verification primitives, e.g.
```lisp
(structural no-half-integral (n) :source "S2" (forall ((x (vertices n))) (not (= (denominator x) 2))))
(structural incidence-bounds (n) :source "S7"
  (forall ((x (vertices n)))
    (and (<= (incidence x) (* 3 (binom n 3)))
         (implies (fully-fractional? x) (<= (incidence x) (binom n 3))))))
(structural dominating-set (n) :source "S8" (forall ((x (vertices n))) (exists ((c (cuts n))) (adjacent? x c))))
(structural switch-class-nonadjacent (n) :source "S18 (UNREAD)"
  (forall ((x (vertices n))) (where (not (integral? x)))
    (forall ((S (switchings n))) (where (not (= S {}))) (not (adjacent? x (switch S x))))))
```

## 8. The required test rules

**"Every orbit lifts from n−1"** (two versions that differ):
```lisp
(structural projects-to-smaller-vertex (n) :domain (4)      ; literature predicts FAILURE at n = 7 (LP92 Ex. 2.14)
  (forall ((x (vertices n))) (exists ((i (range 0 n))) (vertex? (restrict (all-but n i) x)))))
(define C-lift (closure (list (cut 3 {})) (list lift-fiber) :max-n 8 :checkpoint "C-lift"))
(structural lift-closure-complete (n) :domain (3 8)
  (forall ((x (vertices n))) (in-orbits? x (closure-orbits C-lift n))))
```

**Block / fractal hypothesis**, parametrised by a middle class so the data says which class is needed:
```lisp
(define (decomposes? x mid-ok?)
  (or (<= (size x) 2)
      (exists ((T (subsets (size x)))) (where (and (in 0 T) (< (card T) (size x))))
        (let (((A M B) (split T x)))
          (and (mid-ok? M A B) (decomposes? A mid-ok?) (decomposes? B mid-ok?))))))
;; middle classes, strictest first
(define (const-mid? M) (= (card (distinct (mvalues M))) 1))
(define (mid-const? M A B)                                  ; constant up to switching
  (exists ((S1 (subsets (rows M))) (S2 (subsets (cols M)))) (const-mid? (mflip S1 S2 M))))
(define (mid-twin? M A B)                                   ; each bottom node is a twin/antitwin of a top node
  (forall ((j (range 0 (cols M))))
    (exists ((i (range 0 (rows M)))) (or (= (mcol M j) (col A i)) (= (mcol M j) (affine -1 1 (col A i)))))))
(define (mid-two-valued? M A B) (<= (card (distinct (mvalues M))) 2))
(define (mid-any? M A B) #t)                                ; sanity: always decomposes
(structural block-fractal-const (n) (forall ((x (vertices n))) (decomposes? x mid-const?)))
(structural block-fractal-twin  (n) (forall ((x (vertices n))) (decomposes? x mid-twin?)))
(structural block-fractal-2val  (n) (forall ((x (vertices n))) (decomposes? x mid-two-valued?)))
```
The first failing n per class is a measurable mutation point.

## 9. Extensibility without touching the grammar or core (R3)

Three levels of growth, in order of preference; each is recorded in the ledger with date, the counterexample that
triggered it, and the level:

1. **New move or rule written in the DSL** — add a `(move …)` / `(generative …)` form to a file in `rules/`.
   No code change. This is the expected response to most mutations.
2. **New primitive** (an operation not expressible, or too slow when expressed) — a Python function registered in
   `metricpoly/dsl/ext/<name>.py` with `@primitive(name, signature, formula=…, equivariance=…)`. The grammar is
   unchanged (generic call form); the type checker, pretty-printer and closure read the registry.
3. **New base case** — a literal seed (as in `sporadic`) for an orbit no move reaches yet. Always allowed, always
   recorded as such: a base case is an admission that no rule explains the orbit.

Guarantees, enforced by tests:
- a "core freeze" test hashes `parser.py` and the kernel primitive table, so an extension that edits either fails CI;
- adding vocabulary never changes the hash or cached result of an existing rule unless that rule calls the new name;
- every primitive and move must ship an equivariance tag and pass the seeded equivariance check before `closure`
  accepts it.

**DSL growth as evidence.** The ledger tracks, for each n, how many level-1/2/3 additions were needed for
`closure` to cover m_n. If the count of required new moves or base cases keeps rising with n, that is the measured
version of the mutation thesis.

## 10. Not in the kernel (deliberately)

No floating point. No unbounded search: every domain is finite and sized. No hidden randomness (seeds explicit).
No side effects except the cache and checkpoints the interpreter controls.

## 11. Implementation plan once approved (Phase 4c)

`metricpoly/dsl/` — `parser.py`, `types.py`, `registry.py`, `interp.py` (exact evaluator, recursion guard, memo +
disk cache, checkpointed `closure`), `prims.py` (kernel; thin wrappers over Phase 2–3 code), `pretty.py`.
`rules/stdlib.mpr` (§7 helpers and moves), `rules/literature.mpr` (generative + structural rules with sources).
Tests: parser round-trip; each primitive against hand-computed values; every C* rule reproduces its stated example;
equivariance check accepts the shipped moves and rejects a deliberately label-dependent one; closure on n ≤ 5 is
saturated and matches Phase 2; core-freeze test.
