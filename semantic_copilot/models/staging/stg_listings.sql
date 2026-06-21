with source as (

    select * from {{ source('airbnb_nyc_raw', 'listings') }}

),

renamed as (

    select
        id as listing_id,
        name as listing_name,

        host_id,
        host_name,
        host_is_superhost,
        host_listings_count,
        host_has_profile_pic,
        host_identity_verified,

        neighbourhood,
        neighbourhood_cleansed,
        neighbourhood_group_cleansed,
        latitude,
        longitude,

        property_type,
        room_type,
        accommodates,
        bathrooms,
        bathrooms_text,
        bedrooms,
        beds,

        price as listing_price,
        price_quote_checkin_date,
        price_quote_checkout_date,
        price_quote_total_price,
        price_quote_price_per_night,

        minimum_nights,
        maximum_nights,
        has_availability,
        availability_30,
        availability_60,
        availability_90,
        availability_365,

        number_of_reviews,
        number_of_reviews_ltm,
        number_of_reviews_l30d,
        first_review,
        last_review,
        review_scores_rating,
        reviews_per_month,

        estimated_occupancy_l365d,
        estimated_revenue_l365d,

        case
            when lower(instant_bookable) in ('t', 'true', 'yes', '1') then true
            when lower(instant_bookable) in ('f', 'false', 'no', '0') then false
            else null
        end as is_instant_bookable,

        last_scraped,
        calendar_last_scraped

    from source

)

select * from renamed