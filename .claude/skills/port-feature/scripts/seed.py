"""Bước 1 - Seed: so feature_before vs feature_after ở cấp SYMBOL.

Input: graph của feature_before và feature_after (dựng bằng cùng builder).
Output: symbol thêm mới / bị sửa / bị xoá + danh sách file thay đổi (kể cả Makefile...).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import re
from common import CODE_EXT, load_graph, normalize, read_lines  # noqa: E402

IDENT = re.compile(r"\b[A-Za-z_]\w*\b")


def compute_seed(g_before: dict, g_after: dict, before_dir: Path, after_dir: Path) -> dict:
    nb, na = g_before["nodes"], g_after["nodes"]
    added = sorted(k for k in na if k not in nb)
    removed = sorted(k for k in nb if k not in na)
    modified = sorted(k for k in na if k in nb and na[k]["hash"] != nb[k]["hash"])

    files_b = {str(p.relative_to(before_dir)) for p in before_dir.rglob("*") if p.is_file()}
    files_a = {str(p.relative_to(after_dir)) for p in after_dir.rglob("*") if p.is_file()}
    new_files = sorted(files_a - files_b)
    changed_files = sorted(f for f in files_a & files_b
                           if (before_dir / f).read_bytes() != (after_dir / f).read_bytes())
    # Với symbol DÙNG CHUNG bị sửa (vd bảng menu), chỉ những tên mà feature THÊM VÀO
    # mới là phụ thuộc của feature. Không được đi theo toàn bộ symbol, vì sẽ kéo nhầm
    # cả code của feature khác cùng nằm trong symbol đó.
    def idents(g, root, k):
        n = g["nodes"][k]
        return set(IDENT.findall(normalize(read_lines(root, n["file"], n["start"], n["end"]))))

    new_tokens = {k: sorted(idents(g_after, after_dir, k) - idents(g_before, before_dir, k))
                  for k in modified}
    return dict(
        added=added, modified=modified, removed=removed, new_tokens=new_tokens,
        after_hash={k: na[k]["hash"] for k in added + modified},
        new_files=new_files, changed_files=changed_files,
        non_code_changed=[f for f in changed_files if Path(f).suffix not in CODE_EXT],
    )


if __name__ == "__main__":
    gb, ga = load_graph(sys.argv[1]), load_graph(sys.argv[2])
    seed = compute_seed(gb, ga, Path(gb["root"]), Path(ga["root"]))
    Path(sys.argv[3]).write_text(json.dumps(seed, indent=2))
    print(f"[seed] +{len(seed['added'])} ~{len(seed['modified'])} -{len(seed['removed'])} symbols, "
          f"{len(seed['new_files'])} file mới, {len(seed['changed_files'])} file sửa")
