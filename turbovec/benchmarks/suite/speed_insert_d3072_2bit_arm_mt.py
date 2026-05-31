import os, time, json, numpy as np
import faiss
from turbovec import TurboQuantIndex

DATA_DIR = os.path.expanduser("~/data/py-turboquant")
DIM, BIT_WIDTH = 3072, 2

def load_openai(dim, seed=42):
    all_vecs = np.load(os.path.join(DATA_DIR, f"openai-{dim}.npy"))
    rng = np.random.RandomState(seed)
    idx = rng.permutation(len(all_vecs))
    database = all_vecs[idx[:100_000]]
    database /= np.linalg.norm(database, axis=-1, keepdims=True)
    return database

database = load_openai(DIM)

# TurboQuant insert
tq_times = []
for _ in range(5):
    tq = TurboQuantIndex(dim=DIM, bit_width=BIT_WIDTH)
    t0 = time.perf_counter()
    tq.add(database)
    tq_times.append(len(database) / (time.perf_counter() - t0))
tq_vps = sorted(tq_times)[2]

# FAISS PQ insert (train once on 50k, benchmark add on full 100k)
m_pq = 1536
faiss_times = []
train_data = database[:50_000]
for _ in range(5):
    pq = faiss.IndexPQFastScan(DIM, m_pq, 4)
    pq.train(train_data)
    t0 = time.perf_counter()
    pq.add(database)
    faiss_times.append(len(database) / (time.perf_counter() - t0))
faiss_vps = sorted(faiss_times)[2]

result = {"dim": DIM, "bit_width": BIT_WIDTH, "arch": "arm", "threading": "mt",
          "tq_vecs_per_sec": round(tq_vps), "faiss_vecs_per_sec": round(faiss_vps)}
out = os.path.join(os.path.dirname(__file__), "..", "results", "speed_insert_d3072_2bit_arm_mt.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(result, open(out, "w"), indent=2)
print(json.dumps(result, indent=2))
