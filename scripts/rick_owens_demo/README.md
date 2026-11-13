# Rick Owens demo catalog overlay

Optional demo content for Saleor 3.23.41 and the Paper storefront. This does not
change the default seed data or application behavior.

- Replaces the blue Monospace Tee with a black Rick Owens Level T-Shirt.
- Adds milk/black Rick Owens Geobasket sneakers with a transparent PNG cutout.
- Places the sneakers immediately after the shirt in `featured-products`.
- Sets all shirt sizes to $599 and all sneaker sizes to $1,009 in the USD
  `default-channel`, without inherited sale or prior-price amounts.
- Retains the shirt's sizes. Sneakers copy the Plimsolls demo size attributes,
  channel listings, and warehouses, with 10 units per stock. Other channels keep
  their existing demo prices.
- Preserves other featured products and their relative order.

## Apply

Use a disposable, populated demo database with `DEBUG=True`. Back it up first:
the overlay changes the existing tee. Do not run against production.
From the repository root, with the normal Saleor environment and dependencies:

```sh
python manage.py shell < scripts/rick_owens_demo/apply.py
```

The standard demo products `ascii-tee`, `blue-plimsolls`, and the
`featured-products` collection must exist. Run the normal `populatedb` command
first only on a fresh demo database.

Re-running the overlay does not duplicate products, variants, stock, or images.
Existing sneaker stock is preserved on subsequent runs. The specified USD prices
are reapplied on each run, including to products created by an earlier version.
Database writes are atomic; media storage is not transactional.
Refresh the storefront's collection/product cache after applying (or restart
its development server) and reload the homepage. The shirt keeps its original
`ascii-tee` URL so existing links remain valid.

## Images and attribution

These are third-party product photographs, not original or openly licensed artwork.
Rick Owens is not affiliated with this demo. No image license or endorsement is
claimed; obtain permission before redistributing or using these assets commercially.

- `shirt.jpg`: Rick Owens Level T-Shirt, SVD product photography:
  https://media.sivasdescalzo.com/media/catalog/product/R/U/RU01E5264-JA-09_sivasdescalzo-Rick_Owens-KNIT_T-SHIRT_-_LEVEL_T-1742903625-500.jpg
- `sneakers.png`: Rick Owens Geobasket in Milk/Black, SVRN product photography:
  https://www.svrn.com/cdn/shop/products/geobasket-in-milk-black-men-s-sneakers-rick-owens-svrn-chicago-28282753122377.jpg
  Background removed and centered on a transparent square canvas.

The prices, inventory, and size availability are sample data, not retail offers.
