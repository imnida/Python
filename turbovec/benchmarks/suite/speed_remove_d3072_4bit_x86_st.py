import os
os.environ["RAYON_NUM_THREADS"] = "1"
import time, json, numpy as np
from turbovec import TurboQuantIndex, IdMapIndex

DATA_DIR = os.path.expanduser("~/data/py-turboquant")
DIM, BIT_WIDTH = 3072, 4
N = 50_000

def load_openai(dim, seed=42):
    all_vecs = np.load(os.path.join(DATA_DIR, f"openai-{dim}.npy"))
    rng = np.random.RandomState(seed)
    idx = rng.permutation(len(all_vecs))
    database = all_vecs[idx[:N]]
    database /= np.linalg.norm(database, axis=-1, keepdims=True)
    return database

database = load_openai(DIM)
ids = np.arange(N, dtype=np.uint64)

# IdMapIndex removal
im_times = []
for _ in range(5):
    im = IdMapIndex(dim=DIM, bit_width=BIT_WIDTH)
    im.add_with_ids(database, ids)
    t0 = time.perf_counter()
    for i in range(N):
        im.remove(i)
    im_times.append(N / (time.perf_counter() - t0))
im_vps = sorted(im_times)[2]

# TurboQuantIndex swap_remove (lower-level baseline)
tq_times = []
for _ in range(5):
    tq = TurboQuantIndex(dim=DIM, bit_width=BIT_WIDTH)
    tq.add(database)
    t0 = time.perf_counter()
    while len(tq) > 0:
        tq.swap_remove(0)
    tq_times.append(N / (time.perf_counter() - t0))
tq_vps = sorted(tq_times)[2]

result = {"dim": DIM, "bit_width": BIT_WIDTH, "arch": "x86", "threading": "st",
          "id_map_vecs_per_sec": round(im_vps), "swap_remove_vecs_per_sec": round(tq_vps)}
out = os.path.join(os.path.dirname(__file__), "..", "results", "speed_remove_d3072_4bit_x86_st.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(result, open(out, "w"), indent=2)
print(json.dumps(result, indent=2))
