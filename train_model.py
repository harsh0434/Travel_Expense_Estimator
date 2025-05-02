from predict import TravelCostPredictor

def main():
    print("Training travel cost prediction model...")
    predictor = TravelCostPredictor()
    predictor.train()
    print("Model training completed successfully!")

if __name__ == "__main__":
    main() 