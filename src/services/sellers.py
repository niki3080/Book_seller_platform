__all__ = ["SellerService"]


from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.seller import Seller
from src.schemas.sellers import IncomingSeller, PatchSeller, ReturnedSeller


class SellerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    # добавить продавца
    async def add_seller(self, seller: IncomingSeller) -> Seller:
       
        new_seller = Seller(
            **{
                "first_name": seller.first_name,
                "last_name": seller.last_name,
                "e_mail": seller.e_mail,
                "password": seller.password,
            }
        )

        self.session.add(new_seller)
        await self.session.flush()
        await self.session.refresh(new_seller)
        
        return new_seller


    # удалить продавца
    async def delete_seller(self, seller_id: int) -> bool:
        seller = await self.session.get(Seller, seller_id)

        if seller:
            await self.session.delete(seller)
            return True

        else:
            return False


    # обновить данные продавца
    async def update_seller(self, seller_id: int, new_seller_data: ReturnedSeller) -> Seller | None:
       
        if updated_seller := await self.session.get(Seller, seller_id):
            updated_seller.first_name = new_seller_data.first_name
            updated_seller.last_name = new_seller_data.last_name
            updated_seller.e_mail = new_seller_data.e_mail

            await self.session.flush()
            return updated_seller


    # частичное обновление данных продавца
    async def partial_update_seller(self, seller_id: int, patched_seller: PatchSeller) -> Seller | None:
        if seller := await self.session.get(Seller, seller_id):

            if patched_seller.first_name is not None and patched_seller.first_name != seller.first_name:
                seller.first_name = patched_seller.first_name
            if patched_seller.last_name is not None and patched_seller.last_name != seller.last_name:
                seller.last_name = patched_seller.last_name
            if patched_seller.e_mail is not None and patched_seller.e_mail != seller.e_mail:
                seller.e_mail = patched_seller.e_mail

            await self.session.flush()
            return seller


    # вернуть продавца по id
    async def get_single_seller(self, seller_id: int) -> Seller | None:
        query = (
            select(Seller)
            .where(Seller.id == seller_id)
            .options(selectinload(Seller.books))
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    # вернуть список продавцов
    async def get_all_sellers(self) -> list[Seller]:

        query = (
            select(Seller)
            .options(selectinload(Seller.books))
        )

        result = await self.session.execute(query)
        sellers = result.scalars().all()

        for seller in sellers:
            seller.total_books = len(seller.books)

        return sellers