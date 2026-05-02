import joblib
import pandas as pd
import os

def load_models():
    """
    Load all premium models and metadata.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(BASE_DIR, "models")
    
    rating_model = joblib.load(os.path.join(models_dir, "rating_model_pro.joblib"))
    collection_model = joblib.load(os.path.join(models_dir, "collection_model_pro.joblib"))
    success_model = joblib.load(os.path.join(models_dir, "success_model_pro.joblib"))
    metadata = joblib.load(os.path.join(models_dir, "metadata_pro.joblib"))
    
    return rating_model, collection_model, success_model, metadata

def predict_movie_metrics(genre, industry, budget, runtime, star_power, 
                         director_pop, social_buzz, critic_score, release_month):
    """
    Predict movie rating, collection, and success probability.
    """
    rating_model, collection_model, success_model, _ = load_models()
    
    # Prepare input
    input_data = pd.DataFrame({
        'genre': [genre],
        'industry': [industry],
        'budget': [budget],
        'runtime': [runtime],
        'star_power': [star_power],
        'director_popularity': [director_pop],
        'social_buzz': [social_buzz],
        'critic_score': [critic_score],
        'release_month': [release_month]
    })
    
    # Run predictions
    rating_pred = float(rating_model.predict(input_data)[0])
    collection_pred = float(collection_model.predict(input_data)[0])
    success_prob = float(success_model.predict_proba(input_data)[0][1]) if hasattr(success_model, 'predict_proba') else 0.0
    
    return {
        'rating': round(rating_pred, 1),
        'collection_usd': round(collection_pred, 2),
        'success_probability': round(success_prob * 100, 2)
    }

if __name__ == "__main__":
    # Test prediction
    try:
        _, _, _, metadata = load_models()
        result = predict_movie_metrics(
            genre=metadata['genres'][0],
            industry=metadata['industries'][0],
            budget=50.0,
            runtime=120,
            star_power=0.8,
            director_pop=0.7,
            social_buzz=0.9,
            critic_score=75,
            release_month=metadata['months'][0]
        )
        print(f"Test Prediction Results: {result}")
    except Exception as e:
        print(f"Error during test: {e}")
