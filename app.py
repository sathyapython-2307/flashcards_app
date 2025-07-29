from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import random

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app)

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    cards = db.relationship('Card', backref='deck', lazy=True)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False)
    correct = db.Column(db.Integer, default=0)
    incorrect = db.Column(db.Integer, default=0)

@app.route('/')
def index():
    decks = Deck.query.all()
    return render_template('index.html', decks=decks)

@app.route('/deck/<int:deck_id>')
def view_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    return render_template('deck.html', deck=deck)

@app.route('/quiz/<int:deck_id>')
def quiz(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    cards = deck.cards
    if not cards:
        return redirect(url_for('view_deck', deck_id=deck_id))
    return render_template('quiz.html', deck=deck)

@app.route('/api/quiz/<int:deck_id>')
def quiz_data(deck_id):
    cards = Card.query.filter_by(deck_id=deck_id).all()
    random.shuffle(cards)
    return jsonify([{
        'id': card.id,
        'question': card.question,
        'answer': card.answer
    } for card in cards])

@app.route('/api/record_answer/<int:card_id>', methods=['POST'])
def record_answer(card_id):
    card = Card.query.get_or_404(card_id)
    is_correct = request.json.get('correct', False)
    if is_correct:
        card.correct += 1
    else:
        card.incorrect += 1
    db.session.commit()
    return jsonify({'success': True})

@app.route('/add_deck', methods=['POST'])
def add_deck():
    name = request.form['name']
    if name:
        deck = Deck(name=name)
        db.session.add(deck)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_card/<int:deck_id>', methods=['POST'])
def add_card(deck_id):
    question = request.form['question']
    answer = request.form['answer']
    if question and answer:
        card = Card(question=question, answer=answer, deck_id=deck_id)
        db.session.add(card)
        db.session.commit()
    return redirect(url_for('view_deck', deck_id=deck_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)