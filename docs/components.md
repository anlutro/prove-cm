# Components

Instead of this file structure:

	states/
		webserver/
			install.yml
			sites.yml
	files/
		webserver/
			nginx.conf
			vhost.conf

You can have this:

	components/
		webserver/
			states/
				install.yml
				sites.yml
			files/
				nginx.conf
				vhost.conf

The two are functionally equivalent, but components are more self-contained and better organized in the file structure, and are easier to distribute as re-usable modules.
