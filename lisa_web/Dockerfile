FROM continuumio/miniconda3

WORKDIR /app

COPY lisa_web_requirement.txt /app/

RUN conda create -n lisa_web python=2.7.15
SHELL ["conda", "run", "-n", "lisa_web", "/bin/bash", "-c"]
RUN pip install -r /app/lisa_web_requirement.txt
RUN pip install gunicorn


EXPOSE 8000
COPY lisa_web /app/lisa_web

ENTRYPOINT [ "conda", "run", "-n", "lisa_web", "gunicorn", "--bind", "0.0.0.0:8000", "--pythonpath", "/app/", "lisa_web:app", "--timeout", "300" ]
