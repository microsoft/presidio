# End-to-end tests

This folder contains end-to-end tests for Presidio.
It requires the different services to be running as HTTP services.

Steps:
1. [Install presidio](https://microsoft.github.io/presidio/installation/)
2. Run services, e.g., using `docker-compose`:
    ```sh
   docker-compose up --build -d 
   ```
   Note that these might take some time to build for the first time.
   
3. Install the e2e-tests framework, preferrably in a virtual environment:
   ```sh
   pip install -r requirements.txt
   ```
4. Run tests:
   ```
   pytest
   ```

See more information on [Presidio's documentation on E2E tests](https://microsoft.github.io/presidio/development/#end-to-end-tests).