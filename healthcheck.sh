#!/bin/bash

DB_USER=$(cat /run/secrets/db_user)
DB_NAME=$(cat /run/secrets/db_name)
pg_isready -U "$DB_USER" -d "$DB_NAME"
