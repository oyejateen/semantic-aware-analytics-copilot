with listings as (

    select * from {{ ref('stg_listings') }}

),

final as (

    select
        listing_id,
        listing_name,

        neighbourhood_cleansed,
        neighbourhood_group_cleansed,
        latitude,
        longitude,

        property_type,
        room_type,
        accommodates,
        bathrooms,
        bedrooms,
        beds,

        listing_price,
        price_quote_price_per_night,

        minimum_nights,
        maximum_nights,
        availability_365,

        number_of_reviews,
        reviews_per_month,
        review_scores_rating,

        estimated_occupancy_l365d,
        estimated_revenue_l365d,

        is_instant_bookable,
        last_scraped

    from listings
    where listing_price is not null
       or price_quote_price_per_night is not null

)

select * from final