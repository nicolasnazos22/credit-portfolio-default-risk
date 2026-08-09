## Data preprocessing pipeline
"preprocessor" and "validador" implement a data preprocessing pipeline for this credit risk scoring motor. It turns a crude DataFrame into numeric features ready for training or scoring the model.
They apply simple validation rules based on business rules, null imputations and one-hot encoding.
## Components:
### Validador
Validates a customer DataFrame against a set of configurable-by-attribute business rules defined in a dictionary (loaded from a YAML file).
**supported rules:**
1. "required": not null. If a required field is empty, the entire row is discarded.
2. min/max: lower and upper inclusive bound
3. mayor / menor: lower and upper exclusive bound
4. relation: comparision between two fields from same customer
It's important to notice that these rules are implemented via dispatch tables instead of using multiple if/else. This improves readability and allows adding more rules simply by adding an
extra rule to the dispatch table.
#### expected behaviour:
- Validation is only performed for required fields. If there's a not required field with a null value, this validator lets it go through (nulls get handled later by imputation, not here).
- If after validation there are no valid customers, then throws a ValueError.

Values for validation rules are to be provided in the following fashion:
```yaml
fields:
  person_age:
    required: true
    min: 18
    max: 100
    dtype: int

  person_emp_length:
    required: true
    min: 0
    max: 60
    dtype: float
    relation:
      type: menor_o_igual
      field: person_age
      offset: -16
```

### Preprocessor
Orchestrates the whole transformation pipeline: validation (optional) -> imputation -> encoding. It exposes two constructors depending on the context it's used in, so it's not possible to
instantiate it with an inconsistent config (e.g. running inference without a fixed feature list).

**constructors:**
1. `para_entrenamiento`: used for training the model. Needs a `validador`, features get inferred from the encoding step so they're not passed in.
2. `para_inferencia`: used for scoring in production. Needs a fixed `features` list (the exact columns the trained model expects), doesn't take a `validador`.

#### what `transformar()` does, step by step:
1. **validation** (only if there's a `validador`): drops invalid rows and rows missing required fields.
2. **imputation** (`_imputar`): fills numeric columns with pre-computed medians (`self.medianas`), categorical columns with `"desconocido"`.
3. **encoding** (`_encoding`): one-hot encodes everything, and during inference it reindexes against the fixed `features` list from the trained model — missing columns get filled with 0, unseen new columns get dropped. Everything gets cast to `float32` at the end.
4. **sanity check**: if any NaN survives all of that, it throws a `RuntimeError` instead of letting it silently reach the model.

#### expected behaviour:
- Since `para_entrenamiento` and `para_inferencia` are the only entry points, you can't end up with a `validador` but no fixed `features`, or vice versa.
- Reindexing against the fixed `features` in inference guarantees the model always gets the same columns in the same order, even if the batch being scored has categories the training set didn't.
- Fail-fast: same philosophy as `Validador`, better to blow up early than send garbage into the model.

Basic usage looks like this:
```python
# training
preprocessor = Preprocessor.para_entrenamiento(
    medianas=train_medians,
    config=processing_config,
    validador=validador,
)
X_train = preprocessor.transformar(train_customers_df)

# inference
preprocessor = Preprocessor.para_inferencia(
    features=model.feature_names_,
    medianas=train_medians,
    config=processing_config,
)
X_score = preprocessor.transformar(new_customers_df)
```

## Dependencies
- pandas, numpy
- app.core.config.ProcessingConfig

## Notes
- `config: ProcessingConfig` is received by `Preprocessor` but not actually used inside it — worth checking if that's dead code or a placeholder for something coming later.
- `Validador.validar` doesn't log how many rows get dropped, which would probably be useful to monitor data quality once this runs in production.
