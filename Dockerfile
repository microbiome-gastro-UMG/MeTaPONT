# Use the official image as a parent image.
FROM ubuntu:20.04

# Set the working directory.
WORKDIR /

RUN apt-get update && apt-get -y upgrade

RUN apt-get -y install cdbfasta
RUN apt-get -y install bc
RUN apt-get -y install python3
RUN apt-get update && apt-get -y install python3-pip
RUN pip3 install pandas

RUN apt-get -y install git

#Centrifuge
WORKDIR /programs
RUN git clone https://github.com/infphilo/centrifuge
WORKDIR /programs/centrifuge
RUN make
ENV PATH "$PATH:/programs/centrifuge/"

#minimap2
WORKDIR /programs
RUN git clone https://github.com/lh3/minimap2
WORKDIR /programs/minimap2
RUN make
ENV PATH "$PATH:/programs/minimap2/"

#copy script to docker
WORKDIR /src
COPY metapont ./metapont
COPY mmp2_processing.py ./mmp2_processing.py
COPY centrifuge_processing.py ./centrifuge_processing.py

#make directory to host Database, input and output in
WORKDIR /database
WORKDIR /input
WORKDIR /output
WORKDIR /files
RUN chmod 777 /files

WORKDIR /
ENTRYPOINT ["/src/metapont"]
