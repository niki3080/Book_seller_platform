from pydantic import BaseModel, Field, computed_field, field_validator, EmailStr, ConfigDict
from pydantic_core import PydanticCustomError

from src.schemas.books import ReturnedBook

__all__ = [
    "PatchSeller",
    "IncomingSeller",
    "ReturnedSeller",
    "ReturnedSellerWithBooks",
    "ReturnedAllSellers",
]


# Базовый класс "Seller"
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr


# создание продавца
class IncomingSeller(BaseSeller):
    password: str = Field(min_length=6)


# продавец для списка (без книг)
class ReturnedSeller(BaseSeller):
    id: int
    # список книг пустой
    books: list[ReturnedBook] = Field(default_factory=list, exclude=True)

    model_config = ConfigDict(from_attributes=True)

    # вывести количество книг у продавца:
    @computed_field
    def total_books(self) -> int:
        return len(getattr(self, "books", []))


# продавец со списком книг  
class ReturnedSellerWithBooks(BaseSeller):
    id: int
    books: list[ReturnedBook]

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    def total_books(self) -> int:
        return len(self.books)
    
# список продавцов
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
   

# обновление данных продавца
class PatchSeller(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    e_mail: EmailStr | None = None