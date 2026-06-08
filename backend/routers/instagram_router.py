from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from repository.instagram_repository import InstagramRepository
from schemas.instagram_schemas import (
    CommentCreate,
    CommentResponse,
    PostCreate,
    PostResponse,
    UserCreate,
    UserResponse,
    UserUpdate
)

instagram_router = APIRouter()
repo = InstagramRepository()

@instagram_router.post('/users/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    try:
        return repo.create_user(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            bio=user.bio
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username or email already exists'
        )

@instagram_router.get('/users/', response_model=list[UserResponse])
def list_users():
    return repo.list_users()

@instagram_router.get('/users/{user_id}', response_model=UserResponse)
def get_user(user_id: int):
    user = repo.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return user

@instagram_router.put('/users/{user_id}', response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate):
    try:
        updated_user = repo.update_user(
            user_id=user_id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            bio=user.bio
        )
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        return updated_user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username or email already exists'
        )

@instagram_router.delete('/users/{user_id}')
def delete_user(user_id: int):
    if not repo.delete_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return {'message': 'User deleted successfully'}

@instagram_router.post('/posts/', response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
    new_post = repo.create_post(
        user_id=post.user_id,
        image_url=post.image_url,
        caption=post.caption
    )
    if not new_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return new_post

@instagram_router.get('/posts/', response_model=list[PostResponse])
def list_posts():
    return repo.list_posts()

@instagram_router.get('/posts/{post_id}', response_model=PostResponse)
def get_post(post_id: int):
    post = repo.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post not found'
        )
    return post

@instagram_router.get('/users/{user_id}/posts', response_model=list[PostResponse])
def list_user_posts(user_id: int):
    user = repo.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return repo.list_user_posts(user_id)

@instagram_router.post('/posts/{post_id}/comments', response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(post_id: int, comment: CommentCreate):
    new_comment = repo.add_comment(
        post_id=post_id,
        user_id=comment.user_id,
        text=comment.text
    )
    if not new_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post or user not found'
        )
    return new_comment

@instagram_router.get('/posts/{post_id}/comments', response_model=list[CommentResponse])
def list_comments(post_id: int):
    post = repo.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post not found'
        )
    return repo.list_comments(post_id)

@instagram_router.post('/posts/{post_id}/likes')
def like_post(post_id: int, user_id: int):
    if not repo.like_post(post_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Post already liked or not found'
        )
    return {'message': 'Post liked'}

@instagram_router.delete('/posts/{post_id}/likes')
def unlike_post(post_id: int, user_id: int):
    if not repo.unlike_post(post_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Like not found'
        )
    return {'message': 'Post unliked'}

@instagram_router.post('/users/{follower_id}/follow/{followed_id}')
def follow_user(follower_id: int, followed_id: int):
    if follower_id == followed_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You cannot follow yourself'
        )
    if not repo.follow_user(follower_id, followed_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Already following or user not found'
        )
    return {'message': 'User followed'}

@instagram_router.delete('/users/{follower_id}/follow/{followed_id}')
def unfollow_user(follower_id: int, followed_id: int):
    if not repo.unfollow_user(follower_id, followed_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Follow relationship not found'
        )
    return {'message': 'User unfollowed'}

@instagram_router.get('/feed/{user_id}', response_model=list[PostResponse])
def feed(user_id: int, limit: int = 20):
    posts = repo.get_feed(user_id, limit=limit)
    if posts is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return posts
