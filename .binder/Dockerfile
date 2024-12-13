# Definition of the Docker image with PyPEEC and Jupyter.
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

# copy the package lists
COPY --chown=${NB_UID}:${NB_GID} pkgs.txt .

# install all the dependencies (but not PyPEEC)
RUN mamba install --yes --channel conda-forge --file pkgs.txt

# install PyPEEC (no-deps as everything required has been installed)
RUN mamba install --yes --no-deps conda-forge::pypeec

# clean mamba and fix permissions
RUN mamba clean --all --force-pkgs-dirs --yes
RUN fix-permissions "${CONDA_DIR}" 
RUN fix-permissions "/home/${NB_USER}"

# extract the PyPEEC examples
RUN pypeec examples .

# clean the workspace
RUN rm -rf *.py
RUN rm -rf *.sh
RUN rm -rf pkgs.txt
RUN rm -rf work

# allow Jupyter to display VTK graphics
ENV PYVISTA_TRAME_SERVER_PROXY_PREFIX="/proxy/"

# ensure that the working directory and folder are correct
USER ${NB_UID}
WORKDIR ${HOME}
