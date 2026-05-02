import pandas as pd
import xgboost as xgb
from src.crud import get_data_for_recommendation, get_all_events

def preprocess_features(df):
    """
    Tiền xử lý:
    1. Chuyển đổi chuỗi 'categories' thành các cột One-Hot Encoding.
    """
    if 'categories' in df.columns:
        # categories có dạng "Conference, Workshop", dùng get_dummies tách ra
        cats = df['categories'].str.get_dummies(sep=', ')
        df_processed = pd.concat([df.drop(columns=['categories']), cats], axis=1)
    else:
        df_processed = df.copy()
        
    return df_processed

def train_xgboost_recommender(session):
    """
    Huấn luyện mô hình XGBoost.
    Trả về model và danh sách cột feature.
    """
    data = get_data_for_recommendation(session)
    
    # Cần có cả lớp 0 và 1 để huấn luyện (ai đó đã check-in và ai đó chưa/không)
    if data.empty or len(data['attendance_status'].unique()) < 2:
        return None, None
        
    # Tiền xử lý
    df_processed = preprocess_features(data)
    
    # Định nghĩa features: bỏ các cột ID và Target
    drop_cols = ['guest_id', 'event_id', 'attendance_status', 'status']
    features = [c for c in df_processed.columns if c not in drop_cols]
    
    # Ép kiểu base_price về số thực (nếu cần)
    if 'base_price' in features:
        df_processed['base_price'] = pd.to_numeric(df_processed['base_price'], errors='coerce').fillna(0.0)

    X = df_processed[features]
    y = df_processed['attendance_status']
    
    # Khởi tạo và huấn luyện mô hình XGBoost Classification
    model = xgb.XGBClassifier(
        n_estimators=50, 
        max_depth=3, 
        learning_rate=0.1, 
        random_state=42, 
        eval_metric='logloss'
    )
    model.fit(X, y)
    
    return model, features

def get_recommended_events(session, guest_id, top_n=3):
    """
    Gợi ý Top N sự kiện cho Guest.
    """
    model, features = train_xgboost_recommender(session)
    
    # Lấy toàn bộ sự kiện hiện có
    all_events = get_all_events(session)
    
    # Chỉ chọn các sự kiện Upcoming
    upcoming = all_events[all_events['status'] == 'Upcoming'].copy()
    if upcoming.empty:
        return pd.DataFrame()
        
    # Lấy danh sách sự kiện mà khách đã đăng ký (để loại bỏ khỏi gợi ý)
    train_data = get_data_for_recommendation(session)
    registered_event_ids = []
    if not train_data.empty:
        registered_event_ids = train_data[train_data['guest_id'] == guest_id]['event_id'].tolist()
        
    candidates = upcoming[~upcoming['event_id'].isin(registered_event_ids)].copy()
    if candidates.empty:
        return pd.DataFrame()
        
    # Nếu không đủ data train, fallback bằng cách gợi ý đại sự kiện Upcoming ngẫu nhiên hoặc giá trị mặc định
    if model is None:
        return candidates.head(top_n)
        
    # Tiền xử lý tập candidate để chuẩn bị predict
    cand_processed = preprocess_features(candidates)
    if 'base_price' in cand_processed.columns:
        cand_processed['base_price'] = pd.to_numeric(cand_processed['base_price'], errors='coerce').fillna(0.0)
    
    # Khớp (align) columns: Ensure candidates có đủ tất cả feature lúc train
    for f in features:
        if f not in cand_processed.columns:
            cand_processed[f] = 0
            
    # Lấy X theo đúng thứ tự features của tập train
    X_pred = cand_processed[features]
    
    # Predict xác suất tham dự (attendance_status = 1)
    probs = model.predict_proba(X_pred)[:, 1]
    
    candidates['recommend_score'] = probs
    
    # Sort theo điểm từ cao đến thấp và lấy top_n
    recommended = candidates.sort_values(by='recommend_score', ascending=False).head(top_n)
    
    return recommended
