import importlib
import inspect
import os
import glob
from entity_recognizer import EntityRecognizer


class RecognizerRegistry():

    def load_entity_recognizers(self):
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        recognizer_directory_path = os.path.join(SCRIPT_DIR, 'recognizers')
        return self.__load(recognizer_directory_path, base_class=EntityRecognizer)

    def __load(self, plugins_package_directory_path, base_class=None, create_instance=True, filter_abstract=True):

        plugins_package_name = os.path.basename(plugins_package_directory_path)
        result = []
        # -----------------------------
        # Iterate all python files within that directory
        plugin_file_paths = glob.glob(os.path.join(plugins_package_directory_path, "*.py"))
        for plugin_file_path in plugin_file_paths:
            plugin_file_name = os.path.basename(plugin_file_path)

            module_name = os.path.splitext(plugin_file_name)[0]

            if module_name.startswith("__"):
                continue

            # -----------------------------
            # Import python file

            module = importlib.import_module("." + module_name, package=plugins_package_name)

            # -----------------------------
            # Iterate items inside imported python file
            for item in dir(module):
                
                value = getattr(module, item)
                if not value:
                    continue
                
                if not inspect.isclass(value):
                    continue
              
                if filter_abstract and inspect.isabstract(value):
                    continue
                print(value)
                if base_class is not None:
                    if isinstance(value) != type(base_class):
                        continue

                # -----------------------------
                # Instantiate / return type (depends on create_instance)

                #yield value() if create_instance else value
                if create_instance:
                    result.append(value())
                else:
                    result.append(value)
          
        return result
