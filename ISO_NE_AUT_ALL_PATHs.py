import json
class Files:
    pass
    def json_dumps_function(self,my_variable):
        with open('ISO_NE_AUT_PATHS.json', 'r') as json_file:
            data = json.load(json_file)
        print(data)
        return data[my_variable]