# News-Aggregation
News Aggregation  Web Application


*Python install

	  sudo apt install python3.9

*Verify  that the python installation was sucessfull by typing

	  sudo python3.9 –version

*Update the packages list and install the prerequisites (pre essential requirements)

	  sudo apt update
	  sudo apt install software-properties-common

*PIP insatall

	  sudo apt install python3-pip
 
*When the installation is complete verify the installation by checking pip version

	  pip3 –version

*Creating  virtual environment (for source code folder)

	  sudo python3 -m venv env

*For activating virtual environment

	  source env/bin/activate

*Installation for requirements

	  pip3 install -r requirements.txt

*Install docker(docker installation commands)

	   sudo apt install docker
	   sudo systemctl status docker(docker status i.e active or inactive)

*Flask install

	   sudo pip3 install flask


*Verify the installation,run the following command, which prints the Flask 	version:

	  sudo python3 -m  flask --version

*This command will launch the developement builtin server

  	python3 app.py

      *Output

		     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 

*Create a docker file

	  nano dockerfile(text reader, file name)

	    	FROM python:3.8
		    WORKDIR  /app
		    EXPOSE 5001
		    COPY requirements.txt /app
		    RUN pip3 install -r requirements.txt
		    COPY . /app
		    CMD [ “python3”,”app.py” ]

 *Build docker image

	  docker build - -tag lakshman .

*Run docker image

	  sudo docker run lakshman

	    	*Output

		    	* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
