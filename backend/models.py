from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

db = SQLAlchemy()

# Модели базы данных
class Object(db.Model):
    __tablename__ = 'objects'
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, unique=True, index=True)
    photos = relationship("Photo", back_populates="object")

class Photo(db.Model):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True, index=True)
    object_id = Column(Integer, ForeignKey('objects.id'))
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_path_input = Column(String)
    file_path_output = Column(String)
    recognition_date = Column(DateTime, nullable=True)
    recognized = Column(Boolean, default=False)
    object = relationship("Object", back_populates="photos")
    results = relationship("Result", back_populates="photo")

class Result(db.Model):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(Integer, ForeignKey('photos.id'))
    recognized_class = Column(String)
    photo = relationship("Photo", back_populates="results")

class MisclassifiedPhoto(db.Model):
    __tablename__ = 'misclassified_photos'
    id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(Integer, ForeignKey('photos.id'))
    correct_class = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    x_coord = Column(Integer)
    y_coord = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
