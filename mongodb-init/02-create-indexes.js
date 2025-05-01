// MongoDB script to create indexes after data import
// This runs second due to 02 prefix

// Wait for MongoDB to be fully ready
print("Waiting for MongoDB to be fully ready...");
sleep(3000); // Wait a bit longer after import to ensure collections are ready

// Function to safely check if a collection exists and create an index if it doesn't already exist
function createIndexIfNeeded(db, collectionName, indexField, indexName) {
    // List all collections to check if our target exists
    let collections = db.getCollectionNames();
    if (!collections.includes(collectionName)) {
        print(`Collection ${collectionName} does not exist yet. Waiting 5 seconds...`);
        sleep(5000);
        
        // Check again after waiting
        collections = db.getCollectionNames();
        if (!collections.includes(collectionName)) {
            print(`Collection ${collectionName} still does not exist. Cannot create index.`);
            return false;
        }
    }
    
    try {
        // First check if the index already exists
        let existingIndexes = db[collectionName].getIndexes();
        let indexExists = false;
        
        for (let i = 0; i < existingIndexes.length; i++) {
            if (existingIndexes[i].name === indexName) {
                print(`Index ${indexName} already exists on ${collectionName}. Skipping creation.`);
                indexExists = true;
                break;
            }
        }
        
        if (!indexExists) {
            print(`Creating index on ${collectionName}.${indexField}...`);
            let indexSpec = {};
            indexSpec[indexField] = 1;
            
            db[collectionName].createIndex(
                indexSpec, 
                { background: true, name: indexName }
            );
            print(`Successfully created index ${indexName} on ${collectionName}.${indexField}`);
        }
        
        return true;
    } catch (error) {
        print(`Error with index on ${collectionName}.${indexField}: ${error.message}`);
        return false;
    }
}

// Switch to the lawpy database
db = db.getSiblingDB('lawpy');
print("Connected to database: lawpy");

// Create the required indexes
let results = {
    keyword_postings_keyword: createIndexIfNeeded(
        db, 
        "keyword_postings", 
        "keyword", 
        "keyword_idx"
    ),
    
    document_entities_id: createIndexIfNeeded(
        db, 
        "document_entities", 
        "id", 
        "id_idx"
    )
};

// Verify created indexes
print("\nVerifying created indexes:");

// Check keyword_postings indexes
try {
    print("\nIndexes in keyword_postings:");
    db.keyword_postings.getIndexes().forEach(idx => {
        print(`- ${idx.name}: ${JSON.stringify(idx.key)}`);
    });
} catch (error) {
    print("Could not verify keyword_postings indexes: " + error.message);
}

// Check document_entities indexes
try {
    print("\nIndexes in document_entities:");
    db.document_entities.getIndexes().forEach(idx => {
        print(`- ${idx.name}: ${JSON.stringify(idx.key)}`);
    });
} catch (error) {
    print("Could not verify document_entities indexes: " + error.message);
}

print("\nIndex creation script completed");
print("Results summary:");
print(`- keyword_postings.keyword index: ${results.keyword_postings_keyword ? "Verified" : "Failed"}`);
print(`- document_entities.id index: ${results.document_entities_id ? "Verified" : "Failed"}`); 