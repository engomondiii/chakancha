"""
FAQ Retriever
Performs semantic search to find relevant FAQs
"""

import logging
from .embeddings import EmbeddingsGenerator
from .pinecone_client import PineconeClient

logger = logging.getLogger('chatbot')


class FAQRetriever:
    """
    Retrieves relevant FAQs based on user questions using semantic search
    """
    
    def __init__(self):
        """Initialize embeddings generator and Pinecone client"""
        self.embeddings_gen = EmbeddingsGenerator()
        self.pinecone_client = PineconeClient()
        logger.info("FAQ Retriever initialized")
    
    def retrieve(self, query, top_k=3, min_score=0.7, namespace='default', category=None):
        """
        Retrieve relevant FAQs for a user query
        
        Args:
            query (str): User's question
            top_k (int): Number of results to return
            min_score (float): Minimum similarity score (0-1)
            namespace (str): Pinecone namespace to search
            category (str): Optional category filter
        
        Returns:
            list: List of relevant FAQs with scores
        """
        try:
            # Generate embedding for query
            query_embedding = self.embeddings_gen.generate_embedding(query)
            
            if query_embedding is None:
                logger.warning("Could not generate embedding for query")
                return []
            
            # Prepare filter if category is specified
            filter_dict = None
            if category:
                filter_dict = {'category': category}
            
            # Query Pinecone
            results = self.pinecone_client.query_vectors(
                query_vector=query_embedding,
                top_k=top_k * 2,  # Get more results to filter by score
                namespace=namespace,
                filter_dict=filter_dict
            )
            
            # Filter by minimum score and format results
            relevant_faqs = []
            
            for match in results:
                score = match['score']
                
                if score >= min_score:
                    metadata = match['metadata']
                    
                    faq = {
                        'id': metadata['id'],
                        'question': metadata['question'],
                        'answer': metadata['answer'],
                        'category': metadata.get('category', 'general'),
                        'score': float(score),
                        'keywords': metadata.get('keywords', '').split(', ') if metadata.get('keywords') else []
                    }
                    
                    # Add related FAQs if present
                    if 'related_faqs' in metadata:
                        faq['related_faqs'] = metadata['related_faqs'].split(', ')
                    
                    relevant_faqs.append(faq)
            
            # Limit to top_k
            relevant_faqs = relevant_faqs[:top_k]
            
            logger.info(f"Retrieved {len(relevant_faqs)} relevant FAQs for query: '{query[:50]}...'")
            
            return relevant_faqs
            
        except Exception as e:
            logger.error(f"Error retrieving FAQs: {str(e)}")
            return []
    
    def get_by_id(self, faq_id, namespace='default'):
        """
        Get a specific FAQ by ID
        
        Args:
            faq_id (str): FAQ ID
            namespace (str): Pinecone namespace
        
        Returns:
            dict: FAQ data or None
        """
        try:
            index = self.pinecone_client.get_index()
            result = index.fetch(ids=[faq_id], namespace=namespace)
            
            if faq_id in result['vectors']:
                metadata = result['vectors'][faq_id]['metadata']
                return {
                    'id': metadata['id'],
                    'question': metadata['question'],
                    'answer': metadata['answer'],
                    'category': metadata.get('category', 'general')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching FAQ by ID: {str(e)}")
            return None
    
    def get_by_category(self, category, top_k=10, namespace='default'):
        """
        Get FAQs from a specific category
        
        Args:
            category (str): Category name
            top_k (int): Maximum number of FAQs to return
            namespace (str): Pinecone namespace
        
        Returns:
            list: List of FAQs from the category
        """
        try:
            # Use a generic query embedding
            generic_query = f"Tell me about {category}"
            query_embedding = self.embeddings_gen.generate_embedding(generic_query)
            
            # Query with category filter
            results = self.pinecone_client.query_vectors(
                query_vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                filter_dict={'category': category}
            )
            
            faqs = []
            for match in results:
                metadata = match['metadata']
                faqs.append({
                    'id': metadata['id'],
                    'question': metadata['question'],
                    'answer': metadata['answer'],
                    'category': metadata['category'],
                    'score': float(match['score'])
                })
            
            logger.info(f"Retrieved {len(faqs)} FAQs from category '{category}'")
            return faqs
            
        except Exception as e:
            logger.error(f"Error retrieving FAQs by category: {str(e)}")
            return []
    
    def search_keywords(self, keywords, top_k=5, namespace='default'):
        """
        Search FAQs by keywords
        
        Args:
            keywords (list): List of keywords
            top_k (int): Number of results
            namespace (str): Pinecone namespace
        
        Returns:
            list: Relevant FAQs
        """
        try:
            # Create query from keywords
            query = " ".join(keywords)
            return self.retrieve(query, top_k=top_k, namespace=namespace)
            
        except Exception as e:
            logger.error(f"Error searching by keywords: {str(e)}")
            return []
    
    def get_related_faqs(self, faq_id, top_k=3, namespace='default'):
        """
        Get related FAQs for a given FAQ
        
        Args:
            faq_id (str): FAQ ID
            top_k (int): Number of related FAQs to return
            namespace (str): Pinecone namespace
        
        Returns:
            list: Related FAQs
        """
        try:
            # Get the original FAQ
            faq = self.get_by_id(faq_id, namespace=namespace)
            
            if not faq:
                return []
            
            # Use the question as query to find similar FAQs
            related = self.retrieve(
                query=faq['question'],
                top_k=top_k + 1,  # +1 because original FAQ will be in results
                namespace=namespace
            )
            
            # Remove the original FAQ from results
            related = [f for f in related if f['id'] != faq_id][:top_k]
            
            logger.info(f"Found {len(related)} related FAQs for {faq_id}")
            return related
            
        except Exception as e:
            logger.error(f"Error getting related FAQs: {str(e)}")
            return []