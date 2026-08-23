# Credit Risk Scoring Service

This is a FastAPI service that scores credit risk on individual loan applications, explains *why* it made that call using SHAP, and can run a Monte Carlo simulation over a full day's worth of scored loans to get a sense of portfolio-level risk (VaR/CVaR).

It's the ML-serving half of a bigger credit risk system I'm building. The other half — users, auth, and persisting the daily reports — is a separate Java/Spring Boot service that talks to this one over RabbitMQ.

This repo is just the Python scoring engine.

## Why I built it this way

A model that spits out "0.7 chance of default" and nothing else isn't particularly useful to an actual risk team.

There are two things I wanted on top of the prediction:

1. **A reason.** If a loan gets rejected, someone — a risk analyst, an auditor, eventually the applicant — is going to want to know why. The SHAP explainer doesn't just classify the application; it tells you which features pushed the prediction and by how much.

2. **The bigger picture.** One loan defaulting doesn't tell you much. What a risk team actually cares about is what happens to the portfolio. If we're holding 500 of these loans, how many default in a bad scenario, and how bad does "bad" realistically get? That's what the Monte Carlo piece is for. It runs thousands of simulated scenarios and reports VaR95 and CVaR95 for the portfolio.

## How it's built

The main thing I wanted was for `ScoringService` — the piece that actually handles a scoring request — to not know or care what model, classifier, or explainer is being used underneath.

It only depends on three `Protocol` interfaces in `interfaces.py`:

* `ModelPredictor`
* `RiskClassifier`
* `ModelExplainer`

Right now those are backed by scikit-learn and SHAP. If I swapped the model for XGBoost tomorrow, `ScoringService` wouldn't need to change. Only the implementation of `ModelPredictor` would.

All the wiring — loading the model, building the SHAP explainer, putting everything together, and handing it to `ScoringService` — happens in one place: `factory_scoring_service.py`, once at FastAPI startup.

Nothing else in the codebase touches `joblib` or `shap` directly.

that's basically the line I wanted to draw between the ML  plumbing and the actual business logic.

And that same split makes the individual pieces easier to test.

`RiskClassifier` is pure logic — probability in, decision and label out — so I can test every threshold without loading a model or touching SHAP at all.

`ShapTreeExplainer` and `SklearnPredictor` can each be tested against a fake model instead of the real trained one.

And `ScoringService` itself can be tested with mock implementations of the three `Protocol`s, just to check that it calls things in the right order and wraps errors properly.

This prevents the creation of a god class. Each separate component is testable on its own, and the ScoringService can also be tested using fakes or mocks.
## The pieces

* **`SklearnPredictor`** — thin wrapper around a trained sklearn model. Its job is basically to expose `predecir_probabilidad` without leaking the model itself to the rest of the application.

* **`RiskClassifier`** — pure business rules. Takes a probability and returns a binary decision (default/no default) plus a risk bucket (BAJA/MEDIA/ALTA) based on configured thresholds. There is deliberately no ML logic here.

* **`ShapTreeExplainer`** — wraps a `shap.TreeExplainer` and returns the top-N features by absolute impact for a given prediction. N comes from configuration.

* **`ScoringService`** — the orchestrator. Runs preprocess → predict → classify → explain. It also catches errors coming from the ML libraries and wraps them in a `RuntimeError` with some context instead of letting a raw library exception leak upward.

* **`MontecarloService`** — separate from the single-request flow. Takes a batch of probabilities — a day's worth of scored loans in the real setup — and simulates defaults across scenarios to estimate VaR95 and CVaR95 for the portfolio.

## What happens on a request

1. The FastAPI layer parses the incoming JSON and hands `ScoringService.predecir` a plain dict.
2. `Preprocessor` cleans and transforms it into what the model expects.
3. `SklearnPredictor` returns a probability of default.
4. `RiskClassifier` turns that probability into a decision and risk label.
5. `ShapTreeExplainer` figures out which features contributed most to the prediction.
6. Everything gets packed into a `CreditRiskResponse`.

The Monte Carlo piece runs separately. It's meant to run once a day over everything scored that day, not once per request.

## Stack

Python, FastAPI, scikit-learn, SHAP, pandas/numpy, and joblib for model persistence.

## Where this fits in the bigger picture

Individual `/score` calls happen throughout the day, triggered by different users.

At the end of the day, a cron job grabs everything scored that day and runs `MontecarloService` over the batch of probabilities.

That portfolio report gets published to RabbitMQ, and a separate Java/Spring Boot service on the other end — responsible for users, auth, and PostgreSQL — picks it up and stores it against the risk analyst's account.

This service doesn't know anything about users, auth, or persistence. It just scores applications, generates explanations, runs the portfolio simulation, and publishes the results.

It scores, it explains, it simulates, and it hands the result off.
## Testing Strategy

Testing an ML serving engine can quickly turn into a headache if every test requires loading heavy `.joblib` files or running full SHAP calculations.

Since `ScoringService` relies on `Protocol` interfaces, I can isolate its dependencies and test the actual business logic, pipeline orchestration, and edge cases without touching the disk or loading a real model.

The test suite combines standard `pytest` unit tests, `unittest.mock`, and property-based testing with **Hypothesis**.

### What each test file covers

- **`test_factory_wiring.py`** — Tests `construir_scoring_service`. Since the factory is mainly responsible for wiring dependencies together, I mock `joblib.load` and `shap.TreeExplainer` and verify that each component receives exactly what it should, in the expected order. It also exposes a redundant `RiskConfig()` initialization that gets immediately overwritten by the configuration loaded through `joblib`.

- **`test_risk_classifier.py`** — `RiskClassifier` contains pure business rules, so this is where I focus on boundary conditions and invariants. I use `math.nextafter` to test exact threshold edges and Hypothesis to verify properties such as monotonicity of the default decision (`p₁ ≤ p₂ → decision(p₁) ≤ decision(p₂)`), robustness across unusual floating-point inputs, and the fact that `umbral_decision` remains independent from the risk buckets.

- **`test_scoring_service.py`** — Tests the orchestration layer. I verify that `predecir` executes `transform → predict → classify → explain` in the expected sequence, that the processed DataFrame is passed correctly between components, and that collaborator failures are exposed as a consistent `RuntimeError` while preserving the original exception through `__cause__`.

- **`test_shap_tree_explainer.py`** — Uses property-based testing to verify that `calcular_impacto` actually returns the top-N features according to absolute SHAP magnitude, including deterministic handling of ties. It also contains a characterization test for a real compatibility issue I found with SHAP: Python's `match/case` pattern `[_, positive_class]` matches lists and tuples, but not `numpy.ndarray`. Newer SHAP versions (≥ 0.45) can return a 3D `ndarray` for binary tree models, causing that branch to be skipped and eventually leading to a pandas-related failure. The test stays there as an early warning if SHAP changes its output format again.

- **`test_sklearn_predictor.py`** — Verifies that the positive-class probability is extracted through `predict_proba[:, 1]` and explicitly converted to a native Python `float`, avoiding serialization problems when the result comes from NumPy scalar types such as `np.float32` or `np.float64`.
## More docs

This README covers the service as a whole. For details on specific pieces:

* `app/processing/README.md` — the preprocessing pipeline
* `tooling_accesorio/debugger/README.md` — the debugger tooling

## Rough edges I know about

* Model/config paths are hardcoded in the factory for now (`BASE_DIR = Path("model")`). That needs to move to environment variables before this goes anywhere real.

* I went with frozen dataclasses wherever there isn't a real reason for the object to mutate after it's built — predictor, classifier, explainer, service. It keeps them easier to reason about and safe to reuse across requests.

* Classifier and explainer errors get caught and re-raised as a single `RuntimeError` in `ScoringService.predecir`. This means the API layer doesn't have to know about every exception that sklearn or SHAP might throw.

* Business rules (decision threshold, risk buckets) live entirely in `RiskClassifier`, separate from the model on purpose. The model gives you a number. Deciding what that number means for the business is a different job, and I wanted that logic to be testable on its own without dragging sklearn into it.

## How to run it
1. git clone https://github.com/nicolasnazos22/credit-portfolio-default-risk.git
2. cd credit-portfolio-default-risk/FastApiMicroservice
3. docker build -t credit-risk-api
4. docker run --rm -p 8000:8000 credit-risk-api
5. Open http://localhost:8000/docs to access the interactive Swagger UI and test the API endpoints
