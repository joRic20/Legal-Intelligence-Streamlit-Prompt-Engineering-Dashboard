import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from openai import AzureOpenAI
from collections import defaultdict
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from typing import Dict, List, Optional, Any
import re

# Import settings
try:
    from settings import (
        AZURE_API_KEY,
        AZURE_OPENAI_ENDPOINT,
        AZURE_OPENAI_API_VERSION,
        CONTAINER_NAME,
        PARQUET_FILE_PATH
    )
except ImportError:
    st.error("Unable to import settings.py. Please ensure settings.py is in the same directory as app.py")
    st.stop()

# Grant Thornton Brand Colors and Styling
GT_COLORS = {
    'primary_purple': '#663399',
    'secondary_purple': '#8B4FA0',
    'accent_orange': '#FF6900',
    'light_orange': '#FFB366',
    'dark_gray': '#2C3E50',
    'medium_gray': '#5D6D7E',
    'light_gray': '#F8F9FA',
    'white': '#FFFFFF',
    'success_green': '#27AE60',
    'warning_yellow': '#F39C12',
    'error_red': '#E74C3C',
    'info_blue': '#3498DB'
}

# Page configuration with Grant Thornton branding
st.set_page_config(
    page_title="Grant Thornton Legal Intelligence Platform",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Grant Thornton Professional CSS Styling
st.markdown(f"""
<style>
    /* Grant Thornton Brand Styling */
    .main-header {{
        background: linear-gradient(135deg, {GT_COLORS['primary_purple']} 0%, {GT_COLORS['secondary_purple']} 100%);
        color: {GT_COLORS['white']};
        padding: 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(102, 51, 153, 0.2);
    }}
    
    .gt-logo {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {GT_COLORS['white']};
        margin-bottom: 0.5rem;
    }}
    
    .gt-subtitle {{
        font-size: 1.2rem;
        color: {GT_COLORS['light_orange']};
        font-weight: 400;
    }}
    
    .ai-powered-badge {{
        background: {GT_COLORS['accent_orange']};
        color: {GT_COLORS['white']};
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 1rem;
        box-shadow: 0 2px 4px rgba(255, 105, 0, 0.3);
    }}
    
    .document-card {{
        background: {GT_COLORS['white']};
        border: 1px solid #E5E7EB;
        border-left: 4px solid {GT_COLORS['primary_purple']};
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    
    .document-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 51, 153, 0.15);
    }}
    
    .confidence-indicator {{
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }}
    
    .confidence-high {{
        background: {GT_COLORS['success_green']};
        color: {GT_COLORS['white']};
    }}
    
    .confidence-medium {{
        background: {GT_COLORS['warning_yellow']};
        color: {GT_COLORS['white']};
    }}
    
    .confidence-low {{
        background: {GT_COLORS['error_red']};
        color: {GT_COLORS['white']};
    }}
    
    .legal-domain-tag {{
        background: {GT_COLORS['secondary_purple']};
        color: {GT_COLORS['white']};
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.2rem;
        display: inline-block;
    }}
    
    .sidebar .sidebar-content {{
        background: {GT_COLORS['light_gray']};
    }}
    
    .gt-filter-section {{
        background: {GT_COLORS['white']};
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 24px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: {GT_COLORS['light_gray']};
        border-radius: 8px 8px 0 0;
        color: {GT_COLORS['dark_gray']};
        font-weight: 600;
        padding: 0.75rem 1.5rem;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {GT_COLORS['primary_purple']};
        color: {GT_COLORS['white']};
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'ai_analysis_cache' not in st.session_state:
    st.session_state.ai_analysis_cache = {}
if 'document_embeddings' not in st.session_state:
    st.session_state.document_embeddings = {}
if 'search_results' not in st.session_state:
    st.session_state.search_results = {}

# Advanced AI Prompting System for Legal Document Analysis

class SearchRelevancePrompts:
    """Prompts for document search and relevance assessment"""
    
    @staticmethod
    def get_semantic_match_prompt():
        return """Identify if this document contains concepts semantically related to: "{search_query}"

DOCUMENT EXCERPT:
{document_text}

Return JSON:
{{
    "contains_related_concepts": true/false,
    "semantic_similarity_score": 0.0 to 1.0,
    "matched_concepts": ["list of matched concepts"]
}}"""

    @staticmethod
    def get_relevance_scoring_prompt():
        return """Score the relevance of this document to the query: "{search_query}"

CONCEPTS FOUND: {matched_concepts}

Return JSON:
{{
    "relevance_score": 0.0 to 1.0,
    "relevance_category": "Direct Match|Related|Tangential|Not Relevant"
}}"""

    @staticmethod
    def get_excerpt_extraction_prompt():
        return """Extract relevant quotes about "{search_query}" from this text:

TEXT: {document_text}

Return JSON:
{{
    "relevant_excerpts": ["up to 3 quotes, max 50 words each"],
    "excerpt_relevance_scores": [0.0 to 1.0 for each]
}}"""

class RegulatoryTrackingPrompts:
    """Prompts for regulatory evolution tracking"""
    
    @staticmethod
    def get_regulation_detection_prompt():
        return """Detect if this document mentions or relates to: "{regulation_topic}"

TEXT: {document_text}

Return JSON:
{{
    "mentions_regulation": true/false,
    "mention_type": "Explicit|Implicit|Related Area|None",
    "confidence": 0.0 to 1.0
}}"""

    @staticmethod
    def get_relationship_classification_prompt():
        return """Classify how this document relates to "{regulation_topic}":

DOCUMENT CONTEXT: {mention_context}

Return JSON:
{{
    "relationship_type": "Direct mention|Implementation|Amendment|Related topic|Reference|None",
    "relationship_strength": 0.0 to 1.0
}}"""

    @staticmethod
    def get_temporal_extraction_prompt():
        return """Extract temporal information related to "{regulation_topic}":

TEXT: {document_text}

Return JSON:
{{
    "dates_mentioned": ["YYYY-MM-DD format if found"],
    "deadlines": ["deadline descriptions"],
    "time_references": ["any temporal language"]
}}"""

    @staticmethod
    def get_evolution_indicators_prompt():
        return """Identify how this document shows evolution of "{regulation_topic}":

TEXT: {document_text}

Return JSON:
{{
    "evolution_type": "New Introduction|Amendment|Clarification|Extension|None",
    "evolution_indicators": ["specific indicators found"],
    "importance": "High|Medium|Low"
}}"""

class DocumentSummaryPrompts:
    """Prompts for document summarization"""
    
    @staticmethod
    def get_document_type_prompt():
        return """Identify the type of this legal document:

TEXT (first 500 chars): {document_text}

Return JSON:
{{
    "document_type": "Regulation|Directive|Decision|Communication|Recommendation|Opinion|Other",
    "type_confidence": 0.0 to 1.0
}}"""

    @staticmethod
    def get_main_purpose_prompt():
        return """Extract the main purpose of this document in one sentence:

TEXT: {document_text}

Return JSON:
{{
    "main_purpose": "One sentence, max 25 words",
    "purpose_clarity": 0.0 to 1.0
}}"""

    @staticmethod
    def get_key_points_prompt():
        return """Extract 3 key points from this document:

TEXT: {document_text}

Return JSON:
{{
    "key_points": [
        {{"point": "max 15 words", "importance": 0.0 to 1.0}},
        {{"point": "max 15 words", "importance": 0.0 to 1.0}},
        {{"point": "max 15 words", "importance": 0.0 to 1.0}}
    ]
}}"""

class DocumentStructurePrompts:
    """Prompts for document structure analysis"""
    
    @staticmethod
    def get_section_detection_prompt():
        return """Identify structural sections in this document:

TEXT: {document_text}

Return JSON:
{{
    "sections_found": [
        {{"type": "Article|Chapter|Section|Annex", "identifier": "number/name"}}
    ],
    "has_structured_format": true/false
}}"""

    @staticmethod
    def get_article_extraction_prompt():
        return """Extract article information if present:

TEXT: {document_text}

Return JSON:
{{
    "articles": [
        {{"number": "Article X", "title": "if present", "preview": "first 30 words"}}
    ],
    "total_articles": 0
}}"""

class ComplianceAnalysisPrompts:
    """Prompts for compliance impact assessment"""
    
    @staticmethod
    def get_sector_relevance_prompt():
        return """Is this document relevant to the {sector} sector?

TEXT: {document_text}

Return JSON:
{{
    "is_relevant": true/false,
    "relevance_indicators": ["specific indicators"],
    "relevance_score": 0.0 to 1.0
}}"""

    @staticmethod
    def get_compliance_requirements_prompt():
        return """Extract compliance requirements for {sector}:

TEXT: {document_text}

Return JSON:
{{
    "requirements": ["specific requirements found"],
    "requirement_type": "Mandatory|Recommended|Optional",
    "has_deadlines": true/false
}}"""

    @staticmethod
    def get_implementation_complexity_prompt():
        return """Assess implementation complexity for {sector}:

REQUIREMENTS: {requirements}

Return JSON:
{{
    "complexity_level": "High|Medium|Low",
    "complexity_factors": ["factors contributing to complexity"],
    "estimated_effort": "Major|Moderate|Minor"
}}"""

class MetadataExtractionPrompts:
    """Prompts for document metadata extraction"""
    
    @staticmethod
    def get_reference_number_prompt():
        return """Extract document reference number if present:

TEXT (first 1000 chars): {document_text}

Return JSON:
{{
    "reference_number": "exact reference or null",
    "reference_format": "format type or null",
    "confidence": 0.0 to 1.0
}}"""

    @staticmethod
    def get_date_extraction_prompt():
        return """Extract publication or effective dates:

TEXT: {document_text}

Return JSON:
{{
    "publication_date": "YYYY-MM-DD or null",
    "effective_date": "YYYY-MM-DD or null",
    "date_confidence": 0.0 to 1.0
}}"""

    @staticmethod
    def get_issuing_authority_prompt():
        return """Identify the issuing authority:

TEXT (first 1000 chars): {document_text}

Return JSON:
{{
    "issuing_authority": "authority name or Unknown",
    "authority_type": "Commission|Parliament|Council|Other",
    "confidence": 0.0 to 1.0
}}"""

    @staticmethod
    def get_geographic_scope_prompt():
        return """Determine geographic scope of this document:

TEXT: {document_text}

Return JSON:
{{
    "geographic_scope": "EU-wide|Specific Member States|Regional|Unknown",
    "specific_regions": ["if applicable"],
    "scope_confidence": 0.0 to 1.0
}}"""

class TopicAnalysisPrompts:
    """Prompts for legal topic analysis"""
    
    @staticmethod
    def get_legal_domains_prompt():
        return """Identify primary legal domains covered:

TEXT: {document_text}

Return JSON:
{{
    "legal_domains": ["Data Protection", "Competition Law", "Financial Services", etc.],
    "domain_relevance_scores": {{domain: 0.0 to 1.0}},
    "primary_domain": "main domain"
}}"""

    @staticmethod
    def get_affected_sectors_prompt():
        return """Identify business sectors affected by this document:

TEXT: {document_text}

Return JSON:
{{
    "affected_sectors": ["sector names"],
    "impact_level_per_sector": {{sector: "High|Medium|Low"}},
    "sector_confidence": 0.0 to 1.0
}}"""

class LegalAIAnalyzer:
    def __init__(self, client):
        self.client = client
        self.confidence_threshold = 0.7
        self.temperature = 0.0  # Fixed temperature for consistency
        self.seed = 42  # Fixed seed for reproducibility
        
        # Initialize prompt classes
        self.search_prompts = SearchRelevancePrompts()
        self.tracking_prompts = RegulatoryTrackingPrompts()
        self.summary_prompts = DocumentSummaryPrompts()
        self.structure_prompts = DocumentStructurePrompts()
        self.compliance_prompts = ComplianceAnalysisPrompts()
        self.metadata_prompts = MetadataExtractionPrompts()
        self.topic_prompts = TopicAnalysisPrompts()
        
    def create_cache_key(self, text: str, analysis_type: str) -> str:
        """Create unique cache key for AI analysis"""
        content_hash = hashlib.md5(text[:1000].encode()).hexdigest()
        return f"{analysis_type}_{content_hash}"
    
    def comprehensive_document_analysis(self, document_text: str) -> Dict[str, Any]:
        """
        Comprehensive AI-powered document analysis with no hallucinations
        """
        if not document_text or len(str(document_text).strip()) < 50:
            return self.create_fallback_analysis("Document text too short or empty")
        
        cache_key = self.create_cache_key(document_text, "comprehensive")
        
        if cache_key in st.session_state.ai_analysis_cache:
            return st.session_state.ai_analysis_cache[cache_key]
        
        prompt = f"""
You are a senior legal analyst specializing in European Union law. Analyze this document with extreme precision.

CRITICAL RULES:
1. Extract ONLY information that is EXPLICITLY stated in the text
2. If information is not found, use "Not specified"
3. Never infer or guess information
4. Provide confidence scores (0.0-1.0) for each section

DOCUMENT TEXT:
{document_text[:4000]}

Provide analysis in this exact JSON format:

{{
    "document_metadata": {{
        "title": "Extract the exact title if present, otherwise 'Not specified'",
        "document_type": "Regulation|Directive|Decision|Communication|Other",
        "reference_number": "Extract exact reference number if present",
        "publication_date": "Extract date if mentioned (YYYY-MM-DD) or 'Not specified'",
        "confidence_score": 0.0
    }},
    "summary": {{
        "executive_summary": "2-3 sentence summary of what this document does",
        "key_points": [
            "First key point (max 20 words)",
            "Second key point (max 20 words)",
            "Third key point (max 20 words)"
        ],
        "confidence_score": 0.0
    }},
    "legal_analysis": {{
        "primary_topics": ["List main legal topics covered"],
        "affected_sectors": ["List business sectors affected"],
        "geographic_scope": "EU-wide|Specific countries|Not specified",
        "confidence_score": 0.0
    }},
    "compliance_requirements": {{
        "key_obligations": ["List main compliance requirements found"],
        "deadlines": ["List any deadlines mentioned"],
        "penalties": "Describe penalties if mentioned or 'Not specified'",
        "confidence_score": 0.0
    }},
    "risk_indicators": {{
        "urgency": "High|Medium|Low|Not specified",
        "complexity": "High|Medium|Low|Not specified",
        "enforcement_risk": "High|Medium|Low|Not specified",
        "confidence_score": 0.0
    }},
    "overall_confidence": 0.0
}}

IMPORTANT: Only extract what is explicitly written. Never make assumptions."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a precise legal document analyzer. Extract only explicit information. Never hallucinate."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Cache the result
            st.session_state.ai_analysis_cache[cache_key] = analysis
            return analysis
            
        except Exception as e:
            return self.create_fallback_analysis(f"AI analysis failed: {str(e)}")
    
    def ai_powered_search(self, document_text: str, search_query: str) -> Dict[str, Any]:
        """
        AI-powered semantic search using multiple focused prompts
        """
        cache_key = self.create_cache_key(f"{document_text[:500]}_{search_query}", "search")
        
        if cache_key in st.session_state.ai_analysis_cache:
            return st.session_state.ai_analysis_cache[cache_key]
        
        try:
            # Step 1: Semantic matching
            semantic_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a legal semantic analysis expert."},
                    {"role": "user", "content": self.search_prompts.get_semantic_match_prompt().format(
                        search_query=search_query,
                        document_text=document_text[:1500]
                    )}
                ],
                temperature=self.temperature,
                seed=self.seed,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            semantic_result = json.loads(semantic_response.choices[0].message.content)
            
            # Step 2: Relevance scoring
            relevance_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a legal relevance scoring expert."},
                    {"role": "user", "content": self.search_prompts.get_relevance_scoring_prompt().format(
                        search_query=search_query,
                        matched_concepts=', '.join(semantic_result.get('matched_concepts', []))
                    )}
                ],
                temperature=self.temperature,
                seed=self.seed,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            relevance_result = json.loads(relevance_response.choices[0].message.content)
            
            # Step 3: Extract excerpts if relevant
            excerpts = {"relevant_excerpts": [], "excerpt_relevance_scores": []}
            if relevance_result.get('relevance_score', 0) > 0.3:
                excerpt_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a legal text extraction specialist."},
                        {"role": "user", "content": self.search_prompts.get_excerpt_extraction_prompt().format(
                            search_query=search_query,
                            document_text=document_text[:2000]
                        )}
                    ],
                    temperature=self.temperature,
                    seed=self.seed,
                    max_tokens=400,
                    response_format={"type": "json_object"}
                )
                
                excerpts = json.loads(excerpt_response.choices[0].message.content)
            
            # Combine results
            result = {
                "relevance_score": relevance_result.get('relevance_score', 0.0),
                "is_relevant": relevance_result.get('relevance_score', 0) > 0.3,
                "matching_concepts": semantic_result.get('matched_concepts', []),
                "relevant_excerpts": excerpts.get('relevant_excerpts', []),
                "explanation": f"{relevance_result.get('relevance_category', 'Not Relevant')} match for {search_query}",
                "confidence_score": semantic_result.get('semantic_similarity_score', 0.0)
            }
            
            st.session_state.ai_analysis_cache[cache_key] = result
            return result
            
        except Exception as e:
            return {
                "relevance_score": 0.0,
                "is_relevant": False,
                "error": str(e)
            }
    
    def ai_regulatory_tracking(self, document_text: str, regulation_topic: str) -> Dict[str, Any]:
        """
        Specialized regulatory tracking using multiple focused prompts
        """
        cache_key = self.create_cache_key(f"{document_text[:500]}_{regulation_topic}", "tracking")
        
        if cache_key in st.session_state.ai_analysis_cache:
            return st.session_state.ai_analysis_cache[cache_key]
        
        try:
            # Step 1: Detect regulation mentions
            detection_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a regulatory detection expert."},
                    {"role": "user", "content": self.tracking_prompts.get_regulation_detection_prompt().format(
                        regulation_topic=regulation_topic,
                        document_text=document_text[:2000]
                    )}
                ],
                temperature=self.temperature,
                seed=self.seed,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            detection = json.loads(detection_response.choices[0].message.content)
            
            if not detection.get('mentions_regulation'):
                return {
                    "relevance_score": 0.0,
                    "is_related": False,
                    "relationship_type": "None",
                    "confidence_score": detection.get('confidence', 0.0)
                }
            
            # Step 2: Classify relationship
            relationship_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a regulatory relationship classifier."},
                    {"role": "user", "content": self.tracking_prompts.get_relationship_classification_prompt().format(
                        regulation_topic=regulation_topic,
                        mention_context=document_text[:1500]
                    )}
                ],
                temperature=self.temperature,
                seed=self.seed,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            relationship = json.loads(relationship_response.choices[0].message.content)
            
            # Step 3: Extract temporal information
            temporal_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a temporal information extraction expert."},
                    {"role": "user", "content": self.tracking_prompts.get_temporal_extraction_prompt().format(
                        regulation_topic=regulation_topic,
                        document_text=document_text[:2000]
                    )}
                ],
                temperature=self.temperature,
                seed=self.seed,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            temporal = json.loads(temporal_response.choices[0].message.content)
            
            # Step 4: Identify evolution indicators
            evolution_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a regulatory evolution analyst."},
                    {"role": "user", "content": self.tracking_prompts.get_evolution_indicators_prompt().format(
                        regulation_topic=regulation_topic,
                        document_text=document_text[:2000]
                    )}
                ],
                temperature=self.temperature,
                seed=self.seed,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            evolution = json.loads(evolution_response.choices[0].message.content)
            
            # Combine results
            result = {
                "relevance_score": relationship.get('relationship_strength', 0.0),
                "is_related": True,
                "relationship_type": relationship.get('relationship_type', 'Related topic'),
                "specific_mentions": [],  # Would need another prompt for this
                "related_concepts": detection.get('mention_type', '').split('|') if detection.get('mention_type') else [],
                "temporal_references": temporal.get('dates_mentioned', []) + temporal.get('deadlines', []),
                "evolution_indicators": evolution.get('evolution_indicators', []),
                "importance": evolution.get('importance', 'Medium'),
                "confidence_score": detection.get('confidence', 0.0)
            }
            
            st.session_state.ai_analysis_cache[cache_key] = result
            return result
            
        except Exception as e:
            return {
                "relevance_score": 0.0,
                "is_related": False,
                "error": str(e)
            }
    
    def generate_ai_summary(self, document_text: str) -> Dict[str, Any]:
        """
        Generate document summary using multiple focused prompts
        """
        cache_key = self.create_cache_key(document_text, "summary")
        
        if cache_key in st.session_state.ai_analysis_cache:
            return st.session_state.ai_analysis_cache[cache_key]
        
        try:
            # Step 1: Identify document type
            type_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a legal document classifier."},
                    {"role": "user", "content": self.summary_prompts.get_document_type_prompt().format(
                        document_text=document_text[:500]
                    )}
                ],
                temperature=self.temperature,
                seed=self.seed,
                max_tokens=150,
                response_format={"type": "json_object"}
            )
            
            doc_type = json.loads(type_response.choices[0].message.content)
            
            # Step 2: Extract main purpose
            purpose_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a legal document purpose analyst."},
                    {"role": "user", "content": self.summary_prompts.get_main_purpose_prompt().format(
                        document_text=document_text[:1500]
                    )}
                ],
                temperature=self.temperature,
                seed=self.seed,
                max_tokens=150,
                response_format={"type": "json_object"}
            )
            
            purpose = json.loads(purpose_response.choices[0].message.content)
            
            # Step 3: Extract key points
            points_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a legal key points extractor."},
                    {"role": "user", "content": self.summary_prompts.get_key_points_prompt().format(
                        document_text=document_text[:2000]
                    )}
                ],
                temperature=self.temperature,
                seed=self.seed,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            points = json.loads(points_response.choices[0].message.content)
            
            # Step 4: Extract legal domains
            domains_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a legal domain identification expert."},
                    {"role": "user", "content": self.topic_prompts.get_legal_domains_prompt().format(
                        document_text=document_text[:1500]
                    )}
                ],
                temperature=self.temperature,
                seed=self.seed,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            domains = json.loads(domains_response.choices[0].message.content)
            
            # Combine results
            summary = {
                "document_type": doc_type.get('document_type', 'Other'),
                "main_purpose": purpose.get('main_purpose', 'Not specified'),
                "key_points": [p['point'] for p in points.get('key_points', [])],
                "importance": "High" if max([p.get('importance', 0) for p in points.get('key_points', [{'importance': 0}])]) > 0.7 else "Medium",
                "topics": domains.get('legal_domains', [])[:2],
                "confidence_score": min(
                    doc_type.get('type_confidence', 0.0),
                    purpose.get('purpose_clarity', 0.0)
                )
            }
            
            st.session_state.ai_analysis_cache[cache_key] = summary
            return summary
            
        except Exception as e:
            return {
                "main_purpose": "Summary generation failed",
                "key_points": ["Unable to generate summary"],
                "confidence_score": 0.0,
                "error": str(e)
            }
    
    def extract_document_structure(self, document_text: str) -> Dict[str, Any]:
        """
        Extract document structure using focused prompts
        """
        cache_key = self.create_cache_key(document_text, "structure")
        
        if cache_key in st.session_state.ai_analysis_cache:
            return st.session_state.ai_analysis_cache[cache_key]
        
        try:
            # Step 1: Detect sections
            sections_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a document structure analyst."},
                    {"role": "user", "content": self.structure_prompts.get_section_detection_prompt().format(
                        document_text=document_text[:2000]
                    )}
                ],
                temperature=self.temperature,
                seed=self.seed,
                max_tokens=400,
                response_format={"type": "json_object"}
            )
            
            sections = json.loads(sections_response.choices[0].message.content)
            
            # Step 2: Extract articles if structured
            articles = {"articles": [], "total_articles": 0}
            if sections.get('has_structured_format'):
                articles_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an article extraction specialist."},
                        {"role": "user", "content": self.structure_prompts.get_article_extraction_prompt().format(
                            document_text=document_text[:3000]
                        )}
                    ],
                    temperature=self.temperature,
                    seed=self.seed,
                    max_tokens=600,
                    response_format={"type": "json_object"}
                )
                
                articles = json.loads(articles_response.choices[0].message.content)
            
            # Combine results
            structure = {
                "title": "Document Structure Analysis",
                "sections": [
                    {
                        "type": s['type'],
                        "number": s['identifier'],
                        "heading": f"{s['type']} {s['identifier']}",
                        "summary": ""
                    } for s in sections.get('sections_found', [])
                ],
                "has_articles": articles.get('total_articles', 0) > 0,
                "has_annexes": any(s['type'] == 'Annex' for s in sections.get('sections_found', [])),
                "total_sections": len(sections.get('sections_found', [])),
                "confidence_score": 0.8
            }
            
            st.session_state.ai_analysis_cache[cache_key] = structure
            return structure
            
        except Exception as e:
            return {"sections": [], "confidence_score": 0.0, "error": str(e)}
    
    def assess_compliance_impact(self, document_text: str, sectors: List[str]) -> Dict[str, Any]:
        """
        Assess compliance impact using multiple focused prompts
        """
        cache_key = self.create_cache_key(f"{document_text[:500]}_{','.join(sectors)}", "compliance")
        
        if cache_key in st.session_state.ai_analysis_cache:
            return st.session_state.ai_analysis_cache[cache_key]
        
        try:
            sector_impacts = {}
            
            for sector in sectors[:3]:  # Limit to 3 sectors for performance
                # Step 1: Check sector relevance
                relevance_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a sector relevance analyst."},
                        {"role": "user", "content": self.compliance_prompts.get_sector_relevance_prompt().format(
                            sector=sector,
                            document_text=document_text[:1500]
                        )}
                    ],
                    temperature=self.temperature,
                    seed=self.seed,
                    max_tokens=200,
                    response_format={"type": "json_object"}
                )
                
                relevance = json.loads(relevance_response.choices[0].message.content)
                
                if relevance.get('is_relevant'):
                    # Step 2: Extract requirements
                    requirements_response = self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a compliance requirements extractor."},
                            {"role": "user", "content": self.compliance_prompts.get_compliance_requirements_prompt().format(
                                sector=sector,
                                document_text=document_text[:2000]
                            )}
                        ],
                        temperature=self.temperature,
                        seed=self.seed,
                        max_tokens=400,
                        response_format={"type": "json_object"}
                    )
                    
                    requirements = json.loads(requirements_response.choices[0].message.content)
                    
                    # Step 3: Assess complexity
                    complexity_response = self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are an implementation complexity assessor."},
                            {"role": "user", "content": self.compliance_prompts.get_implementation_complexity_prompt().format(
                                sector=sector,
                                requirements=', '.join(requirements.get('requirements', []))
                            )}
                        ],
                        temperature=self.temperature,
                        seed=self.seed,
                        max_tokens=200,
                        response_format={"type": "json_object"}
                    )
                    
                    complexity = json.loads(complexity_response.choices[0].message.content)
                    
                    sector_impacts[sector] = {
                        "impact_level": complexity.get('complexity_level', 'Medium'),
                        "specific_requirements": requirements.get('requirements', []),
                        "deadlines": [],
                        "actions_required": []
                    }
            
            # Determine overall impact
            impact_levels = [v.get('impact_level', 'Low') for v in sector_impacts.values()]
            overall_impact = 'High' if 'High' in impact_levels else 'Medium' if 'Medium' in impact_levels else 'Low'
            
            result = {
                "overall_impact": overall_impact,
                "sector_impacts": sector_impacts,
                "cross_sector_requirements": [],
                "implementation_complexity": overall_impact,
                "confidence_score": 0.7
            }
            
            st.session_state.ai_analysis_cache[cache_key] = result
            return result
            
        except Exception as e:
            return {"overall_impact": "Error", "confidence_score": 0.0, "error": str(e)}
    
    def create_fallback_analysis(self, error_message: str = "Analysis failed") -> Dict[str, Any]:
        """Create a safe fallback analysis when AI fails"""
        return {
            "document_metadata": {
                "title": "Analysis unavailable",
                "document_type": "Other",
                "reference_number": "Not specified",
                "confidence_score": 0.0
            },
            "summary": {
                "executive_summary": error_message,
                "key_points": ["Analysis failed"],
                "confidence_score": 0.0
            },
            "overall_confidence": 0.0,
            "error": error_message
        }

@st.cache_resource
def initialize_ai_client():
    """Initialize Azure OpenAI client"""
    try:
        client = AzureOpenAI(
            api_key=AZURE_API_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION
        )
        
        # Test connection
        test_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        
        return LegalAIAnalyzer(client), True
        
    except Exception as e:
        st.error(f"Failed to initialize AI client: {str(e)}")
        return None, False

@st.cache_data(show_spinner=False)
def load_legal_dataset():
    """Load the legal documents dataset"""
    try:
        # Try multiple possible paths
        possible_paths = [
            "/Users/joric/Documents/NLP Project/Prompt Engineering /eurolex_consolidated.parquet",
            PARQUET_FILE_PATH,
            "eurolex_consolidated.parquet",
            "data/eurolex_consolidated.parquet"
        ]
        
        df = None
        for path in possible_paths:
            if os.path.exists(path):
                df = pd.read_parquet(path)
                break
        
        if df is None:
            st.error("❌ Dataset not found. Please check file location.")
            return None
        
        # Basic data validation
        required_columns = ['filename', 'folder', 'text']
        if not all(col in df.columns for col in required_columns):
            st.error(f"❌ Missing required columns. Found: {list(df.columns)}")
            return None
        
        # Data preprocessing
        df['publication_date'] = pd.to_datetime(df['folder'], format='%Y-%m', errors='coerce')
        df['text_length'] = df['text'].fillna('').str.len()
        df = df[df['text_length'] > 100]  # Filter empty documents
        df = df.dropna(subset=['publication_date'])
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error loading dataset: {str(e)}")
        return None

def render_confidence_indicator(confidence: float) -> str:
    """Render confidence indicator"""
    if confidence >= 0.8:
        css_class = "confidence-high"
        label = "High"
    elif confidence >= 0.6:
        css_class = "confidence-medium"
        label = "Medium"
    else:
        css_class = "confidence-low"
        label = "Low"
    
    return f'<span class="confidence-indicator {css_class}">{label} Confidence: {confidence:.0%}</span>'

def display_summary_card(doc: Dict, summary: Dict) -> None:
    """Display document summary card"""
    doc_id = doc.get('filename', 'Unknown')
    
    card_html = f"""
    <div class="document-card">
        <h4 style="color: {GT_COLORS['primary_purple']}; margin: 0 0 0.5rem 0;">
            📄 {doc_id[:80]}{'...' if len(doc_id) > 80 else ''}
        </h4>
        <p style="color: {GT_COLORS['medium_gray']}; margin: 0 0 0.5rem 0; font-size: 0.9rem;">
            <strong>Type:</strong> {summary.get('document_type', 'Unknown')} | 
            <strong>Importance:</strong> {summary.get('importance', 'Unknown')} |
            <strong>Date:</strong> {doc.get('publication_date', pd.NaT).strftime('%B %Y') if pd.notna(doc.get('publication_date')) else 'Unknown'}
        </p>
        <p style="margin: 0.5rem 0;"><strong>Purpose:</strong> {summary.get('main_purpose', 'Not specified')}</p>
        <div style="margin: 0.5rem 0;">
            <strong>Key Points:</strong>
            <ul style="margin: 0.5rem 0 0 1rem; padding-left: 1rem;">
                {"".join([f"<li style='margin: 0.25rem 0;'>{point}</li>" for point in summary.get('key_points', [])])}
            </ul>
        </div>
        <div style="margin-top: 0.5rem;">
            {"".join([f'<span class="legal-domain-tag">{topic}</span>' for topic in summary.get('topics', [])])}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def display_detailed_analysis(doc: Dict, analysis: Dict, ai_analyzer: LegalAIAnalyzer) -> None:
    """Display detailed AI analysis view"""
    metadata = analysis.get('document_metadata', {})
    doc_id = metadata.get('reference_number', doc.get('filename', 'Unknown'))
    
    # Header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {GT_COLORS['primary_purple']} 0%, {GT_COLORS['secondary_purple']} 100%); 
                color: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;">
        <h3 style="margin: 0;">{doc_id}</h3>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
            {metadata.get('document_type', 'Unknown Type')} | 
            Published: {doc.get('publication_date', pd.NaT).strftime('%B %Y') if pd.notna(doc.get('publication_date')) else 'Unknown'}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Analysis tabs
    tabs = st.tabs(["📊 Overview", "⚖️ Legal Analysis", "💼 Compliance", "📄 Full Document"])
    
    with tabs[0]:  # Overview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Executive Summary")
            st.info(analysis.get('summary', {}).get('executive_summary', 'Not available'))
            
            st.markdown("#### Key Points")
            for point in analysis.get('summary', {}).get('key_points', []):
                st.write(f"• {point}")
        
        with col2:
            st.markdown("#### Confidence Score")
            confidence = analysis.get('overall_confidence', 0.0)
            st.markdown(render_confidence_indicator(confidence), unsafe_allow_html=True)
            
            st.markdown("#### Risk Indicators")
            risks = analysis.get('risk_indicators', {})
            st.metric("Urgency", risks.get('urgency', 'Not specified'))
            st.metric("Complexity", risks.get('complexity', 'Not specified'))
            st.metric("Enforcement Risk", risks.get('enforcement_risk', 'Not specified'))
    
    with tabs[1]:  # Legal Analysis
        legal = analysis.get('legal_analysis', {})
        
        st.markdown("#### Primary Topics")
        for topic in legal.get('primary_topics', []):
            st.markdown(f'<span class="legal-domain-tag">{topic}</span>', unsafe_allow_html=True)
        
        st.markdown("#### Affected Sectors")
        for sector in legal.get('affected_sectors', []):
            st.write(f"• {sector}")
        
        st.markdown("#### Geographic Scope")
        st.info(legal.get('geographic_scope', 'Not specified'))
    
    with tabs[2]:  # Compliance
        compliance = analysis.get('compliance_requirements', {})
        
        st.markdown("#### Key Obligations")
        for obligation in compliance.get('key_obligations', []):
            st.write(f"• {obligation}")
        
        st.markdown("#### Deadlines")
        deadlines = compliance.get('deadlines', [])
        if deadlines and deadlines != ["Not specified"]:
            for deadline in deadlines:
                st.warning(f"📅 {deadline}")
        else:
            st.info("No specific deadlines found")
        
        st.markdown("#### Penalties")
        st.write(compliance.get('penalties', 'Not specified'))
    
    with tabs[3]:  # Full Document
        # Get document structure
        with st.spinner("🤖 AI analyzing document structure..."):
            structure = ai_analyzer.extract_document_structure(doc['text'])
        
        if structure.get('sections'):
            st.markdown("#### Document Structure")
            for section in structure['sections'][:10]:  # Limit to first 10 sections
                st.write(f"**{section.get('type', '')} {section.get('number', '')}**: {section.get('heading', '')}")
                if section.get('summary'):
                    st.write(f"   _{section['summary']}_")
        
        st.markdown("#### Full Text")
        st.text_area("Document Content", doc['text'], height=500, disabled=True)

def main():
    # Grant Thornton Header
    st.markdown(f"""
    <div class="main-header">
        <div class="gt-logo">Grant Thornton Legal</div>
        <div class="gt-subtitle">Advanced AI-Powered Legal Intelligence Platform</div>
        <div class="ai-powered-badge">🤖 Fully AI-Driven Analysis</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize AI system
    ai_analyzer, ai_connected = initialize_ai_client()
    
    if not ai_connected:
        st.error("🚫 AI System Required. Please configure Azure OpenAI credentials.")
        return
    
    # Load dataset
    df = load_legal_dataset()
    if df is None:
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="background: {GT_COLORS['primary_purple']}; color: white; 
                    padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
            <h3 style="margin: 0;">🔍 AI Legal Intelligence</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # AI Status
        st.markdown("### 🤖 AI System Status")
        st.success("✅ Advanced AI Analysis Active")
        
        # Dataset Overview
        st.markdown("### 📊 Dataset Overview")
        st.info(f"""
        **Total Documents:** {len(df):,}  
        **Date Range:** {df['publication_date'].min().strftime('%Y-%m')} to {df['publication_date'].max().strftime('%Y-%m')}
        """)
        
        # Filters
        st.markdown('<div class="gt-filter-section">', unsafe_allow_html=True)
        st.markdown("### 🎯 Intelligent Filters")
        
        # Date range
        date_range = st.date_input(
            "Publication Period",
            value=(df['publication_date'].max() - pd.DateOffset(months=6), df['publication_date'].max()),
            min_value=df['publication_date'].min(),
            max_value=df['publication_date'].max()
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply date filter
    filtered_df = df.copy()
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['publication_date'] >= pd.to_datetime(date_range[0])) &
            (filtered_df['publication_date'] <= pd.to_datetime(date_range[1]))
        ]
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs([
        "🔍 Document Browser & Search",
        "⚖️ Compliance Intelligence",
        "🎯 Regulatory Tracking"
    ])
    
    with tab1:
        st.markdown("## 📚 AI-Powered Document Browser")
        
        # Search interface
        search_query = st.text_input(
            "🔍 AI-Powered Semantic Search",
            placeholder="e.g., data protection, GDPR, financial services, competition law",
            help="AI will understand your intent and find semantically relevant documents"
        )
        
        # Display mode
        display_mode = st.radio(
            "Display Mode",
            ["📋 Summary Cards", "📖 Detailed Analysis"],
            horizontal=True
        )
        
        if search_query:
            # AI-powered search
            if st.button("🚀 Start AI Search", type="primary", key="search_button"):
                with st.spinner(f"🧠 AI searching for '{search_query}'..."):
                    search_results = []
                    
                    # Use AI to search documents
                    progress_bar = st.progress(0)
                    search_sample = filtered_df.head(50)  # Search first 50 docs
                    
                    for idx, (_, doc) in enumerate(search_sample.iterrows()):
                        # AI relevance check
                        relevance = ai_analyzer.ai_powered_search(doc['text'], search_query)
                        
                        if relevance.get('is_relevant', False) and relevance.get('relevance_score', 0) > 0.3:
                            search_results.append({
                                'doc': doc,
                                'relevance': relevance
                            })
                        
                        progress_bar.progress((idx + 1) / len(search_sample))
                    
                    progress_bar.empty()
                    
                    # Sort by relevance
                    search_results.sort(key=lambda x: x['relevance']['relevance_score'], reverse=True)
                    st.session_state.search_results = search_results
            
            # Display search results
            if st.session_state.search_results:
                st.success(f"✅ Found {len(st.session_state.search_results)} relevant documents")
                
                for idx, result in enumerate(st.session_state.search_results[:10]):
                    doc = result['doc']
                    relevance = result['relevance']
                    
                    # Show relevance score
                    st.markdown(f"""
                    <div style="background: {GT_COLORS['info_blue']}; color: white; 
                                padding: 0.5rem; border-radius: 4px; margin: 0.5rem 0;">
                        🎯 Relevance: {relevance['relevance_score']:.0%} - {relevance.get('explanation', '')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if display_mode == "📋 Summary Cards":
                        # Get AI summary
                        summary = ai_analyzer.generate_ai_summary(doc['text'])
                        display_summary_card(doc, summary)
                        
                        # Action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🔬 Full Analysis", key=f"analyze_{idx}"):
                                with st.spinner("Generating analysis..."):
                                    analysis = ai_analyzer.comprehensive_document_analysis(doc['text'])
                                    display_detailed_analysis(doc, analysis, ai_analyzer)
                        
                        with col2:
                            st.download_button(
                                "📥 Download",
                                doc['text'],
                                file_name=f"{doc['filename'].replace('/', '_')}.txt",
                                mime="text/plain",
                                key=f"download_{idx}"
                            )
                    
                    else:  # Detailed Analysis
                        with st.spinner("Generating comprehensive analysis..."):
                            analysis = ai_analyzer.comprehensive_document_analysis(doc['text'])
                            display_detailed_analysis(doc, analysis, ai_analyzer)
        
        else:
            # Show recent documents
            st.markdown("### 📅 Recent Documents")
            recent_docs = filtered_df.head(10)
            
            for idx, (_, doc) in enumerate(recent_docs.iterrows()):
                if display_mode == "📋 Summary Cards":
                    # Generate AI summary
                    with st.spinner(f"Generating summary {idx+1}/10..."):
                        summary = ai_analyzer.generate_ai_summary(doc['text'])
                    display_summary_card(doc, summary)
                    
                    # Action buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔬 Full Analysis", key=f"analyze_recent_{idx}"):
                            with st.spinner("Generating analysis..."):
                                analysis = ai_analyzer.comprehensive_document_analysis(doc['text'])
                                display_detailed_analysis(doc, analysis, ai_analyzer)
                    
                    with col2:
                        st.download_button(
                            "📥 Download",
                            doc['text'],
                            file_name=f"{doc['filename'].replace('/', '_')}.txt",
                            mime="text/plain",
                            key=f"download_recent_{idx}"
                        )
                
                else:  # Detailed Analysis
                    with st.spinner(f"Generating analysis {idx+1}/10..."):
                        analysis = ai_analyzer.comprehensive_document_analysis(doc['text'])
                        display_detailed_analysis(doc, analysis, ai_analyzer)
    
    with tab2:
        st.markdown("## ⚖️ AI Compliance Intelligence")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company/Client Name", placeholder="Enter company name")
        
        with col2:
            sectors = st.multiselect(
                "Business Sectors",
                ["Financial Services", "Data Protection", "Environmental", "Digital Markets", 
                 "Healthcare", "Energy", "Transportation", "Manufacturing", "Telecommunications"]
            )
        
        if company_name and sectors:
            if st.button("🚀 Generate AI Compliance Assessment", type="primary"):
                with st.spinner("🧠 AI analyzing compliance requirements..."):
                    
                    # Find relevant documents using AI
                    relevant_docs = []
                    sector_query = " ".join(sectors)
                    
                    for _, doc in filtered_df.head(30).iterrows():
                        relevance = ai_analyzer.ai_powered_search(doc['text'], sector_query)
                        if relevance.get('relevance_score', 0) > 0.4:
                            relevant_docs.append(doc)
                    
                    if relevant_docs:
                        st.success(f"✅ Found {len(relevant_docs)} relevant documents for {company_name}")
                        
                        # Analyze each document for compliance
                        for idx, doc in enumerate(relevant_docs[:5]):
                            with st.spinner(f"Analyzing document {idx+1}/5..."):
                                impact = ai_analyzer.assess_compliance_impact(doc['text'], sectors)
                            
                            if impact.get('overall_impact') != 'None':
                                st.markdown(f"""
                                <div class="document-card">
                                    <h4>📋 {doc['filename'][:60]}...</h4>
                                    <p><strong>Overall Impact:</strong> {impact['overall_impact']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Create tabs for Summary and Full Publication
                                tab_summary, tab_full = st.tabs(["📊 Summary", "📄 Full Publication"])
                                
                                with tab_summary:
                                    # Show sector-specific impacts
                                    for sector, details in impact.get('sector_impacts', {}).items():
                                        if details.get('impact_level') != 'None':
                                            st.markdown(f"**{sector}:**")
                                            
                                            col1, col2 = st.columns([1, 3])
                                            with col1:
                                                impact_color = {
                                                    'High': GT_COLORS['error_red'],
                                                    'Medium': GT_COLORS['warning_yellow'],
                                                    'Low': GT_COLORS['success_green']
                                                }.get(details['impact_level'], GT_COLORS['medium_gray'])
                                                
                                                st.markdown(f"""
                                                <div style="background: {impact_color}; color: white; 
                                                            padding: 0.5rem; border-radius: 8px; text-align: center;">
                                                    {details['impact_level']} Impact
                                                </div>
                                                """, unsafe_allow_html=True)
                                            
                                            with col2:
                                                st.markdown("**Specific Requirements:**")
                                                for req in details.get('specific_requirements', [])[:3]:
                                                    st.write(f"• {req}")
                                                
                                                if details.get('deadlines'):
                                                    st.markdown("**Deadlines:**")
                                                    for deadline in details.get('deadlines', [])[:2]:
                                                        st.warning(f"📅 {deadline}")
                                                
                                                if details.get('actions_required'):
                                                    st.markdown("**Actions Required:**")
                                                    for action in details.get('actions_required', [])[:3]:
                                                        st.info(f"✓ {action}")
                                    
                                    # Cross-sector requirements
                                    if impact.get('cross_sector_requirements'):
                                        st.markdown("---")
                                        st.markdown("**🔗 Cross-Sector Requirements:**")
                                        for req in impact['cross_sector_requirements'][:3]:
                                            st.write(f"• {req}")
                                    
                                    # Implementation complexity
                                    st.markdown("---")
                                    complexity_color = {
                                        'High': GT_COLORS['error_red'],
                                        'Medium': GT_COLORS['warning_yellow'],
                                        'Low': GT_COLORS['success_green']
                                    }.get(impact.get('implementation_complexity', 'Medium'), GT_COLORS['medium_gray'])
                                    
                                    st.markdown(f"""
                                    <div style="background: {GT_COLORS['light_gray']}; padding: 1rem; border-radius: 8px;">
                                        <strong>Implementation Complexity:</strong> 
                                        <span style="color: {complexity_color}; font-weight: bold;">
                                            {impact.get('implementation_complexity', 'Not specified')}
                                        </span>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Download summary button
                                    summary_text = f"""
COMPLIANCE SUMMARY - {company_name}
Document: {doc['filename']}
Overall Impact: {impact['overall_impact']}

SECTOR-SPECIFIC IMPACTS:
{chr(10).join([f"{sector}: {details.get('impact_level', 'Unknown')}" for sector, details in impact.get('sector_impacts', {}).items()])}

KEY REQUIREMENTS:
{chr(10).join(['- ' + req for sector_impacts in impact.get('sector_impacts', {}).values() for req in sector_impacts.get('specific_requirements', [])[:3]])}

Implementation Complexity: {impact.get('implementation_complexity', 'Not specified')}
                                    """
                                    
                                    st.download_button(
                                        "📥 Download Compliance Summary",
                                        summary_text,
                                        file_name=f"{company_name}_{doc['filename'][:20]}_compliance_summary.txt",
                                        mime="text/plain",
                                        key=f"download_compliance_summary_{idx}"
                                    )
                                
                                with tab_full:
                                    # Document metadata
                                    st.markdown(f"""
                                    <div style="background: {GT_COLORS['light_gray']}; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                                        <strong>Document:</strong> {doc['filename']}<br>
                                        <strong>Publication Date:</strong> {doc.get('publication_date', pd.NaT).strftime('%B %Y') if pd.notna(doc.get('publication_date')) else 'Unknown'}<br>
                                        <strong>Document Length:</strong> {len(doc['text'])} characters
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Full document text
                                    st.text_area(
                                        "Full Document Text",
                                        doc['text'],
                                        height=600,
                                        disabled=True,
                                        key=f"full_text_compliance_{idx}"
                                    )
                                    
                                    # Download full document button
                                    st.download_button(
                                        "📥 Download Full Document",
                                        doc['text'],
                                        file_name=f"{doc['filename'].replace('/', '_')}.txt",
                                        mime="text/plain",
                                        key=f"download_full_compliance_{idx}"
                                    )
                                
                                st.markdown("---")  # Separator between documents
                    else:
                        st.info("No highly relevant documents found for the specified sectors.")
    
    with tab3:
        st.markdown("## 🎯 AI Regulatory Tracking")
        
        track_query = st.text_input(
            "🔍 Track Regulation/Topic",
            placeholder="e.g., GDPR, AI Act, Sustainability Reporting, Data Protection",
            help="AI will track evolution of this topic across ALL documents in your selected date range"
        )
        
        if track_query:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                threshold = st.slider(
                    "Relevance Threshold",
                    min_value=0.1,
                    max_value=0.9,
                    value=0.3,
                    step=0.1,
                    help="Lower = more results (including loosely related)"
                )
            
            with col2:
                sort_by = st.selectbox(
                    "Sort Results By",
                    ["Date (Chronological)", "Relevance Score", "Importance"]
                )
            
            # Show how many documents will be analyzed
            docs_to_analyze = len(filtered_df)
            if docs_to_analyze > 0:
                st.info(f"""
                📊 **Documents to analyze:** {docs_to_analyze:,} documents 
                from {filtered_df['publication_date'].min().strftime('%B %Y')} to {filtered_df['publication_date'].max().strftime('%B %Y')}
                
                ⏱️ **Estimated time:** {max(1, docs_to_analyze // 50)} - {max(2, docs_to_analyze // 25)} minutes
                """)
                
                # Warning for large datasets
                if docs_to_analyze > 1000:
                    st.warning("""
                    ⚠️ **Large Dataset**: Analyzing over 1,000 documents. Consider:
                    - Narrowing your date range for faster results
                    - Using a higher relevance threshold
                    - This comprehensive analysis will provide the most complete tracking
                    """)
            
            if st.button("🕵️ Start Comprehensive AI Tracking", type="primary"):
                with st.spinner(f"🤖 AI tracking '{track_query}' across {docs_to_analyze:,} documents..."):
                    
                    tracking_results = []
                    
                    # Create progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Process in batches for better performance and progress updates
                    batch_size = 25  # Larger batches for efficiency
                    total_batches = (docs_to_analyze + batch_size - 1) // batch_size
                    
                    for batch_num in range(total_batches):
                        start_idx = batch_num * batch_size
                        end_idx = min((batch_num + 1) * batch_size, docs_to_analyze)
                        batch = filtered_df.iloc[start_idx:end_idx]
                        
                        status_text.text(f"Analyzing documents {start_idx+1} to {end_idx} of {docs_to_analyze}...")
                        
                        for _, doc in batch.iterrows():
                            # Use specialized regulatory tracking
                            try:
                                tracking_analysis = ai_analyzer.ai_regulatory_tracking(doc['text'], track_query)
                            except AttributeError:
                                # Fallback to regular search if method doesn't exist
                                tracking_analysis = ai_analyzer.ai_powered_search(doc['text'], track_query)
                                # Convert to tracking format
                                tracking_analysis = {
                                    'relevance_score': tracking_analysis.get('relevance_score', 0.0),
                                    'is_related': tracking_analysis.get('is_relevant', False),
                                    'relationship_type': 'Related topic',
                                    'specific_mentions': tracking_analysis.get('relevant_excerpts', []),
                                    'related_concepts': tracking_analysis.get('matching_concepts', []),
                                    'temporal_references': [],
                                    'evolution_indicators': [],
                                    'importance': 'Medium' if tracking_analysis.get('relevance_score', 0) > 0.5 else 'Low',
                                    'confidence_score': tracking_analysis.get('confidence_score', 0.0)
                                }
                            
                            if tracking_analysis.get('is_related') and tracking_analysis.get('relevance_score', 0) >= threshold:
                                tracking_results.append({
                                    'doc': doc,
                                    'analysis': tracking_analysis
                                })
                        
                        # Update progress
                        progress = (batch_num + 1) / total_batches
                        progress_bar.progress(progress)
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    if tracking_results:
                        st.success(f"🎯 Found {len(tracking_results)} documents related to '{track_query}' out of {docs_to_analyze:,} analyzed")
                        
                        # Calculate and show coverage statistics
                        coverage_percentage = (len(tracking_results) / docs_to_analyze) * 100
                        relevance_distribution = {
                            'High': sum(1 for r in tracking_results if r['analysis'].get('importance') == 'High'),
                            'Medium': sum(1 for r in tracking_results if r['analysis'].get('importance') == 'Medium'),
                            'Low': sum(1 for r in tracking_results if r['analysis'].get('importance') == 'Low')
                        }
                        
                        # Sort results based on selection
                        if sort_by == "Date (Chronological)":
                            tracking_results.sort(key=lambda x: x['doc']['publication_date'])
                        elif sort_by == "Relevance Score":
                            tracking_results.sort(key=lambda x: x['analysis']['relevance_score'], reverse=True)
                        else:  # Importance
                            importance_order = {"High": 3, "Medium": 2, "Low": 1}
                            tracking_results.sort(
                                key=lambda x: importance_order.get(x['analysis'].get('importance', 'Low'), 0), 
                                reverse=True
                            )
                        
                        # Show comprehensive statistics
                        st.markdown("### 📊 Comprehensive Tracking Results")
                        
                        col1, col2, col3, col4, col5 = st.columns(5)
                        
                        with col1:
                            st.metric("Documents Analyzed", f"{docs_to_analyze:,}")
                        
                        with col2:
                            st.metric("Relevant Documents", len(tracking_results))
                        
                        with col3:
                            st.metric("Coverage", f"{coverage_percentage:.1f}%")
                        
                        with col4:
                            st.metric("High Importance", relevance_distribution['High'])
                        
                        with col5:
                            avg_relevance = sum(r['analysis']['relevance_score'] for r in tracking_results) / len(tracking_results)
                            st.metric("Avg Relevance", f"{avg_relevance:.0%}")
                        
                        # Create timeline visualization
                        timeline_data = []
                        for result in tracking_results:
                            timeline_data.append({
                                'Date': result['doc']['publication_date'],
                                'Document': result['doc']['filename'][:50] + '...',
                                'Relevance': result['analysis']['relevance_score'],
                                'Type': result['analysis'].get('relationship_type', 'Unknown'),
                                'Importance': result['analysis'].get('importance', 'Medium')
                            })
                        
                        if timeline_data:
                            timeline_df = pd.DataFrame(timeline_data)
                            
                            # Timeline chart
                            fig = px.scatter(
                                timeline_df,
                                x='Date',
                                y='Relevance',
                                size='Relevance',
                                color='Type',
                                hover_data=['Document', 'Importance'],
                                title=f"Complete Evolution of '{track_query}' Across {docs_to_analyze:,} EU Legal Documents",
                                labels={'Relevance': 'Relevance Score'}
                            )
                            
                            fig.update_layout(
                                height=400,
                                xaxis_title="Publication Date",
                                yaxis_title="Relevance Score",
                                showlegend=True
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Temporal distribution
                            st.markdown("### 📅 Temporal Distribution")
                            
                            # Group by year
                            timeline_df['Year'] = timeline_df['Date'].dt.year
                            yearly_counts = timeline_df.groupby('Year').size().reset_index(name='Count')
                            
                            fig2 = px.bar(
                                yearly_counts,
                                x='Year',
                                y='Count',
                                title=f"'{track_query}' Documents by Year",
                                labels={'Count': 'Number of Documents'}
                            )
                            st.plotly_chart(fig2, use_container_width=True)
                            
                            # Relationship type distribution
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                type_counts = timeline_df['Type'].value_counts()
                                fig3 = px.pie(
                                    values=type_counts.values,
                                    names=type_counts.index,
                                    title="Document Relationship Types"
                                )
                                st.plotly_chart(fig3, use_container_width=True)
                            
                            with col2:
                                importance_counts = timeline_df['Importance'].value_counts()
                                fig4 = px.pie(
                                    values=importance_counts.values,
                                    names=importance_counts.index,
                                    title="Importance Distribution",
                                    color_discrete_map={
                                        'High': '#E74C3C',
                                        'Medium': '#F39C12',
                                        'Low': '#27AE60'
                                    }
                                )
                                st.plotly_chart(fig4, use_container_width=True)
                        
                        # Show detailed results
                        st.markdown("### 📄 Detailed Document Analysis")
                        
                        # Add filter for relationship type
                        selected_types = st.multiselect(
                            "Filter by Relationship Type",
                            options=list(set(r['analysis'].get('relationship_type', 'Unknown') for r in tracking_results)),
                            default=None
                        )
                        
                        # Add pagination for large result sets
                        if len(tracking_results) > 20:
                            st.info(f"Showing results in pages (20 per page)")
                            
                            # Calculate pages
                            total_pages = (len(tracking_results) + 19) // 20
                            page = st.number_input(
                                "Page", 
                                min_value=1, 
                                max_value=total_pages, 
                                value=1,
                                help=f"Total pages: {total_pages}"
                            )
                            
                            start_idx = (page - 1) * 20
                            end_idx = min(page * 20, len(tracking_results))
                            
                            displayed_results = tracking_results[start_idx:end_idx]
                            
                            st.markdown(f"Showing documents {start_idx + 1} to {end_idx} of {len(tracking_results)}")
                        else:
                            displayed_results = tracking_results
                        
                        # Apply type filter if selected
                        if selected_types:
                            displayed_results = [r for r in displayed_results if r['analysis'].get('relationship_type') in selected_types]
                    
                        # Display documents with tabs
                        for idx, result in enumerate(displayed_results):
                            doc = result['doc']
                            analysis = result['analysis']
                            
                            # Color code by importance
                            border_color = {
                                'High': GT_COLORS['error_red'],
                                'Medium': GT_COLORS['warning_yellow'],
                                'Low': GT_COLORS['success_green']
                            }.get(analysis.get('importance', 'Medium'), GT_COLORS['medium_gray'])
                            
                            st.markdown(f"""
                            <div class="document-card" style="border-left-color: {border_color};">
                                <div style="display: flex; justify-content: space-between; align-items: start;">
                                    <div style="flex-grow: 1;">
                                        <h4 style="color: {GT_COLORS['primary_purple']}; margin: 0;">
                                            📄 {doc['filename'][:80]}...
                                        </h4>
                                        <p style="color: {GT_COLORS['medium_gray']}; margin: 0.5rem 0;">
                                            <strong>Date:</strong> {doc['publication_date'].strftime('%B %Y')} | 
                                            <strong>Type:</strong> {analysis.get('relationship_type', 'Unknown')} |
                                            <strong>Importance:</strong> <span style="color: {border_color};">{analysis.get('importance', 'Unknown')}</span>
                                        </p>
                                    </div>
                                    <div>
                                        <span class="confidence-indicator confidence-{'high' if analysis['relevance_score'] > 0.7 else 'medium' if analysis['relevance_score'] > 0.4 else 'low'}">
                                            {analysis['relevance_score']:.0%}
                                        </span>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Create tabs for Summary and Full Publication
                            track_tab_summary, track_tab_full = st.tabs(["📊 Tracking Summary", "📄 Full Publication"])
                            
                            with track_tab_summary:
                                # Related concepts
                                if analysis.get('related_concepts'):
                                    st.markdown("**Related Concepts:**")
                                    concepts_html = "".join([f'<span class="legal-domain-tag">{concept}</span>' for concept in analysis.get('related_concepts', [])[:5]])
                                    st.markdown(concepts_html, unsafe_allow_html=True)
                                
                                # Specific mentions
                                if analysis.get('specific_mentions'):
                                    st.markdown("**Specific Mentions:**")
                                    for mention in analysis.get('specific_mentions', [])[:2]:
                                        st.info(f"💬 {mention}")
                                
                                # Evolution indicators
                                if analysis.get('evolution_indicators'):
                                    st.markdown("**Evolution Indicators:**")
                                    for indicator in analysis.get('evolution_indicators', [])[:2]:
                                        st.write(f"📈 {indicator}")
                                
                                # Temporal references
                                if analysis.get('temporal_references'):
                                    st.markdown("**Temporal References:**")
                                    for ref in analysis.get('temporal_references', [])[:2]:
                                        st.warning(f"📅 {ref}")
                                
                                # Analysis actions
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button(f"🔬 Full Analysis", key=f"track_analyze_{idx}_{page if len(tracking_results) > 20 else ''}"):
                                        with st.spinner("Generating comprehensive analysis..."):
                                            full_analysis = ai_analyzer.comprehensive_document_analysis(doc['text'])
                                            display_detailed_analysis(doc, full_analysis, ai_analyzer)
                                
                                with col2:
                                    # Download tracking summary
                                    tracking_summary = f"""
REGULATORY TRACKING SUMMARY
Topic: {track_query}
Document: {doc['filename']}
Date: {doc['publication_date'].strftime('%B %Y')}

RELEVANCE: {analysis['relevance_score']:.0%}
RELATIONSHIP TYPE: {analysis.get('relationship_type', 'Unknown')}
IMPORTANCE: {analysis.get('importance', 'Unknown')}

RELATED CONCEPTS:
{chr(10).join(['- ' + concept for concept in analysis.get('related_concepts', [])])}

SPECIFIC MENTIONS:
{chr(10).join(['- ' + mention for mention in analysis.get('specific_mentions', [])])}

EVOLUTION INDICATORS:
{chr(10).join(['- ' + indicator for indicator in analysis.get('evolution_indicators', [])])}
                                    """
                                    
                                    st.download_button(
                                        "📥 Download Summary",
                                        tracking_summary,
                                        file_name=f"{track_query}_{doc['filename'][:20]}_tracking_summary.txt",
                                        mime="text/plain",
                                        key=f"download_track_summary_{idx}_{page if len(tracking_results) > 20 else ''}"
                                    )
                            
                            with track_tab_full:
                                # Document metadata
                                st.markdown(f"""
                                <div style="background: {GT_COLORS['light_gray']}; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                                    <strong>Document:</strong> {doc['filename']}<br>
                                    <strong>Publication Date:</strong> {doc['publication_date'].strftime('%B %Y')}<br>
                                    <strong>Relevance to "{track_query}":</strong> {analysis['relevance_score']:.0%}<br>
                                    <strong>Document Length:</strong> {len(doc['text'])} characters
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Full document text
                                st.text_area(
                                    "Full Document Text",
                                    doc['text'],
                                    height=600,
                                    disabled=True,
                                    key=f"full_text_track_{idx}_{page if len(tracking_results) > 20 else ''}"
                                )
                                
                                # Download full document
                                st.download_button(
                                    "📥 Download Full Document",
                                    doc['text'],
                                    file_name=f"{doc['filename'].replace('/', '_')}.txt",
                                    mime="text/plain",
                                    key=f"download_full_track_{idx}_{page if len(tracking_results) > 20 else ''}"
                                )
                            
                            st.markdown("---")  # Separator between documents
                        
                        # Export all results option
                        if len(tracking_results) > 0:
                            st.markdown("### 📥 Export Options")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Export summary CSV
                                summary_data = []
                                for result in tracking_results:
                                    summary_data.append({
                                        'Document': result['doc']['filename'],
                                        'Date': result['doc']['publication_date'].strftime('%Y-%m-%d'),
                                        'Relevance Score': result['analysis']['relevance_score'],
                                        'Relationship Type': result['analysis'].get('relationship_type', 'Unknown'),
                                        'Importance': result['analysis'].get('importance', 'Unknown')
                                    })
                                
                                summary_df = pd.DataFrame(summary_data)
                                csv = summary_df.to_csv(index=False)
                                
                                st.download_button(
                                    "📊 Download Results CSV",
                                    csv,
                                    file_name=f"{track_query}_tracking_results_{datetime.now().strftime('%Y%m%d')}.csv",
                                    mime="text/csv"
                                )
                            
                            with col2:
                                # Export detailed report
                                report = f"""
COMPREHENSIVE REGULATORY TRACKING REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

TRACKING QUERY: {track_query}
DOCUMENTS ANALYZED: {docs_to_analyze:,}
RELEVANT DOCUMENTS FOUND: {len(tracking_results)}
COVERAGE: {coverage_percentage:.1f}%
DATE RANGE: {filtered_df['publication_date'].min().strftime('%B %Y')} to {filtered_df['publication_date'].max().strftime('%B %Y')}

IMPORTANCE DISTRIBUTION:
- High: {relevance_distribution['High']}
- Medium: {relevance_distribution['Medium']}
- Low: {relevance_distribution['Low']}

AVERAGE RELEVANCE SCORE: {avg_relevance:.1%}

DETAILED RESULTS:
{"="*80}

"""
                                for i, result in enumerate(tracking_results, 1):
                                    doc = result['doc']
                                    analysis = result['analysis']
                                    report += f"""
{i}. {doc['filename']}
   Date: {doc['publication_date'].strftime('%B %Y')}
   Relevance: {analysis['relevance_score']:.0%}
   Type: {analysis.get('relationship_type', 'Unknown')}
   Importance: {analysis.get('importance', 'Unknown')}
   
"""
                                
                                st.download_button(
                                    "📄 Download Full Report",
                                    report,
                                    file_name=f"{track_query}_comprehensive_report_{datetime.now().strftime('%Y%m%d')}.txt",
                                    mime="text/plain"
                                )
                    
                    else:
                        st.warning(f"""
                        🔍 No documents found related to '{track_query}' with threshold {threshold:.0%}
                        
                        **Analysis Complete:**
                        - Analyzed {docs_to_analyze:,} documents
                        - Date range: {filtered_df['publication_date'].min().strftime('%B %Y')} to {filtered_df['publication_date'].max().strftime('%B %Y')}
                        - No documents exceeded the {threshold:.0%} relevance threshold
                        
                        **Try:**
                        - Lowering the relevance threshold
                        - Using broader search terms
                        - Checking if the topic exists in this date range
                        - Using related terms (e.g., "data protection" instead of "GDPR")
                        """)
            else:
                st.info("👆 Enter a regulation or topic to track its evolution across the entire dataset")

if __name__ == "__main__":
    main()