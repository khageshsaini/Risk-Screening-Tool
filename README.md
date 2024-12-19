# Climate RiSc-Tool

Climate RiSc Tool provides a free, publicly accessible, open-source platform for calculating, understanding, and indentiying climate impacts in power systems. While power system tools struggle to integrate large climate datasets, RiSc provides a fast and approximate method for identifying time periods and events of potential high risk of energy shortfalls across many Global Climate Models (GCMs), Shared Socioeconomic Pathways (SSPs) and with granular time and geospatial resoltions. High-Impact Low Frequency events can be used to facilitate climate-informed integrated system planning and guide resilience and adaptation strategies when properly integrating them in capacity expansion, resource adequacy and production cost models. RiSc also facilitates the understanding of structural system vulnerabilities of plausible future capacity buildout scenarios. It allows to assess how climate change will impact the power system under different horizons and scenarios. 

Climate RiSc was developed as part of the EPRI Resource Adequacy Iniatiave and Climate READi. EPRI plans to support continuing updates and enhancements.

## Getting Started

These instruction will help you to deploy RiSc on a remote/enterpise server and run a demo case. See the Software Manual for more detailed information including screenshots.

### Installation

1. #### Clone/download this repository onto your server.

	Get Git installed on your server.

	Navigate to a folder on your server where you want to place the tool. 

	Enter the following command from a terminal/prompt to 'clone' the repo and download it to your computer:
        ```
        git clone  https://github.com/epri-dev/Climate-RiSc-Tool.git
        ```
	When cloning a repo with 'git clone', if you do not specify a new directory as the last argument (as shown above),
	it will be named `Climate-RiSc-Tool`. Alternatively, you can specify this and name it as you please. 
        
	Note: You can also clone your repo on your local computer and transfer it to the server through a mount or SFTP.

2. #### Pull and load the docker image

	Get docker installed on your server. 
	
	When risctool docker image is provided as .tar file in this repo. run the command: `docker load -i risctool_docker.tar`. 

	If the docker image is provided through a public registry run docker `docker pull risctool:1.0`. If no tag is specified, Docker will pull the latest tag by default.
 	
 	Finally verity that the image is loaded `docker images`.

	Note: You might you need must have privileges (e.g., sudo in bash) to run docker commands including pulling and running docker images. 

3. #### Run the application
	
	Make sure the .env file is available in the application directory. The.env file should contain two variables: DJANGO_KEY and DB_PASSWORD

	Docker compose file `deft.yml` contain all the required configuration settings to run the containers. However, to run the tool from your local laptop (otherwise comment this line using #) you will have to modify and specify the mount path in the docker compose backend volumes  `<your_mount_path>/input:/code/share` to your own path. 

	Finally, execute `./up.sh` to run the containers and `./down.sh` to stop and remove them. Note: you might need priviledges to perform this (e.g., `sudo`) 
	
	

### Running Your First Case: DEMO

This version comes with a demo datset to test the application. The public input data is specific of the Texas power system. 

1. #### Configuration settings
	Navigate to the `demo` folder. There are two files  `config.yml` and  `sysconfig.yml`. Both are ready to be used when running the tool locally (on your server)

	If you want to run the tool remotely (on your local laptop) in the `config.yml` you need to change `sync_type` from 'local' to 'remote_share'. In addition, in `sysconfig.yml` you need to change the `hostname`. 

	Note: Username and password should not be changed. 

2. #### Running the tool locally (on your server)

	You need to access the docker container running this command `docker exec -it deft-backend-1 bash`. 
	
	Make sure that the input data has been correctly transferred to the `cd backend/demo/input` folder inside the container. Run `docker cp /home/Climate-RiSc-Tool/demo/input/ deft-backend-1:/code/backend/demo/ `

	Finally, run the case executing `python demo.py` in the demo folder within the container.

	Solution will appear in the container `backend/demo/output` folder. You can export this running `docker cp deft-backend-1:/code/backend/demo/output /home/Climate-RiSc-Tool/demo/`

3. #### Running the tool remotely (on your local computer)
	
	After changing configuration settings accordingly as decribed in step 1 and configure the mount (heavy files are transferred through this channel).
	
	Then, run the python demo.py script on your local machine:  `python demo.py` 

	Note: remember to set-up the mount path as volume in the deft.yml file (docker-compose file)

## Deployment

The application is designed to run on enterprise environments where deployment is secure and not publicly exposed to the internet. A docker-proxy set-up to encript http requests through https is recommended. 

## Versioning

This is version 0.1 (1/1/2025)

## Authors

* **Amir Cicak**
* **Juan Carlos Martin**
* **Eamonn Lannoye**

## Contributing
Pull requests are welcome. For major changes, please contact the team to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

This project is licensed under the BSD (3-clause) License - see [LICENSE.txt](./LICENSE.txt).
