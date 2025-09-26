# physiboss-models

![PhysiBoSS logo](https://avatars.githubusercontent.com/u/179001945?s=400&u=02c8638da9de9d9cd68820187adbfcb45c9d8007&v=4)

This python library provides and API to the [PhysiBoSS-Models Database](https://github.com/PhysiBoSS-Models). You can list models, look at their metadata, and download them. 

## Install

```
pip install physiboss-models
```

## Usage

To start, you need to create the Database object:

```
import physiboss_models as pm
db = pm.DataBase()
```

### List models
```
models = db.all()
```

### Search models
```
models = db.search("invasion")
```

### List versions of a model
```
versions = db.versions(model)
```

### Download model
```
db.download_model(model, path, version)
```

This will download a model (pre-compiled binary, config files) into the informed path. You can inform a version, if you don't it will dowload the latest one.

Once loaded, you can access the model metadata with 
```
metadata = db.current_model_info()
```