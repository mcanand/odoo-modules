Pre Order
=========
* Website orders can be pre-ordered.
* Use enable_pre_order field in res.config.settings for turning On/Off
this feature.
* If the feature is enabled orders placed will be shown for accepting
just before it needs to be done.
* Website should block completing the pre-order if time remaining to
finish order preparation is less than time required to prepare the order.

Preparation Time Calculation
============================
Important:
----------
Do not use preparation_time field in sale.order or pos.order.
This field is set only when the order is accepted in Kitchen review screen

Calculation:
-----------
Time required to prepare the order is the sum of product of preparation time
for each product and its quantity.
* Eg:
  * Preparation time for a product is 10 minutes
  * Order line quantity is 2
  * Preparation time for second product is 20 minutes
  * Order line quantity is 3
  * So the total preparation time for the order will be
    * (10 x 2) + (20 x 3) = 80 minutes
For preparation time for a product use preparation_minutes field in product.product
if it is > 0. Else use preparation_minutes field in product.template if it is > 0.
If both field are zero then last option is to take the default preparation time for
products. Use minimum_preparation_time field in res.config.settings.