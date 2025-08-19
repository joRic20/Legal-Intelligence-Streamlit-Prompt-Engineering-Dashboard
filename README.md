# Legal Intelligence Platform

A comprehensive AI-powered system for legal document analysis, compliance assessment, and regulatory tracking.

## Overview

The Legal Intelligence Platform is an advanced AI-driven solution designed to streamline legal and regulatory information processing. Built specifically for legal professionals, the platform leverages Azure OpenAI services and sophisticated natural language processing to provide intelligent document analysis, compliance assessment, and regulatory tracking capabilities.

## Dashboard Preview

![Legal Intelligence Dashboard](https://github.com/joRic20/Legal-Intelligence-Streamlit-Prompt-Engineering-Dashboard/blob/main/dashboard%20screenshot.jpeg?raw=true)
*AI-powered legal intelligence dashboard with document analysis, compliance tracking, and regulatory monitoring capabilities*

## Key Features

### Advanced Document Processing
- **Automated PDF Processing**: Processes over 3,000 EuroLex legal documents with hierarchical organization
- **Multi-Stage NLP Pipeline**: Advanced text preprocessing including punctuation removal, stopword filtering, stemming, and BERT tokenization
- **AI Document Classification**: Automated document type identification and legal domain categorization

### Intelligent Search and Analysis
- **Semantic Search**: AI-powered search that understands legal context and intent
- **Relevance Scoring**: Advanced relevance assessment with confidence indicators
- **Document Summarization**: Automated generation of executive summaries and key legal points
- **Structure Analysis**: Extraction of document sections, articles, and legal framework

### Compliance Intelligence
- **Sector-Specific Analysis**: Tailored compliance impact assessment across multiple business sectors
- **Risk Assessment**: Automated identification of compliance requirements, deadlines, and penalties
- **Implementation Complexity**: Assessment of effort and resources required for compliance
- **Cross-Sector Requirements**: Identification of regulations affecting multiple business areas

### Regulatory Tracking
- **Evolution Monitoring**: Track specific regulations across the entire document corpus
- **Temporal Analysis**: Chronological tracking with interactive timeline visualizations
- **Relationship Classification**: Identification of document relationships to regulations
- **Trend Analysis**: Statistical analysis of regulatory changes over time

## Technical Architecture

### Core Components

**Data Processing Layer**
- Custom PDF text extraction utilities
- Parquet-based storage with Snappy compression for 70-90% size reduction
- Hierarchical document organization by publication date
- Comprehensive metadata extraction and validation

**AI Analysis Layer**
- Azure OpenAI GPT-4o-mini integration
- Specialized prompt engineering for legal document analysis
- Multiple focused AI analysis modules:
  - Document summarization and classification
  - Compliance requirement extraction
  - Regulatory relationship tracking
  - Semantic search and relevance scoring

**Application Layer**
- Streamlit-based web interface with professional styling
- Real-time AI analysis with progress tracking
- Interactive visualizations using Plotly
- Comprehensive export capabilities for reports and data

### Technology Stack

- **Backend**: Python 3.8+, Pandas, NLTK, Gensim
- **AI/ML**: Azure OpenAI API, BERT tokenization, Custom NLP pipelines
- **Frontend**: Streamlit with professional UI components
- **Data Storage**: Parquet files with PyArrow engine optimization
- **Visualization**: Plotly for interactive charts, timelines, and analytics
- **Authentication**: Azure OpenAI credential management

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- Azure OpenAI API access with GPT-4o-mini model
- Minimum 8GB RAM for large document processing
- Required Python packages listed in requirements.txt

### Environment Configuration

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd legal-intelligence-platform
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Azure OpenAI credentials**
   
   Create a `settings.py` file:
   ```python
   # Azure OpenAI Configuration
   AZURE_API_KEY = "your_api_key_here"
   AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
   AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
   
   # Data Configuration
   CONTAINER_NAME = "legal-documents"
   PARQUET_FILE_PATH = "eurolex_consolidated.parquet"
   ```

4. **Verify dataset availability**
   
   Ensure the processed legal document dataset is available at the specified path.

### Application Launch

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Usage Guide

### Document Browser and Search

**Semantic Search**
1. Navigate to the "Document Browser & Search" tab
2. Enter search terms (e.g., "data protection", "GDPR", "financial services")
3. AI analyzes semantic relevance across all documents
4. View results with relevance scores and explanations

**Display Options**
- **Summary Cards**: Quick overview with key points and metadata
- **Detailed Analysis**: Comprehensive AI analysis with full document structure

**Export Capabilities**
- Download individual documents as text files
- Export analysis summaries and reports
- Save search results for further analysis

### Compliance Intelligence

**Client Assessment Workflow**
1. Access the "Compliance Intelligence" tab
2. Enter company/client name and relevant business sectors
3. AI analyzes documents for sector-specific compliance requirements
4. Review detailed impact assessments by sector

**Analysis Features**
- **Impact Level Assessment**: High, Medium, Low impact classification
- **Specific Requirements**: Extraction of actionable compliance items
- **Deadline Identification**: Automatic detection of compliance deadlines
- **Implementation Complexity**: Assessment of required effort and resources

**Reporting**
- Download compliance summaries for client communications
- Export full publications with highlighted relevant sections
- Generate comprehensive compliance reports

### Regulatory Tracking

**Comprehensive Tracking Process**
1. Navigate to the "Regulatory Tracking" tab
2. Enter regulation or topic to track (e.g., "AI Act", "Sustainability Reporting")
3. Set relevance threshold and sorting preferences
4. AI analyzes evolution across entire document corpus

**Analysis Capabilities**
- **Timeline Visualization**: Interactive charts showing regulatory evolution
- **Relationship Classification**: Direct mentions, implementations, amendments
- **Statistical Analysis**: Coverage percentages and importance distribution
- **Temporal Distribution**: Year-over-year regulatory activity

**Advanced Features**
- **Batch Processing**: Analyze thousands of documents efficiently
- **Progress Tracking**: Real-time analysis progress with estimated completion
- **Filtering Options**: Filter by relationship type and importance level
- **Pagination**: Handle large result sets with organized pagination

## Project Structure

```
legal-intelligence-platform/
├── src/
│   ├── utilities/
│   │   ├── load_pdfs_to_parquet.py         # PDF processing utilities
│   │   └── preprocessing_parquet.py        # NLP preprocessing classes
│   └── resources/
│       └── eurolex_consolidated.parquet    # Processed document dataset
├── app.py                                  # Main Streamlit application
├── settings.py                             # Configuration settings
├── requirements.txt                        # Python dependencies
├── dashboard screenshot.jpeg               # Dashboard preview image
├── paste.txt                              # Project documentation
└── README.md                              # This file
```

## Data Processing Pipeline

### Stage 1: Document Ingestion
- **Source**: EuroLex legal documents in PDF format
- **Processing**: Recursive directory traversal and text extraction
- **Output**: Structured DataFrame with metadata and full text content
- **Storage**: Compressed Parquet format for optimal performance

### Stage 2: NLP Preprocessing
- **Text Cleaning**: Punctuation removal and case normalization
- **Advanced Filtering**: Custom stopword removal preserving legal negations
- **Normalization**: Stemming for consistent word forms
- **Tokenization**: BERT-compatible tokenization for transformer models

### Stage 3: AI Analysis Pipeline
- **Document Classification**: Type identification and purpose extraction
- **Content Analysis**: Legal domain identification and key point extraction
- **Compliance Mapping**: Requirement extraction and sector impact analysis
- **Relationship Detection**: Cross-document regulatory relationship identification

## AI Prompt Engineering Framework

The platform employs a sophisticated prompt engineering approach with specialized modules:

### Core Prompt Categories

**Search and Relevance**
- Semantic matching algorithms
- Relevance scoring with confidence intervals
- Excerpt extraction for relevant content

**Regulatory Analysis**
- Evolution detection and classification
- Temporal reference extraction
- Relationship strength assessment

**Document Structure**
- Section and article identification
- Hierarchical content analysis
- Structural element extraction

**Compliance Assessment**
- Sector-specific relevance determination
- Requirement extraction and classification
- Implementation complexity evaluation

### Quality Assurance Features

- **Confidence Scoring**: All AI outputs include reliability indicators
- **Response Caching**: Optimized performance through intelligent caching
- **Error Handling**: Comprehensive fallback mechanisms for AI failures
- **Consistency Controls**: Fixed temperature and seed values for reproducible results

## Performance Metrics

### Dataset Scale
- **Document Volume**: 3,000+ processed legal documents
- **Time Coverage**: Multi-year regulatory tracking capability
- **Processing Speed**: Optimized batch processing for large-scale analysis

### Storage Optimization
- **Compression Ratio**: 70-90% size reduction through Parquet format
- **Query Performance**: Columnar storage for fast analytical queries
- **Memory Efficiency**: Optimized data loading and processing

### AI Performance
- **Response Time**: Cached results for repeated queries
- **Accuracy**: Confidence scoring for all AI-generated content
- **Scalability**: Batch processing capabilities for comprehensive analysis

## Security and Compliance

### Data Protection
- **API Security**: Secure Azure OpenAI credential management
- **Data Privacy**: No persistent storage of API responses
- **Access Control**: Session-based state management

### Quality Controls
- **Source Verification**: Full traceability to original documents
- **Content Validation**: AI confidence scoring and fallback mechanisms
- **Export Integrity**: Consistent formatting and metadata preservation

## Future Development Roadmap

### Technical Enhancements
- **Enhanced Relevance Scoring**: Implementation of cosine similarity with document embeddings
- **Real-time Data Integration**: Automated scraping from EUR-Lex and national institutions
- **Advanced Classification**: Machine learning models for consistent legal domain tagging

### Feature Expansion
- **Client-Specific Customization**: Integration of client metadata for targeted analysis
- **Multilingual Support**: German and other European language processing
- **Advanced Analytics**: Predictive modeling for regulatory trend analysis

### Platform Integration
- **API Development**: RESTful API for integration with existing legal systems
- **Database Integration**: Enterprise database connectivity for large-scale deployments
- **Advanced Reporting**: Professional report generation with legal formatting

## Business Impact

### Operational Benefits
- **Early Warning System**: Detection of upcoming regulatory changes for proactive response
- **Efficiency Gains**: 80%+ reduction in manual document review time
- **Quality Improvement**: Consistent, AI-powered analysis with confidence scoring

### Strategic Advantages
- **Proactive Advisory**: Enhanced ability to advise clients before regulations are enacted
- **Risk Mitigation**: Early identification of compliance gaps and requirements
- **Competitive Differentiation**: Advanced AI capabilities for superior service delivery

### Measurable Outcomes
- **Time Savings**: Hours to minutes for comprehensive regulatory analysis
- **Coverage Improvement**: Analysis of entire regulatory corpus vs. manual sampling
- **Service Enhancement**: Faster, more comprehensive insights for stakeholders

## Challenges and Learnings

### Technical Challenges
- **Document Variability**: Handling diverse formatting and structure across legal documents
- **AI Model Selection**: Balancing performance, cost, and reliability across different models
- **Prompt Engineering**: Achieving consistent, structured outputs through iterative development

### Organizational Insights
- **Modular Architecture**: Essential for flexibility and independent component iteration
- **Transparency Requirements**: Need for explainable AI outputs in legal contexts
- **Scalability Considerations**: Optimizing for large-scale document processing

## Support and Maintenance

### Technical Support
- Comprehensive error handling with detailed logging
- Performance monitoring and optimization recommendations
- Regular updates for AI model improvements

### Documentation
- Complete API documentation for all custom utilities
- User guides for each major platform feature
- Technical specifications for system administrators

### Training and Resources
- User training materials for legal professionals
- Technical documentation for development teams
- Best practices guide for optimal platform utilization

## License

This project is open source and available for legal monitoring and compliance analysis applications. All AI-generated content includes appropriate confidence scoring and source attribution for professional legal analysis.

## Contributing

Contributions are welcome! Please read the contribution guidelines and submit pull requests for any improvements or new features.