FROM condaforge/mambaforge-pypy3

WORKDIR /app

# Create the environment:
COPY sqanti3_lrgasp.yml .
RUN mamba env create -n sqanti_env -f sqanti3_lrgasp.yml -v

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "sqanti_env", "/bin/bash", "-c"]

# Download and set-up cDNA_Cupcake, v.27.0.0 commit d5432f37ab4869a3012e20d28f227ce9dda35014
RUN apt-get update && wget https://github.com/Magdoll/cDNA_Cupcake/archive/refs/tags/v24.0.0.tar.gz && tar -xvf v24.0.0.tar.gz
COPY . /app
ENV PYTHONPATH "${PYTHONPATH}:/app/cDNA_Cupcake-24.0.0/sequence/"
ENV PYTHONPATH "${PYTHONPATH}:/app/cDNA_Cupcake-24.0.0/"

RUN apt-get install libcurl4 libcurl4-openssl-dev -y


# The code to run when container is started:
COPY . /app
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "sqanti_env","python", "sqanti3_lrgasp.challenge1.py"]