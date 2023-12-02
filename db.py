from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """
    User Model
    """
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    auctions = db.relationship("Auction", cascade="delete")
    bids = db.relationship("Bid", cascade="delete")

    def __init__(self, **kwargs):
        """
        Initialize a User object
        """
        self.username = kwargs.get("username", "")
        self.password = kwargs.get("password", "")

    def serialize(self):
        """
        Serialize a User object
        """
        return {
            "id": self.id,
            "username": self.username,
            "auctions": [auction.id for auction in self.auctions],
            "bids": [bid.id for bid in self.bids],
        }
    
    def verify_credentials(self, password):
        """
        Verify the credentials of a user
        """
        return self.password == password
    
class Auction(db.Model):
    """
    Auction Model
    """
    __tablename__ = "auction"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    starting_bid = db.Column(db.Integer, nullable=False)
    highest_bid = db.Column(db.Integer)
    status = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    bids = db.relationship("Bid", cascade="delete")

    def __init__(self, **kwargs):
        """
        Initialize an Auction object
        """
        self.title = kwargs.get("title", "")
        self.date = kwargs.get("date", "")
        self.starting_bid = kwargs.get("starting_bid", 0)
        self.highest_bid = kwargs.get("highest_bid", 0)
        self.description = kwargs.get("description", "")
        self.status = True
        self.user_id = kwargs.get("user_id")

    def serialize(self, short=False):
        """
        Serialize an Auction object
        """
        if short:
            return {
                "id": self.id,
                "title": self.title,
                "seller": self.user_id,
                "status": self.status,
            }
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date,
            "description": self.description,
            "starting_bid": self.starting_bid,
            "highest_bid": self.highest_bid,
            "seller": self.user_id,
            "status": self.status,
            "bids": [bid.id for bid in self.bids],
        }
    
    def update_highest_bid(self, bid_amount):
        """
        Update the highest bid for the auction
        """
        if self.highest_bid is None or bid_amount > self.highest_bid:
            self.highest_bid = bid_amount
            db.session.commit()

class Bid(db.Model):
    """
    Bid Model
    """
    __tablename__ = "bid"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Integer, nullable=False)
    accepted = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    auction_id = db.Column(db.Integer, db.ForeignKey("auction.id"), nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize a Bid object
        """
        self.amount = kwargs.get("amount", 0)
        self.accepted = False
        self.user_id = kwargs.get("user_id")
        self.auction_id = kwargs.get("auction_id")

    def serialize(self, short=False):
        """
        Serialize a Bid object
        """
        if short:
            return {
                "id": self.id,
                "amount": self.amount,
                "accepted": self.accepted,
            }
        return {
            "id": self.id,
            "amount": self.amount,
            "accepted": self.accepted,
            "bidder": self.user_id,
            "auction": self.user_id,
        }