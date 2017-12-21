
# configuration code (I)
import sys
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Numeric, Boolean
#import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

## additional enums
#class Nutriment(enum.Enum):
#	proteins = 1		# meat, fish, eggs, dairy
#	carbohydrates = 2	# cereals and derivates, legumes
#	fat = 3
#	salts = 4
#	vitamins = 5		# Fruits, vegetables

# class code and mapper code
class Recipe(Base):
	__tablename__ = 'recipe'
	id = Column(
		Integer,
		primary_key = True)
	name = Column(
		String(64),
		nullable = False)
	time = Column(
		Integer)
	description = Column(
		String(512))
	video = Column(
		String(128))	# location to the video within the server

class Aliment(Base):
	__tablename__ = 'aliment'
	id = Column(
		Integer,
		primary_key = True)
	name = Column(
		String(32),
		nullable = False)
	nutriment = Column(
		String(16))					#enum.Enum(Nutriment))
	#these following might be added into a new table: 
	# aliment_id | restriction
	# -----------|------------
	#         12 | vegetarian
	#         12 | vegan
	#         28 | dairy
	#dairy = Column(
	#	Boolean)
	#vegetarian = Column(
	#	Boolean)
	#vegan = Column(
	#	Boolean)
		
class Ingredient(Base):
	__tablename__ = 'ingredient'
	id = Column(
		Integer,
		primary_key = True)
	recipe_id = Column(
		Integer, ForeignKey('recipe.id'))
	aliment_id = Column(
		Integer, ForeignKey('aliment.id'))
	amount = Column(
		Numeric(10,2))
	units = Column(		# create Enum??
		String(16))		# kg, kilograms, litres, teaspoons, units ...
	recipe = relationship(Recipe)
	aliment = relationship(Aliment)
	
# configuration code (II)
engine = create_engine('sqlite:///mamarecipes.db')
Base.metadata.create_all(engine)