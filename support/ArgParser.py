import argparse
import importlib
import ast

#from support.Config import config
from configurations.Config import config

class ArgParser:
    parser = None

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="PMCSN project command line interface")
        #parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")
        self.parser.add_argument("-cf", "--configFile", metavar="FILEPATH", help="specify a configuration file to load")
        self.parser.add_argument("-scf", "--storeConfigFile", metavar="FILEPATH", help="specify an output file where to store config")
        self.parser.add_argument("-fh", "--finite_horizont", action="store_true", help="simulate a finite horizont case")
        self.parser.add_argument("-ih", "--infinite_horizont", action="store_true", help="simulate a finite horizont case. Use with -st/--slot-time")
        self.parser.add_argument("-cc", "--change_config", nargs=2, metavar=("OPTION", "VALUE"), action='append', help="specify configuration to change")
        self.parser.add_argument("-fb", "--find_b_value", metavar=("THRESHOLD"), help="find the value of b such tath autocorellation lag j=1 is <= THRESHOLD")
        self.parser.add_argument("-s", "--seed", metavar=("SEED"), help="use the given SEED as random seed. if SEED = 0 then the initial seed is to be supplied interactively; if SEED < 0 then the initial seed is obtained from the system clock; if SEED > 0 > 0 then it is the initial seed (unless too large). default value is 0")
        self.parser.add_argument("-ngf", "--no_gaussian_factor", action="store_true", help="don't use the gaussian probability value to weight interarrival times")
        

    def parse(self):
        args = self.parser.parse_args()
        if args.configFile:
            configFilePath = args.configFile
            self.loadPersonalConfig(configFilePath)
        if args.change_config:
            self.changeConfig(args.change_config)
        if args.storeConfigFile:
            self.storePersonalConfig(args.storeConfigFile)
        
        if args.finite_horizont:
            if not args.infinite_horizont:
                config.FINITE_H = True
            else:
                raise argparse.ArgumentTypeError("Cannot perform finite and infinite horizont together.")
        
        if args.infinite_horizont:
            if not args.finite_horizont:
                config.INFINITE_H = True
            else:
                raise argparse.ArgumentTypeError("Cannot perform finite and infinite horizont together.")
        
        if args.find_b_value:
            config.FIND_B_VALUE = True

        if args.seed:
            config.SEED = int(args.seed)

        if args.no_gaussian_factor:
            config.USE_GAUSSIAN_FACTOR = False


    def storePersonalConfig(self, filePath):
        try:
            config.storeConfig(filePath)
        except Exception as e:
            print(e)
            raise argparse.ArgumentTypeError("Invalid output path.")


    def loadPersonalConfig(self, filePath):
        global config
        try:
            newConfig = importlib.import_module(filePath.strip('.py'))
            config = newConfig.Config()
        except Exception as e:
            print(e)
            raise argparse.ArgumentTypeError("Invalid file.")


    
    def changeConfig(self, listOption):
        # list option is [ ['OPTION1', 'VALUE1'], ['OPTION2', 'VALUE2'], ...]
        # and its relative to -cc option
        global config
        type_converters = {
            int: int,
            float: float,
            str: str,
            list: lambda x: ast.literal_eval(x),
            bool: lambda x: x.lower() in ('true', 'yes', '1')
        }
        try:
            for l in listOption:
                attr = l[0]
                value = l[1]
                original_value = getattr(config, attr)
                new_value = None

                value_type = type(original_value)
                if value_type in type_converters:
                    new_value = type_converters[value_type](value)
                    # check if the new format is the same of the original one:
                    if type(new_value) != value_type:
                        raise ValueError(f"Bad format type representation. Please use brackets for list.")
                    else:
                        setattr(config, attr, new_value)
                else:
                    raise TypeError(f"Unsupported attribute type: {value_type}")
                

        except AttributeError:
            raise argparse.ArgumentTypeError("Given configuration attribute doesn't exist.")
        except ValueError:
            raise argparse.ArgumentTypeError("Invalid value format.")
        except TypeError as e:
            raise argparse.ArgumentTypeError(str(e))

        
