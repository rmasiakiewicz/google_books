# google_books
Webapp + api builded with flask, bootstrap and sqlalchemy
## HEROKU APP URL
https://google-books-rm.herokuapp.com/

## APPLICATION
List of books imported from google API https://developers.google.com/books/docs/v1/using#WorkingVolumes

You can filter records by title, authors, publication date and language

New books can be added in two ways:
- import from google via https://google-books-rm.herokuapp.com/books/import by providing query string
- manually via https://google-books-rm.herokuapp.com/book/add (fields are validated)

You can edit single book by clicking on "gid" field.

## API
You can download list of books in json response by using API endpoint

https://google-books-rm.herokuapp.com//v1/books

Available query parameters:
1. Filtering data:
    - title
    - author
    - from_date ( format YYYY-MM-DD )
    - to_date ( format YYYY-MM-DD )
    - language
    

2. Pagination:
    - page - page number
    - per_page - items per page, default 20
    

Sample query: GET https://google-books-rm.herokuapp.com/v1/books?title=masiakiewicz&author=kowalski

Response
```javascript
{
  "error": false, 
  "items": [
    {
      "authors": [
        {
          "name": "Rafa\u0142 Masiakiewicz"
        }, 
        {
          "name": "Jan Kowalski"
        }
      ], 
      "gid": "9876abc", 
      "image_link": "", 
      "isbn_10": "3333333333", 
      "isbn_13": "2222222222222", 
      "language": "pl", 
      "number_of_pages": 100, 
      "publication_date": "Tue, 12 Dec 2000 00:00:00 GMT", 
      "title": "rafal masiakiewicz"
    }
  ], 
  "message": "ok", 
  "total_items": 1
}
```
API response fields:
- error: True or False
- items: list of book's jsons
- message: server message
- total_items: number of items which can be found using provided query parameters
## HOW TO RUN LOCAL VERSION

1. Download repository
2. Install dependencies from requirements.txt
3. Update `.flaskenv` `SQLALCHEMY_DATABASE_URI` with your postgress url
5. Type flask run (from root repo directory)

No need to provide yor own database. I put

###LINTER AND FORMATTER
- linter on demand - sh scripts/pre-push.sh
- formatter - sh scripts/format_code.sh
###PRE-PUSH LINTER
1. run script sh scripts/install_hooks.sh
2. then make sure that .git/hooks/pre-push is executable (chmod +x)

## UNIT TESTS
I just wrote some basic unit test.
To perform tests first Update SQLALCHEMY_DATABASE_URI in config.py for TestConfig class with another postgress url
and then execute run_tests.sh script from scripts directory