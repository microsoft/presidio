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
```bash
$ ./presctl
```

![usage output](./docs/images/usage-output.png)

#### Examples

1. Adding a new template 
    ```bash
    $ ./presctl add template --action analyze --project myprojectname --template mynewtemplatename --file template_def.json
    ```

2. Analyze using the new template
    ```bash
    ./presctl analyze --project myprojectname --analyzeTemplateId mynewtemplatename --string "see you tomorrow"
    ```