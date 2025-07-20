# test_pickle_issue.py
import pickle

# Test 1: Pickle a simple dict (this should work)
simple_data = {"model": "test", "version": 1.0}
with open("test_simple.pkl", "wb") as f:
    pickle.dump(simple_data, f)
print("✅ Created test_simple.pkl")

# Test 2: Pickle a custom class (this will fail in container)
class CustomPredictor:
    def predict(self): return "test"

custom_obj = CustomPredictor()
with open("test_custom.pkl", "wb") as f:
    pickle.dump(custom_obj, f)
print("✅ Created test_custom.pkl")

# Test 3: What you should do instead
config_only = {
    "model_type": "cv_evaluator",
    "model_path": "model_files/model_a_prose_evaluator"
}
with open("test_config.pkl", "wb") as f:
    pickle.dump(config_only, f)
print("✅ Created test_config.pkl")
