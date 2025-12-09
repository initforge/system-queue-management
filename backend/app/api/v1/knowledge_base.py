"""
Knowledge Base API endpoints
Handles article management, categories, search, and file uploads
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from typing import List, Optional
from pydantic import BaseModel
import re
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, KnowledgeBaseArticle, KnowledgeBaseCategory, KnowledgeBaseAttachment, Department
from app.services.cloudinary_service import cloudinary_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic models
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    display_order: int = 0

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    icon: Optional[str]
    parent_id: Optional[int]
    display_order: int
    is_active: bool
    
    class Config:
        from_attributes = True

class ArticleCreate(BaseModel):
    title: str
    content: str
    category_id: Optional[int] = None
    department_id: Optional[int] = None
    tags: Optional[List[str]] = []
    is_published: bool = False
    is_featured: bool = False

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    department_id: Optional[int] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None

class ArticleResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    category_id: Optional[int]
    category_name: Optional[str]
    author_id: int
    author_name: str
    department_id: Optional[int]
    department_name: Optional[str]
    tags: List[str]
    is_published: bool
    is_featured: bool
    view_count: int
    rating: float
    created_at: str
    updated_at: str
    published_at: Optional[str]
    attachments: List[dict] = []
    
    class Config:
        from_attributes = True

def slugify(text: str) -> str:
    """Generate URL-friendly slug from text"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text

# Category Endpoints
@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """Get all knowledge base categories"""
    try:
        query = db.query(KnowledgeBaseCategory)
        if not include_inactive:
            query = query.filter(KnowledgeBaseCategory.is_active == True)
        
        categories = query.order_by(KnowledgeBaseCategory.display_order, KnowledgeBaseCategory.name).all()
        return categories
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving categories"
        )

@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new category (Manager/Admin only)"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers and admins can create categories"
        )
    
    try:
        slug = slugify(category_data.name)
        
        # Check if slug exists
        existing = db.query(KnowledgeBaseCategory).filter(KnowledgeBaseCategory.slug == slug).first()
        if existing:
            slug = f"{slug}-{db.query(KnowledgeBaseCategory).count() + 1}"
        
        category = KnowledgeBaseCategory(
            name=category_data.name,
            slug=slug,
            description=category_data.description,
            icon=category_data.icon,
            parent_id=category_data.parent_id,
            display_order=category_data.display_order
        )
        
        db.add(category)
        db.commit()
        db.refresh(category)
        
        return category
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating category"
        )

# Article Endpoints
@router.get("/articles", response_model=List[ArticleResponse])
async def get_articles(
    category_id: Optional[int] = None,
    department_id: Optional[int] = None,
    published_only: bool = True,
    featured: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get articles with filters"""
    try:
        query = db.query(KnowledgeBaseArticle)
        
        # For non-managers, only show published articles
        if current_user and current_user.role not in ['manager', 'admin']:
            published_only = True
        
        if published_only:
            query = query.filter(KnowledgeBaseArticle.is_published == True)
        
        if category_id:
            query = query.filter(KnowledgeBaseArticle.category_id == category_id)
        
        if department_id:
            query = query.filter(
                or_(
                    KnowledgeBaseArticle.department_id == department_id,
                    KnowledgeBaseArticle.department_id.is_(None)  # Global articles
                )
            )
        
        if featured is not None:
            query = query.filter(KnowledgeBaseArticle.is_featured == featured)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    KnowledgeBaseArticle.title.ilike(search_term),
                    KnowledgeBaseArticle.content.ilike(search_term)
                )
            )
        
        articles = query.order_by(desc(KnowledgeBaseArticle.is_featured), desc(KnowledgeBaseArticle.created_at)).offset(offset).limit(limit).all()
        
        # Format response
        result = []
        for article in articles:
            attachments = db.query(KnowledgeBaseAttachment).filter(
                KnowledgeBaseAttachment.article_id == article.id
            ).all()
            
            result.append({
                "id": article.id,
                "title": article.title,
                "slug": article.slug,
                "content": article.content,
                "category_id": article.category_id,
                "category_name": article.category.name if article.category else None,
                "author_id": article.author_id,
                "author_name": article.author.full_name if article.author else None,
                "department_id": article.department_id,
                "department_name": article.department.name if article.department else None,
                "tags": article.tags or [],
                "is_published": article.is_published,
                "is_featured": article.is_featured,
                "view_count": article.view_count,
                "rating": float(article.rating) if article.rating else 0.0,
                "created_at": article.created_at.isoformat() if article.created_at else None,
                "updated_at": article.updated_at.isoformat() if article.updated_at else None,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "attachments": [
                    {
                        "id": att.id,
                        "file_name": att.file_name,
                        "file_url": att.file_url,
                        "file_type": att.file_type,
                        "file_size": att.file_size
                    }
                    for att in attachments
                ]
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting articles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving articles"
        )

@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get article by ID and increment view count"""
    try:
        article = db.query(KnowledgeBaseArticle).filter(KnowledgeBaseArticle.id == article_id).first()
        
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        # Check if user can view (must be published for non-managers)
        if current_user and current_user.role not in ['manager', 'admin']:
            if not article.is_published:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Article is not published"
                )
        
        # Increment view count
        article.view_count = (article.view_count or 0) + 1
        db.commit()
        
        # Get attachments
        attachments = db.query(KnowledgeBaseAttachment).filter(
            KnowledgeBaseAttachment.article_id == article.id
        ).all()
        
        return {
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "content": article.content,
            "category_id": article.category_id,
            "category_name": article.category.name if article.category else None,
            "author_id": article.author_id,
            "author_name": article.author.full_name if article.author else None,
            "department_id": article.department_id,
            "department_name": article.department.name if article.department else None,
            "tags": article.tags or [],
            "is_published": article.is_published,
            "is_featured": article.is_featured,
            "view_count": article.view_count,
            "rating": float(article.rating) if article.rating else 0.0,
            "created_at": article.created_at.isoformat() if article.created_at else None,
            "updated_at": article.updated_at.isoformat() if article.updated_at else None,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "attachments": [
                {
                    "id": att.id,
                    "file_name": att.file_name,
                    "file_url": att.file_url,
                    "file_type": att.file_type,
                    "file_size": att.file_size
                }
                for att in attachments
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting article: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving article"
        )

@router.post("/articles", response_model=ArticleResponse)
async def create_article(
    article_data: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new article (Manager/Admin only)"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers and admins can create articles"
        )
    
    try:
        slug = slugify(article_data.title)
        
        # Check if slug exists
        existing = db.query(KnowledgeBaseArticle).filter(KnowledgeBaseArticle.slug == slug).first()
        if existing:
            slug = f"{slug}-{db.query(KnowledgeBaseArticle).count() + 1}"
        
        from datetime import datetime
        
        article = KnowledgeBaseArticle(
            title=article_data.title,
            slug=slug,
            content=article_data.content,
            category_id=article_data.category_id,
            author_id=current_user.id,
            department_id=article_data.department_id or current_user.department_id,
            tags=article_data.tags or [],
            is_published=article_data.is_published,
            is_featured=article_data.is_featured,
            published_at=datetime.now() if article_data.is_published else None
        )
        
        db.add(article)
        db.commit()
        db.refresh(article)
        
        # Format response
        return {
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "content": article.content,
            "category_id": article.category_id,
            "category_name": article.category.name if article.category else None,
            "author_id": article.author_id,
            "author_name": article.author.full_name if article.author else None,
            "department_id": article.department_id,
            "department_name": article.department.name if article.department else None,
            "tags": article.tags or [],
            "is_published": article.is_published,
            "is_featured": article.is_featured,
            "view_count": article.view_count,
            "rating": float(article.rating) if article.rating else 0.0,
            "created_at": article.created_at.isoformat() if article.created_at else None,
            "updated_at": article.updated_at.isoformat() if article.updated_at else None,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "attachments": []
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating article: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating article"
        )

@router.put("/articles/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update article (Manager/Admin only, or author)"""
    article = db.query(KnowledgeBaseArticle).filter(KnowledgeBaseArticle.id == article_id).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check permissions
    if current_user.role not in ['manager', 'admin'] and article.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own articles"
        )
    
    try:
        from datetime import datetime
        
        if article_data.title:
            article.title = article_data.title
            # Regenerate slug if title changed
            article.slug = slugify(article_data.title)
        
        if article_data.content is not None:
            article.content = article_data.content
        
        if article_data.category_id is not None:
            article.category_id = article_data.category_id
        
        if article_data.department_id is not None:
            article.department_id = article_data.department_id
        
        if article_data.tags is not None:
            article.tags = article_data.tags
        
        if article_data.is_published is not None:
            article.is_published = article_data.is_published
            if article_data.is_published and not article.published_at:
                article.published_at = datetime.now()
        
        if article_data.is_featured is not None:
            article.is_featured = article_data.is_featured
        
        db.commit()
        db.refresh(article)
        
        # Format response (similar to create)
        attachments = db.query(KnowledgeBaseAttachment).filter(
            KnowledgeBaseAttachment.article_id == article.id
        ).all()
        
        return {
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "content": article.content,
            "category_id": article.category_id,
            "category_name": article.category.name if article.category else None,
            "author_id": article.author_id,
            "author_name": article.author.full_name if article.author else None,
            "department_id": article.department_id,
            "department_name": article.department.name if article.department else None,
            "tags": article.tags or [],
            "is_published": article.is_published,
            "is_featured": article.is_featured,
            "view_count": article.view_count,
            "rating": float(article.rating) if article.rating else 0.0,
            "created_at": article.created_at.isoformat() if article.created_at else None,
            "updated_at": article.updated_at.isoformat() if article.updated_at else None,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "attachments": [
                {
                    "id": att.id,
                    "file_name": att.file_name,
                    "file_url": att.file_url,
                    "file_type": att.file_type,
                    "file_size": att.file_size
                }
                for att in attachments
            ]
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating article: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating article"
        )

@router.delete("/articles/{article_id}")
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete article (Manager/Admin only, or author)"""
    article = db.query(KnowledgeBaseArticle).filter(KnowledgeBaseArticle.id == article_id).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check permissions
    if current_user.role not in ['manager', 'admin'] and article.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own articles"
        )
    
    try:
        # Delete attachments from Cloudinary
        attachments = db.query(KnowledgeBaseAttachment).filter(
            KnowledgeBaseAttachment.article_id == article_id
        ).all()
        
        for att in attachments:
            if att.cloudinary_public_id:
                cloudinary_service.delete_file(att.cloudinary_public_id)
        
        db.delete(article)
        db.commit()
        
        return {"message": "Article deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting article: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting article"
        )

@router.post("/articles/{article_id}/upload")
async def upload_attachment(
    article_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload attachment to article"""
    article = db.query(KnowledgeBaseArticle).filter(KnowledgeBaseArticle.id == article_id).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check permissions
    if current_user.role not in ['manager', 'admin'] and article.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload attachments to your own articles"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Upload to Cloudinary
        upload_result = cloudinary_service.upload_file(
            file_content=file_content,
            file_name=file.filename,
            folder='knowledge-base'
        )
        
        if not upload_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file"
            )
        
        # Save attachment record
        attachment = KnowledgeBaseAttachment(
            article_id=article_id,
            file_name=file.filename,
            file_url=upload_result['secure_url'],
            file_type=file.content_type,
            file_size=file_size,
            cloudinary_public_id=upload_result['public_id'],
            uploaded_by=current_user.id
        )
        
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        
        return {
            "id": attachment.id,
            "file_name": attachment.file_name,
            "file_url": attachment.file_url,
            "file_type": attachment.file_type,
            "file_size": attachment.file_size
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading attachment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading attachment"
        )

@router.get("/search")
async def search_articles(
    q: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Search articles by query"""
    try:
        search_term = f"%{q}%"
        
        query = db.query(KnowledgeBaseArticle)
        
        # For non-managers, only show published articles
        if current_user and current_user.role not in ['manager', 'admin']:
            query = query.filter(KnowledgeBaseArticle.is_published == True)
        
        query = query.filter(
            or_(
                KnowledgeBaseArticle.title.ilike(search_term),
                KnowledgeBaseArticle.content.ilike(search_term)
            )
        )
        
        articles = query.order_by(desc(KnowledgeBaseArticle.is_featured), desc(KnowledgeBaseArticle.view_count)).limit(limit).all()
        
        # Format response
        return [
            {
                "id": article.id,
                "title": article.title,
                "slug": article.slug,
                "content": article.content[:200] + "..." if len(article.content) > 200 else article.content,
                "category_name": article.category.name if article.category else None,
                "view_count": article.view_count
            }
            for article in articles
        ]
    except Exception as e:
        logger.error(f"Error searching articles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching articles"
        )

