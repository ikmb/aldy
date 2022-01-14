FROM nfcore/base
LABEL authors="Marc Hoeppner" \
      description="Docker image containing fork of Aldy pharacoenomics tool"

COPY environment.yml /
RUN conda env create -f /environment.yml && conda clean -a
ENV PATH /opt/conda/envs/aldy-3.3/bin:$PATH

RUN pip install 'aldy==3.3'
RUN pip install ortools
