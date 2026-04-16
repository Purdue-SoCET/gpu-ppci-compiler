from .. import ir
from collections import defaultdict


def _add_pred(pred_set, pred_id):
    if pred_id not in (None, 0):
        pred_set.add(pred_id)


def _instruction_pred_uses_defs(ins):
    """Return (uses, defs) for predicate values in a single IR instruction.

    This models *real* predicate dataflow used by backend lowering.
    PredicateAnnotation is metadata only and does not itself define a
    predicate register.
    """
    uses = set()
    defs = set()

    # Regular predicated instruction execution.
    pred = getattr(ins, "pred", None)
    _add_pred(uses, pred)

    if isinstance(ins, ir.PredicateAnnotation):
        # Annotation only: the predicate is defined in a predecessor jump.
        # Do not create fake defs/uses here.
        return uses, defs

    if isinstance(ins, ir.SJump):
        _add_pred(defs, ins.pred_yes_id)
        _add_pred(uses, ins.pred_parent_id)
        return uses, defs

    if isinstance(ins, ir.PJump):
        # PJMP is now a real test-predicate jump.
        _add_pred(uses, ins.pred_test_id)
        # pred_parent_id is structural metadata only; backend PJMP does not
        # consume it, so it should not extend liveness artificially.
        return uses, defs

    if isinstance(ins, ir.BJump):
        _add_pred(defs, ins.pred_yes_id)
        _add_pred(defs, ins.pred_no_id)
        _add_pred(uses, ins.pred_parent_id)
        return uses, defs

    return uses, defs


def collect_predicate_info(ir_function):
    """Collect per-block predicate defs/uses for IR-level allocation."""
    block_defs = defaultdict(set)
    block_uses = defaultdict(set)
    all_preds = {0}

    for block in ir_function:
        for ins in block:
            uses, defs = _instruction_pred_uses_defs(ins)
            block_uses[block].update(uses)
            block_defs[block].update(defs)
            all_preds.update(uses)
            all_preds.update(defs)

    return block_defs, block_uses, all_preds


def compute_liveness(ir_function, block_defs, block_uses):
    """Compute classic block-level liveness for virtual predicates."""
    live_in = {block: set() for block in ir_function}
    live_out = {block: set() for block in ir_function}

    changed = True
    while changed:
        changed = False
        for block in reversed(list(ir_function)):
            old_in = live_in[block].copy()
            old_out = live_out[block].copy()

            succs = list(block.successors)
            live_out[block] = (
                set().union(*(live_in[s] for s in succs)) if succs else set()
            )
            live_in[block] = block_uses[block] | (
                live_out[block] - block_defs[block]
            )

            if live_in[block] != old_in or live_out[block] != old_out:
                changed = True

    return live_in, live_out


def build_interference(ir_function, live_in, live_out):
    """Build an interference graph that also respects in-block ordering."""
    graph = defaultdict(set)

    def add_edge(a, b):
        if a in (None, 0) or b in (None, 0) or a == b:
            return
        graph[a].add(b)
        graph[b].add(a)

    for block in ir_function:
        live = set(live_out[block])

        # Walk backwards so in-block ordering is respected.
        for ins in reversed(list(block)):
            uses, defs = _instruction_pred_uses_defs(ins)

            # A predicate defined here must not alias with:
            #   1) anything live after this instruction
            #   2) any predicate used by this same instruction
            #   3) any other predicate defined by this same instruction
            for d in defs:
                for other in live | uses | (defs - {d}):
                    add_edge(d, other)

            live.difference_update(defs)
            live.update(uses)

        # Any predicates simultaneously live at block entry also interfere.
        live_list = [p for p in live_in[block] if p not in (None, 0)]
        for i in range(len(live_list)):
            for j in range(i + 1, len(live_list)):
                add_edge(live_list[i], live_list[j])

    return graph


def assign_physical_predicates(interference, all_preds, max_physical=32):
    """Greedily color virtual predicates onto the hardware predicate file."""
    mapping = {0: 0}  # VP0 -> P0

    alloc_order = sorted(
        (v for v in all_preds if v != 0),
        key=lambda v: (-len(interference.get(v, ())), v),
    )

    for vpred in alloc_order:
        used = {
            mapping[n] for n in interference.get(vpred, set()) if n in mapping
        }

        assigned = None
        for preg in range(1, max_physical):
            if preg not in used:
                assigned = preg
                break

        if assigned is None:
            raise RuntimeError(
                "Predicate allocation failed: no free physical "
                f"predicate for VP{vpred}"
            )

        mapping[vpred] = assigned

    return mapping


def rewrite_predicates(ir_function, mapping):
    """Rewrite IR instructions in place once the virtual mapping is fixed."""
    for block in ir_function:
        for ins in block:
            if hasattr(ins, "pred") and ins.pred in mapping:
                ins.pred = mapping[ins.pred]

            if isinstance(ins, ir.PredicateAnnotation):
                ins.pred_reg = mapping.get(ins.pred_reg, ins.pred_reg)
                ins.parent_pred_reg = mapping.get(
                    ins.parent_pred_reg, ins.parent_pred_reg
                )

            if isinstance(ins, ir.SJump):
                ins.pred_yes_id = mapping.get(ins.pred_yes_id, ins.pred_yes_id)
                ins.pred_parent_id = mapping.get(
                    ins.pred_parent_id, ins.pred_parent_id
                )

            if isinstance(ins, ir.PJump):
                ins.pred_test_id = mapping.get(
                    ins.pred_test_id, ins.pred_test_id
                )
                ins.pred_parent_id = mapping.get(
                    ins.pred_parent_id, ins.pred_parent_id
                )

            if isinstance(ins, ir.BJump):
                ins.pred_yes_id = mapping.get(ins.pred_yes_id, ins.pred_yes_id)
                ins.pred_no_id = mapping.get(ins.pred_no_id, ins.pred_no_id)
                ins.pred_parent_id = mapping.get(
                    ins.pred_parent_id, ins.pred_parent_id
                )


def allocate_predicates_for_function(ir_function):
    """Late predicate allocation pass run after IR CFG construction."""
    block_defs, block_uses, all_preds = collect_predicate_info(ir_function)
    live_in, live_out = compute_liveness(ir_function, block_defs, block_uses)
    interference = build_interference(ir_function, live_in, live_out)
    mapping = assign_physical_predicates(interference, all_preds)
    rewrite_predicates(ir_function, mapping)
    return mapping
