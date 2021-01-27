from flask import Flask, render_template, request, redirect, url_for
from joblib import load
from get_tweets import get_related_tweets


pipeline = load("text_classification.joblib")


def requestResults(name):
    tweets = get_related_tweets(name)
    tweets['prediction'] = pipeline.predict(tweets['tweet_text'])
    data = str(tweets.prediction.value_counts()) + '\n\n'
    return data + str(tweets)


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/', methods=['POST'])
def get_data():
    print('THIS IS THE REQUEST:', request, 'THIS IS THE REQUEST METHOD:', request.method, 'THIS IS THE REQUEST FORM:', request.form['search'])
    if request.method == 'POST': # verify method = POST
        user = request.form['search']

        return redirect(url_for('success', name=user)) # defines redirect url. e.g. success/donald


@app.route('/success/<name>')
def success(name): # defines what to return on redirect url page of results
    return "<xmp>" + str(requestResults(name)) + "what bitch" + " </xmp> "


if __name__ == '__main__' :
    app.run(debug=True)