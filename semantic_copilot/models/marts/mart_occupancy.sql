with calendar as (

    select * from {{ ref('stg_calendar') }}

),

occupancy as (

    select
        listing_id,
        date_trunc(date, month) as month,
        count(*) as total_nights,
        countif(available = false) as booked_nights,
        round(countif(available = false) / count(*), 4) as occupancy_rate
    from calendar
    group by listing_id, month

)

select * from occupancy