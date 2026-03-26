import pytest
from fastapi import status
from icecream import ic
from sqlalchemy import select

from src.models.books import Book
from src.models.seller import Seller

API_V1_URL_PREFIX = "/api/v1/sellers"



# POST seller
@pytest.mark.asyncio()
async def test_create_seller(async_client):
    data = {
        "first_name": "Yulia",
        "last_name": "Nikitina",
        "e_mail": "nikitina@example.com",
        "password": "123456"
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_seller_id = result_data.pop("id", None)
    assert resp_seller_id is not None, "Seller id not returned from endpoint"

    assert result_data == {
        "first_name": "Yulia",
        "last_name": "Nikitina",
        "e_mail": "nikitina@example.com",
        "total_books": 0
    }



# POST seller - invalid password
@pytest.mark.asyncio()
async def test_create_seller_with_short_password(async_client):
    data = {
        "first_name": "Yulia",
        "last_name": "Nikitina",
        "e_mail": "nikitina@example.com",
        "password": "123"   
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT



# POST seller - invalid email
@pytest.mark.asyncio()
async def test_create_seller_with_invalid_email(async_client):
    data = {
        "first_name": "Yulia",
        "last_name": "Nikitina",
        "e_mail": "nikitinaexamplecom",
        "password": "123456"   
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT



# GET sellers list
@pytest.mark.asyncio()
async def test_get_sellers(db_session, async_client):

    seller = Seller(
        first_name="Yulia",
        last_name="Nikitina",
        e_mail="nikitina@example.com",
        password="123456"
        )
    seller_2 = Seller(
        first_name="Max",
        last_name="Bekaruykov",
        e_mail="bekaryukovmv@gmail.com",
        password="654321"
        )
    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {
                "first_name": "Yulia",
                "last_name": "Nikitina",
                "e_mail": "nikitina@example.com",
                "id": seller.id,
                "total_books": 0
            },
            {
                "first_name": "Max",
                "last_name": "Bekaruykov",
                "e_mail": "bekaryukovmv@gmail.com",
                "id": seller_2.id,
                "total_books": 0
            },
        ]
    }


# GET single seller by ID
@pytest.mark.asyncio()
async def test_get_single_seller(db_session, async_client):

    seller = Seller(
        first_name="Yulia",
        last_name="Nikitina",
        e_mail="nikitina@example.com",
        password="123456"
        )
    seller_2 = Seller(
        first_name="Max",
        last_name="Bekaruykov",
        e_mail="bekaryukovmv@gmail.com",
        password="654321"
        )
    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "first_name": "Yulia",
        "last_name": "Nikitina",
        "e_mail": "nikitina@example.com",
        "id": seller.id,
        "books": [],
        "total_books": 0
        }



# GET seller – not existing 
@pytest.mark.asyncio()
async def test_get_single_seller_with_wrong_id(db_session, async_client):

    seller = Seller(
        first_name="Yulia",
        last_name="Nikitina",
        e_mail="nikitina@example.com",
        password="123456"
        )
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/426548")

    assert response.status_code == status.HTTP_404_NOT_FOUND



# GET seller with his books
@pytest.mark.asyncio()
async def test_get_seller_with_books(db_session, async_client):

    seller = Seller(
        first_name="Yulia",
        last_name="Nikitina",
        e_mail="nikitina@example.com",
        password="123456",
    )
    db_session.add(seller)
    await db_session.flush()

    book_1 = Book(author="Pushkin", title="Eugeny Onegin", year=2021, pages=104, seller_id=seller.id)
    book_2 = Book(author="Lermontov", title="Mziri", year=2021, pages=108, seller_id=seller.id)

    db_session.add_all([book_1, book_2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == seller.id
    assert data["total_books"] == 2
    assert len(data["books"]) == 2



# PUT seller update
@pytest.mark.asyncio()
async def test_update_seller(db_session, async_client):

    seller = Seller(
        first_name="Yulia",
        last_name="Nikitina",
        e_mail="nikitina@example.com",
        password="123456",
        )
    db_session.add(seller)
    await db_session.flush()

    data = {
        "first_name": "Yulia theBest",
        "last_name": "Pavlova",
        "e_mail": "pavlova@example.com"
        }

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{seller.id}",
        json=data,
    )

    assert response.status_code == status.HTTP_200_OK

    res = await db_session.get(Seller, seller.id)
    assert res.first_name == "Yulia theBest"
    assert res.last_name == "Pavlova"
    assert res.e_mail == "pavlova@example.com"
    assert res.id == seller.id



# PATCH seller
@pytest.mark.asyncio()
async def test_patch_seller(db_session, async_client):

    seller = Seller(
        first_name="Yulia",
        last_name="Nikitina",
        e_mail="nikitina@example.com",
        password="123456",
    )
    db_session.add(seller)
    await db_session.flush()

    data = {"first_name": "Yulia Patched"}

    response = await async_client.patch(
        f"{API_V1_URL_PREFIX}/{seller.id}",
        json=data,
    )

    assert response.status_code == status.HTTP_200_OK

    res = await db_session.get(Seller, seller.id)
    assert res.first_name == "Yulia Patched"
    assert res.last_name == "Nikitina"          
    assert res.e_mail == "nikitina@example.com" 
    assert res.id == seller.id


# DELETE seller without books
@pytest.mark.asyncio()
async def test_delete_seller_without_books(db_session, async_client):

    seller = Seller(
        first_name="Yulia",
        last_name="Nikitina",
        e_mail="nikitina@example.com",
        password="123456",
    )
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    result = await db_session.execute(select(Seller))
    sellers = result.scalars().all()

    assert len(sellers) == 0



# DELETE seller with all books
@pytest.mark.asyncio()
async def test_delete_seller_with_books(db_session, async_client):

    seller = Seller(
        first_name="Yulia",
        last_name="Nikitina",
        e_mail="nikitina@example.com",
        password="123456",
    )
    db_session.add(seller)
    await db_session.flush()

    book_1 = Book(author="Pushkin", title="Eugeny Onegin", year=2021, pages=104, seller_id=seller.id)
    book_2 = Book(author="Lermontov", title="Mziri", year=2021, pages=108, seller_id=seller.id)

    db_session.add_all([book_1, book_2])
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()

    seller_result = await db_session.execute(select(Seller))
    res = seller_result.scalars().all()
    assert len(res) == 0

    books_result = await db_session.execute(select(Book))
    books = books_result.scalars().all()
    assert len(books) == 0



# DELETE seller - invalid ID
@pytest.mark.asyncio()
async def test_delete_seller_with_invalid_id(db_session, async_client):

    seller = Seller(
        first_name="Yulia",
        last_name="Nikitina",
        e_mail="nikitina@example.com",
        password="123456",
    )
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


