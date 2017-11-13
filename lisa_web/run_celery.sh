#!/bin/bash 

celery worker -A lisa_web.celery --loglevel=info

