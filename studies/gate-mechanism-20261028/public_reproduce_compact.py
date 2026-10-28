"""Reproduce released compact mechanism-study counts, never detector/SDK output.

Python 3.11+ standard library only. Default inputs are beside this script.
This is a numerical check of saved matching statuses, not GT rematching,
training, fresh-data validation, or external independent replication.
"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

CLASSES = ("pedestrian", "bicycle", "motorcycle")
CLASS_CODES = {"p": "pedestrian", "b": "bicycle", "m": "motorcycle"}
BURDEN = ("saved_all", "saved_pedestrian", "unmatched_pedestrian_allrange")
STATES = ("recovered", "newly_lost", "persistent_matched", "persistent_missed")
FRAME_NAMES = ("fully_recovered_frame", "newly_failed_frame", "persistent_failed_frame",
               "within_frame_identity_exchange", "equal_count_identity_exchange",
               "persistent_failed_fewer_misses", "persistent_failed_equal_misses",
               "persistent_failed_more_misses")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def equal(expected, actual, label="value"):
    """Compare all expected numeric/identity fields, allowing copied prose extras."""
    count = 1
    if isinstance(expected, dict):
        require(isinstance(actual, dict), label + ": expected mapping")
        for key, value in expected.items():
            require(key in actual, label + ": missing " + key)
            count += equal(value, actual[key], label + "/" + key)
    elif isinstance(expected, list):
        require(isinstance(actual, list) and len(expected) == len(actual), label + ": list length differs")
        for i, (x, y) in enumerate(zip(expected, actual)):
            count += equal(x, y, label + "/" + str(i))
    elif isinstance(expected, float):
        require(isinstance(actual, (int, float)) and math.isfinite(actual) and
                math.isclose(expected, actual, rel_tol=1e-12, abs_tol=1e-12), label + ": float differs")
    else:
        require(expected == actual, label + ": value differs")
    return count


def decode_scope(payload):
    require(payload.get("schema_version") == 1, "Unknown compact schema")
    frames, samples, annotations = [], set(), set()
    for frame in payload["frames"]:
        require(set(frame) == {"s", "l", "f", "r", "g", "b", "h", "t"}, "Unexpected compact frame fields")
        require(frame["s"] not in samples, "Duplicate compact sample")
        samples.add(frame["s"])
        require(frame["f"] in ("F1", "F2") and frame["r"] in ("outer", "development"), "Invalid role/fold")
        require(isinstance(frame["h"], str) and len(frame["h"]) == 64 and
                all(c in "0123456789abcdef" for c in frame["h"]), "Invalid prediction-file digest")
        require(len(frame["b"]) == 3 and all(isinstance(x, int) and x >= 0 for x in frame["b"]), "Invalid burden input")
        require(len(frame["g"]) == 4 and all(isinstance(x, (int, float)) and math.isfinite(x) and
                0 <= x <= 1 for x in frame["g"]), "Invalid gate coefficient input")
        targets, slots = {}, set()
        for target in frame["t"]:
            require(len(target) == 6, "Invalid target tuple")
            annotation, instance, code, slot, distance, score = target
            require(annotation not in annotations and annotation not in targets, "Duplicate compact annotation")
            require(code in CLASS_CODES and isinstance(instance, str), "Invalid critical-target identity/class")
            if slot is None:
                require(distance is None and score is None, "Unmatched target has match metadata")
            else:
                require(isinstance(slot, int) and slot >= 0 and slot not in slots, "Invalid or duplicate matched output slot")
                require(isinstance(distance, (int, float)) and math.isfinite(distance) and 0 <= distance < 2,
                        "Saved match violates distance threshold")
                require(isinstance(score, (int, float)) and math.isfinite(score) and .1 <= score <= 1,
                        "Saved match violates score threshold")
                slots.add(slot)
            annotations.add(annotation)
            targets[annotation] = {"instance": instance, "class": CLASS_CODES[code],
                                   "slot": slot, "distance": distance, "score": score}
        frames.append({"sample": frame["s"], "log": frame["l"], "fold": frame["f"], "role": frame["r"],
                       "gates": frame["g"], "burden": dict(zip(BURDEN, frame["b"])),
                       "prediction_sha256": frame["h"], "targets": targets})
    require(frames, "Empty compact scope")
    return frames


def total(frames, cls="joint"):
    observations = [(r, annotation, target) for r in frames for annotation, target in r["targets"].items()
                    if cls == "joint" or target["class"] == cls]
    n = len(observations)
    hits = sum(t["slot"] is not None for _, _, t in observations)
    instance_ids = {t["instance"] for _, _, t in observations}
    targets, failed = 0, 0
    for frame in frames:
        chosen = [t for t in frame["targets"].values() if cls == "joint" or t["class"] == cls]
        targets += bool(chosen)
        failed += any(t["slot"] is None for t in chosen)
    return {"objects": n, "hits": hits, "recall": hits / n if n else None,
            "unique_instances": len(instance_ids), "frames": len(frames), "target_frames": targets,
            "failure_frames": failed, "AnyMiss_target": failed / targets if targets else None,
            "AnyMiss_allframe": failed / len(frames) if frames else None}


def instance_summary(frames):
    groups = {}
    for frame in frames:
        for target in frame["targets"].values():
            obj = groups.setdefault(target["instance"], {"instance_token": target["instance"],
                "class": target["class"], "objects": 0, "hits": 0})
            require(obj["class"] == target["class"], "Mapped instance class changes")
            obj["objects"] += 1
            obj["hits"] += target["slot"] is not None
    for obj in groups.values():
        obj["recall"] = obj["hits"] / obj["objects"]
        obj["any_observation_matched"] = obj["hits"] > 0
        obj["all_observations_matched"] = obj["hits"] == obj["objects"]
    return [groups[k] for k in sorted(groups)]


def scope_summary(frames):
    logs = sorted({r["log"] for r in frames})
    per_log = {g: {"joint": total([r for r in frames if r["log"] == g]),
                  "per_class": {c: total([r for r in frames if r["log"] == g], c) for c in CLASSES}} for g in logs}
    result = {"joint": total(frames), "per_class": {c: total(frames, c) for c in CLASSES},
        "burden": {k: sum(r["burden"][k] for r in frames) for k in BURDEN},
        "per_log": per_log, "samples": sorted(r["sample"] for r in frames), "log_tokens": logs,
        "folds": sorted({r["fold"] for r in frames}), "per_instance": instance_summary(frames),
        "per_log_burden": {g: {k: sum(r["burden"][k] for r in frames if r["log"] == g) for k in BURDEN} for g in logs},
        "equal_log": {}}
    for cls in ("joint",) + CLASSES:
        parts = [per_log[g]["joint"] if cls == "joint" else per_log[g]["per_class"][cls] for g in logs]
        recalls = [p["recall"] for p in parts if p["objects"]]
        target_rates = [p["AnyMiss_target"] for p in parts if p["target_frames"]]
        result["equal_log"][cls] = {"logs": len(logs), "supported_logs": len(recalls),
            "recall_all_logs": sum(recalls) / len(logs) if logs and len(recalls) == len(logs) else None,
            "recall_supported_logs": sum(recalls) / len(recalls) if recalls else None,
            "AnyMiss_target_all_logs": sum(target_rates) / len(logs) if logs and len(target_rates) == len(logs) else None,
            "AnyMiss_allframe": sum(p["AnyMiss_allframe"] for p in parts) / len(parts) if parts else None}
    result["equal_log_pedestrian_recall"] = result["equal_log"]["pedestrian"]["recall_all_logs"]
    result["gate_telemetry"] = {"frames_with_telemetry": len(frames), "per_layer": [
        {"layer": i, "minimum": min(r["gates"][i] for r in frames), "maximum": max(r["gates"][i] for r in frames),
         "mean": sum(r["gates"][i] for r in frames) / len(frames)} for i in range(4)]}
    return result


def paired_frames(before, after):
    a, b = ({r["sample"]: r for r in data} for data in (before, after))
    require(len(a) == len(before) and len(b) == len(after) and set(a) == set(b), "Paired compact sample coverage differs")
    output = []
    for sample in sorted(a):
        x, y = a[sample], b[sample]
        require(all(x[k] == y[k] for k in ("sample", "log", "fold", "role")), "Paired compact group identity differs")
        require(set(x["targets"]) == set(y["targets"]), "Paired critical annotation identity differs")
        require(all(x["targets"][k]["instance"] == y["targets"][k]["instance"] and
                    x["targets"][k]["class"] == y["targets"][k]["class"] for k in x["targets"]),
                "Paired annotation metadata differs")
        output.append((x, y))
    return output


def pair_summary(before, after, cls="joint"):
    transitions = {k: 0 for k in STATES}
    frame_counts = {k: 0 for k in FRAME_NAMES}
    objects, instances, delta_hits, delta_failures = 0, {}, 0, 0
    for x, y in paired_frames(before, after):
        recovered, lost, h0, h1, missed0, missed1 = 0, 0, 0, 0, 0, 0
        for annotation, g0 in x["targets"].items():
            if cls != "joint" and g0["class"] != cls:
                continue
            g1 = y["targets"][annotation]
            b, a = g0["slot"] is not None, g1["slot"] is not None
            state = "persistent_matched" if b and a else "newly_lost" if b else "recovered" if a else "persistent_missed"
            transitions[state] += 1
            recovered += state == "recovered"
            lost += state == "newly_lost"
            h0 += b
            h1 += a
            missed0 += not b
            missed1 += not a
            objects += 1
            obj = instances.setdefault(g0["instance"], {"instance_token": g0["instance"], "class": g0["class"],
                "objects": 0, "before_hits": 0, "after_hits": 0, **{k: 0 for k in STATES}})
            obj["objects"] += 1
            obj["before_hits"] += b
            obj["after_hits"] += a
            obj[state] += 1
        f0, f1 = missed0 > 0, missed1 > 0
        frame_counts["fully_recovered_frame"] += f0 and not f1
        frame_counts["newly_failed_frame"] += not f0 and f1
        frame_counts["persistent_failed_frame"] += f0 and f1
        frame_counts["within_frame_identity_exchange"] += recovered > 0 and lost > 0
        frame_counts["equal_count_identity_exchange"] += recovered > 0 and lost > 0 and h0 == h1
        frame_counts["persistent_failed_fewer_misses"] += f0 and f1 and missed1 < missed0
        frame_counts["persistent_failed_equal_misses"] += f0 and f1 and missed1 == missed0
        frame_counts["persistent_failed_more_misses"] += f0 and f1 and missed1 > missed0
        delta_hits += h1 - h0
        delta_failures += int(f1) - int(f0)
    require(delta_hits == transitions["recovered"] - transitions["newly_lost"], "Compact target balance failed")
    require(delta_failures == frame_counts["newly_failed_frame"] - frame_counts["fully_recovered_frame"], "Compact frame balance failed")
    return {"objects": objects, "unique_instances": len(instances), "target_transitions": transitions,
            "frame_transitions": frame_counts, "delta_hits": delta_hits, "delta_failure_frames": delta_failures,
            "per_instance": [instances[k] for k in sorted(instances)]}


def comparison_summary(before, after):
    logs = sorted({r["log"] for r in before})
    pairs = paired_frames(before, after)
    deltas = [[y["gates"][i] - x["gates"][i] for i in range(4)] for x, y in pairs]
    return {"joint": pair_summary(before, after), "per_class": {c: pair_summary(before, after, c) for c in CLASSES},
        "per_log": {g: {"joint": pair_summary([r for r in before if r["log"] == g], [r for r in after if r["log"] == g]),
            "per_class": {c: pair_summary([r for r in before if r["log"] == g], [r for r in after if r["log"] == g], c) for c in CLASSES}} for g in logs},
        "burden_change": {k: sum(r["burden"][k] for r in after) - sum(r["burden"][k] for r in before) for k in BURDEN},
        "gate_difference": {"frames_with_telemetry": len(deltas), "per_layer": [
            {"layer": i, "mean_signed": sum(r[i] for r in deltas) / len(deltas),
             "mean_absolute": sum(abs(r[i]) for r in deltas) / len(deltas),
             "maximum_absolute": max(abs(r[i]) for r in deltas)} for i in range(4)]}}


def criterion(summaries, seeds):
    result = []
    for seed in seeds:
        d, c = (summaries[f"seed_{seed}/{arm}/outer_clean"] for arm in ("dynamic", "constant"))
        dr, cr = d["per_class"]["pedestrian"]["recall"], c["per_class"]["pedestrian"]["recall"]
        dl, cl = d["equal_log"]["pedestrian"]["recall_all_logs"], c["equal_log"]["pedestrian"]["recall_all_logs"]
        diff = dr - cr if dr is not None and cr is not None else None
        logdiff = dl - cl if dl is not None and cl is not None else None
        saved_d, saved_c = d["burden"]["saved_pedestrian"], c["burden"]["saved_pedestrian"]
        conditions = {"pedestrian_recall_at_least_1pp": diff is not None and diff >= .01 - 1e-12,
            "joint_failure_frames_do_not_increase": d["joint"]["failure_frames"] <= c["joint"]["failure_frames"],
            "equal_log_pedestrian_effect_nonnegative": logdiff is not None and logdiff >= -1e-12,
            "saved_pedestrian_increase_at_most_5percent": 100 * saved_d <= 105 * saved_c}
        result.append({"seed": seed, "dynamic_minus_constant_pedestrian_recall": diff,
            "dynamic_minus_constant_equal_log_pedestrian_recall": logdiff,
            "dynamic_minus_constant_joint_failure_frames": d["joint"]["failure_frames"] - c["joint"]["failure_frames"],
            "saved_pedestrian_ratio": saved_d / saved_c if saved_c else None,
            "saved_pedestrian_dynamic": saved_d, "saved_pedestrian_constant": saved_c,
            "conditions": conditions, "passes": all(conditions.values())})
    passed = all(r["passes"] for r in result)
    return {"primary_view": "outer_clean", "contrast": "dynamic minus constant, matched final600", "per_seed": result,
        "all_seeds_pass": passed, "decision": "DESCRIPTIVE_CRITERION_MET_NO_EXTERNAL_VALIDATION" if passed else "CRITERION_FAILED_STOP_CANDIDATE_EXPANSION"}


def expected_scope_keys(protocol):
    return {f"seed_{seed}/{arm}/{view}" for seed in protocol["seeds"] for arm in [*protocol["arms"], "neutral"]
            for view in (protocol["evaluation"]["views"] if arm != "neutral" else ("outer_clean", "outer_clean_decoder_lidar_zero"))}


def verify_roles(protocol, scopes):
    audits = protocol["publication_role_audit"]["folds"]
    require(set(audits) == set(protocol["folds"]), "Public role audit is incomplete")
    count = 0
    for fold, audit in audits.items():
        training = audit["ordered_training_samples"]
        require(len(training) == audit["actual_sampling_metadata_frames"] and len({r[0] for r in training}) == len(training),
                "Public training-order frame count differs")
        require(audit["raw_training_count_equals_sampling_count"] ==
                (audit["raw_expected_frames"]["detector_train"] == len(training)), "Raw/sampling count agreement flag differs")
        scene_roles = audit["scene_roles"]
        roles = {"train": "detector_train", "development": "detector_development", "outer": "outer_test"}
        logs = {}
        for role, log_key in roles.items():
            logs[role] = {r["log_token"] for r in scene_roles[role]}
            require(logs[role] == set(audit["logs"][log_key]), "Public scene/log roles disagree")
        require(all(not a & b for a, b in itertools.combinations(logs.values(), 2)), "Same-fold log roles overlap")
        require(all(r[1] in {x["scene_token"] for x in scene_roles["train"]} for r in training),
                "Ordered training scene escaped declared role")
        train_tokens = {r[0] for r in training}
        for key, frames in scopes.items():
            selected = [r for r in frames if r["fold"] == fold]
            require(selected and len({r["role"] for r in selected}) == 1, "Missing or mixed same-fold evaluation role")
            role = selected[0]["role"]
            require(all(r["log"] in logs[role] and r["sample"] not in train_tokens for r in selected),
                    "Evaluation escaped declared same-fold log/sample role")
            require({r["log"] for r in selected} == logs[role], "Evaluation log coverage differs from public roles")
            require(len(selected) == audit["raw_expected_frames"][roles[role]], "Evaluation frame count differs from role inventory")
            count += len(selected) + 1
    return count


def verify(root, check_manifest=True):
    root = Path(root)
    checks = 0
    if check_manifest:
        manifest = read(root / "manifest.json")
        for item in manifest["files"]:
            relative = Path(item["path"])
            require(not relative.is_absolute() and ".." not in relative.parts, "Unsafe manifest relative path")
            path = root / relative
            require(path.stat().st_size == item["bytes"] and sha(path) == item["sha256"], "Public byte hash differs: " + item["path"])
            checks += 1
    p, result, index = (read(root / name) for name in ("protocol.json", "summary_results.json", "compact_index.json"))
    keys = expected_scope_keys(p)
    require(set(index["scopes"]) == keys == set(result["summaries"]), "Released scope matrix incomplete")
    require(len(keys) == 30, "Unexpected frozen pooled scope count")
    frames, summaries = {}, {}
    for key in sorted(keys):
        item = index["scopes"][key]
        relative = Path(item["path"])
        require(not relative.is_absolute() and ".." not in relative.parts, "Unsafe compact input path")
        payload = read(root / relative)
        require(payload["scope_key"] == key, "Compact scope identity differs")
        require(sha(root / relative) == item["sha256"], "Compact scope digest differs")
        frames[key] = decode_scope(payload)
        summaries[key] = scope_summary(frames[key])
        checks += equal(summaries[key], result["summaries"][key], key)
    checks += verify_roles(p, frames)
    require(len(result["comparisons"]) == 39, "Frozen comparison matrix incomplete")
    for label, claimed in result["comparisons"].items():
        require(claimed["before"] in frames and claimed["after"] in frames, "Comparison uses an absent scope")
        observed = comparison_summary(frames[claimed["before"]], frames[claimed["after"]])
        checks += equal(observed, claimed, label)
    reproduced_criterion = criterion(summaries, p["seeds"])
    checks += equal(reproduced_criterion, result["descriptive_criterion"], "criterion")
    return {"status": "PASS", "checks": checks, "pooled_scopes": len(keys), "comparisons": len(result["comparisons"]),
        "criterion": reproduced_criterion["decision"], "synthetic_self_test": self_test(),
        "scope": "Saved critical matching-status and gate/count arithmetic only. SDK mAP/NDS/pedAP, SDK filtered support and decoder RMS are copied local outputs, not recomputed. Burden is saved input, not official FP/precision. No GT rematching, detector training/inference or external replication."}


def self_test():
    configs = 0
    for n in range(5):
        for bits0, bits1 in itertools.product(range(1 << n), repeat=2):
            def frame(bits):
                return {"sample": "s", "log": "l", "fold": "F1", "role": "outer", "gates": [.5] * 4,
                    "burden": dict(zip(BURDEN, (2, 2, 1))), "prediction_sha256": "0" * 64,
                    "targets": {f"a{i}": {"instance": f"i{i//2}", "class": "pedestrian", "slot": i if bits & (1 << i) else None,
                        "distance": .5 if bits & (1 << i) else None, "score": .5 if bits & (1 << i) else None} for i in range(n)}}
            out = pair_summary([frame(bits0)], [frame(bits1)])
            recovered = sum(not bits0 & (1 << i) and bool(bits1 & (1 << i)) for i in range(n))
            lost = sum(bool(bits0 & (1 << i)) and not bits1 & (1 << i) for i in range(n))
            require(out["target_transitions"]["recovered"] == recovered and out["target_transitions"]["newly_lost"] == lost,
                    "Synthetic transition mismatch")
            require(out["delta_hits"] == bits1.bit_count() - bits0.bit_count(), "Synthetic hit balance mismatch")
            require(out["frame_transitions"]["equal_count_identity_exchange"] == int(bits0 != bits1 and bits0.bit_count() == bits1.bit_count()),
                    "Synthetic equal-count exchange mismatch")
            configs += 1
    return {"status": "PASS", "finite_hit_set_configurations": configs, "scope": "Synthetic arithmetic, not real efficacy"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    print(json.dumps(self_test() if args.self_test else verify(args.root), allow_nan=False))
