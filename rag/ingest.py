"""
FAQ Ingestion Script
Loads FAQs from JSON, generates embeddings, and stores in Pinecone
"""

import json
import logging
from .embeddings import EmbeddingsGenerator
from .pinecone_client import PineconeClient

logger = logging.getLogger('chatbot')


class FAQIngestor:
    """
    Handles ingestion of FAQs into Pinecone vector database
    """
    
    def __init__(self):
        """Initialize embeddings generator and Pinecone client"""
        self.embeddings_gen = EmbeddingsGenerator()
        self.pinecone_client = PineconeClient()
        logger.info("FAQ Ingestor initialized")
    
    def load_faq_file(self, filepath):
        """
        Load FAQ data from JSON file
        
        Args:
            filepath (str): Path to FAQ JSON file
        
        Returns:
            dict: FAQ data with metadata and faqs list
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Loaded {len(data.get('faqs', []))} FAQs from {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading FAQ file: {str(e)}")
            raise
    
    def prepare_vectors(self, faqs):
        """
        Generate embeddings for FAQs and prepare for Pinecone
        
        Args:
            faqs (list): List of FAQ dictionaries
        
        Returns:
            list: List of tuples (id, vector, metadata)
        """
        try:
            vectors = []
            
            for faq in faqs:
                # Generate embedding
                embedding = self.embeddings_gen.embed_faq(faq)
                
                if embedding is None:
                    logger.warning(f"Skipping FAQ {faq['id']} - no embedding generated")
                    continue
                
                # Prepare metadata
                metadata = {
                    'id': faq['id'],
                    'question': faq['question'],
                    'answer': faq['answer'],
                    'category': faq.get('category', 'general'),
                    'keywords': ', '.join(faq.get('keywords', [])),
                }
                
                # Add related FAQs if present
                if 'related_faqs' in faq:
                    metadata['related_faqs'] = ', '.join(faq['related_faqs'])
                
                vectors.append((faq['id'], embedding, metadata))
            
            logger.info(f"✅ Prepared {len(vectors)} vectors for ingestion")
            return vectors
            
        except Exception as e:
            logger.error(f"Error preparing vectors: {str(e)}")
            raise
    
    def ingest_faqs(self, filepath, namespace='default', clear_first=False):
        """
        Complete ingestion pipeline: load FAQs, generate embeddings, store in Pinecone
        
        Args:
            filepath (str): Path to FAQ JSON file
            namespace (str): Pinecone namespace
            clear_first (bool): Whether to clear existing data first
        
        Returns:
            dict: Ingestion results
        """
        try:
            logger.info(f"Starting FAQ ingestion from {filepath}")
            
            # Load FAQ data
            faq_data = self.load_faq_file(filepath)
            faqs = faq_data.get('faqs', [])
            
            if not faqs:
                logger.warning("No FAQs found in file")
                return {'status': 'error', 'message': 'No FAQs found'}
            
            # Clear existing data if requested
            if clear_first:
                logger.info(f"Clearing existing data in namespace '{namespace}'")
                self.pinecone_client.delete_all(namespace=namespace)
            
            # Prepare vectors
            vectors = self.prepare_vectors(faqs)
            
            if not vectors:
                logger.error("No vectors prepared for ingestion")
                return {'status': 'error', 'message': 'No vectors prepared'}
            
            # Upsert to Pinecone
            logger.info(f"Upserting {len(vectors)} vectors to Pinecone...")
            result = self.pinecone_client.upsert_vectors(vectors, namespace=namespace)
            
            # Get stats
            stats = self.pinecone_client.get_stats()
            
            logger.info(f"✅ Ingestion complete! {result['upserted_count']} FAQs stored")
            
            return {
                'status': 'success',
                'faqs_loaded': len(faqs),
                'vectors_created': len(vectors),
                'vectors_upserted': result['upserted_count'],
                'index_stats': stats,
                'namespace': namespace
            }
            
        except Exception as e:
            logger.error(f"Error during FAQ ingestion: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def update_single_faq(self, faq, namespace='default'):
        """
        Update or add a single FAQ
        
        Args:
            faq (dict): FAQ dictionary
            namespace (str): Pinecone namespace
        
        Returns:
            bool: Success status
        """
        try:
            vectors = self.prepare_vectors([faq])
            
            if not vectors:
                return False
            
            self.pinecone_client.upsert_vectors(vectors, namespace=namespace)
            logger.info(f"✅ Updated FAQ: {faq['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating FAQ: {str(e)}")
            return False