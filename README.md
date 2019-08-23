# Murd
Python Management of Matrix-like Key-Value store memories across disparate backends.

## Memory Backends

* [JSON String](#json-string)
* [Local Files](#local-files)
* [S3](#s3)
* [AWS DynamoDB Table](#dynamodb)

# Murd Operation

## Murd Memory

A Murd Memory object is made up of at least a "ROW" and "COL" element. These two elements together are treated as a unique identifier for the storage location of the element. Taken together, ideal candidates for the value of 'ROW' and 'COL' are URIs, UUIDs, UTC timestamps, GPS coordinates, and the like.
```
{
    "ROW":{part of unique identifier},
    "COL":{part of unique identifier},
    "{ARBITRARY_KEY}": "{ARBITRARY_VALUE}"
    ...
}
```

## Memory Interface

### update

Update an existing item or create a new item in memory. Existing Murd Memories use an outer join to merge with new data.

### read

Recover a number of Murd Memories

### delete

Drop a number of Murd Memories

## Memory Backends

### JSON String
The    N string backend operates on a single  urd    N object kept in memory. 

### Local Files

The Local Files backend operates on a series of files containing JSON strings.

### S3

The S3 backend operates on a S3 bucket or S3 bucket path containing any number of child S3 bucket paths containing JSON strings.

### DynamoDB

The DynamoDB backend operates on a number of DynamoDB tables containing rows of JSON strings.
