![HyperStream logo](https://cdn.rawgit.com/IRC-SPHERE/HyperStream/dfbac332/hyperstream.svg)


# HyperStreamViewer
Web-app dashboard and visualisation for viewing [HyperStream](https://github.com/IRC-SPHERE/HyperStream) output. Hyperstream is a large-scale, flexible and robust software package for processing streaming data.

# Installation #
## Docker images ##
If you do not want to install all the packages separately you can use our Docker bundle available [here](https://github.com/IRC-SPHERE/Hyperstream-Dockerfiles).

## Local machine ##

``` Bash
git clone git@github.com:IRC-SPHERE/HyperStreamViewer.git
cd HyperStreamViewer
virtuenv venv
. venv/bin/activate
pip install -r requirements.txt
```

It is also necessary to install some javascript libraries using bower. In case
you do not have bower installed follow the next steps (for Debian based OS):

``` Bash
sudo aptitude install npm nodejs-legacy
sudo npm install -g bower
bower install
```

It is necessary to create a file hyperstream_config.json

*TODO* Fill this section

To run HyperStream with the SPHERE plugins it is the sphere plugins in the
current folder

    sphere-hyperstream/SPHERE-HyperStream/sphere_plugins

Now you can start the server in the port 5000

```
python server.py

```

# License #

This code is released under the [MIT license](https://github.com/IRC-SPHERE/Infer.NET-helpers/blob/master/LICENSE).

# Acknowledgements #

This work has been funded by the UK Engineering and Physical Sciences Research Council (EPSRC) under Grant [EP/K031910/1](http://gow.epsrc.ac.uk/NGBOViewGrant.aspx?GrantRef=EP/K031910/1) -  "SPHERE Interdisciplinary Research Collaboration".
