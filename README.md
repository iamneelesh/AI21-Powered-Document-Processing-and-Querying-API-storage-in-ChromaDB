# AI21-Powered Document Processing and Querying API

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Starting the Server](#starting-the-server)
  - [API Endpoints](#api-endpoints)
- [Technical Details](#technical-details)
  - [Document Processing](#document-processing)
  - [Embedding Generation](#embedding-generation)
  - [Vector Storage](#vector-storage)
  - [Query Processing](#query-processing)
  - [Text Summarization](#text-summarization)
- [Performance Considerations](#performance-considerations)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)

## Overview

This Flask-based API harnesses the power of AI21's advanced language models to process, embed, and query documents. It integrates ChromaDB for efficient vector storage and retrieval, enabling sophisticated semantic search and question-answering capabilities.

## Features

- **Document Processing**: Efficiently chunks and processes uploaded text documents.
- **AI-Powered Embeddings**: Utilizes AI21's API to generate high-quality text embeddings.
- **Semantic Search**: Performs context-aware searches using AI21 embeddings.
- **Intelligent Question Answering**: Generates detailed answers based on relevant document contexts.
- **Text Summarization**: Provides concise summaries of uploaded documents.
- **Vector Storage**: Leverages ChromaDB for persistent and efficient vector data management.

## Prerequisites

- Python 3.7+
- Flask
- ChromaDB
- NLTK
- Requests
- AI21 API key

## Configuration

1. Create a `.env` file in the project root and add your AI21 API key:
  AI21_API_KEY=your_api_key_here
2. Adjust the `embedding_dimension` and other parameters in `app.py` if needed.

## Usage

### Starting the Server

Run the following command to start the Flask server:
The API will be available at `http://localhost:5000`

### API Endpoints

1. **Process File**
   - **URL:** `/process`
   - **Method:** POST
   - **Data:** Form-data with file upload (key: 'file')
   - **Response:** JSON with processing status and document overview
   - **Example:**
     ```
     curl -X POST -F "file=@document.txt" http://localhost:5000/process
     ```

2. **Query**
   - **URL:** `/query`
   - **Method:** POST
   - **Data:** JSON with 'query' key
   - **Response:** JSON with AI-generated answer
   - **Example:**
     ```
     curl -X POST -H "Content-Type: application/json" -d '{"query":"What is AI21?"}' http://localhost:5000/query
     ```

3. **Summarize**
   - **URL:** `/summarize`
   - **Method:** POST
   - **Data:** Form-data with file upload (key: 'file')
   - **Response:** JSON with document summary
   - **Example:**
     ```
     curl -X POST -F "file=@document.txt" http://localhost:5000/summarize
     ```

## Technical Details

### Document Processing
- Utilizes NLTK for sentence tokenization
- Implements custom chunking algorithm for optimal text segmentation

### Embedding Generation
- Leverages AI21's embedding API
- Supports both 'segment' and other embedding types
- Default embedding dimension: 1024

### Vector Storage
- Uses ChromaDB for persistent vector storage
- Allows for efficient similarity search and retrieval

### Query Processing
- Employs semantic search to find relevant document chunks
- Utilizes AI21's J2-Ultra model for answer generation and enhancement

### Text Summarization
- Generates comprehensive summaries using AI21's language model
- Handles large documents by summarizing initial content

## Performance Considerations
- Implement caching mechanisms for frequently accessed embeddings
- Consider batch processing for large documents
- Optimize ChromaDB index for faster query responses

## Security Considerations
- Store the AI21 API key securely, preferably using environment variables
- Implement rate limiting to prevent API abuse
- Add authentication and authorization for production use
- Sanitize and validate all user inputs

## Troubleshooting
- Ensure all dependencies are correctly installed
- Check AI21 API key validity and quota
- Verify ChromaDB is properly initialized and accessible
- Monitor server logs for detailed error messages

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## Acknowledgements
- [AI21 Labs](https://www.ai21.com/) for  language models and APIs
- [ChromaDB](https://www.trychroma.com/) for efficient vector storage solutions
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [NLTK](https://www.nltk.org/) for natural language processing tools

