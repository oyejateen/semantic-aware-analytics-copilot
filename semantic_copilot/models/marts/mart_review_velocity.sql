with reviews as (

    select * from {{ ref('stg_reviews') }}

),

listings as (

    select * from {{ ref('stg_listings') }}

),

monthly_reviews as (

    select
        r.review_month,
        r.listing_id,

        l.neighbourhood_cleansed,
        l.neighbourhood_group_cleansed,
        l.property_type,
        l.room_type,

        count(*) as review_count

    from reviews r
    left join listings l
        on r.listing_id = l.listing_id

    group by
        r.review_month,
        r.listing_id,
        l.neighbourhood_cleansed,
        l.neighbourhood_group_cleansed,
        l.property_type,
        l.room_type

)

select * from monthly_reviews