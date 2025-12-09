from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class KnowledgeBaseCategory(Base):
    __tablename__ = "knowledge_base_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    icon = Column(String(50))
    parent_id = Column(Integer, ForeignKey('knowledge_base_categories.id'))
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    parent = relationship("KnowledgeBaseCategory", remote_side=[id], backref="children")
    articles = relationship("KnowledgeBaseArticle", back_populates="category")


class KnowledgeBaseArticle(Base):
    __tablename__ = "knowledge_base_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey('knowledge_base_categories.id'))
    author_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'))
    tags = Column(JSON, default=[])  # Array of tag strings
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    rating = Column(String(10), default='0')  # Store as string or use Numeric
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])
    department = relationship("Department", foreign_keys=[department_id])
    category = relationship("KnowledgeBaseCategory", back_populates="articles")
    attachments = relationship("KnowledgeBaseAttachment", back_populates="article", cascade="all, delete-orphan")


class KnowledgeBaseAttachment(Base):
    __tablename__ = "knowledge_base_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey('knowledge_base_articles.id', ondelete='CASCADE'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_url = Column(Text, nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    cloudinary_public_id = Column(String(255))
    uploaded_by = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    article = relationship("KnowledgeBaseArticle", back_populates="attachments")
