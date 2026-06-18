with source as (

    select * from {{ source('airbnb_nyc_raw', 'calender') }}

),

renamed as (

    select
        listing_id,
        date,
        available,
        minimum_nights,
        maximum_nights
    from source

)

select * from renamed