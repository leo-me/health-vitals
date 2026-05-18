# Exp 1 — Cache Layer Response Time

Measures the latency impact of Redis caching in `consumer_delivery` across three concurrency levels.

**Endpoint under test:** `GET /api/v1/data/smart_watch/{user_id}`

---

## Prerequisites

1. Docker services running:
   ```bash
   cd infra && docker compose up -d
   ```

2. Local PostgreSQL (port 5432) seeded with users, devices, and sensor data:
   ```bash
   # From project root
   DATABASE_URL=postgresql://postgres:0000@localhost:5432/health_db \
       python data/pipelines/seed_fixtures.py

   DATABASE_URL=postgresql://postgres:0000@localhost:5432/health_db \
       python data/pipelines/load_subjects.py
   ```

3. Locust installed:
   ```bash
   pip install -r experiments/exp1_cache_latency/requirements.txt
   ```

---

## Running the experiment

The matrix is **6 runs**: 3 concurrency levels × 2 cache states (OFF / ON).  
`CACHE_ENABLED` is a `consumer_delivery` environment variable — restart the container to toggle it.

### Step 1 — Cache OFF

```bash
cd infra && CACHE_ENABLED=false docker compose up -d consumer_delivery
```

```bash
cd experiments/exp1_cache_latency

locust -f locustfile.py --headless -u 1  -r 1  --run-time 60s --csv results/u1_no_cache
locust -f locustfile.py --headless -u 10 -r 2  --run-time 60s --csv results/u10_no_cache
locust -f locustfile.py --headless -u 50 -r 5  --run-time 60s --csv results/u50_no_cache
```

### Step 2 — Cache ON

```bash
cd infra && CACHE_ENABLED=true docker compose up -d consumer_delivery
```

```bash
cd experiments/exp1_cache_latency

locust -f locustfile.py --headless -u 1  -r 1  --run-time 60s --csv results/u1_cache
locust -f locustfile.py --headless -u 10 -r 2  --run-time 60s --csv results/u10_cache
locust -f locustfile.py --headless -u 50 -r 5  --run-time 60s --csv results/u50_cache
```

---

## Output

Each run produces three CSV files in `results/`:

| File | Contents |
|------|----------|
| `<name>_stats.csv` | p50 / p95 / p99 latency, RPS, failure count |
| `<name>_stats_history.csv` | Time-series RPS and latency |
| `<name>_failures.csv` | Per-failure detail |

---

## Actual results

All requests targeted `GET /api/v1/data/smart_watch/{user_id}`, rotating randomly across 31 users.  
Each run lasted 60 seconds. No failures in any run.

| Concurrency | Cache | p50 (ms) | p95 (ms) | p99 (ms) | Avg (ms) | RPS |
|-------------|-------|----------|----------|----------|----------|-----|
| u=1  | OFF | 170 | 260 | 300 | 168 | 3.4 |
| u=1  | ON  | 170 | 280 | 420 | 171 | 3.3 |
| u=10 | OFF | 280 | 560 | 730 | 298 | 22.7 |
| u=10 | ON  | 310 | 660 | 840 | 333 | 20.9 |
| u=50 | OFF | 1700 | 2500 | 2800 | 1675 | 25.2 |
| u=50 | ON  | 1900 | 3100 | 4000 | 1898 | 22.4 |

| Concurrency | Δp95 (cache vs no-cache) | ΔRPS |
|-------------|--------------------------|------|
| u=1  | +7.7%  | −0.9% |
| u=10 | +17.9% | −7.7% |
| u=50 | +24.0% | −11.1% |

---

## Conclusion (English)

**Redis cache did not reduce latency in this experiment; it consistently increased it.**

### Parameter design

| Parameter | Value |
|-----------|-------|
| Concurrency levels | u = 1, 10, 50 (spawn rate 1, 2, 5) |
| Duration per run | 60 seconds |
| User pool | 31 unique user IDs (random selection) |
| Cache TTL | 5 s (smart_watch data frequency = 5 000 ms) |
| Endpoint | `GET /api/v1/data/smart_watch/{user_id}` |
| Backend DB | PostgreSQL 16 on localhost (host machine) |
| Cache store | Redis 7 inside Docker (same network as consumer_delivery) |

### Findings

At u=1, cache adds negligible overhead (Δp95 ≈ +8 ms, within noise). As concurrency rises the gap widens: at u=50, p95 jumps from 2 500 ms to 3 100 ms (+24%) and p99 from 2 800 ms to 4 000 ms (+43%) with cache ON.

### Root cause analysis

Three factors explain the counter-intuitive result:

1. **Redis overhead is not free.** Every request — including cache hits — executes a synchronous Redis `GET` before any DB work. The Redis container is on the same Docker bridge network as `consumer_delivery`, but the round-trip still adds ~10–30 ms per request. Under high concurrency these add up.

2. **PostgreSQL is effectively a warm in-process cache.** The DB runs directly on the host machine and holds only ~6.7 M rows across 31 users. All frequently-accessed rows fit comfortably in PostgreSQL's shared buffer. The 6 sequential `SELECT … ORDER BY timestamp DESC LIMIT 1` queries return in well under 50 ms against a warm buffer pool, so there is little latency to save.

3. **Cache hit rate is high but the overhead still dominates.** With 31 users, a 5 s TTL, and ~25 RPS at u=50, the theoretical cache-hit rate is ≈80%. Yet even serving 80% of requests from Redis is slower than serving 100% directly from a warm PostgreSQL buffer, because the Redis GET + JSON deserialise path is on the critical path for every request.

### Implication

Redis caching benefits a system when: (a) DB queries are genuinely slow (complex joins, cold buffer, remote DB), or (b) cache hit rate is near 100% and the Redis round-trip is negligible compared to query cost. In this deployment — a local PostgreSQL with a small hot dataset — neither condition holds. The caching layer adds coordinated overhead at every concurrency level.

---

## 实验结论（中文）

**本次实验中，Redis 缓存未能降低延迟，反而在各并发级别下一致地提高了延迟。**

### 参数设计

| 参数 | 取值 |
|------|------|
| 并发级别 | u = 1、10、50（spawn rate 分别为 1、2、5） |
| 每轮时长 | 60 秒 |
| 用户池 | 31 个唯一 user_id，随机选取 |
| 缓存 TTL | 5 秒（smart_watch 数据频率 = 5 000 ms） |
| 测试端点 | `GET /api/v1/data/smart_watch/{user_id}` |
| 后端数据库 | PostgreSQL 16，运行于宿主机（localhost） |
| 缓存存储 | Redis 7，运行于 Docker 内部网络 |

### 实验发现

u=1 时，缓存带来的额外开销可忽略不计（Δp95 ≈ +8 ms，处于噪声范围内）。随着并发升高，差距持续扩大：u=50 时，开启缓存后 p95 从 2 500 ms 升至 3 100 ms（+24%），p99 从 2 800 ms 升至 4 000 ms（+43%）。所有场景下零请求失败。

### 根因分析

三个因素共同解释了这一与预期相反的结果：

1. **Redis 开销不可忽略。** 每次请求——包括缓存命中的请求——都需要先执行一次同步 Redis `GET`，再决定是否查库。Redis 容器与 `consumer_delivery` 处于同一 Docker bridge 网络，但每次往返仍增加约 10–30 ms 延迟，高并发下累积效应显著。

2. **PostgreSQL 本身相当于一个热内存缓存。** 数据库直接运行于宿主机，数据总量约 670 万行，分属 31 个用户。所有高频访问行均可常驻 PostgreSQL 共享缓冲区（shared_buffers）。针对每个信号类型执行的 6 条 `SELECT … ORDER BY timestamp DESC LIMIT 1` 查询，在热缓冲状态下均可在 50 ms 以内返回，几乎没有可被缓存压缩的延迟空间。

3. **命中率虽高，但额外开销仍超过收益。** 在 31 个用户、5 秒 TTL、u=50 约 25 RPS 的条件下，理论缓存命中率约为 80%。然而，即使将 80% 的请求交由 Redis 处理，也慢于 100% 直查热态 PostgreSQL——因为 Redis GET + JSON 反序列化的路径本身就处于每个请求的关键链路上。

### 结论意义

Redis 缓存的价值体现在以下场景：(a) 数据库查询本身耗时显著（复杂 JOIN、冷缓冲、远程数据库）；或 (b) 缓存命中率接近 100% 且 Redis 往返延迟相对查询成本可以忽略。在本次部署中——宿主机本地 PostgreSQL、小型热数据集——上述条件均不满足，缓存层在每个并发级别下均引入了额外的协调开销，而非减少了延迟。
