
import joblib
import json

def predict(instances, **kwargs):
    model = joblib.load("model.joblib")
    predictions = model.predict(instances)
    return predictions
