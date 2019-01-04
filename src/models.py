from datetime import date
from marshmallow import Schema, fields, post_load, EXCLUDE
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


search_hit_category = Table('search_hit_category', Base.metadata,
                            Column('search_hit_id', Integer, ForeignKey('search_hit.id')),
                            Column('category_term', String, ForeignKey('category.term'))
                            )

search_hit_commodity = Table('search_hit_commodity', Base.metadata,
                             Column('search_hit_id', Integer, ForeignKey('search_hit.id')),
                             Column('commodity_term', String, ForeignKey('commodity.term'))
                             )

search_hit_type = Table('search_hit_type', Base.metadata,
                        Column('search_hit_id', Integer, ForeignKey('search_hit.id')),
                        Column('type_term', String, ForeignKey('type.term'))
                        )

search_hit_origin = Table('search_hit_origin', Base.metadata,
                          Column('search_hit_id', Integer, ForeignKey('search_hit.id')),
                          Column('origin_term', String, ForeignKey('origin.term'))
                          )


def get_or_create(session, model, term=None):
    instance = session.query(model).filter(model.term == term).first()
    if instance:
        return instance
    else:
        instance = model(Term=term)
        session.add(instance)
        session.commit()
        return instance


class BaseMixin:
    def __init__(self, Term=None, **kwargs):
        self.term = Term

    def __repr__(self):
        return '<%s>' % self.term

    term = Column(String, primary_key=True, nullable=False)


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    Term = fields.Str()
    SubFilters = fields.Nested('self', many=True, allow_none=True)

    @post_load
    def make_object(self, data):
        return self.__model__(**data)


class Category(BaseMixin, Base):
    __tablename__ = 'category'

    search_hits = relationship("SearchHit", secondary=search_hit_category, back_populates="categories")


class CategorySchema(BaseSchema):
    __model__ = Category


class Commodity(BaseMixin, Base):
    __tablename__ = 'commodity'

    search_hits = relationship("SearchHit", secondary=search_hit_commodity, back_populates="commodities")


class CommoditySchema(BaseSchema):
    __model__ = Commodity


class Type(BaseMixin, Base):
    __tablename__ = 'type'

    search_hits = relationship("SearchHit", secondary=search_hit_type, back_populates="types")


class TypeSchema(BaseSchema):
    __model__ = Type


class Origin(BaseMixin, Base):
    __tablename__ = 'origin'

    search_hits = relationship("SearchHit", secondary=search_hit_origin, back_populates="origins")


class OriginSchema(BaseSchema):
    __model__ = Origin


class PreparationTime(BaseMixin, Base):
    __tablename__ = 'preparation_time'


class PreparationTimeSchema(BaseSchema):
    __model__ = PreparationTime


class Difficulty(BaseMixin, Base):
    __tablename__ = 'difficulty'


class DifficultySchema(BaseSchema):
    __model__ = Difficulty


class SearchHit(Base):
    def __init__(self, **kwargs):
        self.id = kwargs.get('ContentId')
        self.name = kwargs.get('Name')
        self.url = 'https://www.matprat.no' + kwargs.get('Url')
        self.image_url = kwargs.get('ImageUrl')
        self.difficulty_term = kwargs.get('Difficulty').lower()
        self.preparation_time_term = kwargs.get('PreparationTime').lower()
        self.receipe_categories = kwargs.get('RecipeCategories')
        self.receipe_commodities = kwargs.get('RecipeCommodities')
        self.receipe_types = kwargs.get('RecipeFoodTypes')
        self.receipe_origins = kwargs.get('RecipeContinents')

    def process_relationships(self, session):
        self.difficulty = get_or_create(session, Difficulty, term=self.difficulty_term)
        self.preparation_time = get_or_create(session, PreparationTime, term=self.preparation_time_term)
        print('processing', self.name)
        for category in self.receipe_categories:
            result = get_or_create(session, Category, term=category.lower())
            self.categories.append(result)
        for commodity in self.receipe_commodities:
            result = get_or_create(session, Commodity, term=commodity.lower())
            self.commodities.append(result)
        for typ in self.receipe_types:
            result = get_or_create(session, Type, term=typ.lower())
            self.types.append(result)
        for origin in self.receipe_origins:
            result = get_or_create(session, Origin, term=origin.lower())
            self.origins.append(result)
        session.commit()

    def __repr__(self):
        return '<%s>' % self.name

    __tablename__ = 'search_hit'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    difficulty_term = Column(String, ForeignKey("difficulty.term"), nullable=False)
    preparation_time_term = Column(String, ForeignKey("preparation_time.term"), nullable=False)

    difficulty = relationship("Difficulty")
    preparation_time = relationship("PreparationTime")
    categories = relationship("Category", secondary=search_hit_category, back_populates="search_hits")
    commodities = relationship("Commodity", secondary=search_hit_commodity, back_populates="search_hits")
    types = relationship("Type", secondary=search_hit_type, back_populates="search_hits")
    origins = relationship("Origin", secondary=search_hit_origin, back_populates="search_hits")


class SearchHitSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    __model__ = SearchHit

    ContentId = fields.Int()
    Name = fields.Str()
    Url = fields.Str()
    ImageUrl = fields.Str()
    Difficulty = fields.Str()
    PreparationTime = fields.Str()
    RecipeCategories = fields.List(fields.Str())
    RecipeCommodities = fields.List(fields.Str())
    RecipeFoodTypes = fields.List(fields.Str())
    RecipeContinents = fields.List(fields.Str())

    @post_load
    def make_object(self, data):
        return self.__model__(**data)


class ResultSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    SearchHits = fields.List(fields.Nested(SearchHitSchema))
    Categories = fields.List(fields.Nested(CategorySchema))
    Commodities = fields.List(fields.Nested(CommoditySchema))
    Types = fields.List(fields.Nested(TypeSchema))
    Origins = fields.List(fields.Nested(OriginSchema))
    PerparationTime = fields.List(fields.Nested(PreparationTimeSchema))  # type-o in api
    Difficulty = fields.List(fields.Nested(DifficultySchema))
    TotalHits = fields.Int()
