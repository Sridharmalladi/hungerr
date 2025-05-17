import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from datetime import datetime, timedelta
import streamlit as st
from dotenv import load_dotenv

# Load environment variables (for local development)
load_dotenv()

def initialize_firebase():
    """Initialize Firebase if not already initialized"""
    try:
        print("\n=== Firebase Initialization ===")
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            print("Firebase not initialized, starting initialization...")
            # Try to get Firebase credentials from Streamlit secrets first
            if 'firebase' in st.secrets:
                print("Found Firebase credentials in Streamlit secrets")
                # Convert the secrets to a dictionary
                firebase_config = dict(st.secrets['firebase'])
                # Ensure private_key is properly formatted
                if isinstance(firebase_config['private_key'], str):
                    firebase_config['private_key'] = firebase_config['private_key'].replace('\\n', '\n')
                print("Successfully processed Firebase credentials")
            else:
                print("No Firebase credentials in Streamlit secrets, checking environment variables")
                # Fallback to environment variables for local development
                firebase_config = {
                    "type": os.getenv("FIREBASE_TYPE"),
                    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
                    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
                    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
                    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
                }
            
            # Create a temporary JSON file with the credentials
            cred_path = "firebase-credentials.json"
            print(f"Creating temporary credentials file: {cred_path}")
            with open(cred_path, 'w') as f:
                json.dump(firebase_config, f)
            
            # Initialize Firebase with the credentials file
            print("Initializing Firebase with credentials...")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            
            # Clean up the temporary file
            print("Cleaning up temporary credentials file")
            os.remove(cred_path)
            print("Firebase initialization successful!")
            return True
        print("Firebase already initialized")
        return True
    except Exception as e:
        print(f"Firebase initialization error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        st.error(f"Firebase initialization error: {str(e)}")
        return False

def verify_user(id_file):
    """Verify user with uploaded ID"""
    try:
        st.session_state.verified = True
        return True
    except Exception as e:
        st.error(f"Verification error: {str(e)}")
        return False

def save_food_post(post_data):
    """Save food post data to Firebase"""
    try:
        print(f"Attempting to save food post: {post_data}")
        db = firestore.client()
        # Add timestamp if not present
        if 'timestamp' not in post_data:
            post_data['timestamp'] = datetime.now().isoformat()
        
        # Add to Firestore
        doc_ref = db.collection('food_posts').add(post_data)
        print(f"Successfully saved food post with ID: {doc_ref[1].id}")
        return True
    except Exception as e:
        print(f"Error saving post: {str(e)}")
        st.error(f"Error saving post: {str(e)}")
        return False

def get_all_food_posts():
    """Get all food posts from Firebase"""
    try:
        print("\n=== Fetching Food Posts ===")
        print("Attempting to fetch all food posts")
        db = firestore.client()
        posts = db.collection('food_posts').stream()
        post_list = [post.to_dict() for post in posts]
        print(f"Successfully fetched {len(post_list)} food posts")
        if len(post_list) > 0:
            print("Sample post data:", post_list[0])
        return post_list
    except Exception as e:
        print(f"Error fetching posts: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        st.error(f"Error fetching posts: {str(e)}")
        return []

def delete_expired_posts():
    """Delete posts that are past their expiry time"""
    try:
        db = firestore.client()
        current_time = datetime.now()
        
        # Get all posts
        posts = db.collection('food_posts').stream()
        
        for post in posts:
            post_data = post.to_dict()
            if 'timestamp' in post_data and 'expiry_hours' in post_data:
                post_time = datetime.fromisoformat(post_data['timestamp'])
                expiry_time = post_time + timedelta(hours=post_data['expiry_hours'])
                
                if current_time > expiry_time:
                    # Delete expired post
                    db.collection('food_posts').document(post.id).delete()
    except Exception as e:
        st.error(f"Error deleting expired posts: {str(e)}")