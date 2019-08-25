from flask import current_app


# DB => Databases => Tables => Columns/Rows
# Elasticsearch => Indices => Types => Docs and Properties
#   Indices = databases
#   Types = tables
#   Documents = rows
#   Properties = col


##
# @name: add_to_index()
# @para: index, model
#   index:
#   model: SQLAlchemy model/table
# @desc: searches through a model's '__searchable__' attribute to build a document and inserted
#   into an index.
##
def add_to_index(index, model):
    # if Elasticsearch isn't configured, searching is disabled without errors.
    if not current_app.elasticsearch:
        return
    payload = {}

    # payload's 'field' value is the model's field value
    for field in model.__searchable__:
        payload[field] = getattr(model, field)

    # index into elasticsearch using index, model's primary id, and created payload.
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)


##
# @name: remove_from_index()
# @para: index, model
# @desc: delete index from elastidsearch using model's primary id and index
##
def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


##
# @name: query_index()
# @para: index, query, page, per_page
#   index: model name
#   query: body to look for
#   page: which page number
#   per_page: items per page
# @desc: searches index (model name) and uses elasticsearch to search indices for the 'query'
##
def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    # 'body' includes pagination and the query.
    # 'from' and 'size' control what subset of the result set needs to be returned.
    # multi_match is used to search multiple fields, field is set to '*' to search all fields
    search = current_app.elasticsearch.search(
        index=index,
        body={'query':
                  {'multi_match':
                       {'query': query,
                        'fields': ['*']}},
              'from': (page - 1) * per_page,
              'size': per_page})

    # uses Python list comprehension to extract 'id' values from the larger elasticsearch results
    #  ids = for 'hit' in 'search:
    #           if 'int(hit['_id'])'
    ids = [int(hit['_id']) for hit in search['hits']['hits']]

    # id: elements from search results
    # search: total number of results
    return ids, search['hits']['total']['value']