# PACER Dashboard



## Important notes regarding migrations

- If you are making a migration for a partitioned model, you MUST use the following command:

    ``python manage.py pgmakemigrations``
    
    Do not use Django's own command for makemigrations as it will not create a partitioned model but a standard one.

- 