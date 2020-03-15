# Presctl - Presidio's CLI utility

## Installation
1) Navigate to the presctl directory
2) Run 'make' and the presctl binary will be created

## Usage
### prerequisites
1. Running presidio cluster, either locally or remotely
2. create a configuration file named '.presctl.yaml', place it in $HOME/.presctl.yaml and populate the required values [example file](example.presctl.yaml)

### Instructions
Simply running presctl will output the usage instructions
```sh
$ ./presctl
```

![usage output](./docs/images/usage-output.png)

#### Examples

1. Adding a new template
    ```sh
    $ ./presctl add template mytemplate --action analyze --project myproject -f template_def.json
    ```

2. Analyze using the new template
    ```sh
    ./presctl analyze --project myproject -l mytemplate -s "see you tomorrow"
    ```

3. Uploading a custom analyze recognizer
    ```sh
    ./presctl add recognizer myrecognizer -f recognizer.json
    ```

multiple examples (json files) can be found [here](../presidio-tester/cmd/presidio-tester/testdata/) (templates / recognizers / analyze and anonymize requests)