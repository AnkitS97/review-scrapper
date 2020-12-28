from flask import Flask, render_template, request
from urllib.request import urlopen as uReq
from urllib.parse import quote
from bs4 import BeautifulSoup as bs
import requests
from flask_cors import cross_origin, CORS

app = Flask(__name__)
booklist = []
rating_dict = {
    'did not like it': 1,
    'it was ok': 2,
    'liked it': 3,
    'really liked it': 4,
    'it was amazing': 5,
    'No rating': '-'
}
CORS(app)


@app.route('/', methods=['GET'])
@cross_origin()
def home_page():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search_books():
    book = request.form['book']
    search_link = "https://www.goodreads.com/search?query=" + quote(book)
    try:
        uCLient = uReq(search_link)
        search_page = uCLient.read()
        uCLient.close()
        goodreads_html = bs(search_page, "html.parser")
        books = goodreads_html.findAll("tr", {"class": ""})
        booklist.clear()
        for book in books:
            temp = book.findAll("a", {"class": "bookTitle"})[0]
            book_link = temp['href']
            book_name = temp.span.text
            temp = book.findAll("div", {"class": "authorName__container"})
            authors = []
            for author in temp:
                authors.append(author.a.span.text)

            authors = ', '.join(authors)
            temp_dict = {"book_name": book_name, "book_link": book_link, "author": authors}
            booklist.append(temp_dict)
        return render_template('search.html', booklist=booklist)
    except:
        return "something went wrong"


@app.route('/reviews/<book_index>')
def get_reviews(book_index):
    book = booklist[int(book_index) - 1]
    book_link = "https://www.goodreads.com" + book['book_link']
    try:
        book_res = requests.get(book_link)
        book_html = bs(book_res.text, "html.parser")
        review_boxes = book_html.findAll('div', {'class': 'friendReviews elementListBrown'})
        reviews = []

        for review in review_boxes:
            try:
                name = review.div.div.div.div.span.text
            except:
                name = 'Unknown'

            try:
                rating = review.div.div.findAll('span', {'class': 'staticStars notranslate'})[0]['title']
            except:
                rating = 'No rating'

            try:
                content = review.div.div.div.findAll('div', {'class': 'reviewText stacked'})[0].span.contents
                if len(content) > 3:
                    comment = content[3].text
                else:
                    comment = content[1].text
            except:
                comment = 'No comment'

            temp_dict = {'book_name': book['book_name'], 'name': name, 'rating': rating_dict[rating], 'comment': comment}
            reviews.append(temp_dict)

        return render_template('result.html', reviews=reviews)
    except:
        return "No reviews available"


if __name__ == '__main__':
    app.run(port=8000, debug=True)
