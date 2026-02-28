"""
OpenAI Embeddings Generator
Creates vector embeddings from text using OpenAI API
"""

import openai
from django.conf import settings
import logging

logger = logging.getLogger('chatbot')


class EmbeddingsGenerator:
    """
    Generate embeddings using OpenAI's embedding models
    """
    
    def __init__(self):
        """Initialize OpenAI client with API key"""
        self.api_key = settings.OPENAI_API_KEY
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in settings")
        
        # Set API key
        openai.api_key = self.api_key
        
        # Model configuration
        self.model = "text-embedding-3-small"  # 1536 dimensions, cost-effective
        self.dimension = 1536
        
        logger.info(f"Embeddings generator initialized with model: {self.model}")
    
    def generate_embedding(self, text):
        """
        Generate embedding for a single text
        
        Args:
            text (str): Text to embed
        
        Returns:
            list: Embedding vector (1536 dimensions)
        """
        try:
            # Clean text
            text = text.replace("\n", " ").strip()
            
            if not text:
                logger.warning("Empty text provided for embedding")
                return None
            
            # Generate embedding
            response = openai.embeddings.create(
                model=self.model,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            logger.debug(f"Generated embedding for text: '{text[:50]}...'")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def generate_embeddings_batch(self, texts, batch_size=100):
        """
        Generate embeddings for multiple texts in batches
        
        Args:
            texts (list): List of texts to embed
            batch_size (int): Number of texts per API call
        
        Returns:
            list: List of embedding vectors
        """
        try:
            all_embeddings = []
            
            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Clean texts
                cleaned_batch = [text.replace("\n", " ").strip() for text in batch]
                
                # Generate embeddings
                response = openai.embeddings.create(
                    model=self.model,
                    input=cleaned_batch
                )
                
                # Extract embeddings
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.info(f"Generated embeddings for batch {i//batch_size + 1} ({len(batch)} texts)")
            
            logger.info(f"✅ Generated {len(all_embeddings)} embeddings total")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    def embed_faq(self, faq_item):
        """
        Generate embedding for FAQ item (question + answer)
        
        Args:
            faq_item (dict): FAQ dictionary with 'question' and 'answer'
        
        Returns:
            list: Embedding vector
        """
        try:
            # Combine question and answer for better context
            text = f"Question: {faq_item['question']} Answer: {faq_item['answer']}"
            
            # Add keywords if available
            if 'keywords' in faq_item and faq_item['keywords']:
                keywords_text = ", ".join(faq_item['keywords'])
                text += f" Keywords: {keywords_text}"
            
            return self.generate_embedding(text)
            
        except Exception as e:
            logger.error(f"Error embedding FAQ: {str(e)}")
            raise
    
    def get_model_info(self):
        """
        Get information about the embedding model
        
        Returns:
            dict: Model information
        """
        return {
            'model': self.model,
            'dimension': self.dimension,
            'max_tokens': 8191,
            'cost_per_1k_tokens': 0.00002  # As of 2024
        }