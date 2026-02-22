"""
Trending Articles Query Helper
Utilities for fetching trending and most viewed articles
"""

from models import Article, Comment
from datetime import datetime, timedelta
from sqlalchemy import desc, func


class TrendingQuery:
    """Utilities for trending articles queries"""

    @staticmethod
    def get_most_viewed(limit=6, days=30):
        """
        Get most viewed articles in the last N days
        
        Args:
            limit: Number of articles to return
            days: Time period to consider (default 30 days)
        
        Returns:
            List of Article objects sorted by views
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        articles = Article.query.filter(
            Article.status == 'approved',
            Article.deleted_at.is_(None),
            Article.date_posted >= cutoff_date
        ).order_by(
            desc(Article.views)
        ).limit(limit).all()

        return articles

    @staticmethod
    def get_trending(limit=6, days=7):
        """
        Get trending articles (high views + recent comments)
        
        Trending algorithm:
        - Articles from last N days
        - Sorted by views DESC
        - Bonus for recent comments (indicating engagement)
        
        Args:
            limit: Number of articles to return
            days: Time period to consider (default 7 days)
        
        Returns:
            List of Article objects sorted by trending score
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get approved articles from last N days
        articles = Article.query.filter(
            Article.status == 'approved',
            Article.deleted_at.is_(None),
            Article.date_posted >= cutoff_date
        ).all()

        # Calculate trending score (views + engagement bonus)
        for article in articles:
            # Base score is views
            article.trending_score = article.views

            # Bonus for recent comments (indicates engagement)
            recent_comments = Comment.query.filter(
                Comment.article_id == article.id,
                Comment.deleted_at.is_(None),
                Comment.date_posted >= cutoff_date
            ).count()

            article.trending_score += recent_comments * 5  # Weight comments

            # Bonus for recent posts (decay over time)
            hours_old = (datetime.utcnow() - article.date_posted).total_seconds() / 3600
            if hours_old < 24:
                article.trending_score *= 1.5  # 50% bonus for posts < 24 hours
            elif hours_old < 72:
                article.trending_score *= 1.2  # 20% bonus for posts < 3 days

        # Sort by trending score
        articles.sort(key=lambda x: x.trending_score, reverse=True)

        return articles[:limit]

    @staticmethod
    def get_most_commented(limit=6):
        """
        Get articles with most comments
        
        Returns:
            List of Article objects sorted by comment count
        """
        articles = Article.query.filter(
            Article.status == 'approved',
            Article.deleted_at.is_(None)
        ).outerjoin(Comment).group_by(Article.id).order_by(
            desc(func.count(Comment.id))
        ).limit(limit).all()

        return articles

    @staticmethod
    def get_recent(limit=6, days=30):
        """
        Get most recent approved articles
        
        Args:
            limit: Number of articles to return
            days: How far back to look (default 30 days)
        
        Returns:
            List of Article objects sorted by date (newest first)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        articles = Article.query.filter(
            Article.status == 'approved',
            Article.deleted_at.is_(None),
            Article.date_posted >= cutoff_date
        ).order_by(
            desc(Article.date_posted)
        ).limit(limit).all()

        return articles

    @staticmethod
    def get_by_category_trending(category, limit=6, days=7):
        """
        Get trending articles in a specific category
        
        Args:
            category: Article category
            limit: Number of articles to return
            days: Time period to consider
        
        Returns:
            List of Article objects in category sorted by trending score
        """
        return TrendingQuery.get_trending(limit, days)  # Filter by category can be done here
        # This is a simplified version; enhance with category filtering

    @staticmethod
    def increment_view_count(article_id):
        """
        Increment view count for an article
        Used when an article is viewed
        
        Args:
            article_id: ID of the article
        
        Returns:
            Updated view count or None if article not found
        """
        from extensions import db

        article = Article.query.get(article_id)
        if article:
            article.views += 1
            try:
                db.session.commit()
                return article.views
            except Exception as e:
                db.session.rollback()
                print(f"Error incrementing view count: {e}")
                return None

        return None


# Aliases for compatibility
def get_trending_articles(limit=6):
    """Alias for TrendingQuery.get_trending()"""
    return TrendingQuery.get_trending(limit)


def get_most_viewed_articles(limit=6):
    """Alias for TrendingQuery.get_most_viewed()"""
    return TrendingQuery.get_most_viewed(limit)


def get_recent_articles(limit=6):
    """Alias for TrendingQuery.get_recent()"""
    return TrendingQuery.get_recent(limit)
