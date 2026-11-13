"""Apply the optional catalog overlay to an existing populated demo database."""

import copy
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from PIL import Image

from saleor.product.models import Collection, CollectionProduct, Product, ProductMedia
from saleor.thumbnail.models import Thumbnail
from saleor.warehouse.models import Stock

ASSETS = Path("scripts/rick_owens_demo")
SNEAKER_SLUG = "rick-owens-geobasket-sneakers"


def clone_row(row, **changes):
    duplicate = copy.copy(row)
    duplicate._state = copy.copy(row._state)
    duplicate.pk = None
    duplicate._state.adding = True
    for field, value in changes.items():
        setattr(duplicate, field, value)
    duplicate.save()
    return duplicate


def replace_media(product, filename, alt):
    content = (ASSETS / filename).read_bytes()
    media = list(product.media.all())
    if not media:
        media = [ProductMedia(product=product, sort_order=0)]
    for item in media:
        if (
            item.image
            and item.alt == alt
            and item.image.storage.exists(item.image.name)
        ):
            with item.image.open("rb") as existing:
                if existing.read() == content:
                    continue
        item.image.save(filename, ContentFile(content), save=False)
        item.alt = alt
        item.save()
        Thumbnail.objects.filter(product_media=item).delete()


def apply():
    if not settings.DEBUG:
        raise RuntimeError("This catalog overlay is for DEBUG demo databases only.")
    for filename, expected_format in (
        ("shirt.jpg", "JPEG"),
        ("sneakers.png", "PNG"),
    ):
        with Image.open(ASSETS / filename) as image:
            if image.format != expected_format:
                raise ValueError(f"Unexpected image format: {filename}")
            image.verify()
        with Image.open(ASSETS / filename) as image:
            if filename == "sneakers.png" and (
                image.mode != "RGBA" or image.getchannel("A").getextrema() != (0, 255)
            ):
                raise ValueError("Sneakers must retain their transparent background.")

    with transaction.atomic():
        shirt = Product.objects.get(slug="ascii-tee")
        template = Product.objects.get(slug="blue-plimsolls")
        collection = Collection.objects.get(slug="featured-products")
        shirt.name = "Rick Owens Level T-Shirt"
        text = (
            "Rick Owens Level T-shirt in black. A pared-back crewneck silhouette "
            "with short sleeves and signature seam detailing. "
            "Demo catalog item. Price and size availability are sample data."
        )
        shirt.description = {"blocks": [{"type": "paragraph", "data": {"text": text}}]}
        shirt.description_plaintext = text
        shirt.search_index_dirty = True
        shirt.save(
            update_fields=[
                "name",
                "description",
                "description_plaintext",
                "search_index_dirty",
            ]
        )
        replace_media(shirt, "shirt.jpg", "Rick Owens Level T-Shirt in black")

        sneakers = Product.objects.filter(slug=SNEAKER_SLUG).first()
        if sneakers is None:
            text = (
                "Rick Owens Geobasket high-top sneakers in milk and black, "
                "with an oversized tongue and contrast panels. "
                "Demo catalog item; price and availability are sample data."
            )
            sneakers = clone_row(
                template,
                slug=SNEAKER_SLUG,
                name="Rick Owens Geobasket Sneakers",
                default_variant=None,
                external_reference=None,
                description={"blocks": [{"type": "paragraph", "data": {"text": text}}]},
                description_plaintext=text,
                search_document="",
                search_vector=None,
                search_index_dirty=True,
                seo_title="Rick Owens Geobasket Sneakers",
                seo_description=text,
            )
            for listing in template.channel_listings.all():
                clone_row(listing, product=sneakers)
            for variant in template.variants.all():
                new_variant = clone_row(
                    variant,
                    product=sneakers,
                    sku=f"RO-GEOBASKET-DEMO-{variant.pk}",
                    external_reference=None,
                )
                for listing in variant.channel_listings.all():
                    clone_row(listing, variant=new_variant)
                for assignment in variant.attributes.all():
                    new_assignment = clone_row(assignment, variant=new_variant)
                    for value in assignment.variantvalueassignment.all():
                        clone_row(value, variant=new_variant, assignment=new_assignment)
                for stock in variant.stocks.all():
                    Stock.objects.create(
                        product_variant=new_variant,
                        warehouse_id=stock.warehouse_id,
                        quantity=10,
                    )
                if sneakers.default_variant_id is None:
                    sneakers.default_variant = new_variant
                    sneakers.save(update_fields=["default_variant"])
        replace_media(
            sneakers,
            "sneakers.png",
            "Rick Owens Geobasket sneakers in milk and black, background removed",
        )
        others = list(
            CollectionProduct.objects.filter(collection=collection)
            .exclude(product__in=[shirt, sneakers])
            .order_by("sort_order", "product__slug")
            .values_list("product_id", flat=True)
        )
        for position, product_id in enumerate([shirt.pk, sneakers.pk, *others]):
            CollectionProduct.objects.update_or_create(
                collection=collection,
                product_id=product_id,
                defaults={"sort_order": position},
            )


apply()
