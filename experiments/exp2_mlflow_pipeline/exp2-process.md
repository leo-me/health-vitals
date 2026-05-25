                      ┌────────────────────────────────────┐
                      │ POST /api/v1/train  (admin JWT)    │
                      │ body: threshold, force_fail, ...   │
                      └──────────────┬─────────────────────┘
                                     ▼
                      ┌────────────────────────────────────┐
                      │ FastAPI BackgroundTask             │
                      │ returns 202 + job_id immediately   │
                      └──────────────┬─────────────────────┘
                                     ▼
     ┌───────────────────────────────────────────────────────────────────┐
     │ ① DATA — feature_service._generate_synthetic                     │
     │   X = N rows of (eda, bvp, acc, ibi)  ← E4-shaped distributions   │
     │   y = rng.choice([0,1], p=[0.4, 0.6]) ← RANDOM, independent of X  │
     │   (this is what makes the model "learn nothing real")             │
     └──────────────┬────────────────────────────────────────────────────┘
                    ▼
              ┌──────────┐  yes   ┌──────────────────────────────┐
              │force_fail│───────▶│ X += Gaussian(0, 5)          │
              └────┬─────┘        │ (train + test both polluted) │
                   │ no           └──────────────┬───────────────┘
                   ▼                             │
     ┌─────────────────────────────────────────◀─┘────────────────────────
     │ ② FEATURES                                                        │
     │   v1: raw eda, bvp, acc, ibi   (4 cols)                           │
     │   v2: raw + rolling mean & std, window=10  (12 cols)              │
     └──────────────┬────────────────────────────────────────────────────┘
                    ▼
     ┌───────────────────────────────────┐
     │ ③ train_test_split  80% / 20%    │
     └──────────────┬────────────────────┘
                    ▼
     ┌────────────────────────────────────────────────────────────────────┐
     │ ④ FIT  — RandomForestClassifier(n_estimators=100, random_state=R) │
     │   builds 100 decision trees on bootstrap subsamples of X_train     │
     │   each tree = a chain of if/else rules learned from the data       │
     └──────────────┬─────────────────────────────────────────────────────┘
                    ▼
     ┌────────────────────────────────────┐
     │ ⑤ PREDICT  — y_pred on X_test      │
     │   each row → 100 votes → majority  │
     └──────────────┬─────────────────────┘
                    ▼
     ┌────────────────────────────────────┐
     │ ⑥ SCORE  accuracy = #correct/#test │
     │   log to MLflow run                │
     └──────────────┬─────────────────────┘
                    ▼
              ┌──────────────┐
              │ acc ≥ thr ?  │
              └──┬────────┬──┘
          yes ◀──┘        └──▶ no
              ▼                ▼
     ┌─────────────┐   ┌───────────────────────────────────┐
     │ ⑦ REGISTER  │   │ Retrain once? (retrain_count==0)  │
     │   • MLflow  │   └────┬──────────────────────┬───────┘
     │     log_   │     yes │                      │ already retrained
     │     model  │         ▼                      ▼
     │   • PG:    │   ┌──────────────────┐   ┌──────────────────┐
     │     insert │   │ random_state +=  │   │ Tag FAILED       │
     │     Model  │   │   100            │   │ no PG write      │
     │     Version│   │ retrain_count=1  │   │ no registry      │
     │     +      │   │ goto ④          │   └────────┬─────────┘
     │     Model  │   └──────────────────┘            │
     │     Reg.   │                                   │
     │   • stage  │                                   │
     │     PROD,  │                                   │
     │     old →  │                                   │
     │     ARCH.  │                                   │
     └──────┬─────┘                                   │
            └──────────────┬────────────────────────◀─┘
                           ▼
                 ┌────────────────────┐
                 │ job.status =       │
                 │   succeeded        │
                 │ GET /train/{id}    │
                 │   returns summary  │
                 └────────────────────┘
