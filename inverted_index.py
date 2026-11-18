#-------------------------------------------------------------------------
# AUTHOR: Thuy An Nguyen
# FILENAME: inverted_index.py
# SPECIFICATION: Implementation of an inverted index for document retrieval
# FOR: CS 4250 - Assignment #3
# TIME SPENT: start 9:00pm
#-------------------------------------------------------------------------

# Importing Python libraries
from pymongo import MongoClient

# Connecting to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Accessing the database and collections
db = client["assignment3"]
documents = db["documents"]
inverted_index = db["inverted_index"]


#-------------------------------------------------------------------------
# FUNCTION: getTermFrequencies
# SPECIFICATION: receives a text and returns the frequency of each term
#-------------------------------------------------------------------------
def getTermFrequencies(text):

    # Converting text to lowercase
    # --> add your Python code here
    text = text.lower()


    # Removing punctuation
    # --> add your Python code here
    punctuation = "!@#$%^&*()-+"
    for p in punctuation:
        text = text.replace(p, "")

    # Splitting the text into terms
    # --> add your Python code here
    terms = text.split()


    # Returning the term frequencies
    # --> add your Python code here
    term_frequencies = {}
    for term in terms:
        term_frequencies[term] = term_frequencies.get(term, 0) + 1

    return term_frequencies



#-------------------------------------------------------------------------
# FUNCTION: addPosting
# SPECIFICATION: adds a posting to an existing term or creates a new term
#-------------------------------------------------------------------------
def addPosting(term, docId, tf):

    # Searching for the term in the inverted index
    # --> add your Python code here
    existing_term = inverted_index.find_one({"term": term})

    # Creating a new term if it does not exist
    # --> add your Python code here
    if not existing_term:
        inverted_index.insert_one({
            "term": term,
            "postings": []
        })

    # Adding a posting if the term already exists
    # --> add your Python code here
    inverted_index.update_one(
        {"term": term},
        {"$push": {"postings": {"docId": docId, "tf": tf}}}
    )



#-------------------------------------------------------------------------
# FUNCTION: removePosting
# SPECIFICATION: removes a document posting from a term and deletes the
#                term if its postings list becomes empty
#-------------------------------------------------------------------------
def removePosting(term, docId):

    # Removing the posting from the term
    # --> add your Python code here
    inverted_index.update_one(
        {"term": term},
        {"$pull": {"postings": {"docId": docId}}}
    )


    # Retrieving the term after removing the posting
    # --> add your Python code here
    updated_term = inverted_index.find_one({"term": term})


    # Deleting the term if its postings list is empty
    # --> add your Python code here
    if updated_term and not updated_term["postings"]:
        inverted_index.delete_one({"term": term})


#-------------------------------------------------------------------------
# FUNCTION: insertDocument
# SPECIFICATION: inserts a document and updates the inverted index
#-------------------------------------------------------------------------
def insertDocument(document):

    # Inserting the document into the documents collection
    # --> add your Python code here
    documents.insert_one(document)


    # Obtaining the term frequencies
    # --> add your Python code here
    term_frequencies = getTermFrequencies(document["text"])


    # Updating the inverted index
    # --> add your Python code here
    for term, tf in term_frequencies.items():
        addPosting(term, document["_id"], tf)



#-------------------------------------------------------------------------
# FUNCTION: updateDocument
# SPECIFICATION: updates a document and makes the corresponding changes
#                to the inverted index
#-------------------------------------------------------------------------
def updateDocument(docId, newText):

    # Retrieving the current document
    # --> add your Python code here
    current_document = documents.find_one({"_id": docId})


    # Obtaining the old and new term frequencies
    # --> add your Python code here
    old_term_frequencies = getTermFrequencies(current_document["text"])
    new_term_frequencies = getTermFrequencies(newText)


    # Processing terms that existed in the old document
    # --> add your Python code here
    for term, tf in old_term_frequencies.items():
        if term in new_term_frequencies:
            # If the term exists, update its posting
            inverted_index.update_one(
                {"term": term, "postings.docId": docId},
                {"$set": {"postings.$.tf": new_term_frequencies[term]}}
            )
        else:
            # If the term no longer exists, remove its posting
            removePosting(term, docId)


    # Processing terms that occur only in the new document
    # --> add your Python code here
    for term, tf in new_term_frequencies.items():
        if term not in old_term_frequencies:
            addPosting(term, docId, tf)


    # Updating the document text
    # --> add your Python code here
    documents.update_one({"_id": docId}, {"$set": {"text": newText}})


#-------------------------------------------------------------------------
# FUNCTION: deleteDocument
# SPECIFICATION: deletes a document and removes all of its postings from
#                the inverted index
#-------------------------------------------------------------------------
def deleteDocument(docId):

    # Retrieving the document before deleting it
    # --> add your Python code here
    deleted_document = documents.find_one({"_id": docId})


    # Obtaining the terms contained in the document
    # --> add your Python code here
    deleted_term_frequencies = getTermFrequencies(deleted_document["text"])


    # Removing the document from every corresponding posting list
    # --> add your Python code here
    for term, tf in deleted_term_frequencies.items():
        removePosting(term, docId)


    # Deleting the document
    # --> add your Python code here
    documents.delete_one({"_id": docId})



#-------------------------------------------------------------------------
# Executing the sequence of operations
#-------------------------------------------------------------------------

# Operation 1: document 1 is obtained
document1 = {
    "_id": 1,
    "text": "Summer rain is common in Florida."
}

insertDocument(document1)


# Operation 2: document 2 is obtained
document2 = {
    "_id": 2,
    "text": "Summer is hot in Arizona."
}

insertDocument(document2)


# Operation 3: document 1 is updated
updateDocument(
    1,
    "Summer rain is hot rain in Florida."
)


# Operation 4: document 3 is obtained
document3 = {
    "_id": 3,
    "text": "Hot summer rain in California."
}

insertDocument(document3)


# Operation 5: document 2 is deleted
deleteDocument(2)

# Operation 6: print the content of the documents and inverted_index collections
# --> add your Python code here
print("Documents:")
for doc in documents.find():
    print(doc)

print("\nInverted Index:")
for entry in inverted_index.find():
    print(entry)