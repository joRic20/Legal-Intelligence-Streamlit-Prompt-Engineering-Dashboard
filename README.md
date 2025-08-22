# Legal Intelligence Platform

A comprehensive AI-powered system for legal document analysis, compliance assessment, and regulatory tracking.

## Overview

The Legal Intelligence Platform is an advanced AI-driven solution designed to streamline legal and regulatory information processing. Built specifically for legal professionals, the platform leverages OpenAI services and sophisticated natural language processing to provide intelligent document analysis, compliance assessment, and regulatory tracking capabilities.

## Platform Dashboard

<div align="center">
  <img src="https://github.com/joRic20/Legal-Intelligence-Streamlit-Prompt-Engineering-Dashboard/blob/main/homepage.png?raw=true" alt="Legal Intelligence Platform - Main Dashboard" width="100%"/>
  <br><em>🏠 Modern AI-powered legal intelligence dashboard with professional design and intuitive navigation</em>
</div>

<br>

<div align="center">
  <img src="https://github.com/joRic20/Legal-Intelligence-Streamlit-Prompt-Engineering-Dashboard/blob/main/homepage1.png?raw=true" alt="Legal Intelligence Platform - Dashboard Features" width="100%"/>
  <br><em>📊 Advanced dashboard showing dataset statistics, AI processing status, and filtering capabilities</em>
</div>

## Feature Gallery

<table>
  <tr>
    <td width="50%" align="center">
      <img src="https://github.com/joRic20/Legal-Intelligence-Streamlit-Prompt-Engineering-Dashboard/blob/main/documentbrowser.png?raw=true" alt="Document Browser & AI Search" width="100%"/>
      <h3>📄 Document Browser & AI Search</h3>
      <p><strong>Intelligent Semantic Search</strong><br>
      AI-powered search that understands legal context and intent with relevance scoring, document summaries, and automated classification</p>
      <ul align="left">
        <li>Semantic search with confidence indicators</li>
        <li>Document type identification</li>
        <li>Executive summary generation</li>
        <li>Key legal points extraction</li>
      </ul>
    </td>
    <td width="50%" align="center">
      <img src="https://github.com/joRic20/Legal-Intelligence-Streamlit-Prompt-Engineering-Dashboard/blob/main/compliance.png?raw=true" alt="Compliance Intelligence System" width="100%"/>
      <h3>⚖️ Compliance Intelligence</h3>
      <p><strong>Sector-Specific Analysis</strong><br>
      Tailored compliance impact assessment across multiple business sectors with automated risk analysis and requirement extraction</p>
      <ul align="left">
        <li>Multi-sector compliance mapping</li>
        <li>Risk level assessment (High/Medium/Low)</li>
        <li>Deadline identification</li>
        <li>Implementation complexity analysis</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td colspan="2" align="center">
      <img src="https://github.com/joRic20/Legal-Intelligence-Streamlit-Prompt-Engineering-Dashboard/blob/main/tracker.png?raw=true" alt="Regulatory Tracking & Analytics" width="100%"/>
      <h3>📊 Regulatory Tracking & Evolution Monitoring</h3>
      <p><strong>Comprehensive Regulatory Analysis</strong><br>
      Track specific regulations across the entire document corpus with interactive timeline visualizations, statistical analysis, and trend monitoring</p>
      <div align="left" style="max-width: 800px; margin: 0 auto;">
        <ul>
          <li><strong>Evolution Monitoring:</strong> Track regulatory changes across thousands of documents</li>
          <li><strong>Timeline Visualizations:</strong> Interactive charts showing regulatory development over time</li>
          <li><strong>Relationship Classification:</strong> Identify direct mentions, implementations, and amendments</li>
          <li><strong>Statistical Analysis:</strong> Coverage percentages, importance distribution, and trend analysis</li>
          <li><strong>Export Capabilities:</strong> Comprehensive reports and CSV data export</li>
        </ul>
      </div>
    </td>
  </tr>
</table>

## Key Features

### 🤖 Advanced AI Processing
- **Automated Document Analysis**: Process 3,000+ EuroLex legal documents with hierarchical organization
- **Multi-Stage NLP Pipeline**: Advanced text preprocessing with BERT tokenization and semantic understanding
- **AI Document Classification**: Automated document type identification and legal domain categorization
- **Confidence Scoring**: All AI outputs include reliability indicators for professional decision-making

### 🔍 Intelligent Search & Analysis
- **Semantic Search**: AI-powered search understanding legal context and intent beyond keyword matching
- **Relevance Scoring**: Advanced relevance assessment with confidence indicators and explanation
- **Document Summarization**: Automated generation of executive summaries and key legal points
- **Structure Analysis**: Extraction of document sections, articles, and legal framework components

### ⚖️ Compliance Intelligence
- **Sector-Specific Analysis**: Tailored compliance impact assessment across Financial Services, Data Protection, Environmental, Digital Markets, Healthcare, Energy, Transportation, Manufacturing, and Telecommunications
- **Risk Assessment**: Automated identification of compliance requirements, deadlines, and penalties
- **Implementation Complexity**: Assessment of effort and resources required for compliance
- **Cross-Sector Requirements**: Identification of regulations affecting multiple business areas

### 📊 Regulatory Tracking
- **Evolution Monitoring**: Track specific regulations across entire document corpus with comprehensive analysis
- **Temporal Analysis**: Chronological tracking with interactive timeline visualizations and statistical insights
- **Relationship Classification**: Identification of document relationships (Direct mentions, Implementations, Amendments, Related topics)
- **Trend Analysis**: Year-over-year regulatory activity analysis with importance distribution metrics

## Technical Architecture

### Core Technology Stack
- **Backend**: Python 3.8+, Pandas, NLTK, Gensim
- **AI/ML**: OpenAI GPT-4o-mini, BERT tokenization, Custom NLP pipelines
- **Frontend**: Streamlit with modern professional UI components and responsive design
- **Data Storage**: Optimized Parquet files with PyArrow engine (70-90% compression)
- **Visualization**: Plotly for interactive charts, timelines, and analytics
- **Authentication**: Secure OpenAI API credential management

### Data Processing Pipeline

**Stage 1: Document Ingestion**
- **Source**: 3,000+ EuroLex legal documents in PDF format
- **Processing**: Recursive directory traversal and intelligent text extraction
- **Output**: Structured DataFrame with comprehensive metadata and full text content (eurolex_consolidated.parquet)
- **Storage**: Compressed Parquet format for optimal query performance

**Stage 2: Advanced NLP Preprocessing**
- **Text Cleaning**: Punctuation removal and case normalization
- **Advanced Filtering**: Custom stopword removal preserving legal negations
- **Normalization**: Stemming for consistent word forms and legal terminology
- **Tokenization**: BERT-compatible tokenization for transformer model integration

**Stage 3: AI Analysis Pipeline**
- **Document Classification**: Automated type identification and purpose extraction
- **Content Analysis**: Legal domain identification and key point extraction
- **Compliance Mapping**: Requirement extraction and sector impact analysis
- **Relationship Detection**: Cross-document regulatory relationship identification

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- OpenAI API access with GPT-4o-mini model
- Minimum 8GB RAM for large document processing
- Required Python packages listed in requirements.txt

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/joRic20/Legal-Intelligence-Streamlit-Prompt-Engineering-Dashboard.git
   cd Legal-Intelligence-Streamlit-Prompt-Engineering-Dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API credentials**
   
   Create a `settings.py` file:
   ```python
   # OpenAI Configuration
   OPEN_API_KEY = "your_openai_api_key_here"
   ```

4. **Launch the application**
   ```bash
   streamlit run app.py
   ```

   Access at `http://localhost:8501`

### Additional Resources

- **Jupyter Notebook**: `gpt_info_extractor - richard.ipynb` contains GPT analysis experiments and prompt engineering examples
- **Prompt Documentation**: `prompts.md` provides detailed information about AI prompt engineering strategies
- **Sample Data**: `legal_data_sample.csv` and `legal_data_report.txt` contain analysis examples and data insights
- **Testing**: `test.py` includes utility functions for testing and validation

## Usage Guide

### 📄 Document Browser and Search

**AI-Powered Semantic Search**
1. Navigate to "Document Browser & Search" tab
2. Enter search terms (e.g., "data protection", "GDPR", "financial services", "competition law")
3. AI analyzes semantic relevance across all documents with confidence scoring
4. View results with detailed relevance explanations and matching concepts

**Analysis Modes**
- **Summary Cards**: Quick overview with key points, document type, and metadata
- **Detailed Analysis**: Comprehensive AI analysis with legal framework, compliance requirements, and full document structure

### ⚖️ Compliance Intelligence

**Client Assessment Workflow**
1. Access "Compliance Intelligence" tab
2. Enter company/client name and select relevant business sectors
3. AI analyzes documents for sector-specific compliance requirements
4. Review detailed impact assessments with actionable insights

**Analysis Features**
- **Impact Level Assessment**: High, Medium, Low classification with detailed reasoning
- **Specific Requirements**: Extraction of actionable compliance items with deadline identification
- **Implementation Complexity**: Assessment of required effort, resources, and complexity factors
- **Cross-Sector Analysis**: Identification of requirements affecting multiple business areas

### 📊 Regulatory Tracking

**Comprehensive Tracking Process**
1. Navigate to "Regulatory Tracking" tab
2. Enter regulation or topic (e.g., "AI Act", "GDPR", "Sustainability Reporting", "Data Protection")
3. Set relevance threshold and sorting preferences (Date, Relevance, Importance)
4. AI analyzes evolution across entire document corpus with progress tracking

**Advanced Analytics**
- **Timeline Visualization**: Interactive scatter plots showing regulatory evolution over time
- **Statistical Analysis**: Coverage percentages, document distribution, and importance metrics
- **Relationship Classification**: Automated identification of document relationships to regulations
- **Export Capabilities**: CSV data export and comprehensive PDF reports

## Performance Metrics

### Dataset Scale
- **Document Volume**: 3,000+ processed legal documents
- **Time Coverage**: Multi-year regulatory tracking capability
- **Processing Speed**: Optimized batch processing with real-time progress indicators
- **Analysis Accuracy**: AI confidence scoring for all generated content

### Storage Optimization
- **Compression Ratio**: 70-90% size reduction through optimized Parquet format
- **Query Performance**: Columnar storage enabling fast analytical queries
- **Memory Efficiency**: Intelligent data loading and processing with caching mechanisms

### AI Performance
- **Response Time**: Intelligent caching for repeated queries
- **Accuracy**: Confidence scoring and fallback mechanisms for all AI-generated content
- **Scalability**: Batch processing capabilities for comprehensive analysis of large document sets

## Project Structure

```
Legal-Intelligence-Platform/
├── __pycache__/                            # Python cache files
├── .venv/                                  # Virtual environment
├── data/                                   # Data processing files
├── .gitignore                              # Git ignore configuration
├── app.py                                  # Main Streamlit application
├── compliance.png                          # Compliance feature screenshot
├── documentbrowser.png                     # Document browser screenshot
├── eurolex_consolidated.parquet            # Processed legal document dataset
├── gpt_info_extractor - richard.ipynb     # GPT analysis notebook
├── homepage.png                            # Main dashboard screenshot
├── homepage1.png                           # Dashboard features screenshot
├── legal_data_report.txt                   # Data analysis report
├── legal_data_sample.csv                   # Sample data file
├── prompts.md                              # AI prompt engineering documentation
├── README.md                               # This documentation
├── requirements.in                         # Core dependencies
├── requirements.txt                        # All Python dependencies
├── settings.py                             # Configuration settings
├── test.py                                 # Testing utilities
└── tracker.png                             # Regulatory tracking screenshot
```

## Business Impact

### Operational Excellence
- **Early Warning System**: Proactive detection of upcoming regulatory changes
- **Efficiency Gains**: 80%+ reduction in manual document review time
- **Quality Improvement**: Consistent AI-powered analysis with transparent confidence scoring
- **Risk Mitigation**: Early identification of compliance gaps and regulatory requirements

### Strategic Advantages
- **Proactive Advisory**: Enhanced ability to advise clients before regulations are enacted
- **Competitive Differentiation**: Advanced AI capabilities providing superior service delivery
- **Comprehensive Coverage**: Analysis of entire regulatory corpus vs. traditional manual sampling
- **Data-Driven Insights**: Statistical analysis and trend identification for strategic planning

### Measurable Outcomes
- **Time Savings**: Hours to minutes for comprehensive regulatory analysis
- **Coverage Improvement**: Complete corpus analysis vs. selective manual review
- **Service Enhancement**: Faster, more comprehensive insights for stakeholders and clients
- **Accuracy Improvement**: AI-powered consistency with confidence scoring for reliability

## Security and Quality Assurance

### Data Protection
- **API Security**: Secure OpenAI API credential management with no persistent storage of sensitive data
- **Data Privacy**: Session-based processing with no permanent storage of API responses
- **Access Control**: Secure session state management and user isolation

### Quality Controls
- **Source Verification**: Complete traceability to original legal documents
- **Content Validation**: Multi-stage AI confidence scoring and fallback mechanisms
- **Export Integrity**: Consistent formatting and comprehensive metadata preservation
- **Error Handling**: Robust error management with detailed logging and recovery procedures

## Contributing

We welcome contributions! Please feel free to submit pull requests, report bugs, or suggest new features.

### Development Guidelines
- Follow Python PEP 8 style guidelines
- Include comprehensive documentation for new features
- Add unit tests for new functionality
- Update README for any new capabilities

## License

This project is open source and available for legal monitoring and compliance analysis applications. All AI-generated content includes appropriate confidence scoring and source attribution for professional legal analysis.

## Support

For technical support, feature requests, or questions about implementation, please open an issue on GitHub or contact the development team.

---

<div align="center">
  <h3>🚀 Transform Your Legal Intelligence Capabilities</h3>
  <p><em>Harness the power of AI for comprehensive legal document analysis, compliance assessment, and regulatory tracking</em></p>
</div>