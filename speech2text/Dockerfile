FROM flml/flashlight:cpu-consolidation-c427031 as flashlight_base

FROM ubuntu:20.04

ENV APT_INSTALL="apt-get install -y --no-install-recommends"

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
        # for glog
        libgoogle-glog-dev libgoogle-glog0v5 \
        libmkl-intel-lp64 libmkl-core libmkl-gnu-thread \
        libopenmpi3 libatlas3-base libfftw3-3 liblapacke \ 
        # python sox
        sox python3-dev python3-pip python3-distutils && \
        # python (for bindings and preprocessing)
        python3 -m pip --no-cache-dir install --upgrade setuptools numpy sox tqdm && \
# ==================================================================
# clean up everything
# ------------------------------------------------------------------
    apt-get clean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/*

COPY --from=flashlight_base  /opt/arrayfire  /opt/arrayfire
COPY --from=flashlight_base     /opt/onednn     /opt/onednn
COPY --from=flashlight_base       /opt/gloo       /opt/gloo
COPY --from=flashlight_base      /opt/kenlm      /opt/kenlm

ENV MKLROOT="/opt/intel/mkl"
ENV KENLM_ROOT=/opt/kenlm

COPY --from=flashlight_base /root/flashlight /root/flashlight


WORKDIR /app

ADD requirements.txt requirements.txt
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

ADD transcriber.py transcriber.py
ADD app.py app.py

CMD ["python3", "app.py"]