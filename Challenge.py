from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, func
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Defining SQLAlchemy models
class Restaurant(Base):
    __tablename__ = 'restaurants'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    
    # Defining the relationship between Restaurant & Review. One to many
    reviews = relationship('Review', back_populates='restaurant')
    customers = relationship('Customer', secondary='reviews', back_populates='restaurants')

    @classmethod
    def fanciest(cls, session):
        # Sorting restaurannt by price
        return session.query(cls).order_by(cls.price.desc()).first()

    def all_reviews(self):
        # Reviews for the restaurant
        review_strings = []
        for review in self.reviews:
            review_strings.append(review.full_review())
        return review_strings

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    
    # Defining the relationship between Customer and Review
    reviews = relationship('Review', back_populates='customer')
    restaurants = relationship('Restaurant', secondary='reviews', back_populates='customers')

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def favorite_restaurant(self):
        highest_rated_restaurant = max(self.reviews, key=lambda review: review.star_rating)
        return highest_rated_restaurant.restaurant

    def add_review(self, restaurant, rating):
        review = Review(customer=self, restaurant=restaurant, star_rating=rating)
        session.add(review)
        session.commit()

    def delete_reviews(self, restaurant):
        reviews_to_delete = [review for review in self.reviews if review.restaurant == restaurant]
        for review in reviews_to_delete:
            session.delete(review)
        session.commit()

    def reviews(self):
        return self.reviews

    def restaurants(self):
        return self.restaurants

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    star_rating = Column(Integer)
    
    customer_id = Column(Integer, ForeignKey('customers.id'))
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    
    customer = relationship('Customer', back_populates='reviews')
    restaurant = relationship('Restaurant', back_populates='reviews')

    def full_review(self):
        return f"Review for {self.restaurant.name} by {self.customer.full_name()}: {self.star_rating} stars."

engine = create_engine('sqlite:///restaurant_reviews.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

if __name__ == '__main__':

    customer1 = Customer(first_name='Gideon', last_name='Mugere', email='gomugere@gmail.com')
    customer2 = Customer(first_name='Cynthia', last_name='Smith', email='cynthiasmith@gmail.com')


    restaurant1 = Restaurant(name='Fish Friendly Restaurant', price=200)
    restaurant2 = Restaurant(name='Berbecue Friendly', price=300)


    review1 = Review(customer=customer1, restaurant=restaurant1, star_rating=4)
    review2 = Review(customer=customer2, restaurant=restaurant1, star_rating=5)

    session.add_all([customer1, customer2, restaurant1, restaurant2, review1, review2])
    session.commit()
