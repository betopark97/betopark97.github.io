# Streamlit

## Installation

## Setup

## Authentication (RBAC)

## Multi-pages

## Filters & Components

All filters and components that I use will be native Streamlit components or from the bp-streamlit-tools package.  
This package is something that I will build myself as a side project, but that I could use at work too as I develop dashboards solo for now. I might merge my dashboards with the IT team at some point (I’m in the Big Data Team) though.

> **NOTE:**
>
> This is no right or wrong when it comes to UI/UX and the following components that I use for the filters is a convention for myself, but it would be a good place to start. Without a convention or system to structure your filters, a dashboard can become messy real quick.  
> \#### Swapping Data (Radio)

When swapping data use a radio. By this it means when you have to change the criteria. For example, making a big change in how your data is queried like switching the date column. Imagine that normally you display your data in date_utc, but then you have Korean users and make it date_kst. That’s swapping the column that was part of the grain. Also, if this is a filter that you would like to put at the top of the dashboard like a global filter, or in a side by for a vertical stack

#### Choosing from an Enum (Segmented Control)

Use a segmented control when you want to toggle between views like timeframes or metrics. This is a horizontal layout so keep that in mind. Also, this works clean with short texts or emojis.

## Optimizations

@st.cache_data  
@st.cache_resource  
@st.fragment (parallel=True)  
st.form  
st.session_state + st.empty()

------------------------------------------------------------------------

Last modified: 2026-07-22

Back to top
