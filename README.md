# [TEAW-Website](https://toendallwars.org/)


## TODO:
- [ ] Figure out how to not erase db dir on push to prod (data will be lost!)
- [ ] Improve tmux script


## Git guidelines
There are two branches, `prod` and `dev`. The default is `dev`, and where any changes should be made. 

In the future, changes will be deployed by bringing changes over from dev (or some other branch) to prod using a pull request.
Only once approved, will the PR be merged, and the new changes deployed using a GH webhook. 

Before submitting a PR, run the VS Code task to generate the requirements.txt file for pip.


## Starting a development server
To start a local version of the website for testing/development, run the
`teaw_webserver.py` file. This will start Flask in debug mode, with the logger set
to the DEBUG level. This will also enable Flask's debug mode. For any changes to show
up on the website, the process must be restarted.

> [!NOTE]
> In order for the server and API to work, the SQLite DBs will need to contain information. By default, there is some 
data in them. The data will not be updated unless the `db_updater.py` and `stats_updater.py` processes are started, 
but thats not needed for development. 

TODO: add the example data.



## Starting a production server
Before we start, we need to set up the proxy to the Bluemap. TEAW's map is using HTTP, so when we
use it in an iframe we run into issues where the browser prevent the connection, as the website is using HTTPS.
To fix this, we use an nginx proxy. This allows us to use a Cloudflare tunnel to point to the proxy on the server, which then
points to the map. This allows the tunnel to use HTTPS, so we don't run into any browser security rules. 

This has the added benefit of not requiring a port number on the public facing URL for the map. 

To start the proxy, run the `bluemap_proxy.sh` file in the root directory. 



To deploy the server, run the `run_prod.sh` script with Bash. This will take the Flask `app` variable inside the
`teaw_webserver` script, and start it with Gunicorn. Note that this disables any debugging features, and can only be ran on Linux.

The `db_updater.py` and `stats_updater.py` processes need to be started, so the databases are updated. It is best to use 
[tmux](https://github.com/tmux/tmux?tab=readme-ov-file#welcome-to-tmux) to open and keep running the DB updaters and the webserver.
In the future there will be a Bash script to automatically destroy an existing tmux session, and create new ones which contain the 
required processes.

(yes I know tmux is not a proper process management tool, but it works well)