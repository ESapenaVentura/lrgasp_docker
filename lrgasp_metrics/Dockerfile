FROM continuumio/miniconda3

WORKDIR /app

# Create the environment:
COPY sqanti3_lrgasp.yml .
RUN conda install -c conda-forge mamba
RUN mamba env create -n sqanti_env -f sqanti3_lrgasp.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "sqanti_env", "/bin/bash", "-c"]

# Download and set-up cDNA_Cupcake
RUN apt-get update && apt-get install git && git clone https://github.com/Magdoll/cDNA_Cupcake.git
RUN apt-get install -y libcurl4
COPY . /app
WORKDIR /app/cDNA_Cupcake/
RUN python setup.py build
RUN python setup.py install
WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/app/cDNA_Cupcake/sequence/"
ENV PYTHONPATH "${PYTHONPATH}:/app/cDNA_Cupcake/"

# The code to run when container is started:
COPY . /app
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "sqanti_env","python", "sqanti3_lrgasp.challenge1.py"]