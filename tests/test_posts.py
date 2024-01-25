from typing import List
import pytest

from app import schemas


def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")

    posts_map = map(lambda post: schemas.PostOut(**post), res.json())
    posts = list(posts_map)

    assert len(posts) == len(test_posts)
    assert res.status_code == 200
    # assert posts[0].Post.id == test_posts[0].id


def test_unauthorized_user_get_all_posts(client, test_posts):
    res = client.get("/posts/")
    assert res.status_code == 401


def test_unauthorized_user_get_post(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_get_post_not_exist(authorized_client, test_posts):
    res = authorized_client.get("/posts/8888")
    assert res.status_code == 404


def test_get_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    post = schemas.PostOut(**res.json())
    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content


@pytest.mark.parametrize(
    "title, content, published",
    [
        ("first new title", "first new content", True),
        ("second new title", "second new content", False),
    ],
)
def test_create_post(
    authorized_client, test_user, test_posts, title, content, published
):
    res = authorized_client.post(
        "/posts/", json={"title": title, "content": content, "published": published}
    )
    created_post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == title


def test_unauthorized_user_create_post(client):
    res = client.post(
        "/posts/",
        json={"title": "unauthorized", "content": "unauthorized", "published": False},
    )
    assert res.status_code == 401


def test_unauthorized_user_delete_post(client, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_delete_post(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 204


def test_delete_post_non_exist(authorized_client):
    res = authorized_client.delete("/posts/8888")
    assert res.status_code == 404


def test_delete_other_user_post(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert res.status_code == 403


def test_update_post(authorized_client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": "updated content",
        "published": False,
    }
    res = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)
    updated_post = schemas.Post(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data.get("title")


def test_update_other_user_post(
    authorized_client, test_user, test_second_user, test_posts
):
    data = {
        "title": "updated title",
        "content": "updated content",
        "published": False,
    }
    res = authorized_client.put(f"/posts/{test_posts[3].id}", json=data)
    assert res.status_code == 403
