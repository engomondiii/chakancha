"""
Pinecone Client for Vector Database
Handles connection, index creation, and vector operations
"""

import os
from pinecone import Pinecone, ServerlessSpec
import logging

logger = logging.getLogger('chatbot')


class PineconeClient:
    """
    Wrapper class for Pinecone vector database operations
    """
    
    def __init__(self):
        """Initialize Pinecone client with API key from settings"""
        from django.conf import settings
        
        self.api_key = settings.PINECONE_API_KEY
        self.environment = settings.PINECONE_ENVIRONMENT
        self.index_name = settings.PINECONE_INDEX_NAME
        
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY not found in settings")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        self.index = None
        
        logger.info(f"Pinecone client initialized for environment: {self.environment}")
    
    def create_index(self, dimension=1536, metric='cosine'):
        """
        Create a new Pinecone index if it doesn't exist
        
        Args:
            dimension (int): Vector dimension (1536 for OpenAI text-embedding-3-small)
            metric (str): Distance metric (cosine, euclidean, dotproduct)
        
        Returns:
            bool: True if index was created or already exists
        """
        try:
            # Check if index already exists
            existing_indexes = self.pc.list_indexes()
            index_names = [index.name for index in existing_indexes]
            
            if self.index_name in index_names:
                logger.info(f"Index '{self.index_name}' already exists")
                return True
            
            # Create index with serverless spec
            logger.info(f"Creating index '{self.index_name}' with dimension {dimension}")
            
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud='aws',
                    region=self.environment
                )
            )
            
            logger.info(f"✅ Index '{self.index_name}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating Pinecone index: {str(e)}")
            raise
    
    def get_index(self):
        """
        Get connection to Pinecone index
        
        Returns:
            Index: Pinecone index object
        """
        if self.index is None:
            try:
                self.index = self.pc.Index(self.index_name)
                logger.info(f"Connected to index: {self.index_name}")
            except Exception as e:
                logger.error(f"Error connecting to index: {str(e)}")
                raise
        
        return self.index
    
    def upsert_vectors(self, vectors, namespace=''):
        """
        Insert or update vectors in the index
        
        Args:
            vectors (list): List of tuples (id, vector, metadata)
            namespace (str): Optional namespace for data organization
        
        Returns:
            dict: Upsert response from Pinecone
        """
        try:
            index = self.get_index()
            
            # Format vectors for Pinecone
            formatted_vectors = [
                {
                    'id': vec_id,
                    'values': values,
                    'metadata': metadata
                }
                for vec_id, values, metadata in vectors
            ]
            
            # Upsert in batches of 100
            batch_size = 100
            for i in range(0, len(formatted_vectors), batch_size):
                batch = formatted_vectors[i:i + batch_size]
                response = index.upsert(
                    vectors=batch,
                    namespace=namespace
                )
                logger.info(f"Upserted batch {i//batch_size + 1}: {response['upserted_count']} vectors")
            
            logger.info(f"✅ Total vectors upserted: {len(formatted_vectors)}")
            return {'upserted_count': len(formatted_vectors)}
            
        except Exception as e:
            logger.error(f"Error upserting vectors: {str(e)}")
            raise
    
    def query_vectors(self, query_vector, top_k=5, namespace='', filter_dict=None):
        """
        Query the index for similar vectors
        
        Args:
            query_vector (list): Query embedding vector
            top_k (int): Number of results to return
            namespace (str): Namespace to query
            filter_dict (dict): Metadata filters
        
        Returns:
            list: Query results with scores and metadata
        """
        try:
            index = self.get_index()
            
            results = index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                include_metadata=True,
                filter=filter_dict
            )
            
            logger.info(f"Query returned {len(results['matches'])} results")
            return results['matches']
            
        except Exception as e:
            logger.error(f"Error querying vectors: {str(e)}")
            raise
    
    def delete_all(self, namespace=''):
        """
        Delete all vectors in a namespace
        
        Args:
            namespace (str): Namespace to clear
        """
        try:
            index = self.get_index()
            index.delete(delete_all=True, namespace=namespace)
            logger.info(f"✅ Deleted all vectors in namespace '{namespace}'")
        except Exception as e:
            logger.error(f"Error deleting vectors: {str(e)}")
            raise
    
    def get_stats(self):
        """
        Get index statistics
        
        Returns:
            dict: Index statistics
        """
        try:
            index = self.get_index()
            stats = index.describe_index_stats()
            logger.info(f"Index stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            raise
    
    def delete_index(self):
        """
        Delete the entire index (use with caution!)
        """
        try:
            self.pc.delete_index(self.index_name)
            logger.warning(f"⚠️ Index '{self.index_name}' deleted")
        except Exception as e:
            logger.error(f"Error deleting index: {str(e)}")
            raise