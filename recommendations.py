import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import logging

logger = logging.getLogger(__name__)

class TravelRecommender:
    def __init__(self):
        self.destinations = {
            'beach': {
                'keywords': ['beach', 'ocean', 'sun', 'sand', 'swimming', 'surfing'],
                'destinations': [
                    {'name': 'Bali, Indonesia', 'cost': 1500, 'description': 'Tropical paradise with beautiful beaches'},
                    {'name': 'Maldives', 'cost': 3000, 'description': 'Luxury overwater bungalows and crystal clear waters'},
                    {'name': 'Phuket, Thailand', 'cost': 1000, 'description': 'Vibrant nightlife and stunning beaches'}
                ]
            },
            'mountain': {
                'keywords': ['mountain', 'hiking', 'snow', 'skiing', 'adventure'],
                'destinations': [
                    {'name': 'Swiss Alps', 'cost': 2500, 'description': 'World-class skiing and mountain views'},
                    {'name': 'Nepal', 'cost': 2000, 'description': 'Trekking in the Himalayas'},
                    {'name': 'Rocky Mountains, Canada', 'cost': 1800, 'description': 'Scenic mountain ranges and outdoor activities'}
                ]
            },
            'city': {
                'keywords': ['city', 'culture', 'museums', 'shopping', 'nightlife'],
                'destinations': [
                    {'name': 'Paris, France', 'cost': 2200, 'description': 'Art, culture, and romance'},
                    {'name': 'Tokyo, Japan', 'cost': 2800, 'description': 'Modern technology meets traditional culture'},
                    {'name': 'New York, USA', 'cost': 2000, 'description': 'The city that never sleeps'}
                ]
            }
        }
        
        self.vectorizer = TfidfVectorizer()
        self._prepare_vectorizer()
    
    def _prepare_vectorizer(self):
        """Prepare the TF-IDF vectorizer with all keywords."""
        all_keywords = []
        for category in self.destinations.values():
            all_keywords.extend(category['keywords'])
        self.vectorizer.fit([' '.join(all_keywords)])
    
    def get_recommendations(self, preferences, budget):
        """
        Get travel recommendations based on user preferences and budget.
        
        Args:
            preferences (str): User's travel preferences
            budget (float): User's budget in USD
        
        Returns:
            list: List of recommended destinations
        """
        try:
            # Vectorize user preferences
            pref_vector = self.vectorizer.transform([preferences])
            
            # Calculate similarity scores for each category
            recommendations = []
            for category, data in self.destinations.items():
                category_vector = self.vectorizer.transform([' '.join(data['keywords'])])
                similarity = cosine_similarity(pref_vector, category_vector)[0][0]
                
                # Filter destinations by budget
                affordable_destinations = [
                    dest for dest in data['destinations']
                    if dest['cost'] <= budget
                ]
                
                if affordable_destinations:
                    recommendations.extend([
                        {
                            **dest,
                            'category': category,
                            'similarity_score': similarity
                        }
                        for dest in affordable_destinations
                    ])
            
            # Sort by similarity score and return top 3
            recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
            return recommendations[:3]
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []
    
    def get_destination_details(self, destination_name):
        """
        Get detailed information about a specific destination.
        
        Args:
            destination_name (str): Name of the destination
        
        Returns:
            dict: Destination details or None if not found
        """
        for category in self.destinations.values():
            for dest in category['destinations']:
                if dest['name'].lower() == destination_name.lower():
                    return dest
        return None 