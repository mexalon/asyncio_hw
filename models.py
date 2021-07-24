import asyncio

import sqlalchemy as sq
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Char(Base):
    __tablename__ = 'character'

    id = sq.Column(sq.Integer, primary_key=True)
    birth_year = sq.Column(sq.String)
    eye_color = sq.Column(sq.String)
    films = sq.Column(sq.String)
    gender = sq.Column(sq.String)
    hair_color = sq.Column(sq.String)
    height = sq.Column(sq.Integer)
    homeworld = sq.Column(sq.String)
    mass = sq.Column(sq.Integer)
    name = sq.Column(sq.String)
    skin_color = sq.Column(sq.String)
    species = sq.Column(sq.String)
    starships = sq.Column(sq.String)
    vehicles = sq.Column(sq.String)

    def __str__(self):
        return f"{self.id} - {self.name}"

    def __repr__(self):
        return self.__str__()
