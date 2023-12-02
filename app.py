import json

from flask import Flask, request
from db import db
from db import User
from db import Auction
from db import Bid


app = Flask(__name__)
db_filename = "auctions.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

# -- USER ENDPOINTS -------------------------------------------------------------------------

@app.route("/api/users/", methods=["GET"])
def get_all_users():
    """
    Endpoint for getting all users
    """
    users = User.query.all()
    serialized_users = [user.serialize() for user in users]
    return json.dumps(serialized_users), 200

@app.route("/api/users/<int:user_id>/", methods=["GET"])
def get_user(user_id):
    """
    Endpoint for getting a specific user
    """
    user = User.query.get(user_id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404

    serialized_user = user.serialize()
    return json.dumps(serialized_user), 200

@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a user
    """
    body = request.get_json()
    username = body.get("username")
    password = body.get("password")

    if not username or not password:
        return json.dumps({"error": "Both username and password are required"}), 400
    
    user = User(username=username, password=password)

    if user is None:
        return json.dumps({"error": "User not found"}), 404

    db.session.add(user)
    db.session.commit()

    serialized_user = user.serialize()
    return json.dumps(serialized_user), 201

@app.route("/api/users/<int:user_id>/", methods=["POST"])
def update_user(user_id):
    """
    Endpoint for updating a user
    """
    user = User.query.get(user_id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404

    body = request.get_json()
    user.username = body.get("username")
    user.password = body.get("password")
    db.session.commit()

    serialized_user = user.serialize()
    return json.dumps(serialized_user), 200

@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Endpoint for deleting a user
    """
    user = User.query.get(user_id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    serialized_user = user.serialize()
    return json.dumps(serialized_user), 200

@app.route("/api/login/", methods=["POST"])
def login():
    """
    Endpoint for logging in a user
    """
    try:
        body = request.get_json()
        username = body.get("username")
        password = body.get("password")

        if username is None or password is None:
            return json.dumps({"error":"Invalid body"})
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.verify_credentials(password):
            return json.dumps({"error": "Invalid username or password"}), 401
        
        serialized_user = user.serialize()
        return json.dumps(serialized_user), 200
    except Exception as e:
        return json.dumps({"error": "Internal Server Error"}), 500

# -- AUCTION ENDPOINTS -------------------------------------------------------------------------

@app.route("/api/auctions/", methods=["GET"])
def get_all_auctions():
    """
    Endpoint for getting all auctions
    """
    auctions = Auction.query.all()
    serialized_auctions = [auction.serialize() for auction in auctions]
    return json.dumps(serialized_auctions), 200

@app.route("/api/auctions/<int:auction_id>/", methods=["GET"])
def get_auction(auction_id):
    """
    Endpoint for getting a specific auction
    """
    auction = Auction.query.get(auction_id)
    if auction is None:
        return json.dumps({"error": "Auction not found"}), 404

    serialized_auction = auction.serialize()
    return json.dumps(serialized_auction), 200

@app.route("/api/auctions/<int:user_id>", methods=["POST"])
def create_auction(user_id):
    """
    Endpoint for creating an auction
    """
    body = request.get_json()
    title = body.get("title")
    date = body.get("date")
    starting_bid = body.get("starting_bid")
    description = body.get("description")

    # Description is optional.
    if not title or not date or not starting_bid:
        return json.dumps({"error": "Title, date, and starting_bid are required"}), 400

    if not isinstance(starting_bid, int):
        try:
            starting_bid = int(starting_bid)
        except ValueError:
            return json.dumps({"error": "Starting bid must be a number"}), 400

    auction = Auction(title=title, date=date, starting_bid=starting_bid, description=description, user_id=user_id)
    db.session.add(auction)
    db.session.commit()

    serialized_auction = auction.serialize()
    return json.dumps(serialized_auction), 201

@app.route("/api/auctions/<int:auction_id>/", methods=["POST"])
def update_auction(auction_id):
    """
    Endpoint for updating an auction
    """
    auction = Auction.query.get(auction_id)
    if auction is None:
        return json.dumps({"error": "Auction not found"}), 404

    body = request.get_json()
    auction.title = body.get("title")
    auction.date = body.get("date")
    auction.starting_bid = body.get("starting_bid")
    auction.description = body.get("description")
    auction.status = body.get("status")
    db.session.commit()

    serialized_auction = auction.serialize()
    return json.dumps(serialized_auction), 200

@app.route("/api/auctions/<int:auction_id>/", methods=["DELETE"])
def delete_auction(auction_id):
    """
    Endpoint for deleting an auction
    """
    auction = Auction.query.get(auction_id)
    if auction is None:
        return json.dumps({"error": "Auction not found"}), 404

    db.session.delete(auction)
    db.session.commit()

    serialized_auction = auction.serialize()
    return json.dumps(serialized_auction), 200

@app.route("/api/auctions/user/<int:user_id>/", methods=["GET"])
def get_user_auctions(user_id):
    """
    Endpoint for getting all auctions for a specific user
    """
    user = User.query.get(user_id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404

    user_auctions = Auction.query.filter_by(user_id=user.id).all()
    serialized_auctions = [auction.serialize() for auction in user_auctions]
    
    return json.dumps(serialized_auctions), 200

@app.route("/api/auctions/<int:auction_id>/bids/", methods=["GET"])
def get_auction_bids(auction_id):
    """
    Endpoint for getting all bids for a specific auction
    """
    auction = Auction.query.get(auction_id)
    if auction is None:
        return json.dumps({"error": "Auction not found"}), 404

    auction_bids = Bid.query.filter_by(auction_id=auction.id).all()
    serialized_bids = [bid.serialize() for bid in auction_bids]

    return json.dumps(serialized_bids), 200

# -- BID ENDPOINTS -------------------------------------------------------------------------

@app.route("/api/bids/", methods=["GET"])
def get_all_bids():
    """
    Endpoint for getting all bids
    """
    bids = Bid.query.all()
    serialized_bids = [bid.serialize() for bid in bids]
    return json.dumps(serialized_bids), 200

@app.route("/api/bids/<int:bid_id>/", methods=["GET"])
def get_bid(bid_id):
    """
    Endpoint for getting a specific bid
    """
    bid = Bid.query.get(bid_id)
    if bid is None:
        return json.dumps({"error": "Bid not found"}), 404

    serialized_bid = bid.serialize()
    return json.dumps(serialized_bid), 200

@app.route("/api/bids/<int:auction_id>/", methods=["POST"])
def create_bid(auction_id):
    """
    Endpoint for creating a bid
    """
    body = request.get_json()
    amount = body.get("amount")
    user_id = body.get("user_id")

    if not amount or not user_id:
        return json.dumps({"error": "Amount and user_id are required"}), 400

    auction = Auction.query.get(auction_id)
    if auction is None:
        return json.dumps({"error": "Auction not found"}), 404

    bid = Bid(amount=amount, user_id=user_id, auction_id=auction_id)
    db.session.add(bid)

    auction.update_highest_bid(amount)
    db.session.commit()
    serialized_bid = bid.serialize()

    return json.dumps(serialized_bid), 201

@app.route("/api/bids/<int:bid_id>/", methods=["DELETE"])
def delete_bid(bid_id):
    """
    Endpoint for deleting a bid
    """
    bid = Bid.query.get(bid_id)
    if bid is None:
        return json.dumps({"error": "Bid not found"}), 404

    db.session.delete(bid)
    db.session.commit()

    serialized_bid = bid.serialize()

    return json.dumps(serialized_bid), 200

@app.route("/api/bids/users/<int:user_id>/", methods=["GET"])
def get_user_bids(user_id):
    """
    Endpoint for getting all bids made by a specific user
    """
    user = User.query.get(user_id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404

    user_bids = Bid.query.filter_by(user_id=user.id).all()
    serialized_bids = [bid.serialize() for bid in user_bids]

    return json.dumps(serialized_bids), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)