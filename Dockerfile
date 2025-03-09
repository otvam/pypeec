# Definition of the Docker image with PyPEEC and Jupyter.
#
# The Docker image is only intended for test purposes.
# This image is not screened for eventual vulnerabilities.
# Do not use the image for public-facing servers.
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

# definition of the base image
FROM quay.io/jupyter/base-notebook:2024-11-25

# image metadata
LABEL org.opencontainers.image.authors="Thomas Guillod <guillod@otvam.ch>"
LABEL org.opencontainers.image.source="https://github.com/otvam/pypeec"
LABEL org.opencontainers.image.documentation="https://pypeec.otvam.ch"
LABEL org.opencontainers.image.title="PyPEEC - 3D Quasi-Magnetostatic Solver"
LABEL org.opencontainers.image.description="Docker image with PyPEEC and Jupyter"
LABEL org.opencontainers.image.licenses="MPL-2.0 and others"

# install all the dependencies (but not PyPEEC)
RUN mamba install --yes --channel conda-forge \
    scilogger==1.2.4=pyhd8ed1ab_0 \
    scisave==1.6.0=pyhd8ed1ab_0 \
    numpy==2.1.3=py312h58c1407_0 \
    scipy==1.14.1=py312h62794b6_1 \
    joblib==1.4.2=pyhd8ed1ab_0 \
    vtk==9.3.1=osmesa_py312h838d114_109 \
    pyvista==0.44.2=pyhd8ed1ab_0 \
    shapely==2.0.6=py312h391bc85_2 \
    rasterio==1.4.2=py312h8cae83d_1 \
    pillow==11.0.0=py312h7b63e92_0 \
    matplotlib-base==3.9.2=py312hd3ec401_2 \
    jupyterlab==4.3.1=pyhff2d567_0 \
    jupyter-server-proxy==4.4.0=pyhd8ed1ab_0 \
    ipywidgets==8.1.5=pyhd8ed1ab_0 \
    trame-vtk==2.8.12=pyhbc30e4a_0 \
    trame-vuetify==2.7.2=pyhff2d567_0 \
    trame==3.7.0=pyhd8ed1ab_0 \
    ipympl=0.9.4=pyhd8ed1ab_0

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
