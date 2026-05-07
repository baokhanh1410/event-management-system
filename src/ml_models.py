import pandas as pd
import xgboost as xgb
from src.crud import get_data_for_recommendation, get_all_events

# ============================================================
# ML DATA PREPROCESSING
# ============================================================

def compute_guest_profiles(df):
    """
    Compute guest profile metrics (historical avg_price, category frequencies) 
    from their registration history.
    """
    if df.empty or 'guest_id' not in df.columns:
        return pd.DataFrame()
        
    # 1. Compute historical avg_price per guest
    avg_price = df.groupby('guest_id')['base_price'].mean().reset_index()
    avg_price.rename(columns={'base_price': 'guest_avg_price'}, inplace=True)
    
    # 2. Compute category frequencies
    if 'categories' not in df.columns:
        return avg_price
        
    cats = df['categories'].str.get_dummies(sep=', ')
    cats['guest_id'] = df['guest_id']
    cat_freq = cats.groupby('guest_id').sum().reset_index()
    
    # Rename category columns to indicate they are guest profile features
    cat_freq.columns = [f'guest_freq_{c}' if c != 'guest_id' else c for c in cat_freq.columns]
    
    # Merge
    profile = pd.merge(avg_price, cat_freq, on='guest_id', how='left')
    return profile

def preprocess_features(df, guest_profiles=None):
    """
    Preprocessing step:
    1. Convert 'categories' string into One-Hot Encoding columns.
    2. Join guest profile metrics if provided.
    """
    if 'categories' in df.columns:
        # categories string looks like "Conference, Workshop", split using get_dummies
        cats = df['categories'].str.get_dummies(sep=', ')
        df_processed = pd.concat([df.drop(columns=['categories']), cats], axis=1)
    else:
        df_processed = df.copy()
        
    if guest_profiles is not None and not guest_profiles.empty and 'guest_id' in df_processed.columns:
        df_processed = pd.merge(df_processed, guest_profiles, on='guest_id', how='left')
        # Fill NaN for missing guests (cold start)
        df_processed.fillna(0, inplace=True)
        
    return df_processed

# ============================================================
# MODEL TRAINING
# ============================================================

def train_xgboost_recommender(session):
    """
    Train an XGBoost classifier.
    Returns the trained model and a list of feature columns used.
    """
    data = get_data_for_recommendation(session)
    
    # Needs both class 0 and 1 to train (someone checked-in and someone didn't)
    if data.empty or len(data['attendance_status'].unique()) < 2:
        return None, None
        
    # Compute guest profiles
    guest_profiles = compute_guest_profiles(data)
        
    # Preprocess categorical features and join guest profiles
    df_processed = preprocess_features(data, guest_profiles)
    
    # Define features: exclude IDs and target columns
    drop_cols = ['guest_id', 'event_id', 'attendance_status', 'status']
    features = [c for c in df_processed.columns if c not in drop_cols]
    
    # Ensure base_price is a float type
    if 'base_price' in features:
        df_processed['base_price'] = pd.to_numeric(df_processed['base_price'], errors='coerce').fillna(0.0)

    X = df_processed[features]
    y = df_processed['attendance_status']
    
    # Initialize and train XGBoost Classification Model
    model = xgb.XGBClassifier(
        n_estimators=50, 
        max_depth=3, 
        learning_rate=0.1, 
        random_state=42, 
        eval_metric='logloss'
    )
    model.fit(X, y)
    
    return model, features

# ============================================================
# EVENT RECOMMENDATION INFERENCE
# ============================================================

def get_recommended_events(session, guest_id, top_n=3):
    """
    Recommend Top N upcoming events for a specific Guest using the ML model.
    """
    model, features = train_xgboost_recommender(session)
    
    # Retrieve all existing events
    all_events = get_all_events(session)
    
    # Filter for only 'Upcoming' events
    upcoming = all_events[all_events['status'] == 'Upcoming'].copy()
    if upcoming.empty:
        return pd.DataFrame()
        
    # Retrieve the list of events the guest has already registered for (to exclude from recommendations)
    train_data = get_data_for_recommendation(session)
    registered_event_ids = []
    guest_profiles = pd.DataFrame()
    if not train_data.empty:
        guest_profiles = compute_guest_profiles(train_data)
        registered_event_ids = train_data[train_data['guest_id'] == guest_id]['event_id'].tolist()
        
    candidates = upcoming[~upcoming['event_id'].isin(registered_event_ids)].copy()
    if candidates.empty:
        return pd.DataFrame()
        
    # If there isn't enough training data, fallback by recommending random upcoming events
    if model is None:
        return candidates.head(top_n)
        
    # Preprocess candidate dataset to prepare for prediction
    # Candidates need a guest_id column so the merge works!
    candidates['guest_id'] = guest_id
    cand_processed = preprocess_features(candidates, guest_profiles)
    if 'base_price' in cand_processed.columns:
        cand_processed['base_price'] = pd.to_numeric(cand_processed['base_price'], errors='coerce').fillna(0.0)
    
    # Column alignment: Ensure candidates have all features present during training
    for f in features:
        if f not in cand_processed.columns:
            cand_processed[f] = 0
            
    # Extract X mapping exactly the training feature order
    X_pred = cand_processed[features]
    
    # Predict the probability of attendance (attendance_status = 1)
    probs = model.predict_proba(X_pred)[:, 1]
    
    candidates['recommend_score'] = probs
    
    # Sort by probability score descending and take the top_n results
    recommended = candidates.sort_values(by='recommend_score', ascending=False).head(top_n)
    
    return recommended
