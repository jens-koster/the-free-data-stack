# Papermill container for running notebooks

Run a notebook in papermill.
Intended as entrypoint to a docker container

test interactively as:

    python3 book_runner.py --notebook helloworld --parameters '{"p1":"hello", "p2":"world"}'

To test the container version, first build it:

    docker compose build

then run the helloworld notebook in a container

    docker compose run book-runner --notebook 'helloworld' --parameters '{"p1":"hello", "p2":"world"}'

to open a shell inside a docker for troubleshooting dependencies.

    docker compose run --remove-orphans --rm -it --entrypoint /bin/bash book-runner


To configure a venv as jupyter kernel:
    # unless it is alreayd there:
    pip install ipykernel
    python -m ipykernel install --user --name=your_venv_name --display-name "Python (your_venv_name)"


Activate the New Virtual Environment
Activate the virtual environment where you installed the required dependencies (e.g., pyspark):

Install ipykernel in the Virtual Environment
Ensure that the ipykernel package is installed in your virtual environment:

    pip install ipykernel

Add the Virtual Environment to Jupyter
Register the virtual environment as a Jupyter kernel:

    python -m ipykernel install --user --name=your_venv_name --display-name "Python (your_venv_name)"

Replace your_venv_name with the name of your virtual environment.
The --display-name is what will appear in the Jupyter Notebook interface.

Restart Jupyter Notebook
Restart your Jupyter Notebook server:

    jupyter notebook

Select the Correct Kernel
Open your notebook in Jupyter.
Go to the Kernel menu > Change Kernel.
Select the kernel corresponding to your virtual environment (e.g., Python (your_venv_name)).