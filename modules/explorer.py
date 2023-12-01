import os

class Explorer:
    def __init__(self, directory="./"):
        self.directory = directory
        if not self.directory.endswith("/"):
            self.directory += "/"

    def __iter__(self):
        if not os.path.isdir(self.directory):
            return iter([])
        return iter(os.listdir(self.directory))

    def find(self, needle):
        for file in self:
            if file == needle:
                return True, self.directory + file
        return False, ""

    def fmap(self, f):
        html_string = ""
        for file in self:
            full_path = self.directory + file
            html_string += str(f(file, full_path)) + "\n"
        return html_string

