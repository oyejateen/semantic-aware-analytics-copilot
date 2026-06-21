with source as (

    select * from {{ source('airbnb_nyc_raw', 'reviews') }}

),

renamed as (

    select
        listing_id,
        date as review_date,
        date_trunc(date, month) as review_month

    from source

)

select * from renamed