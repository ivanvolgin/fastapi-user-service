from fastapi import APIRouter

router = APIRouter()


# @router.get("/product/{product_id}", response_model=Product)
# async def get_product_by_product_id(product_id: Annotated[int, Path(...)]):
#     for product in PRODUCT_LIST:
#         if product["product_id"] == product_id:
#             return product
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail="Product not found.",
#     )
#
#
# @router.get("/product/search/")
# async def get_products_by_keyword(
#     keyword: Annotated[str, Query(..., description="Название товара для поиска.")],
#     category: Annotated[
#         str | None,
#         Query(
#             description="Фильтр категории для поиска товаров.",
#             max_length=50,
#         ),
#     ] = None,
#     limit: Annotated[
#         int,
#         Query(gt=0, description="Количесво отображаемых товаров"),
#     ] = 10,
# ):
#     result = []
#     for product in PRODUCT_LIST:
#         if keyword.lower() in product["name"].lower():
#             if category:
#                 if category.lower() in product["category"].lower():
#                     result.append(product)
#             else:
#                 result.append(product)
#         if len(result) >= limit:
#             break
#
#     return result or HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND, detail="Products  not found."
#     )
