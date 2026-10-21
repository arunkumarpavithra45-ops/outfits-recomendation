"""Generate dataset, train the models and print test accuracy."""
import outfit_ai as ai

if __name__ == "__main__":
    ai.train()
    print("Saved:", ai.MODEL_PATH)
