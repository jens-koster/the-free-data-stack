from book_runner import
def test_hello_world():
    # os.environ["TFDS_CONFIG_URL"] = "http://127.0.0.1:8005/api/configs"
    os.environ["TFSD_CONFIG_LOCALHOST"] = "Yes please"
    execute_notebook(notebook="helloworld", parameters={"p1": "hello", "p2": "world"})
