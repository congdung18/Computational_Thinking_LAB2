from fastapi import HTTPException
from firebase_admin import firestore


def sync_user_profile(db, user_info: dict):
    if not db:
        return {"status": "Firestore not initialized"}

    user_id = user_info.get("uid")
    email = user_info.get("email")

    try:
        user_ref = db.collection("users").document(user_id)
        doc = user_ref.get()

        if not doc.exists:
            user_ref.set({"email": email, "created_at": firestore.SERVER_TIMESTAMP})
            return {"status": "New user created"}

        return {"status": "User synced"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def get_user_history(db, user_info: dict, limit: int = 10):
    if not db:
        return []

    user_id = user_info.get("uid")

    try:
        docs = (
            db.collection("users")
            .document(user_id)
            .collection("history")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )

        history = []
        for doc in docs:
            data = doc.to_dict()
            if "timestamp" in data and data["timestamp"]:
                data["timestamp"] = data["timestamp"].isoformat()
            history.append(data)

        return history
    except Exception as exc:
        print(f"Error fetching history: {exc}")
        return []


def save_user_history(
    db,
    user_info: dict,
    weather: str,
    preferences: str,
    suggestion: str,
):
    if not db:
        return

    user_id = user_info.get("uid")
    history_ref = db.collection("users").document(user_id).collection("history")
    history_ref.add(
        {
            "weather": weather,
            "preferences": preferences,
            "suggestion": suggestion,
            "timestamp": firestore.SERVER_TIMESTAMP,
        }
    )
