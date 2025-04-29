"""
Script to process court opinions and generate keyword postings and document entities.
This script uses PySpark to efficiently process large volumes of legal text data,
extracting keywords and creating searchable postings for legal document search.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, regexp_replace, explode, count, length, trim, size, split, expr
import os
import json
import gc
from bson import ObjectId

def process_batch(df, neutral_legal_terms):
    """
    Process a batch of documents to extract keywords and create postings.
    
    Args:
        df (DataFrame): PySpark DataFrame containing document text
        neutral_legal_terms (list): List of legal terms to exclude from keywords
        
    Returns:
        list: List of keyword postings with document IDs and counts
    """
    
    # Clean text by removing URLs, special characters, and normalizing whitespace
    df = df.withColumn("cleaned_text", 
        regexp_replace(
            regexp_replace(
                regexp_replace(
                    regexp_replace(
                        regexp_replace(
                            lower(col("text")),
                            r'http\S+|www\S+|https\S+', ''  # Remove URLs
                        ),
                        r'[^a-zA-Z\s]', ' '  # Remove non-alphabetic characters
                    ),
                    r'\s+', ' '  # Normalize whitespace
                ),
                r'^\s+|\s+$', ''  # Trim leading/trailing spaces
            ),
            r'\b[a-z]\b', ' '  # Remove single-letter words
        )
    )
    
    # Tokenize text into individual words
    from pyspark.ml.feature import Tokenizer
    tokenizer = Tokenizer(inputCol="cleaned_text", outputCol="words")
    df = tokenizer.transform(df)
    
    # Remove stop words and neutral legal terms
    from pyspark.ml.feature import StopWordsRemover
    remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
    standard_stop_words = StopWordsRemover.loadDefaultStopWords("english")
    all_stop_words = standard_stop_words + neutral_legal_terms
    remover.setStopWords(all_stop_words)
    df = remover.transform(df)
    
    # Generate n-grams for phrase matching
    from pyspark.ml.feature import NGram
    bigram = NGram(n=2, inputCol="filtered_words", outputCol="bigrams")
    df = bigram.transform(df)
    
    trigram = NGram(n=3, inputCol="filtered_words", outputCol="trigrams")
    df = trigram.transform(df)
    
    # Process each type of posting separately to manage memory
    result_postings = []
    
    # Create postings for single words with frequency counts
    word_postings = df.select(
        col("uid"),
        explode("filtered_words").alias("keyword")
    ).filter(
        (length("keyword") > 1) &  # Remove single letters
        (col("keyword") != "")     # Remove empty strings
    ).groupBy("uid", "keyword").count()
    
    # Collect and clear memory
    word_postings_list = word_postings.collect()
    result_postings.extend(word_postings_list)
    word_postings = None
    gc.collect()
    
    # Create postings for bigrams (2-word phrases)
    bigram_postings = df.select(
        col("uid"),
        explode("bigrams").alias("keyword")
    ).filter(
        (length("keyword") > 3) &   # Remove very short phrases
        (col("keyword") != "") &    # Remove empty strings
        (size(split("keyword", " ")) == 2)  # Ensure exactly two words
    ).groupBy("uid", "keyword").count()
    
    # Collect and clear memory
    bigram_postings_list = bigram_postings.collect()
    result_postings.extend(bigram_postings_list)
    bigram_postings = None
    gc.collect()
    
    # Create postings for trigrams (3-word phrases)
    trigram_postings = df.select(
        col("uid"),
        explode("trigrams").alias("keyword")
    ).filter(
        (length("keyword") > 5) &   # Remove very short phrases
        (col("keyword") != "") &    # Remove empty strings
        (size(split("keyword", " ")) == 3) &  # Ensure exactly three words
        (~col("keyword").rlike(r'\s{2,}')) &  # No multiple spaces
        (~col("keyword").rlike(r'\b[a-z]\b'))  # No single-letter words
    ).groupBy("uid", "keyword").count()
    
    # Collect and clear memory
    trigram_postings_list = trigram_postings.collect()
    result_postings.extend(trigram_postings_list)
    trigram_postings = None
    
    # Clean up the main dataframe
    df = None
    gc.collect()
    
    return result_postings

def main():
    """
    Main function to process court opinions and generate searchable postings.
    Sets up Spark session, processes documents in batches, and writes results to files.
    """
    # Set environment variables for Spark
    os.environ['PYSPARK_PYTHON'] = os.path.join(os.getcwd(), '.venv/bin/python')
    
    # Define neutral legal terms to exclude from keyword extraction
    neutral_legal_terms = [
        # Court system roles/actors
        "court", "judge", "justice", "magistrate", "clerk", "bailiff",
        "plaintiff", "defendant", "appellant", "respondent", "petitioner", "prosecutor",
        "attorney", "lawyer", "counsel", "esquire", "barrister", "solicitor",
        "witness", "expert", "jury", "juror",
        
        # Procedural legal terms
        "motion", "hearing", "trial", "proceeding", "case", "matter", "action",
        "appeal", "petition", "complaint", "pleading", "filing", "docket",
        "evidence", "testimony", "exhibit", "affidavit", "deposition",
        "brief", "memorandum", "argument", "objection", "overruled", "sustained",
        "verdict", "judgment", "opinion", "decision", "order", "ruling",
        "section", "paragraph", "statute", "regulation", "code", "article",
        
        # Citation and reference terms
        "supra", "infra", "herein", "therein", "hereof", "thereof", 
        "id", "ibid", "see", "cf", "eg", "ie",
        "versus", "vs", "v", "et", "al", "seq",
        "cite", "cited", "citing",
        
        # Common court procedure terms
        "filed", "denied", "granted", "dismissed", "affirmed", "reversed", "remanded",
        "sustained", "overruled", "admitted", "excluded",
        "preliminary", "summary", "final",
        
        # Common generic legal text elements
        "pursuant", "accordance", "relevant", "following", "foregoing",
        "subject", "matter", "regarding", "concerning", "pertaining",
        "review", "standard", "examination", "determine", "determined",
        "issue", "issued", "fact", "facts", "allegation", "allegations",
        "submit", "submitted", "contend", "contends", "claim", "claims",
        "finding", "findings", "hold", "holding", "holds", "conclude", "concludes",
        "dr", "honorable", "hon",
        
        # Non-substantive words that appear in legal documents
        "page", "record", "transcript", "document", "documents", "file",
        "paragraph", "chapter", "volume", "title", "part", "section", "subsection",
        "amendment", "clause", "provision",
        
        # Additional neutral terms
        "state", "york", "di", "also", "however", "therefore", "thus",
        "said", "made", "may", "first", "second", "third", "last", "next",
        "previous", "following", "above", "below", "here", "there", "this",
        "that", "these", "those", "which", "what", "when", "where", "who",
        "whom", "whose", "why", "how", "whether", "while", "although",
        "because", "since", "unless", "until", "whenever", "wherever",
        "misc", "relative", "rule", "march", "december", "july", "november",
        "january", "february", "april", "may", "june", "august", "september",
        "october", "suffolk", "county", "town", "city", "village", "borough",
        "district", "region", "area", "zone", "territory", "jurisdiction",
        "passalacqua", "muro", "service", "commission", "police",
    ]
    
    # Initialize Spark session with optimized configuration
    spark = SparkSession.builder \
        .appName("CourtOpinionsProcessing") \
        .master("local[*]") \
        .config("spark.driver.memory", "12g") \
        .config("spark.executor.memory", "8g") \
        .config("spark.sql.shuffle.partitions", "8") \
        .config("spark.default.parallelism", "8") \
        .config("spark.driver.extraJavaOptions", "-Djava.security.manager=allow") \
        .config("spark.executor.extraJavaOptions", "-Djava.security.manager=allow") \
        .config("spark.driver.host", "localhost") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.local.ip", "127.0.0.1") \
        .getOrCreate()

    try:
        print("🚀 Starting court opinions processing...")
        
        # Define output file paths
        keyword_output_file = "data/keyword_postings.json"
        entity_output_file = "data/document_entities.json"
        
        # Initialize output files
        with open(keyword_output_file, 'w') as f:
            f.write('')
        with open(entity_output_file, 'w') as f:
            f.write('')
        
        # Configure batch processing parameters
        batch_size = 100      # Number of documents per batch
        max_batches = None    # Process all documents (or set to limit processing)
        
        # Read and analyze input data
        print("📚 Reading input JSON file...")
        sample_df = spark.read \
            .option("multiLine", "true") \
            .option("mode", "PERMISSIVE") \
            .json("data/court_listener_db.opinions.json")
            
        print("📊 Data schema:")
        sample_df.printSchema()
        
        total_docs = sample_df.count()
        print(f"📑 Total documents to process: {total_docs:,}")
        
        # Calculate batch processing parameters
        max_docs = total_docs if max_batches is None else min(total_docs, max_batches * batch_size)
        num_batches = (max_docs + batch_size - 1) // batch_size
        print(f"📦 Will process {max_docs:,} documents in {num_batches} batches of {batch_size}")
        
        # Prepare document IDs for batch processing
        print("🔍 Preparing document IDs for batch processing...")
        doc_ids = sample_df.select("link").limit(max_docs).collect()
        
        # Initialize tracking variables
        total_entities = 0
        total_postings = 0
        entity_uids = set()
        posting_uids = set()
        
        # Process documents in batches
        for batch_idx in range(num_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, max_docs)
            
            # Skip if we're out of documents
            if start_idx >= len(doc_ids):
                break
                
            # Get document IDs for current batch
            batch_links = [doc["link"] for doc in doc_ids[start_idx:end_idx]]
            
            if not batch_links:
                print(f"⚠️ No documents in batch {batch_idx+1}, skipping")
                continue
                
            print(f"\n📦 Processing batch {batch_idx+1}/{num_batches} (documents {start_idx+1}-{end_idx})")
            print(f"📄 Batch contains {len(batch_links)} documents")
            
            # Filter and process current batch
            from pyspark.sql.functions import array, lit
            current_batch = sample_df.filter(col("link").isin(batch_links))
            
            # Verify batch data
            batch_count = current_batch.count()
            print(f"✅ Retrieved {batch_count} documents for processing")
            
            if batch_count == 0:
                print("⚠️ No documents could be retrieved, skipping")
                continue
            
            # Transform data for processing
            df = current_batch.select(
                col("link").alias("url"),
                col("textBlock").alias("text"),
                expr("hex(sha1(link))").alias("uid")  # Generate unique document ID
            ).na.fill("")
            
            # Extract entities and process keywords
            entities = df.select("uid", "url").collect()
            print("🔑 Processing keywords...")
            postings_list = process_batch(df, neutral_legal_terms)
            
            # Write entities to output file
            with open(entity_output_file, 'a') as f:
                for entity in entities:
                    entity_doc = {
                        "id": entity.uid,
                        "url": entity.url
                    }
                    f.write(json.dumps(entity_doc) + '\n')
                    entity_uids.add(entity.uid)
            
            # Write postings to output file
            with open(keyword_output_file, 'a') as f:
                for posting in postings_list:
                    posting_doc = {
                        "keyword": posting.keyword,
                        "id": posting.uid,
                        "count": posting["count"]
                    }
                    f.write(json.dumps(posting_doc) + '\n')
                    posting_uids.add(posting.uid)
            
            # Update totals and print batch summary
            total_entities += len(entities)
            total_postings += len(postings_list)
            
            print(f"\n📊 Batch {batch_idx+1} summary:")
            print(f"- 📄 Entities: {len(entities):,}")
            print(f"- 🔑 Postings: {len(postings_list):,}")
            print(f"📈 Running totals: {total_entities:,} entities, {total_postings:,} postings")
            
            # Clean up batch data
            current_batch = None
            df = None
            entities = None
            postings_list = None
            gc.collect()
        
        # Print final processing summary
        print("\n✨ Processing complete!")
        print(f"📄 Total entities generated: {total_entities:,}")
        print(f"🔑 Total postings generated: {total_postings:,}")
        
        # Validate UID consistency between collections
        print("\n🔍 Validating UID consistency between collections...")
        missing_in_postings = entity_uids - posting_uids
        missing_in_entities = posting_uids - entity_uids
        
        if missing_in_postings:
            print(f"⚠️ Warning: {len(missing_in_postings)} UIDs found in entities but not in postings")
            print("Sample of missing UIDs:", list(missing_in_postings)[:5])
        
        if missing_in_entities:
            print(f"⚠️ Warning: {len(missing_in_entities)} UIDs found in postings but not in entities")
            print("Sample of missing UIDs:", list(missing_in_entities)[:5])
        
        if not missing_in_postings and not missing_in_entities:
            print("✅ All UIDs match between entities and postings collections")
        
    finally:
        spark.stop()

if __name__ == "__main__":
    main() 