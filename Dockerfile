# Definition of the Docker image with PyPEEC and Jupyter.
#
# The Docker image is only intended for test purposes.
# This image is not screened for eventual vulnerabilities.
# Do not use the image for public-facing servers.
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

# definition of the base image
FROM quay.io/jupyter/base-notebook:2025-11-10

# image metadata
LABEL org.opencontainers.image.authors="Thomas Guillod <guillod@otvam.ch>"
LABEL org.opencontainers.image.source="https://github.com/otvam/pypeec"
LABEL org.opencontainers.image.documentation="https://pypeec.otvam.ch"
LABEL org.opencontainers.image.title="PyPEEC - 3D Quasi-Magnetostatic Solver"
LABEL org.opencontainers.image.description="Docker image with PyPEEC and Jupyter"
LABEL org.opencontainers.image.licenses="MPL-2.0 and others"

# install all the dependencies (but not PyPEEC)
RUN mamba install --yes --channel conda-forge \
    vtk==9.5.2 \
    mesalib==25.0.5 \
    scilogger==1.2.5 \
    scisave==1.6.0 \
    numpy==2.3.5 \
    scipy==1.16.3 \
    joblib==1.5.2 \
    pyvista==0.46.4 \
    shapely==2.1.2 \
    rasterio==1.4.3 \
    pillow==12.0.0 \
    matplotlib-base==3.10.8 \
    jupyterlab==4.5.0 \
    ipython=9.7.0

# install PyPEEC (no-deps as everything required has been installed)
RUN mamba install --yes --no-deps --channel conda-forge pypeec

# clean conda data
RUN mamba clean --all --force-pkgs-dirs --yes

# fix permissions
RUN fix-permissions "${CONDA_DIR}" && fix-permissions "${HOME}"

# extract the PyPEEC examples
RUN pypeec examples .

# clean the workspace
RUN rm -rf *.py *.sh work

# allow Jupyter to display VTK graphics
ENV PYVISTA_TRAME_SERVER_PROXY_PREFIX="/proxy/"

# ensure that the working directory and folder are correct
USER ${NB_UID}
WORKDIR ${HOME}
